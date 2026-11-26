"""Explicit approved real-store acceptance; never part of unittest discovery."""
import json
import math
import hashlib
import argparse
import platform
import traceback
from pathlib import Path
from time import perf_counter
from typing import Any, Literal
from unittest.mock import patch
from uuid import UUID, uuid4, uuid5
from importlib.metadata import version
from datetime import datetime, timezone

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointIdsList, PointStruct, VectorParams

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, delete, inspect, select, text, update

from app.core.runtime import activate
from app.core.constants import constants

from app.db.qdrant import query_scoped
from app.db.postgres import Database, url

from app.pipeline.folders import resolve
from app.pipeline.storage import Storage
from app.pipeline.retrieval import retrieve_scoped
from app.pipeline.embeddings.bge_m3 import get_bge_m3_embedder

from app.schemas.scope import AuthorizedFileScope

from app.models.qdrant.chunk import Chunk
from app.models.postgres import File, Folder, User

from app.errors.api import ApiError
from app.errors.folder import FolderNotFoundError
from app.errors.qdrant import QdrantCollectionError, QdrantConnectionError

from tests.folder_scope_postgres import raises

from tests.scoped_retrieval_evaluation import (
    FIXTURE, LIMITS, Capacity, capacity_matrix, capacity_points, evaluate,
    identity, load, measure_capacity, payloads, percentile,
)


def save(directory: Path, name: str, value: Any) -> None:
    """Keep detailed synthetic/private evidence off the repository and console."""
    (directory / name).write_text(json.dumps(value,
                                             indent=2, sort_keys=True) + '\n', encoding='utf-8')


def inventory(client: QdrantClient) -> dict[str, Any]:
    """Capture full original payloads/vectors and durable configuration, not counts alone."""
    collections = {}
    for entry in sorted(client.get_collections().collections, key=lambda item: item.name):
        info = client.get_collection(entry.name)
        points = []
        offset = None
        while True:
            batch, offset = client.scroll(entry.name, limit=256, offset=offset,
                                          with_payload=True, with_vectors=True)
            points.extend(item.model_dump(mode='json') for item in batch)
            if offset is None:
                break
        collections[entry.name] = {
            'config': info.config.model_dump(mode='json'),
            'payload_schema': {key: value.model_dump(mode='json') for key, value in info.payload_schema.items()},
            'points': sorted(points, key=lambda item: str(item['id'])),
        }

    return {'collections': collections, 'aliases': client.get_aliases().model_dump(mode='json')}


class ControlledProvider:
    """1024-dimensional controlled geometry proves rank/filter correctness, not semantics."""
    dimension = 1024

    def __init__(self) -> None:
        self.calls = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1

        return [[1.0] + [0.0] * (self.dimension - 1) for _ in texts]


class TimedProvider:
    """Observe the one prepared BGE provider without changing its outputs or lifecycle."""

    def __init__(self, provider: Any) -> None:
        self.provider = provider
        self.dimension = provider.dimension
        self.seconds: list[float] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        started = perf_counter()
        try:
            return self.provider.embed(texts)
        finally:
            self.seconds.append(perf_counter() - started)


