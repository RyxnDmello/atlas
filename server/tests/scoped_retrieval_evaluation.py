"""Explicit offline evaluation preparation; importing this module never contacts a service.

The CLI validates fixed labels or runs label-derived controlled vectors in memory.
Real BGE-M3/persistent Qdrant execution requires a separately approved coordinator.
"""
import json
import math
import hashlib
import argparse
import platform
from pathlib import Path
from statistics import mean
from uuid import UUID, uuid5
from time import perf_counter
from typing import Any, Literal
from contextlib import ExitStack
from dataclasses import dataclass
from pydantic import BaseModel, Field
from importlib.metadata import version
from collections.abc import Callable, Sequence

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchAny, PointStruct, VectorParams

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.runtime import activate
from app.models.qdrant.chunk import Chunk

from app.db.postgres import Database
from app.db.qdrant import query_scoped

from app.pipeline.storage import Storage
from app.pipeline.retrieval import retrieve_scoped

from app.schemas.retrieval import RetrievedChunk
from app.schemas.scope import AuthorizedFileScope, FileSource

FIXTURE = Path(__file__).parent / 'fixtures' / 'scoped_retrieval_v1.json'
NAMESPACE = UUID('a5700000-0000-4000-8000-000000000000')
LIMITS = (5, 8, 12)


class Evidence(BaseModel, frozen=True):
    file_id: UUID
    chunk_index: int = Field(ge=0)


class Snippet(BaseModel):
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    display_text: str = Field(min_length=1)
    page: int | None
    heading: str | None
    section: str | None


class Source(BaseModel):
    file_id: UUID
    file_name: str
    chunks: list[Snippet]


class Question(BaseModel):
    id: str
    kind: Literal['single', 'paraphrase', 'cross', 'unsupported']
    question: str = Field(min_length=1)
    evidence: list[Evidence]


class Corpus(BaseModel):
    version: str
    description: str
    files: list[Source]
    allowed_file_ids: list[UUID]
    questions: list[Question]

    def scope(self) -> AuthorizedFileScope:
        return AuthorizedFileScope(tuple(FileSource(source.file_id, source.file_name)
                                         for source in self.files if source.file_id in self.allowed_file_ids))


def load(path: Path = FIXTURE) -> Corpus:
    """Reject duplicate/unknown evidence and inconsistent unsupported/cross-file labels."""
    corpus = Corpus.model_validate_json(path.read_bytes())
    identities = [source.file_id for source in corpus.files]
    evidence = [Evidence(file_id=source.file_id, chunk_index=chunk.chunk_index)
                for source in corpus.files for chunk in source.chunks]
    if len(set(identities)) != len(identities) or len(set(evidence)) != len(evidence):
        raise ValueError('Duplicate corpus source identity')
    if not corpus.allowed_file_ids or len(set(corpus.allowed_file_ids)) != len(corpus.allowed_file_ids):
        raise ValueError('Invalid authorized corpus scope')
    if not set(corpus.allowed_file_ids).issubset(identities):
        raise ValueError('Unknown authorized file')
    if len({question.id for question in corpus.questions}) != len(corpus.questions):
        raise ValueError('Duplicate question identity')
    eligible = {
        item for item in evidence if item.file_id in corpus.allowed_file_ids}
    for question in corpus.questions:
        labels = set(question.evidence)
        if len(labels) != len(question.evidence) or not labels.issubset(eligible):
            raise ValueError('Invalid question evidence')
        if (question.kind == 'unsupported') != (not labels):
            raise ValueError(
                'Unsupported questions must have no positive labels')
        if question.kind == 'cross' and len({item.file_id for item in labels}) < 2:
            raise ValueError('Cross-file questions require multiple files')

    return corpus


def payloads(corpus: Corpus, count: Callable[[str], int]) -> list[Chunk]:
    """Build existing payloads; caller supplies real tokenizer counts or a declared proxy."""
    return [Chunk(file_id=source.file_id, token_count=count(chunk.text), **chunk.model_dump())
            for source in corpus.files for chunk in source.chunks]


