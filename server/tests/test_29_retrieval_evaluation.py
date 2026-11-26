"""Hand-checked metric and fixture tests; no live semantic or capacity claims."""
import unittest
from uuid import UUID
from typing import Any
from unittest.mock import patch

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.pipeline.storage import Storage
from app.schemas.retrieval import RetrievedChunk

from tests import scoped_retrieval_evaluation as evaluation
from tests.test_28_scoped_retrieval import Provider


class EvaluationTests(unittest.TestCase):
    """Independent labels verify denominators, evidence coverage and timing boundaries."""

    def result(self, identifier: UUID, index: int) -> RetrievedChunk:
        return RetrievedChunk(file_id=identifier, chunk_index=index, score=.5,
                              token_count=7, text='context', display_text='source',
                              page=None, heading=None, section=None)

    def test_fixed_corpus_labels_and_candidate_matrix(self) -> None:
        corpus = evaluation.load()
        self.assertEqual(corpus.version, 'aster-v1')
        self.assertEqual(len(corpus.questions), 30)
        self.assertEqual(len(corpus.scope().file_ids), 10)
        self.assertEqual(len(corpus.files), 12)
        self.assertEqual(len(evaluation.payloads(
            corpus, lambda text: len(text.split()))), 36)
        self.assertEqual([sum(question.kind == kind for question in corpus.questions)
                          for kind in ('single', 'paraphrase', 'cross', 'unsupported')], [10, 10, 6, 4])
        cases = evaluation.capacity_matrix()
        self.assertEqual(len(cases), 16)
        self.assertEqual({case.files for case in cases}, {10, 50, 100, 250})
        self.assertEqual({case.chunks_per_file for case in cases}, {2, 20})
        self.assertEqual({case.excluded_points for case in cases}, {0, 1000})
        for case in cases:
            self.assertEqual(len(case.scope().file_ids), case.files)

    def test_recall_file_coverage_and_complete_evidence_are_independent(self) -> None:
        first, second = UUID(int=1), UUID(int=2)
        question = evaluation.Question(id='hand', kind='cross', question='synthetic', evidence=[
            evaluation.Evidence(file_id=first, chunk_index=0),
            evaluation.Evidence(file_id=first, chunk_index=1),
            evaluation.Evidence(file_id=second, chunk_index=0)])
        results = [self.result(first, 0), self.result(
            first, 99), self.result(second, 0)]
        measured = evaluation.metrics(question, results)
        self.assertEqual(measured['recall'], 2 / 3)
        self.assertEqual(measured['required_file_coverage'], 1.0)
        self.assertTrue(measured['hit'])
        self.assertFalse(measured['all_evidence'])
        self.assertEqual(measured['stored_token_count'], 21)
        measured = evaluation.metrics(question, [self.result(first, 99)])
        self.assertEqual(measured['required_file_coverage'], 0)
        self.assertEqual(measured['recall'], 0)

    def test_unsupported_excluded_from_positive_denominators_and_failures_retained(self) -> None:
        corpus = evaluation.load()
        calls = []

        def failed(question, scope, limit):
            calls.append((scope.file_ids, limit))
            raise ValueError('private synthetic failure')

        report = evaluation.evaluate(corpus, failed)
        self.assertEqual(len(calls), 90)
        self.assertEqual({files for files, _ in calls},
                         {corpus.scope().file_ids})
        for experiment in report.values():
            summary = experiment['summary']
            self.assertEqual(summary['positive_queries'], 26)
            self.assertEqual(summary['unsupported_queries'], 4)
            self.assertEqual(summary['failures'], 30)
            self.assertEqual(summary['recall_at_k'], 0)
            self.assertEqual(summary['hit_rate'], 0)
            self.assertEqual(summary['cross_all_evidence_success'], 0)
            self.assertNotIn('private synthetic failure', str(experiment))
            for row in experiment['queries']:
                if row['kind'] == 'unsupported':
                    self.assertIsNone(row['metrics']['recall'])
                    self.assertIsNone(row['metrics']['all_evidence'])

    def test_controlled_oracle_exercises_pipeline_without_semantic_claim(self) -> None:
        report = evaluation.controlled(evaluation.load())
        for experiment in report.values():
            self.assertEqual(experiment['summary']['failures'], 0)
            self.assertEqual(experiment['summary']['recall_at_k'], 1)
            self.assertEqual(experiment['summary']
                             ['cross_all_evidence_success'], 1)

    def test_percentiles_match_hand_calculation(self) -> None:
        self.assertIsNone(evaluation.percentile([], .5))
        self.assertEqual(evaluation.percentile([1, 2, 3, 4], .5), 2.5)
        measured = evaluation.percentile([1, 2, 3, 4], .95)
        assert measured is not None
        self.assertAlmostEqual(measured, 3.85)
        self.assertEqual(evaluation.percentile([7], .95), 7)

    def test_capacity_precomputed_queries_counts_and_independent_embedding_timing(self) -> None:
        case = evaluation.Capacity(2, 3, 4)
        client = QdrantClient(':memory:')
        self.addCleanup(client.close)
        client.create_collection('capacity', vectors_config=VectorParams(
            size=3, distance=Distance.COSINE))
        points = evaluation.capacity_points(case, 3)
        client.upsert('capacity', points, wait=True)
        self.assertEqual(len({str(point.id) for point in points}), 10)
        provider = Provider()
        services = Storage(provider, client, 'capacity')
        with patch('app.pipeline.retrieval.storage', return_value=services), patch.object(client, 'query_points', wraps=client.query_points) as search:
            rows = evaluation.measure_capacity(
                services, case, 'q', repeats=3, warmups=1, scope=case.scope())
        self.assertEqual(len(provider.calls), 4)
        self.assertEqual(search.call_count, 15)
        for row in rows:
            self.assertEqual(row['measurements'], 3)
            self.assertEqual(len(row['qdrant_seconds']), 3)
            self.assertEqual(row['total_points'], 10)
            self.assertEqual(row['eligible_points'], 6)
            self.assertEqual(row['filter_ids'], 2)
            self.assertGreater(row['filter_bytes'], 0)
        with self.assertRaisesRegex(ValueError, 'inventory'):
            evaluation.measure_capacity(
                services, evaluation.Capacity(2, 4, 4), 'q', repeats=1)
        calls = len(provider.calls)
        with self.assertRaisesRegex(ValueError, 'scope'):
            evaluation.measure_capacity(
                services, case, 'q', scope=evaluation.Capacity(1, 3, 4).scope())
        self.assertEqual(len(provider.calls), calls)

    def test_fixture_validation_rejects_unknown_or_duplicate_labels(self) -> None:
        original = evaluation.load().model_dump(mode='json')
        for field in ('unknown', 'duplicate', 'unsupported'):
            changed: dict[str, Any] = evaluation.Corpus.model_validate(
                original).model_dump(mode='json')
            labels = changed['questions'][0]['evidence']
            if field == 'unknown':
                labels[0]['file_id'] = str(UUID(int=1))
            elif field == 'duplicate':
                labels.append(labels[0])
            else:
                changed['questions'][0]['kind'] = 'unsupported'
            with patch.object(evaluation.Corpus, 'model_validate_json', return_value=evaluation.Corpus.model_validate(changed)):
                with self.assertRaises(ValueError):
                    evaluation.load()