def cleanup(directory: Path, client: QdrantClient, database: Database, before: dict[str, Any]) -> None:
    """Idempotently remove only absent-before ledger IDs, independent of ORM expiration."""
    ledger = json.loads((directory / 'ledger.json').read_text())
    target = json.loads((directory / 'target.json').read_text())
    assert json.loads(
        (directory / 'ownership-checked.json').read_text())['ids_absent']
    assert ledger['run'] == target['run'] and ledger['capacity_collection'] == target['collection']
    assert ledger['collection'] == constants.qdrant.QDRANT_COLLECTION
    with database.engine.connect() as connection:
        assert connection.scalar(
            text('SELECT current_database()')) == target['database']
    collection, benchmark = ledger['collection'], ledger['capacity_collection']
    live_ids = ledger['production_point_ids']
    owners = [UUID(item) for item in ledger['owners']]
    files = [UUID(item) for item in ledger['files']]
    folders = list(ledger['folders'].values())
    client.delete(collection, PointIdsList(
        points=[identifier for identifier in live_ids]), wait=True)
    assert benchmark not in before['collections']
    if client.collection_exists(benchmark):
        client.delete_collection(benchmark)
    with database.session() as session:
        session.execute(delete(File).where(
            File.id.in_(files), File.owner_id.in_(owners)))
        ordered = ('capacity', 'semantic', 'foreign', 'nonready',
                   'empty', 'sibling', 'deep', 'child', 'selected')
        assert set(ordered) == set(ledger['folders'])
        for name in ordered:
            session.execute(delete(Folder).where(Folder.id == UUID(
                ledger['folders'][name]), Folder.owner_id.in_(owners)))
        session.execute(delete(User).where(User.id.in_(owners)))
        session.commit()
        assert not session.scalar(select(File.id).where(File.id.in_(files)))
        assert not session.scalar(select(Folder.id).where(
            Folder.id.in_(list(map(UUID, folders)))))
        assert not session.scalar(select(User.id).where(User.id.in_(owners)))
    after = inventory(client)
    save(directory, 'qdrant-after.json', after)
    assert before == after, 'Qdrant durable configuration/payload/vector preservation mismatch; STOP'
    encoded = json.dumps(after, sort_keys=True).encode('utf-8')
    save(directory, 'cleanup-result.json', {'rows_absent': True, 'production_points_absent': not client.retrieve(collection, live_ids, with_payload=False, with_vectors=False),
                                            'benchmark_absent': benchmark not in after['collections'], 'qdrant_full_preservation': True,
                                            'qdrant_sha256': hashlib.sha256(encoded).hexdigest()})


