"""Explicit Stage 02 acceptance; never discovered by the ordinary test runner."""
import json
import argparse
from pathlib import Path
from uuid import UUID, uuid4
from unittest.mock import patch
from typing import cast, Literal
from collections.abc import Callable
from datetime import datetime, timezone
from dataclasses import FrozenInstanceError

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, delete, inspect, select, text

from app.pipeline.folders import resolve

from app.core.constants import constants
from app.db.postgres import Database, url

from app.schemas.scope import AuthorizedFileScope
from app.models.postgres import File, Folder, User

from app.errors.postgres import PostgresOperationError
from app.errors.folder import FolderNotFoundError, FolderScopeLimitError

from tests.test_27_folder_scope import ReadSession


def raises(error: type[Exception], operation: Callable[[], object]) -> Exception:
    """Require the expected exception without printing SQL or private state."""
    try:
        operation()
    except error as failure:
        return failure

    raise AssertionError('Expected failure did not occur')


def execute(directory: Path) -> None:
    """Use real constraints and independent commits; clean only pre-ledgered IDs."""
    target = json.loads((directory / 'target.json').read_text())
    assert (directory / 'postgres-before.sql').is_file()
    assert (directory / 'globals-before.sql').is_file()
    assert not (directory / 'ledger.json').exists(), 'Never reuse a fixture run'
    engine = create_engine(url(constants.postgres), hide_parameters=True,
                           connect_args={'connect_timeout': 5})
    writer = Database(engine, sessionmaker(bind=engine))
    with engine.connect() as connection:
        assert connection.scalar(
            text('SELECT current_database()')) == target['database']
        assert connection.scalar(
            text('SELECT version()')).startswith('PostgreSQL 18.')
        assert connection.scalar(
            text('SELECT version_num FROM alembic_version')) == '0002_drive'
    schema = inspect(engine)
    assert set(schema.get_table_names()) == {
        'alembic_version', 'users', 'verifications', 'sessions', 'folders', 'files'}
    assert 'fk_files_folder_id_owner_id_folders' in {
        item['name'] for item in schema.get_foreign_keys('files')}
    assert 'ix_files_owner_id_folder_id' in {
        item['name'] for item in schema.get_indexes('files')}

    owners = [uuid4(), uuid4()]
    names = ('selected', 'child', 'deep', 'sibling',
             'empty', 'nonready', 'foreign', 'large')
    folders = {name: uuid4() for name in names}
    rows: list[File] = []
    now = datetime.now(timezone.utc)

    def file(location: UUID | None, status: Literal['processing', 'ready', 'deleting'] = 'ready',
             owner: UUID = owners[0], name: str = 'same') -> UUID:
        identifier = uuid4()
        rows.append(File(id=identifier, owner_id=owner, folder_id=location,
                         name=name, description=None, original_name='synthetic.md',
                         extension='.md', size_bytes=19, status=status,
                         created_at=now, updated_at=now))

        return identifier

    first, second = file(folders['selected']), file(folders['selected'])
    incoming = file(folders['selected'], 'processing')
    file(folders['selected'], 'deleting')
    for location in (None, folders['child'], folders['deep'], folders['sibling']):
        file(location)
    for status in ('processing', 'deleting'):
        file(folders['nonready'], cast(
            Literal['processing', 'deleting'], status))
        file(folders['large'], cast(Literal['processing', 'deleting'], status))
    foreign = file(folders['foreign'], owner=owners[1], name='foreign')
    large = {file(folders['large']): 'same' for _ in range(99)}
    hundred = file(folders['large'], 'processing')
    overflow = file(folders['large'], 'processing')
    ledger = {'owners': [str(item) for item in owners],
              'folders': {name: str(item) for name, item in folders.items()},
              'files': [str(item.id) for item in rows]}
    (directory / 'ledger.json').write_text(json.dumps(ledger, indent=2) + '\n')
    with writer.session() as session:
        assert not session.scalar(select(User.id).where(User.id.in_(owners)))
        assert not session.scalar(select(Folder.id).where(
            Folder.id.in_(folders.values())))
        assert not session.scalar(select(File.id).where(
            File.id.in_([item.id for item in rows])))

    reads: list[ReadSession] = []
    reader = Database(engine, sessionmaker[Session](
        bind=engine, class_=ReadSession, observed=reads))
    checks: list[str] = []

    def scope(folder: UUID, owner: UUID = owners[0], limit: int = 100) -> AuthorizedFileScope:
        before = len(reads)
        try:
            return resolve(owner, folder, max_files=limit)
        finally:
            assert len(reads) == before + 1
            assert reads[-1].closed and len(reads[-1].statements) == 1
            statement = reads[-1].statements[0]
            sql = str(statement.compile(dialect=engine.dialect))
            assert sql.startswith('SELECT ') and 'LEFT OUTER JOIN' in sql
            assert 'FOR UPDATE' not in sql and 'LIMIT' in sql
            assert limit + \
                1 in statement.compile(dialect=engine.dialect).params.values()

    def sources(value: AuthorizedFileScope, expected: dict[UUID, str]) -> None:
        assert {item.file_id: item.file_name for item in value.files} == expected
        assert value.file_ids == frozenset(
            expected) and len(value.files) == len(expected)

    def change(identifier: UUID, **values: object) -> None:
        with writer.session() as session:
            item = session.get(File, identifier)
            assert item is not None and item.owner_id in owners
            for name, value in values.items():
                setattr(item, name, value)
            session.commit()

    try:
        with writer.session() as session:
            for owner in owners:
                session.add(User(id=owner, name='Synthetic', email=f'{owner}@example.invalid',
                                 password='synthetic-placeholder', verified_at=now,
                                 created_at=now, updated_at=now))
            session.commit()
        for name, identifier in folders.items():
            parent = folders['selected'] if name == 'child' else folders['child'] if name == 'deep' else None
            with writer.session() as session:
                session.add(Folder(id=identifier, owner_id=owners[1] if name == 'foreign' else owners[0],
                                   parent_id=parent, name='same', description=None,
                                   created_at=now, updated_at=now))
                session.commit()
        with writer.session() as session:
            session.add_all(rows)
            session.commit()

        with patch('app.pipeline.folders.postgres', return_value=reader), patch(
                'app.core.runtime.storage', side_effect=AssertionError('No storage access')):
            expected = {first: 'same', second: 'same'}
            old = scope(folders['selected'])
            sources(old, expected)
            sources(scope(folders['foreign'], owners[1]), {foreign: 'foreign'})
            sources(scope(folders['empty']), {})
            sources(scope(folders['nonready']), {})
            missing = raises(FolderNotFoundError, lambda: scope(uuid4()))
            denied = raises(FolderNotFoundError,
                            lambda: scope(folders['foreign']))
            assert vars(missing) == vars(denied)
            raises(FolderNotFoundError, lambda: scope(
                folders['selected'], owners[1]))
            checks.append(
                'two-owner exact membership, privacy, empty/nonready and exclusions')

            sources(scope(folders['selected'], limit=3), expected)
            sources(scope(folders['selected'], limit=2), expected)
            raises(FolderScopeLimitError, lambda: scope(
                folders['selected'], limit=1))
            sources(scope(folders['large']), large)
            change(hundred, status='ready')
            large[hundred] = 'same'
            sources(scope(folders['large']), large)
            change(overflow, status='ready')
            raises(FolderScopeLimitError, lambda: scope(folders['large']))
            checks.append(
                'small boundaries and 99/100/101, ineligible rows excluded, no truncation')

            dynamic = cast(Callable[..., AuthorizedFileScope], resolve)
            count = len(reads)
            raises(TypeError, lambda: dynamic(owners[0], None, max_files=2))
            raises(TypeError, lambda: dynamic(
                str(owners[0]), folders['selected'], max_files=2))
            raises(TypeError, lambda: dynamic(owners[0], folders['selected']))
            raises(TypeError, lambda: dynamic(
                owners[0], folders['selected'], max_files=True))
            raises(ValueError, lambda: dynamic(
                owners[0], folders['selected'], max_files=0))
            assert len(reads) == count
            raises(FrozenInstanceError, lambda: setattr(old, 'files', ()))
            raises(FrozenInstanceError, lambda: setattr(
                old.files[0], 'file_name', 'changed'))
            raises(AttributeError, lambda: getattr(
                old.file_ids, 'add')(uuid4()))
            checks.append(
                'strict arguments before database access; detached frozen snapshot')

            change(first, name='renamed')
            sources(scope(folders['selected']), {
                    first: 'renamed', second: 'same'})
            change(incoming, status='ready')
            sources(scope(folders['selected']), {
                    first: 'renamed', second: 'same', incoming: 'same'})
            change(first, status='deleting')
            sources(scope(folders['selected']), {
                    second: 'same', incoming: 'same'})
            with writer.session() as session:
                session.execute(delete(File).where(
                    File.id == first, File.owner_id == owners[0]))
                session.commit()
            sources(scope(folders['selected']), {
                    second: 'same', incoming: 'same'})
            sources(old, expected)
            checks.append(
                'independent committed rename/new-ready/deleting/removal; old scope unchanged')

            with patch.object(ReadSession, 'execute', side_effect=SQLAlchemyError('private-sentinel')):
                failure = raises(PostgresOperationError,
                                 lambda: resolve(owners[0], folders['selected'], max_files=100))
                assert 'private-sentinel' not in str(
                    failure) and reads[-1].closed
            checks.append(
                'injected failure separately labelled: sanitized error and closed session')
            checks.append(
                'all real resolutions: one bounded unlocked SELECT; no flush/commit/storage')
    finally:
        with writer.session() as session:
            session.execute(delete(File).where(File.id.in_([UUID(item) for item in ledger['files']]),
                                               File.owner_id.in_(owners)))
            for name in reversed(names):
                session.execute(delete(Folder).where(
                    Folder.id == folders[name], Folder.owner_id.in_(owners)))
            session.execute(delete(User).where(User.id.in_(owners)))
            session.commit()
            assert not session.scalar(select(File.id).where(
                File.id.in_([UUID(item) for item in ledger['files']])))
            assert not session.scalar(select(Folder.id).where(
                Folder.id.in_(folders.values())))
            assert not session.scalar(
                select(User.id).where(User.id.in_(owners)))
        (directory /
         'cleanup.json').write_text(json.dumps({'exact_ledger_removed': True}) + '\n')
        engine.dispose()

    report = {'result': 'PASS', 'checks': checks, 'real_resolutions': len(reads) - 1,
              'owners': len(owners), 'folders': len(folders), 'files': len(rows)}
    (directory / 'postgres-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', required=True)
    parser.add_argument('--cleanup-ledger', action='store_true', required=True)
    arguments = parser.parse_args()
    execute(arguments.run)
