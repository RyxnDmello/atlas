"""Offline scope retrieval uses controlled vectors and isolated in-memory datastores."""
import unittest
from threading import Event
from typing import Any, cast
from uuid import UUID, uuid4
from httpx import ConnectError
from unittest.mock import patch
from pydantic import ValidationError
from concurrent.futures import ThreadPoolExecutor

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.http.models import Distance, PointStruct, QueryResponse, ScoredPoint, VectorParams

from app.pipeline.storage import Storage
from app.pipeline.retrieval import retrieve_scoped

from app.models.postgres import File
from app.models.qdrant.chunk import Chunk

from app.db.qdrant import query_scoped
from app.schemas.scope import AuthorizedFileScope, FileSource

from app.errors.api import ApiError
from app.errors.qdrant import QdrantCollectionError, QdrantConnectionError

from tests import test_27_folder_scope as folders


class Provider:
    """Return a known unit direction without loading any model."""
    dimension = 3

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)

        return [[1.0, 0.0, 0.0] for _ in texts]


class ScopedRetrievalTests(unittest.TestCase):
    """Prove pre-ranking membership, resource safety, integrity and snapshot behavior."""

    def setUp(self) -> None:
        self.provider = Provider()
        self.client = QdrantClient(':memory:')
        self.addCleanup(self.client.close)
        self.client.create_collection(
            'scoped', vectors_config=VectorParams(size=3, distance=Distance.COSINE))
        self.services = Storage(self.provider, self.client, 'scoped')
        runtime = patch('app.pipeline.retrieval.storage',
                        return_value=self.services)
        self.access = runtime.start()
        self.addCleanup(runtime.stop)
        self.identifiers = (UUID(int=1), UUID(int=2))
        self.scope = self.scope_for(*self.identifiers)
        self.points = []
        for offset, identifier in enumerate(self.identifiers):
            for index in range(12):
                score = 0.1 + (index * 2 + offset) * 0.03
                self.points.append(PointStruct(
                    id=str(uuid4()), vector=[score, (1 - score ** 2) ** 0.5, 0.0],
                    payload=self.payload(identifier, index).model_dump(mode='json')))
        for category in ('foreign', 'descendant', 'sibling', 'root', 'orphan'):
            self.points.append(PointStruct(id=str(uuid4()), vector=[1.0, 0.0, 0.0],
                                           payload=self.payload(uuid4(), 0, category).model_dump(mode='json')))
        self.client.upsert('scoped', self.points, wait=True)

    def scope_for(self, *identifiers: UUID) -> AuthorizedFileScope:
        return AuthorizedFileScope(tuple(FileSource(identifier, 'synthetic.md') for identifier in identifiers))

    def payload(self, identifier: UUID, index: int, label: str = 'source') -> Chunk:
        return Chunk(file_id=identifier, chunk_index=index, token_count=index + 10,
                     text=f'Contextual {label} {index}', display_text=f'Raw {label} {index}',
                     page=None, heading='Policy', section=None)

    def test_global_limits_full_filter_order_scores_and_read_only(self) -> None:
        before = self.client.scroll('scoped', limit=100, with_vectors=True)
        for limit in (1, 5, 8, 12, 20):
            with self.subTest(limit=limit), patch.object(self.client, 'query_points', wraps=self.client.query_points) as search:
                results = retrieve_scoped(
                    '  synthetic question \n', self.scope, limit)
                search.assert_called_once()
                args = search.call_args.kwargs
                self.assertEqual(args['limit'], limit)
                self.assertEqual(args['collection_name'], 'scoped')
                self.assertEqual(args['query'], [1.0, 0.0, 0.0])
                self.assertTrue(args['with_payload'])
                self.assertFalse(args['with_vectors'])
                self.assertNotIn('score_threshold', args)
                self.assertEqual(args['query_filter'].model_dump(exclude_none=True),
                                 {'must': [{'key': 'file_id', 'match': {'any': sorted(map(str, self.identifiers))}}]})
            expected = self.client.query_points(**args).points
            self.assertEqual(len(results), limit)
            self.assertEqual([item.model_dump(mode='json') for item in results],
                             [{**cast(dict, point.payload), 'score': point.score} for point in expected])
            self.assertTrue(
                all(item.file_id in self.scope.file_ids for item in results))
        self.assertEqual(self.provider.calls, [['synthetic question']] * 5)
        self.assertEqual(self.client.scroll(
            'scoped', limit=100, with_vectors=True), before)
        self.assertEqual({(item.file_id, item.chunk_index) for item in retrieve_scoped('q', self.scope, 5)},
                         {(self.identifiers[1], 11), (self.identifiers[0], 11),
                          (self.identifiers[1], 10), (self.identifiers[0], 10), (self.identifiers[1], 9)})

    def test_complete_candidate_scope_and_duplicate_uuid_deduplication(self) -> None:
        identifiers = tuple(UUID(int=index) for index in range(1, 101))
        scope = self.scope_for(*reversed(identifiers), identifiers[0])
        with patch.object(self.client, 'query_points', wraps=self.client.query_points) as search:
            self.assertEqual(len(retrieve_scoped('q', scope, 20)), 20)
        values = search.call_args.kwargs['query_filter'].model_dump(exclude_none=True)[
            'must'][0]['match']['any']
        self.assertEqual(values, sorted(map(str, identifiers)))
        self.assertEqual(len(values), 100)

    def test_empty_scope_and_no_hits_are_distinct_resource_paths(self) -> None:
        with patch.object(self.client, 'query_points', wraps=self.client.query_points) as search:
            self.assertEqual(retrieve_scoped(
                'q', AuthorizedFileScope(()), 5), [])
            self.access.assert_not_called()
            self.assertEqual(self.provider.calls, [])
            search.assert_not_called()
            self.assertEqual(retrieve_scoped(
                'q', self.scope_for(uuid4()), 5), [])
            search.assert_called_once()
        self.assertEqual(self.provider.calls, [['q']])
        self.assertEqual(
            len(retrieve_scoped('q', self.scope_for(self.identifiers[0]), 20)), 12)

    def test_invalid_inputs_fail_before_resources_even_when_empty(self) -> None:
        empty = AuthorizedFileScope(())
        cases: list[tuple[Any, Any, Any]] = [
            ('', empty, 5), (' \n', empty, 5), (None, empty, 5), (7, empty, 5),
            *[('q', empty, value)
              for value in (True, False, 1.0, '8', None, 0, 21, -1)],
            ('q', None, 5), ('q', [], 5), ('q', self.identifiers, 5),
            ('q', AuthorizedFileScope(cast(Any, [])), 5),
            ('q', AuthorizedFileScope(cast(Any, (object(),))), 5),
            ('q', AuthorizedFileScope(
                (FileSource(cast(Any, str(self.identifiers[0])), 'name'),)), 5),
            ('q', AuthorizedFileScope(
                (FileSource(self.identifiers[0], cast(Any, None)),)), 5),
        ]
        for question, scope, limit in cases:
            with self.subTest(question=question, scope=scope, limit=limit):
                with self.assertRaises((ValueError, ValidationError)):
                    retrieve_scoped(question, scope, limit)
        self.access.assert_not_called()
        self.assertEqual(self.provider.calls, [])

    def test_invalid_vectors_and_embedding_failures_never_query(self) -> None:
        for vectors in ([], [[1.0]], [[1.0, 0.0, 0.0]] * 2, [[0.0] * 3],
                        [[float('nan'), 0.0, 0.0]], [[float('inf'), 0.0, 0.0]]):
            with self.subTest(vectors=vectors), patch.object(self.provider, 'embed', return_value=vectors), patch.object(self.client, 'query_points') as search:
                with self.assertRaisesRegex(ApiError, 'Unable to embed retrieval question'):
                    retrieve_scoped('q', self.scope, 5)
                search.assert_not_called()
        with patch.object(self.provider, 'embed', side_effect=RuntimeError('private body')), patch.object(self.client, 'query_points') as search:
            with self.assertRaisesRegex(ApiError, 'Unable to embed retrieval question'):
                retrieve_scoped('q', self.scope, 5)
            search.assert_not_called()

    def test_query_failures_preserve_categories(self) -> None:
        for error, category in ((ConnectionError('private'), QdrantConnectionError),
                                (TimeoutError('private'), QdrantConnectionError),
                                (ConnectError('private'), QdrantConnectionError),
                                (ResponseHandlingException(ConnectionError(
                                    'private')), QdrantConnectionError),
                                (ValueError('private'), QdrantCollectionError)):
            with self.subTest(category=category), patch.object(self.client, 'query_points', side_effect=error):
                with self.assertRaises(category) as raised:
                    retrieve_scoped('q', self.scope, 5)
                self.assertNotIn('private', str(raised.exception))

    def test_malformed_or_out_of_scope_point_rejects_whole_response(self) -> None:
        payload = self.payload(self.identifiers[0], 0).model_dump(mode='json')
        broken: list[Any] = [
            None] + [{key: value for key, value in payload.items() if key != missing} for missing in payload]
        broken += [{**payload, 'file_id': 'bad'}, {**payload, 'file_id': str(uuid4())},
                   {**payload, 'chunk_index': -1}, {**payload, 'token_count': -1}, {**payload, 'text': None}]
        valid = ScoredPoint(id=str(uuid4()), version=0,
                            score=0.8, payload=payload)
        points = [ScoredPoint(id=str(uuid4()), version=0,
                              score=0.7, payload=value) for value in broken]
        points += [ScoredPoint(id=str(uuid4()), version=0, score=value, payload=payload)
                   for value in (float('nan'), float('inf'))]
        for point in points:
            with self.subTest(point=point.id), patch.object(self.client, 'query_points', return_value=QueryResponse(points=[valid, point])):
                with self.assertRaisesRegex(ApiError, 'Invalid retrieved chunk payload or file scope'):
                    retrieve_scoped('q', self.scope, 5)

    def test_encoding_uses_existing_shared_lock(self) -> None:
        entered = Event()
        encoding = self.services.encoding

        def attempted():
            entered.set()

            return encoding()

        with ThreadPoolExecutor(max_workers=1) as pool:
            with encoding(), patch.object(self.services, 'encoding', side_effect=attempted):
                future = pool.submit(retrieve_scoped, 'q', self.scope, 5)
                self.assertTrue(entered.wait(2))
                self.assertEqual(self.provider.calls, [])
                self.assertFalse(future.done())
            self.assertEqual(len(future.result(timeout=5)), 5)

    def test_logs_and_errors_do_not_expose_content_or_full_membership(self) -> None:
        with self.assertLogs('app.core.logging', level='INFO') as logs:
            retrieve_scoped('private question', self.scope, 5)
            with patch.object(self.client, 'query_points', side_effect=ValueError('private error')):
                with self.assertRaises(ApiError):
                    retrieve_scoped('private question', self.scope, 5)
            with patch.object(self.provider, 'embed', side_effect=ValueError('private error')):
                with self.assertRaises(ApiError):
                    retrieve_scoped('private question', self.scope, 5)
        output = '\n'.join(logs.output)
        for expected in ('files=2', 'top_k=5', 'count=5', 'scores=', 'embedding_seconds=', 'query_seconds=', 'total_seconds='):
            self.assertIn(expected, output)
        for forbidden in ('private question', 'private error', 'Contextual', 'Raw source', *map(str, self.identifiers)):
            self.assertNotIn(forbidden, output)

    def test_empty_database_query_does_not_access_client(self) -> None:
        with patch.object(self.client, 'query_points') as search:
            self.assertEqual(query_scoped(self.client, 'scoped', [
                             1.0, 0.0, 0.0], AuthorizedFileScope(()), 5), [])
            search.assert_not_called()

    def test_captured_scope_survives_committed_changes_and_fresh_scope_excludes(self) -> None:
        fixture = folders.FolderScopeTests(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        identifier = fixture.file(
            fixture.owners[0], fixture.root, name='captured.md')
        captured = fixture.scope()
        self.client.upsert('scoped', [PointStruct(id=str(uuid4()), vector=[1.0, 0.0, 0.0],
                           payload=self.payload(identifier, 0).model_dump(mode='json'))], wait=True)
        with fixture.database.session() as session:
            source = session.get(File, identifier)
            assert source is not None
            source.status = 'deleting'
            source.name = 'renamed.md'
            session.commit()
        fresh = fixture.scope()
        reads = len(fixture.reads)
        self.assertEqual(retrieve_scoped('q', fresh, 5), [])
        self.assertEqual(
            [item.file_id for item in retrieve_scoped('q', captured, 5)], [identifier])
        self.assertEqual(captured.files[0].file_name, 'captured.md')
        self.assertEqual(len(fixture.reads), reads)
        self.services.delete(identifier)
        self.assertEqual(retrieve_scoped('q', captured, 5), [])
        with fixture.database.session() as session:
            source = session.get(File, identifier)
            assert source is not None
            session.delete(source)
            session.commit()
        self.assertEqual(fixture.scope().files, ())