def execute(directory: Path) -> None:
    """Preledger every mutation; preserve canonical state and exact original vectors."""
    target = json.loads((directory / 'target.json').read_text())
    assert (directory / 'postgres-before.sql').is_file() and (directory /
                                                              'globals-before.sql').is_file()
    assert not (
        directory / 'ledger.json').exists(), 'Never reuse a fixture ledger'
    engine = create_engine(url(
        constants.postgres), hide_parameters=True, connect_args={'connect_timeout': 5})
    database = Database(engine, sessionmaker(bind=engine))
    client = QdrantClient(url=constants.qdrant.QDRANT_URL, timeout=30)
    collection = constants.qdrant.QDRANT_COLLECTION
    benchmark = target['collection']
    before = inventory(client)
    save(directory, 'qdrant-before.json', before)
    assert collection in before['collections'] and benchmark not in before['collections']
    info = client.get_collection(collection)
    assert isinstance(info.config.params.vectors, VectorParams)
    assert info.config.params.vectors.size == 1024 and info.config.params.vectors.distance == Distance.COSINE
    with engine.connect() as connection:
        assert connection.scalar(
            text('SELECT current_database()')) == target['database']
        postgres_version = str(connection.scalar(text('SELECT version()')))
        assert postgres_version.startswith('PostgreSQL 18.')
        assert connection.scalar(
            text('SELECT version_num FROM alembic_version')) == '0002_drive'
    assert set(inspect(engine).get_table_names()) == {
        'alembic_version', 'users', 'verifications', 'sessions', 'folders', 'files'}

    corpus = load()
    owners = [uuid4(), uuid4()]
    folders = {name: uuid4() for name in ('selected', 'child', 'deep',
                                          'sibling', 'empty', 'nonready', 'foreign', 'semantic', 'capacity')}
    now = datetime.now(timezone.utc)
    rows: list[File] = []

    def file(location: UUID | None, status: Literal['processing', 'ready', 'deleting'] = 'ready',
             owner: UUID = owners[0], identifier: UUID | None = None, name: str = 'duplicate.md') -> UUID:
        identifier = identifier or uuid4()
        rows.append(File(id=identifier, owner_id=owner, folder_id=location, status=status, name=name,
                         description=None, original_name='synthetic.md', extension='.md', size_bytes=25,
                         created_at=now, updated_at=now))

        return identifier

    first, second = file(folders['selected']), file(folders['selected'])
    excluded = [file(None), file(folders['child']), file(folders['deep']), file(folders['sibling']),
                file(folders['selected'], 'processing'), file(
                    folders['selected'], 'deleting'),
                file(folders['foreign'], owner=owners[1]), uuid4()]
    file(folders['nonready'], 'processing')
    file(folders['nonready'], 'deleting')
    for source in corpus.files:
        allowed = source.file_id in corpus.allowed_file_ids
        foreign = source == corpus.files[-1]
        file(folders['foreign'] if foreign else folders['semantic'] if allowed else folders['sibling'],
             owner=owners[1] if foreign else owners[0], identifier=source.file_id, name=source.file_name)
    for source in Capacity(250, 20, 1000).scope().files:
        file(folders['capacity'], 'processing',
             identifier=source.file_id, name=source.file_name)

    control_points = []
    for number, identifier in enumerate([first, second, *excluded]):
        for index in range(3 if number < 2 else 1):
            score = .9 - .1 * (number * 3 + index) if number < 2 else 1.0
            payload = Chunk(file_id=identifier, chunk_index=index, token_count=7,
                            text='Controlled synthetic evidence.', display_text='Raw synthetic evidence.',
                            page=None, heading='Synthetic', section=None)
            control_points.append(PointStruct(id=str(uuid5(identifier, str(index))),
                                  vector=[score, math.sqrt(
                                      1 - score ** 2)] + [0.0] * 1022,
                                  payload=payload.model_dump(mode='json')))
    semantic_ids = [str(uuid5(source.file_id, str(chunk.chunk_index)))
                    for source in corpus.files for chunk in source.chunks]
    live_ids = [str(point.id) for point in control_points] + semantic_ids
    capacity_ids = [str(point.id)
                    for point in capacity_points(Capacity(250, 20, 1000), 2)]
    ledger = {'run': target['run'], 'owners': list(map(str, owners)),
              'folders': {key: str(value) for key, value in folders.items()},
              'files': [str(row.id) for row in rows], 'collection': collection,
              'production_point_ids': live_ids, 'capacity_collection': benchmark,
              'capacity_point_ids': capacity_ids, 'orphan_file_id': str(excluded[-1])}
    save(directory, 'ledger.json', ledger)
    with database.session() as session:
        assert not session.scalar(select(User.id).where(User.id.in_(owners)))
        assert not session.scalar(select(Folder.id).where(
            Folder.id.in_(folders.values())))
        assert not session.scalar(select(File.id).where(
            File.id.in_([row.id for row in rows])))
    assert not client.retrieve(
        collection, live_ids, with_payload=False, with_vectors=False), 'Point ID collision'
    original_file_ids = {str(point.get('payload', {}).get('file_id'))
                         for point in before['collections'][collection]['points']}
    assert not original_file_ids.intersection(
        [str(row.id) for row in rows] + [str(excluded[-1])]), 'File ID collision'
    save(directory, 'ownership-checked.json', {'ids_absent': True})

    checks: list[str] = []
    report = {'identity': identity(FIXTURE, corpus), 'postgres': postgres_version,
              'qdrant': client.info().model_dump(mode='json'), 'python': platform.python_version(),
              'versions': {key: version(key) for key in ('qdrant-client', 'torch', 'transformers', 'FlagEmbedding', 'SQLAlchemy')},
              'checks': checks}
    report['identity']['qdrant_server'] = report['qdrant']['version']

    def scope(name: str, owner: UUID = owners[0], maximum: int = 250) -> AuthorizedFileScope:
        return resolve(owner, folders[name], max_files=maximum)

    def change(identifier: UUID, **values: Any) -> None:
        with database.session() as session:
            session.execute(update(File).where(
                File.id == identifier, File.owner_id == owners[0]).values(**values))
            session.commit()

    try:
        with database.session() as session:
            session.add_all([User(id=owner, name='Synthetic acceptance', email=f'am02-{owner}@example.invalid',
                                  password='unusable-synthetic-fixture', verified_at=now, created_at=now, updated_at=now) for owner in owners])
            session.commit()
            for name, identifier in folders.items():
                parent = folders['selected'] if name == 'child' else folders['child'] if name == 'deep' else None
                session.add(Folder(id=identifier, owner_id=owners[1] if name == 'foreign' else owners[0], parent_id=parent,
                                   name='Synthetic ' + name, description=None, created_at=now, updated_at=now))
                session.flush()
            session.add_all(rows)
            session.commit()

        provider = ControlledProvider()
        services = Storage(provider, client, collection)
        with activate(services, database):
            captured = scope('selected')
            assert captured.file_ids == {first, second} and {
                item.file_name for item in captured.files} == {'duplicate.md'}
            for name in ('empty', 'nonready'):
                with patch('app.pipeline.retrieval.storage', side_effect=AssertionError('Empty scope accessed runtime')):
                    assert retrieve_scoped(
                        'Synthetic question', scope(name), 5) == []
            missing = raises(FolderNotFoundError, lambda: resolve(
                owners[0], uuid4(), max_files=250))
            foreign = raises(FolderNotFoundError, lambda: scope('foreign'))
            assert vars(missing) == vars(foreign)
            raises(FolderNotFoundError, lambda: scope('selected', owners[1]))
            assert scope('foreign', owners[1]).file_ids == {
                excluded[-2], corpus.files[-1].file_id}
            client.upsert(collection, control_points, wait=True)
            queries = []

            def query(*args: Any, **kwargs: Any) -> Any:
                queries.append(kwargs)

                return original_query(*args, **kwargs)

            original_query = client.query_points
            for limit in (1, 5, 8, 12, 20):
                count = provider.calls
                with patch.object(client, 'query_points', side_effect=query), patch('app.pipeline.folders.postgres', side_effect=AssertionError('Unexpected reauthorization')):
                    results = retrieve_scoped(
                        'Synthetic question', captured, limit)
                assert provider.calls == count + 1 and len(queries) == 1
                call = queries.pop()
                terms = call['query_filter'].must[0].match.any
                assert terms == sorted(map(str, captured.file_ids))
                assert call['limit'] == limit and call['with_payload'] is True and call['with_vectors'] is False
                assert len(results) == min(limit, 6)
                assert [(item.file_id, item.chunk_index) for item in results] == [
                    (identifier, index) for identifier in (first, second) for index in range(3)][:limit]
                assert all(abs(item.score - (.9 - .1 * index)) <
                           1e-5 for index, item in enumerate(results))
                assert all(item.text == 'Controlled synthetic evidence.' and item.display_text ==
                           'Raw synthetic evidence.' and item.page is None and item.heading == 'Synthetic' for item in results)
            checks.append('Real PostgreSQL two-owner direct/ready scope, privacy, empty bypass and one complete pre-ranking MatchAny/global query at k=1/5/8/12/20; stronger excluded points never participate')

            with patch.object(client, 'query_points', return_value=original_query(collection, query=[1.0] + [0.0] * 1023, limit=1, with_payload=True, with_vectors=False)):
                raises(ApiError, lambda: retrieve_scoped(
                    'Synthetic question', captured, 5))
            corrupt = PointStruct(id=control_points[0].id, vector=control_points[0].vector, payload={
                                  'file_id': str(first)})
            client.upsert(collection, [corrupt], wait=True)
            raises(ApiError, lambda: retrieve_scoped(
                'Synthetic question', captured, 5))
            client.upsert(collection, [control_points[0]], wait=True)
            raises(QdrantCollectionError, lambda: query_scoped(
                client, benchmark, [1.0] + [0.0] * 1023, captured, 5))
            failure = __import__('httpx').ConnectError(
                'Synthetic private dependency detail')
            with patch.object(client, 'query_points', side_effect=failure):
                error = raises(QdrantConnectionError, lambda: retrieve_scoped(
                    'Synthetic question', captured, 5))
                assert 'private dependency' not in str(error)
            checks.append('Real malformed stored payload and missing collection fail; injected unfiltered transport response fails membership; injected connection error retains sanitized category')

            change(first, name='renamed.md', status='deleting')
            fresh = scope('selected')
            assert fresh.file_ids == {
                second} and captured.files[0].file_name == 'duplicate.md'
            with patch('app.pipeline.folders.postgres', side_effect=AssertionError('Unexpected reauthorization')):
                assert any(item.file_id == first for item in retrieve_scoped(
                    'Synthetic question', captured, 5))
            client.delete(collection, PointIdsList(points=[str(
                point.id) for point in control_points if point.payload and point.payload['file_id'] == str(first)]), wait=True)
            assert all(item.file_id == second for item in retrieve_scoped(
                'Synthetic question', captured, 5))
            with database.session() as session:
                session.execute(delete(File).where(
                    File.id == first, File.owner_id == owners[0]))
                session.commit()
            assert scope('selected').file_ids == {second}
            client.delete(collection, PointIdsList(points=[str(
                point.id) for point in control_points if point.payload and point.payload['file_id'] == str(second)]), wait=True)
            assert retrieve_scoped('Synthetic question', captured, 5) == []
            change(second, status='deleting')
            assert not scope('selected').files
            checks.append('Independent committed rename/deleting/delete; captured scope uses remaining vectors without SQL recheck, fresh scope excludes removed/nonready files; exact vector cleanup yields zero hits')

        client.delete(collection, PointIdsList(
            points=[str(point.id) for point in control_points]), wait=True)
        save(directory, 'progress.json', {
             'stage': 'real-store-correctness-complete', 'checks': checks})

        started = perf_counter()
        bge = get_bge_m3_embedder()
        import torch
        torch.set_num_threads(2)
        from app.pipeline.chunking import _chunker
        tokenizer = _chunker().tokenizer
        report['model_load_seconds'] = perf_counter() - started
        report['model'] = {'name': constants.embedding.EMBEDDING_MODEL, 'dimension': bge.dimension,
                           'fp16': constants.embedding.EMBEDDING_USE_FP16, 'torch_threads': torch.get_num_threads(),
                           'chunk_tokenizer': 'Existing Docling HuggingFaceTokenizer.count_tokens; BGE-M3, not Gemini',
                           'offline': True}
        timed = TimedProvider(bge)
        chunks = payloads(corpus, tokenizer.count_tokens)
        started = perf_counter()
        vectors = timed.embed([item.text for item in chunks])
        report['corpus_embedding_seconds'] = perf_counter() - started
        client.upsert(collection, [PointStruct(id=str(uuid5(item.file_id, str(item.chunk_index))),
                      payload=item.model_dump(mode='json'), vector=vector) for item, vector in zip(chunks, vectors, strict=True)], wait=True)
        services = Storage(timed, client, collection)
        semantic_scope: AuthorizedFileScope
        with activate(services, database):
            semantic_scope = scope('semantic')
            assert semantic_scope == corpus.scope()
            timed.embed(['Synthetic model warmup question.'])
            query_samples: list[float] = []
            timings: list[dict[str, Any]] = []
            original_query = client.query_points

            def measured_query(*args: Any, **kwargs: Any) -> Any:
                started = perf_counter()
                try:
                    return original_query(*args, **kwargs)
                finally:
                    query_samples.append(perf_counter() - started)

            def retrieval(question: str, supplied: AuthorizedFileScope, limit: int) -> Any:
                assert supplied == semantic_scope
                before_embeddings, before_queries = len(
                    timed.seconds), len(query_samples)
                started = perf_counter()
                with patch.object(client, 'query_points', side_effect=measured_query):
                    results = retrieve_scoped(question, semantic_scope, limit)
                assert len(timed.seconds) == before_embeddings + \
                    1 and len(query_samples) == before_queries + 1
                timings.append({'top_k': limit, 'question_id': next(item.id for item in corpus.questions if item.question == question),
                                'embedding_seconds': timed.seconds[-1], 'qdrant_seconds': query_samples[-1],
                                'end_to_end_seconds': perf_counter() - started})

                return results

            report['semantic'] = evaluate(corpus, retrieval)
            report['semantic_timings'] = timings
            assert all(value['summary']['failures'] ==
                       0 for value in report['semantic'].values())
            for limit in LIMITS:
                samples = [item for item in timings if item['top_k'] == limit]
                report['semantic'][str(limit)]['timing_summary'] = {
                    name + '_p' + str(quantile): percentile([item[name] for item in samples], quantile / 100)
                    for name in ('embedding_seconds', 'qdrant_seconds', 'end_to_end_seconds') for quantile in (50, 95)}
        save(directory, 'semantic-result.json', report)
        save(directory, 'progress.json', {
             'stage': 'semantic-complete', 'checks': checks})
        client.delete(collection, PointIdsList(
            points=[identifier for identifier in semantic_ids]), wait=True)

        client.create_collection(
            benchmark, vectors_config=info.config.params.vectors.model_copy(deep=True))
        save(directory, 'capacity-config.json', {'production': info.model_dump(mode='json'),
             'temporary': client.get_collection(benchmark).model_dump(mode='json'),
             'qualification': 'Same 1024 cosine vector parameters; fresh collection uses server default HNSW/optimizer/WAL/shard settings and no payload index; raw configs retained for comparison. Controlled geometry and fixed synthetic token_count=4 proxy, not BGE semantic capacity or tokenizer measurement.'})
        capacity_rows = []
        previous_ids: list[str] = []
        services = Storage(ControlledProvider(), client, benchmark)
        with activate(services, database):
            for case in capacity_matrix():
                allowed = case.scope().file_ids
                with database.session() as session:
                    session.execute(update(File).where(
                        File.folder_id == folders['capacity'], File.owner_id == owners[0]).values(status='processing'))
                    session.execute(update(File).where(File.id.in_(
                        allowed), File.owner_id == owners[0]).values(status='ready'))
                    session.commit()
                resolution_samples = []
                resolved = None
                for index in range(32):
                    started = perf_counter()
                    resolved = scope('capacity', maximum=250)
                    elapsed = perf_counter() - started
                    assert resolved.file_ids == allowed
                    if index >= 2:
                        resolution_samples.append(elapsed)
                assert resolved is not None
                if previous_ids:
                    client.delete(benchmark, PointIdsList(
                        points=[identifier for identifier in previous_ids]), wait=True)
                points = capacity_points(case, 1024)
                for start in range(0, len(points), 128):
                    client.upsert(
                        benchmark, points[start:start + 128], wait=True)
                previous_ids = [str(point.id) for point in points]
                measurements = measure_capacity(
                    services, case, 'Controlled capacity question.', scope=resolved)
                for measurement in measurements:
                    measurement.update({'resolver_seconds': resolution_samples,
                                        'resolver_seconds_p50': percentile(resolution_samples, .5),
                                        'resolver_seconds_p95': percentile(resolution_samples, .95),
                                        'embedding_kind': 'controlled unit vector; not BGE',
                                        'token_measure': 'fixed synthetic token_count=4; not tokenizer measurement'})
                capacity_rows.extend(measurements)
                save(directory, 'capacity-result.json', capacity_rows)
                save(directory, 'progress.json', {
                     'stage': 'capacity', 'cases_complete': len(capacity_rows) // 3})
        assert len(capacity_rows) == 48 and all(
            len(item['qdrant_seconds']) == 30 for item in capacity_rows)
        report['capacity_cases'] = 16
        report['capacity_measurements'] = 1440
        checks.append('Fixed aster-v1 real cached BGE-M3 semantic 90 retrievals and 16 persistent capacity configurations × 3 k × 30 timed queries, each using actual PostgreSQL-resolved complete scope')
        save(directory, 'acceptance-result.json', report)
    except BaseException:
        (directory / 'acceptance-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
    finally:
        try:
            cleanup(directory, client, database, before)
        finally:
            client.close()
            database.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', required=True)
    parser.add_argument('--cleanup-ledger', action='store_true', required=True)
    parser.add_argument('--recover-cleanup', action='store_true',
                        help='Only finish exact cleanup for an existing ownership-checked ledger')
    args = parser.parse_args()
    try:
        if args.recover_cleanup:
            engine = create_engine(url(
                constants.postgres), hide_parameters=True, connect_args={'connect_timeout': 5})
            database = Database(engine, sessionmaker(bind=engine))
            client = QdrantClient(url=constants.qdrant.QDRANT_URL, timeout=30)
            try:
                cleanup(args.run, client, database, json.loads(
                    (args.run / 'qdrant-before.json').read_text()))
            finally:
                client.close()
                database.close()
        else:
            execute(args.run)
    except BaseException as error:
        (args.run / 'last-error.txt').write_text(traceback.format_exc(), encoding='utf-8')
        print('Persistent acceptance failed: ' +
              type(error).__name__ + '; private evidence retained')
        raise SystemExit(1) from None
    print('Exact-ledger cleanup recovery PASS; private evidence retained' if args.recover_cleanup
          else 'Persistent acceptance and exact Qdrant cleanup PASS; private evidence retained')


if __name__ == '__main__':
    main()