def metrics(question: Question, results: Sequence[RetrievedChunk]) -> dict[str, Any]:
    """Evidence recall is chunk-based; file coverage only counts labeled evidence hits."""
    expected = set(question.evidence)
    returned = {Evidence(file_id=item.file_id,
                         chunk_index=item.chunk_index) for item in results}
    hits = expected & returned
    files = {item.file_id for item in expected}
    found = {item.file_id for item in hits}

    return {
        'recall': len(hits) / len(expected) if expected else None,
        'hit': bool(hits) if expected else None,
        'required_file_coverage': len(found) / len(files) if files else None,
        'all_evidence': expected.issubset(returned) if expected else None,
        'chunks': len(results), 'stored_token_count': sum(item.token_count for item in results),
        'context_characters': sum(len(item.text) for item in results),
        'ranked': [{'file_id': str(item.file_id), 'chunk_index': item.chunk_index, 'score': item.score}
                   for item in results],
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Keep all positive queries in denominators, including failed retrieval attempts."""
    positive = [row for row in rows if row['metrics']['recall'] is not None]
    cross = [row for row in positive if row['kind'] == 'cross']

    return {
        'queries': len(rows), 'positive_queries': len(positive),
        'unsupported_queries': len(rows) - len(positive),
        'failures': sum(row['status'] == 'error' for row in rows),
        'recall_at_k': mean(row['metrics']['recall'] for row in positive) if positive else None,
        'hit_rate': mean(row['metrics']['hit'] for row in positive) if positive else None,
        'all_evidence_success': mean(row['metrics']['all_evidence'] for row in positive) if positive else None,
        'cross_file_coverage': mean(row['metrics']['required_file_coverage'] for row in cross) if cross else None,
        'cross_all_evidence_success': mean(row['metrics']['all_evidence'] for row in cross) if cross else None,
        'end_to_end_seconds_p50': percentile([row['seconds'] for row in rows], .5),
        'end_to_end_seconds_p95': percentile([row['seconds'] for row in rows], .95),
        'mean_stored_token_count': mean(row['metrics']['stored_token_count'] for row in rows) if rows else 0,
    }


def evaluate(corpus: Corpus, retrieve: Callable[[str, AuthorizedFileScope, int], list[RetrievedChunk]]) -> dict[str, Any]:
    """Run the unchanged corpus/scope at each k; sanitize failures without dropping queries."""
    scope = corpus.scope()
    experiments = {}
    for limit in LIMITS:
        rows = []
        for question in corpus.questions:
            started = perf_counter()
            status, category = 'ok', None
            try:
                results = retrieve(question.question, scope, limit)
            except Exception as error:
                results, status, category = [], 'error', type(error).__name__
            rows.append({'question_id': question.id, 'kind': question.kind, 'status': status,
                         'error_category': category, 'seconds': perf_counter() - started,
                         'metrics': metrics(question, results)})
        experiments[str(limit)] = {'summary': aggregate(rows), 'queries': rows}

    return experiments


def percentile(values: Sequence[float], quantile: float) -> float | None:
    """Use linear interpolation between sorted samples, with no discarded outliers."""
    if not values:
        return None

    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)

    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


@dataclass(frozen=True)
class Capacity:
    files: int
    chunks_per_file: int
    excluded_points: int

    def scope(self) -> AuthorizedFileScope:
        return AuthorizedFileScope(tuple(FileSource(uuid5(NAMESPACE, f'capacity-file-{index}'),
                                                    f'capacity-{index}.md') for index in range(self.files)))


def capacity_matrix() -> list[Capacity]:
    """Candidate sizes are experiment inputs and never production resolver defaults."""
    return [Capacity(files, chunks, excluded) for files in (10, 50, 100, 250)
            for chunks in (2, 20) for excluded in (0, 1000)]


def capacity_points(case: Capacity, dimension: int) -> list[PointStruct]:
    """Prepare stable controlled points; no write or resource construction occurs here."""
    if dimension < 2:
        raise ValueError('Capacity vectors require at least two dimensions')

    points = []
    for source in case.scope().files:
        for index in range(case.chunks_per_file):
            score = .1 + (index % 20) * .04
            payload = Chunk(file_id=source.file_id, chunk_index=index, token_count=4,
                            text='Synthetic capacity evidence.', display_text='Synthetic capacity evidence.')
            points.append(PointStruct(id=str(uuid5(source.file_id, str(index))),
                          vector=[score, math.sqrt(
                              1 - score ** 2)] + [0.0] * (dimension - 2),
                          payload=payload.model_dump(mode='json')))
    excluded = uuid5(NAMESPACE, 'capacity-excluded')
    for index in range(case.excluded_points):
        payload = Chunk(file_id=excluded, chunk_index=index, token_count=4,
                        text='Excluded capacity evidence.', display_text='Excluded capacity evidence.')
        points.append(PointStruct(id=str(uuid5(excluded, str(index))),
                      vector=[1.0] + [0.0] * (dimension - 1), payload=payload.model_dump(mode='json')))

    return points


def measure_capacity(services: Storage, case: Capacity, question: str, *, repeats: int = 30,
                     warmups: int = 2, scope: AuthorizedFileScope | None = None) -> list[dict[str, Any]]:
    """Read an explicitly prepared collection; separate embedding and repeated query-only timings.

    The caller must verify collection ownership/inventory and activate the same Storage.
    This function never creates a collection or points and never cleans persistent state.
    """
    if repeats < 1 or warmups < 0:
        raise ValueError('Invalid measurement counts')

    scope = case.scope() if scope is None else scope
    if scope.file_ids != case.scope().file_ids:
        raise ValueError('Resolved capacity scope does not match experiment')

    started = perf_counter()
    with services.encoding():
        vectors = services.provider.embed([question])
    embedding = perf_counter() - started
    if (len(vectors) != 1 or len(vectors[0]) != services.provider.dimension
            or not all(map(math.isfinite, vectors[0])) or not any(vectors[0])):
        raise ValueError('Invalid benchmark query vector')
    vector = vectors[0]
    expected = case.files * case.chunks_per_file
    total = services.client.count(services.collection, exact=True).count
    condition = Filter(must=[FieldCondition(
        key='file_id', match=MatchAny(any=sorted(map(str, scope.file_ids))))])
    eligible = services.client.count(
        services.collection, count_filter=condition, exact=True).count
    if eligible != expected or total != expected + case.excluded_points:
        raise ValueError(
            'Capacity fixture inventory does not match experiment')

    rows = []
    for limit in LIMITS:
        timings = []
        for index in range(warmups + repeats):
            started = perf_counter()
            points = query_scoped(
                services.client, services.collection, vector, scope, limit)
            elapsed = perf_counter() - started
            if index >= warmups:
                timings.append(elapsed)
            if len(points) != min(limit, eligible) or any(
                    point.payload is None or UUID(
                        str(point.payload.get('file_id'))) not in scope.file_ids
                    for point in points):
                raise ValueError(
                    'Capacity ranking violates authorized membership or global limit')
        started = perf_counter()
        results = retrieve_scoped(question, scope, limit)
        end_to_end = perf_counter() - started
        rows.append({'files': case.files, 'chunks_per_file': case.chunks_per_file, 'top_k': limit,
                     'total_points': total, 'eligible_points': eligible, 'excluded_points': case.excluded_points,
                     'filter_ids': len(scope.file_ids), 'filter_bytes': len(condition.model_dump_json(exclude_none=True).encode('utf-8')),
                     'warmups': warmups, 'measurements': repeats, 'qdrant_seconds': timings,
                     'qdrant_seconds_p50': percentile(timings, .5), 'qdrant_seconds_p95': percentile(timings, .95),
                     'embedding_seconds': embedding, 'end_to_end_seconds': end_to_end,
                     'stored_token_count': sum(item.token_count for item in results),
                     'context_characters': sum(len(item.text) for item in results)})

    return rows


class ControlledProvider:
    """Label-derived oracle vectors exercise metrics/ranking, never semantic relevance."""

    def __init__(self, corpus: Corpus) -> None:
        evidence = [Evidence(file_id=source.file_id, chunk_index=item.chunk_index)
                    for source in corpus.files for item in source.chunks]
        self.dimension = len(evidence) + 1
        self.vectors: dict[str, list[float]] = {}
        for source in corpus.files:
            for item in source.chunks:
                vector = [0.0] * self.dimension
                vector[evidence.index(
                    Evidence(file_id=source.file_id, chunk_index=item.chunk_index))] = 1.0
                self.vectors[item.text] = vector
        for question in corpus.questions:
            vector = [0.0] * self.dimension
            for label in question.evidence:
                vector[evidence.index(label)] = 1.0
            if not question.evidence:
                vector[-1] = 1.0
            self.vectors[question.question] = vector

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [list(self.vectors[text]) for text in texts]


def identity(path: Path, corpus: Corpus) -> dict[str, Any]:
    configuration = {'limits': LIMITS, 'capacity_matrix': [case.__dict__ for case in capacity_matrix()],
                     'capacity_repeats': 30, 'capacity_warmups': 2, 'percentile': 'linear-interpolation'}
    encoded = json.dumps(configuration, sort_keys=True).encode('utf-8')

    return {'corpus_version': corpus.version, 'corpus_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'config_sha256': hashlib.sha256(encoded).hexdigest(), 'configuration': configuration,
            'python': platform.python_version(), 'platform': platform.platform(),
            'qdrant_client': version('qdrant-client'), 'qdrant_server': 'not contacted by offline CLI', 'limits': LIMITS,
            'scope_files': len(corpus.allowed_file_ids), 'questions': len(corpus.questions),
            'capacity_matrix': [case.__dict__ for case in capacity_matrix()],
            'numeric_policy': 'PROVISIONAL; no production k, scope or prompt-token budget selected'}


def controlled(corpus: Corpus) -> dict[str, Any]:
    """Run only isolated in-memory Qdrant and synthetic label-derived vectors."""
    provider = ControlledProvider(corpus)
    with ExitStack() as resources:
        client = QdrantClient(':memory:')
        resources.callback(client.close)
        client.create_collection('controlled', vectors_config=VectorParams(
            size=provider.dimension, distance=Distance.COSINE))
        chunks = payloads(corpus, lambda text: len(text.split()))
        vectors = provider.embed([item.text for item in chunks])
        client.upsert('controlled', [PointStruct(id=str(uuid5(item.file_id, str(item.chunk_index))),
                      payload=item.model_dump(mode='json'), vector=vector) for item, vector in zip(chunks, vectors, strict=True)], wait=True)
        engine = create_engine('sqlite://')
        resources.callback(engine.dispose)
        services = Storage(provider, client, 'controlled')
        resources.enter_context(
            activate(services, Database(engine, sessionmaker(bind=engine))))

        return evaluate(corpus, retrieve_scoped)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, default=FIXTURE)
    parser.add_argument('--deterministic', action='store_true',
                        help='Label-derived vectors in memory; not BGE-M3 evidence')
    parser.add_argument('--output', type=Path,
                        help='Optional report file; must not already exist')
    args = parser.parse_args()
    corpus = load(args.corpus)
    report = identity(args.corpus, corpus)
    report.update({'mode': 'controlled-label-vectors' if args.deterministic else 'fixture-validation-only',
                   'datastore': 'isolated-memory' if args.deterministic else 'none',
                   'token_measure': 'word-count proxy; neither BGE-M3 nor Gemini tokens',
                   'real_semantic_evaluation': 'UNRUN', 'persistent_capacity': 'UNRUN'})
    if args.deterministic:
        report['experiments'] = controlled(corpus)
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items()
          if key not in ('experiments', 'capacity_matrix')}, indent=2))
    if args.deterministic:
        print(json.dumps({limit: result['summary'] for limit,
              result in report['experiments'].items()}, indent=2))
        if any(result['summary']['failures'] for result in report['experiments'].values()):
            raise SystemExit(1)


if __name__ == '__main__':
    main()
