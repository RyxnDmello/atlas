"""Canonical scope tests use isolated SQLite; they do not verify real PostgreSQL."""
import unittest
from typing import cast
from uuid import UUID, uuid4
from collections.abc import Callable
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from dataclasses import FrozenInstanceError

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import Table, create_engine, event, select

from app.db.postgres import Database
from app.pipeline.folders import resolve

from app.models.postgres import Base, File, Folder, User
from app.schemas.scope import AuthorizedFileScope, FileSource

from app.errors.postgres import PostgresOperationError
from app.errors.folder import FolderNotFoundError, FolderScopeLimitError


class ReadSession(Session):
    """Observe actual reads and closure, rejecting any attempt to flush or commit."""

    def __init__(self, *args, observed: list["ReadSession"] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.statements = []
        self.closed = False
        self.failure: SQLAlchemyError | None = None
        if observed is not None:
            observed.append(self)

    def execute(self, statement, *args, **kwargs):
        self.statements.append(statement)
        if self.failure is not None:
            raise self.failure

        return super().execute(statement, *args, **kwargs)

    def flush(self, *args, **kwargs):
        raise AssertionError("Scope resolution must not flush")

    def commit(self):
        raise AssertionError("Scope resolution must not commit")

    def close(self):
        self.closed = True
        super().close()


class FolderScopeTests(unittest.TestCase):
    """Exercise real SQL predicates, bounded reads and detached authorization values."""

    def setUp(self):
        engine = create_engine("sqlite://", hide_parameters=True)
        self.addCleanup(engine.dispose)

        @event.listens_for(engine, "connect")
        def constraints(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(engine)
        self.database = Database(engine, sessionmaker(bind=engine))
        self.now = datetime.now(timezone.utc)
        self.owners = (uuid4(), uuid4())
        with self.database.session() as session:
            for owner in self.owners:
                session.add(User(id=owner, name="Synthetic", email=f"{owner}@example.invalid",
                                 password="synthetic-placeholder", verified_at=self.now,
                                 created_at=self.now, updated_at=self.now))
            session.commit()
        self.root = self.folder(self.owners[0])
        self.child = self.folder(self.owners[0], self.root)
        self.deep = self.folder(self.owners[0], self.child)
        self.sibling = self.folder(self.owners[0])
        self.foreign = self.folder(self.owners[1])
        self.reads: list[ReadSession] = []
        factory = sessionmaker[Session](
            bind=engine, class_=ReadSession, observed=self.reads)
        self.reader = Database(engine, factory)
        scope = patch("app.pipeline.folders.postgres",
                      return_value=self.reader)
        self.runtime = scope.start()
        self.addCleanup(scope.stop)

    def folder(self, owner, parent=None):
        identifier = uuid4()
        with self.database.session() as session:
            session.add(Folder(id=identifier, owner_id=owner, parent_id=parent,
                               name="same", description=None,
                               created_at=self.now, updated_at=self.now))
            session.commit()

        return identifier

    def file(self, owner, folder, status="ready", name="same", database=None):
        identifier = uuid4()
        with (database or self.database).session() as session:
            session.add(File(id=identifier, owner_id=owner, folder_id=folder,
                             name=name, description=None, original_name="synthetic.md",
                             extension=".md", size_bytes=19, status=status,
                             created_at=self.now, updated_at=self.now))
            session.commit()

        return identifier

    def scope(self, folder=None, owner=None, limit=3):
        return resolve(owner or self.owners[0], folder or self.root, max_files=limit)

    def assert_sources(self, scope, expected):
        self.assertIsInstance(scope, AuthorizedFileScope)
        self.assertIsInstance(scope.files, tuple)
        self.assertEqual(
            {item.file_id: item.file_name for item in scope.files}, expected)
        self.assertEqual(scope.file_ids, frozenset(expected))
        self.assertEqual(len(scope.files), len(expected))
        self.assertTrue(all(isinstance(item, FileSource)
                        for item in scope.files))

    def test_exact_direct_ready_membership_for_two_owners_and_duplicate_names(self):
        expected = {
            self.file(self.owners[0], self.root): "same" for _ in range(2)}
        other = self.file(self.owners[1], self.foreign, name="other")
        for location in (None, self.child, self.deep, self.sibling):
            self.file(self.owners[0], location)
        for status in ("processing", "deleting"):
            self.file(self.owners[0], self.root, status)
        self.file(self.owners[1], None)

        self.assert_sources(self.scope(), expected)
        self.assert_sources(self.scope(
            self.foreign, self.owners[1]), {other: "other"})

    def test_owned_empty_and_non_ready_only_folders_are_not_missing(self):
        self.assert_sources(self.scope(limit=1), {})
        for status in ("processing", "deleting"):
            self.file(self.owners[0], self.root, status)

        self.assert_sources(self.scope(limit=1), {})

    def test_foreign_and_missing_folders_share_the_exact_error(self):
        self.file(self.owners[1], self.foreign, name="private-name")
        for identifier in (self.foreign, uuid4(), UUID(int=0)):
            with self.subTest(folder=identifier), self.assertRaises(FolderNotFoundError) as caught:
                self.scope(identifier)
            self.assertEqual(caught.exception.status, 404)
            self.assertEqual(caught.exception.to_dict(), {
                "error": "Folder not found", "code": "FOLDER_NOT_FOUND"})
            self.assertEqual(len(self.reads[-1].statements), 1)
            self.assertTrue(self.reads[-1].closed)

    def test_internal_uuid_validation_rejects_logical_root_before_runtime(self):
        invoke = cast(Callable[..., AuthorizedFileScope], resolve)
        for invalid in (None, "root", str(self.root), 0, True, [], {}):
            for owner, folder in ((invalid, self.root), (self.owners[0], invalid)):
                with self.subTest(owner=owner, folder=folder), self.assertRaises(TypeError):
                    invoke(owner, folder, max_files=1)
        self.runtime.assert_not_called()

    def test_ceiling_is_required_and_strictly_positive_without_coercion(self):
        invoke = cast(Callable[..., AuthorizedFileScope], resolve)
        with self.assertRaises(TypeError):
            invoke(self.owners[0], self.root)
        for invalid in (None, True, False, 1.0, "1", [], {}):
            with self.subTest(ceiling=invalid), self.assertRaises(TypeError):
                invoke(self.owners[0], self.root, max_files=invalid)
        for invalid in (0, -1, -100):
            with self.subTest(ceiling=invalid), self.assertRaises(ValueError):
                self.scope(limit=invalid)
        self.runtime.assert_not_called()

    def test_small_ceiling_boundaries_never_return_a_partial_scope(self):
        expected = {}
        for count in range(4):
            if count:
                expected[self.file(self.owners[0], self.root)] = "same"
            with self.subTest(count=count):
                if count <= 2:
                    self.assert_sources(self.scope(limit=2), expected)
                else:
                    with self.assertRaises(FolderScopeLimitError) as caught:
                        self.scope(limit=2)
                    self.assertEqual(caught.exception.status, 409)
                    self.assertEqual(caught.exception.to_dict(), {
                        "error": "This folder exceeds the supported Ask scope.",
                        "code": "FOLDER_SCOPE_LIMIT_EXCEEDED"})

    def test_provisional_100_boundary_is_only_an_explicit_test_input(self):
        expected = {
            self.file(self.owners[0], self.root): "same" for _ in range(100)}
        self.assert_sources(self.scope(limit=100), expected)
        self.file(self.owners[0], self.root)
        with self.assertRaises(FolderScopeLimitError):
            self.scope(limit=100)

    def test_ineligible_rows_do_not_consume_the_ceiling(self):
        expected = {self.file(self.owners[0], self.root): "same"}
        for _ in range(5):
            self.file(self.owners[0], self.root, "processing")
            self.file(self.owners[0], self.root, "deleting")
            self.file(self.owners[0], self.child)
            self.file(self.owners[1], self.foreign)

        self.assert_sources(self.scope(limit=1), expected)

    def test_sql_is_one_folder_anchored_bounded_unlocked_authorization_read(self):
        self.scope(limit=7)
        self.assertEqual(len(self.reads), 1)
        self.assertEqual(len(self.reads[0].statements), 1)
        statement = self.reads[0].statements[0]
        compiled = statement.compile(dialect=postgresql.dialect())
        sql = " ".join(str(compiled).split())
        join, where = sql.split(" WHERE ")
        self.assertTrue(sql.startswith(
            "SELECT folders.id, files.id AS id_1, files.name FROM folders LEFT OUTER JOIN files ON "))
        for predicate in ("files.folder_id = folders.id", "files.owner_id =", "files.status ="):
            self.assertIn(predicate, join)
        for predicate in ("folders.id =", "folders.owner_id =", "ORDER BY files.id", "LIMIT"):
            self.assertIn(predicate, where)
        self.assertNotIn("files.status", where)
        self.assertNotIn("FOR UPDATE", sql)
        self.assertNotIn("COUNT(", sql)
        self.assertNotIn("parent_id", sql)
        self.assertCountEqual(compiled.params.values(), [
                              self.owners[0], "ready", self.root, self.owners[0], 8])
        self.assertTrue(self.reads[0].closed)

    def test_fetch_materializes_at_most_ceiling_plus_one_rows(self):
        for _ in range(8):
            self.file(self.owners[0], self.root)
        original = ReadSession.execute
        observed = []

        def execute(session, statement, *args, **kwargs):
            result = original(session, statement, *args, **kwargs)
            rows = result.all()
            observed.append(len(rows))
            return Mock(all=Mock(return_value=rows))

        with patch.object(ReadSession, "execute", execute), self.assertRaises(FolderScopeLimitError):
            self.scope(limit=2)
        self.assertEqual(observed, [3])
        self.assertTrue(self.reads[-1].closed)

    def test_independent_owner_predicate_with_isolated_inconsistent_fixture(self):
        engine = create_engine("sqlite://", hide_parameters=True)
        self.addCleanup(engine.dispose)
        Base.metadata.create_all(engine)
        database = Database(engine, sessionmaker(bind=engine))
        with self.database.engine.connect() as source, engine.begin() as target:
            for table in (User.__table__, Folder.__table__):
                table = cast(Table, table)
                target.execute(table.insert(), [dict(
                    row) for row in source.execute(select(table)).mappings()])
        identifier = self.file(
            self.owners[1], self.root, name="foreign", database=database)
        with database.session() as session:
            self.assertIsNotNone(session.get(File, identifier))
        with patch("app.pipeline.folders.postgres", return_value=database):
            self.assert_sources(self.scope(), {})

    def test_entries_scope_and_membership_are_immutable_after_session_close(self):
        identifier = self.file(self.owners[0], self.root)
        scope = self.scope()
        self.assertTrue(self.reads[-1].closed)
        self.assert_sources(scope, {identifier: "same"})
        with self.assertRaises(FrozenInstanceError):
            setattr(scope, "files", ())
        with self.assertRaises(FrozenInstanceError):
            setattr(scope.files[0], "file_name", "changed")
        with self.assertRaises(AttributeError):
            getattr(scope.file_ids, "add")(uuid4())
        self.assertFalse(hasattr(scope, "__dict__"))
        self.assertFalse(hasattr(scope.files[0], "__dict__"))

    def test_snapshot_survives_rename_new_ready_deleting_and_removal(self):
        identifier = self.file(self.owners[0], self.root, name="before")
        pending = self.file(self.owners[0], self.root, "processing", "new")
        original = self.scope()
        with self.database.session() as session:
            file = session.get(File, identifier)
            assert file is not None
            file.name = "after"
            ready = session.get(File, pending)
            assert ready is not None
            ready.status = "ready"
            session.commit()
        renamed = self.scope()
        self.assert_sources(renamed, {identifier: "after", pending: "new"})
        self.assert_sources(original, {identifier: "before"})
        with self.database.session() as session:
            file = session.get(File, identifier)
            assert file is not None
            file.status = "deleting"
            session.commit()
        self.assert_sources(self.scope(), {pending: "new"})
        with self.database.session() as session:
            file = session.get(File, identifier)
            assert file is not None
            session.delete(file)
            session.commit()
        self.assert_sources(self.scope(), {pending: "new"})
        self.assert_sources(original, {identifier: "before"})
        self.assert_sources(renamed, {identifier: "after", pending: "new"})

    def test_success_missing_and_overflow_do_not_write_or_initialize_storage(self):
        expected = {
            self.file(self.owners[0], self.root): "same" for _ in range(2)}
        statements = []

        def record(connection, cursor, statement, parameters, context, many):
            statements.append(statement)

        event.listen(self.database.engine, "before_cursor_execute", record)
        self.addCleanup(event.remove, self.database.engine,
                        "before_cursor_execute", record)
        with patch("app.core.runtime.storage", side_effect=AssertionError("Unexpected storage access")):
            self.assert_sources(self.scope(limit=2), expected)
            with self.assertRaises(FolderNotFoundError):
                self.scope(self.foreign)
            with self.assertRaises(FolderScopeLimitError):
                self.scope(limit=1)
        self.assertEqual(len(statements), 3)
        self.assertTrue(all(statement.startswith("SELECT ")
                        for statement in statements))
        self.assertTrue(all(session.closed for session in self.reads))

    def test_sqlalchemy_execute_failure_is_sanitized_and_session_closes(self):
        factory = self.reader.sessions

        def failing_session():
            value = factory()
            assert isinstance(value, ReadSession)
            value.failure = SQLAlchemyError("private driver parameters")
            return value

        with patch.object(self.reader, "sessions", side_effect=failing_session):
            with self.assertRaises(PostgresOperationError) as caught:
                self.scope()
        self.assertEqual(caught.exception.to_dict(), {
            "error": "Unable to complete database operation", "code": "POSTGRES_OPERATION_FAILED"})
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertTrue(self.reads[-1].closed)

    def test_sqlalchemy_entry_fetch_and_exit_failures_remain_database_errors(self):
        for phase in ("entry", "fetch", "exit"):
            context = Mock()
            context.__enter__ = Mock(return_value=Mock())
            context.__exit__ = Mock(return_value=False)
            error = SQLAlchemyError("private database diagnostic")
            if phase == "entry":
                context.__enter__.side_effect = error
            elif phase == "fetch":
                context.__enter__.return_value.execute.return_value.all.side_effect = error
            else:
                context.__enter__.return_value.execute.return_value.all.return_value = [
                    (self.root, None, None)]
                context.__exit__.side_effect = error
            with self.subTest(phase=phase), patch.object(self.reader, "session", return_value=context):
                with self.assertRaises(PostgresOperationError) as caught:
                    self.scope()
                self.assertNotIn("private", str(caught.exception))
            if phase != "entry":
                context.__exit__.assert_called_once()
