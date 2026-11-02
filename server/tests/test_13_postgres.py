import io
import os
import asyncio
import traceback
from typing import cast
from pathlib import Path
from unittest import TestCase
from threading import get_ident
from contextlib import ExitStack
from unittest.mock import Mock, patch

from pydantic import ValidationError
from fastapi.testclient import TestClient

from alembic import command
from alembic.config import Config

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import CHAR, DateTime, Engine, String, Text, UniqueConstraint, Uuid

from app.core.runtime import postgres
from app.core.constants import Constants

from app.models.postgres import Base
from app.db.postgres import Database, prepare, url
from app.schemas.constants import PostgresConstants

from app.errors.api import ApiError
from app.errors.postgres import PostgresConnectionError

from app.main import app

from tests.postgres import database


class PostgresConfigTests(TestCase):
    """Cover literal credentials, required settings, and safe validation failures."""

    def test_required_nonblank_and_port_validation(self) -> None:
        values = {name: value for name, value in os.environ.items()
                  if name in PostgresConstants.model_fields}
        values.update({
            "POSTGRES_HOST": "localhost", "POSTGRES_DB": "test",
            "POSTGRES_USER": "test", "POSTGRES_PASSWORD": "fake-secret",
        })
        values.pop("POSTGRES_PORT", None)
        self.assertEqual(PostgresConstants.model_validate(
            values).POSTGRES_PORT, 5432)
        for name in ("POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"):
            for value in (None, "", " \t"):
                current = dict(values)
                if value is None:
                    current.pop(name)
                else:
                    current[name] = value

                with self.subTest(name=name, value=value), self.assertRaises(ValidationError):
                    PostgresConstants.model_validate(current)

        for value in (0, -1, 65536, "not-an-int", "", None):
            with self.subTest(port=value), self.assertRaises(ValidationError):
                PostgresConstants.model_validate(
                    {**values, "POSTGRES_PORT": value})

    def test_reserved_credentials_survive_url_construction(self) -> None:
        password = "fake:@/%?#[] secret"
        with patch.dict(os.environ, {"POSTGRES_PASSWORD": password, "POSTGRES_USER": "test@user"}):
            config = Constants().postgres
            address = url(config)

        self.assertEqual(address.get_backend_name(), "postgresql")
        self.assertEqual(address.get_driver_name(), "psycopg")
        self.assertEqual(address.password, password)
        self.assertEqual(address.username, "test@user")
        self.assertNotIn(password, repr(config.POSTGRES_PASSWORD))
        self.assertNotIn(password, repr(address))
        self.assertNotIn(password, str(address))

    def test_validation_errors_hide_input(self) -> None:
        sentinel = "private-port-sentinel"
        with patch.dict(os.environ, {"POSTGRES_PORT": sentinel}):
            with self.assertRaises(ValidationError) as caught:
                Constants()

        self.assertNotIn(sentinel, str(caught.exception))


class PostgresMetadataTests(TestCase):
    """Verify exact identity metadata without claiming live PostgreSQL acceptance."""

    def test_exact_columns_types_and_nullability(self) -> None:
        expected = {
            "users": {"id", "name", "email", "password", "verified_at", "created_at", "updated_at"},
            "verifications": {"id", "user_id", "type", "otp", "expires_at", "created_at"},
            "sessions": {"id", "user_id", "token_hash", "expires_at", "created_at"},
        }
        self.assertEqual(set(Base.metadata.tables), set(expected))
        for name, columns in expected.items():
            table = Base.metadata.tables[name]
            self.assertEqual(set(table.columns.keys()), columns)
            self.assertEqual(
                [column.name for column in table.primary_key], ["id"])
            self.assertIsInstance(table.c.id.type, Uuid)
            self.assertIsNotNone(table.c.id.default)
            self.assertIsNone(table.c.id.server_default)
            for column in table.columns:
                self.assertEqual(column.nullable, column.name == "verified_at")
                if column.name.endswith("_at"):
                    self.assertIsInstance(column.type, DateTime)
                    self.assertTrue(cast(DateTime, column.type).timezone)

        users = Base.metadata.tables["users"]
        for name in ("name", "email", "password"):
            self.assertIsInstance(users.c[name].type, Text)

        verification = Base.metadata.tables["verifications"]
        self.assertIsInstance(verification.c.type.type, ENUM)
        purpose = cast(ENUM, verification.c.type.type)
        self.assertEqual(purpose.name, "verification_type")
        self.assertEqual(purpose.enums,
                         ["auth", "reset", "forgot"])
        self.assertIsInstance(verification.c.otp.type, String)
        self.assertEqual(cast(String, verification.c.otp.type).length, 6)
        self.assertIsInstance(
            Base.metadata.tables["sessions"].c.token_hash.type, CHAR)
        self.assertEqual(
            cast(CHAR, Base.metadata.tables["sessions"].c.token_hash.type).length, 64)

    def test_exact_constraints_indexes_and_cascades(self) -> None:
        expected = {
            "users": {("email",)},
            "verifications": {("user_id", "type")},
            "sessions": {("token_hash",)},
        }
        for name, keys in expected.items():
            table = Base.metadata.tables[name]
            self.assertEqual({tuple(constraint.columns.keys()) for constraint in table.constraints
                              if isinstance(constraint, UniqueConstraint)}, keys)
            self.assertTrue(
                all(constraint.name for constraint in table.constraints))
            if name == "users":
                self.assertEqual(len(table.foreign_keys), 0)
            else:
                self.assertEqual(len(table.foreign_keys), 1)
                key = next(iter(table.foreign_keys))
                self.assertEqual(key.target_fullname, "users.id")
                self.assertEqual(key.parent.name, "user_id")
                self.assertEqual(key.ondelete, "CASCADE")
                self.assertIsInstance(key.parent.type, Uuid)

        indexes = {index.name: (tuple(index.columns.keys()), index.unique)
                   for table in Base.metadata.tables.values() for index in table.indexes}
        self.assertEqual(
            indexes, {"ix_sessions_user_id": (("user_id",), False)})


class PostgresRuntimeTests(TestCase):
    """Exercise ownership and read-only queries through mocked engine connections."""

    def test_prepare_once_and_probe_reuses_engine(self) -> None:
        engine = Mock(spec=Engine)
        connection = Mock()
        scope = Mock()
        scope.__enter__ = Mock(return_value=connection)
        scope.__exit__ = Mock(return_value=False)
        engine.connect.return_value = scope
        connection.execute.return_value.scalar_one.return_value = "18.6"

        with patch("app.db.postgres.create_engine", return_value=engine) as factory:
            ready = prepare()
            self.assertIs(ready.sessions.kw["bind"], engine)
            self.assertEqual(ready.check(), "18.6")
            self.assertEqual(ready.check(), "18.6")
            ready.close()

        factory.assert_called_once()
        self.assertTrue(factory.call_args.kwargs["pool_pre_ping"])
        self.assertTrue(factory.call_args.kwargs["hide_parameters"])
        self.assertEqual([str(call.args[0]) for call in connection.execute.call_args_list],
                         ["SELECT 1", "SHOW server_version"] * 3)
        self.assertEqual(scope.__exit__.call_count, 3)
        engine.dispose.assert_called_once()

    def test_sessions_are_distinct_close_and_do_not_implicitly_commit(self) -> None:
        engine = Mock(spec=Engine)
        factory = sessionmaker(bind=engine)
        ready = Database(engine, factory)
        with patch.object(Session, "close", autospec=True) as closer, patch.object(Session, "commit") as commit:
            with ready.session() as first:
                self.assertIs(first.get_bind(), engine)
            with ready.session() as second:
                self.assertIs(second.get_bind(), engine)

        self.assertIsNot(first, second)
        self.assertEqual(closer.call_count, 2)
        commit.assert_not_called()
        engine.connect.assert_not_called()

    def test_failed_transaction_rolls_back_and_closes(self) -> None:
        session = Session()
        ready = Database(Mock(spec=Engine), sessionmaker())
        with patch.object(ready, "sessions", return_value=session), patch.object(Session, "rollback", autospec=True) as rollback, patch.object(Session, "close", autospec=True) as close:
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with ready.session() as current:
                    self.assertIs(current, session)
                    raise RuntimeError("injected")

        rollback.assert_called_once_with(session)
        close.assert_called_once_with(session)

    def test_connectivity_failures_are_safe_and_dispose_failed_preparation(self) -> None:
        engine = Mock(spec=Engine)
        engine.connect.side_effect = RuntimeError("private-driver-secret")
        with patch("app.db.postgres.create_engine", return_value=engine):
            with self.assertRaises(PostgresConnectionError) as caught:
                prepare()

        self.assertEqual(caught.exception.status, 503)
        self.assertEqual(caught.exception.to_dict(), {
            "error": "Unable to connect to PostgreSQL", "code": "POSTGRES_CONNECTION_FAILED",
        })
        self.assertNotIn("private-driver-secret",
                         "".join(traceback.format_exception(caught.exception)))
        engine.dispose.assert_called_once()

    def test_engine_construction_failure_is_safe(self) -> None:
        with patch("app.db.postgres.create_engine", side_effect=RuntimeError("private-driver-secret")):
            with self.assertRaises(PostgresConnectionError) as caught:
                prepare()

        self.assertNotIn("private-driver-secret",
                         "".join(traceback.format_exception(caught.exception)))

    def test_query_failure_closes_connection_and_hides_driver_details(self) -> None:
        engine = Mock(spec=Engine)
        connection = Mock()
        scope = Mock()
        scope.__enter__ = Mock(return_value=connection)
        scope.__exit__ = Mock(return_value=False)
        engine.connect.return_value = scope
        connection.execute.side_effect = RuntimeError("private-query-sentinel")
        ready = Database(engine, sessionmaker(bind=engine))

        with self.assertNoLogs("app.core.logging"), self.assertRaises(PostgresConnectionError) as caught:
            ready.check()

        scope.__exit__.assert_called_once()
        self.assertNotIn("private-query-sentinel",
                         "".join(traceback.format_exception(caught.exception)))
        engine.dispose.assert_not_called()


class PostgresLifespanTests(TestCase):
    """Prove startup/shutdown cleanup, thread ownership, and runtime restoration."""

    def test_ready_runtime_is_reused_and_restored_without_schema_work(self) -> None:
        ready = database()
        resources = Mock()
        loop = get_ident()
        workers = []
        try:
            previous = postgres()
        except ApiError:
            previous = None

        def prepared():
            with self.assertRaises(RuntimeError):
                asyncio.get_running_loop()

            workers.append(get_ident())

            return ready

        def closed():
            with self.assertRaises(RuntimeError):
                asyncio.get_running_loop()

            workers.append(get_ident())

        ready.close.side_effect = closed
        with (
            patch("app.core.lifespan.prepare", side_effect=prepared) as factory,
            patch("app.core.lifespan.initialize", return_value=resources),
            patch.object(Base.metadata, "create_all") as create,
            patch("alembic.command.upgrade") as migrate,
        ):
            with TestClient(app):
                self.assertIs(postgres(), ready)
                self.assertIs(postgres(), ready)

            factory.assert_called_once_with()
            ready.close.assert_called_once_with()
            resources.client.close.assert_called_once_with()
            create.assert_not_called()
            migrate.assert_not_called()

        self.assertEqual(len(workers), 2)
        self.assertTrue(all(worker != loop for worker in workers))
        if previous is None:
            with self.assertRaises(ApiError):
                postgres()
        else:
            self.assertIs(postgres(), previous)

    def test_later_startup_failure_disposes_postgres(self) -> None:
        ready = database()
        with patch("app.core.lifespan.prepare", return_value=ready), patch(
                "app.core.lifespan.initialize", side_effect=RuntimeError("injected")):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with TestClient(app):
                    self.fail("Startup must fail")

        ready.close.assert_called_once_with()

    def test_postgres_failure_prevents_later_startup(self) -> None:
        with patch("app.core.lifespan.prepare", side_effect=PostgresConnectionError()), patch(
                "app.core.lifespan.initialize") as initialize:
            with self.assertRaises(PostgresConnectionError):
                with TestClient(app):
                    self.fail("Startup must fail")

        initialize.assert_not_called()

    def test_postgres_closes_even_if_qdrant_close_fails(self) -> None:
        ready = database()
        resources = Mock()
        resources.client.close.side_effect = RuntimeError("injected")
        with patch("app.core.lifespan.prepare", return_value=ready), patch(
                "app.core.lifespan.initialize", return_value=resources):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with TestClient(app):
                    pass

        ready.close.assert_called_once_with()


class PostgresHealthTests(TestCase):
    """Test all independent database states and recovery over the HTTP contract."""

    def test_independent_health_combinations_and_recovery(self) -> None:
        ready = database()
        services = Mock()
        services.collection = "test-collection"
        healthy = {"status": "PostgreSQL Healthy", "version": "18.6"}
        unhealthy = {
            "status": "PostgreSQL Unhealthy", "error": "Unable to connect to PostgreSQL",
            "code": "POSTGRES_CONNECTION_FAILED",
        }
        with ExitStack() as scope:
            factory = scope.enter_context(
                patch("app.core.lifespan.prepare", return_value=ready))
            scope.enter_context(
                patch("app.core.lifespan.initialize", return_value=services))
            qdrant = scope.enter_context(
                patch("app.routers.system.qdrant_health"))
            http = scope.enter_context(TestClient(app))
            for qdrant_ok in (True, False):
                for postgres_ok in (True, False, True):
                    qdrant.return_value = {"status": "Qdrant Healthy"} if qdrant_ok else {
                        "status": "unhealthy", "error": "Unable to inspect Qdrant collection",
                        "code": "QDRANT_CONNECTION_FAILED",
                    }
                    ready.check.side_effect = None if postgres_ok else PostgresConnectionError()
                    response = http.get("/system/health/databases")

                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json()["postgres"], healthy if postgres_ok else unhealthy)
                    self.assertEqual(
                        response.json()["qdrant"], qdrant.return_value)

            factory.assert_called_once_with()
            self.assertEqual(ready.check.call_count, 6)
            ready.session.assert_not_called()

    def test_unavailable_postgres_runtime_is_safe(self) -> None:
        with patch("app.routers.system.postgres", side_effect=ApiError("not ready", "INTERNAL_SERVER_ERROR")), patch(
                "app.routers.system.qdrant_health", return_value={"status": "Qdrant Healthy"}):
            response = TestClient(app).get("/system/health/databases")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["postgres"]["code"], "POSTGRES_CONNECTION_FAILED")
        self.assertNotIn("not ready", response.text)


class PostgresMigrationTests(TestCase):
    """Check revision discovery and offline DDL; live constraint acceptance is deferred."""

    def test_offline_upgrade_and_downgrade_render_dependency_safe_identity_ddl(self) -> None:
        buffer = io.StringIO()
        config = Config(
            str(Path(__file__).resolve().parents[1] / "alembic.ini"), output_buffer=buffer)
        command.upgrade(config, "head", sql=True)
        sql = buffer.getvalue()
        self.assertEqual(sql.count("CREATE TYPE verification_type"), 1)
        self.assertIn("ENUM ('auth', 'reset', 'forgot')", sql)
        for name in ("users", "verifications", "sessions"):
            self.assertEqual(sql.count(f"CREATE TABLE {name} ("), 1)

        self.assertEqual(sql.count("ON DELETE CASCADE"), 2)
        self.assertIn("UNIQUE (email)", sql)
        self.assertIn("UNIQUE (user_id, type)", sql)
        self.assertIn("UNIQUE (token_hash)", sql)
        self.assertIn(
            "CREATE INDEX ix_sessions_user_id ON sessions (user_id)", sql)
        self.assertIn("TIMESTAMP WITH TIME ZONE", sql)
        self.assertNotIn("CREATE TABLE folders", sql)
        self.assertNotIn("CREATE TABLE files", sql)
        self.assertNotIn("postgresql+psycopg", sql)
        buffer.seek(0)
        buffer.truncate()
        command.downgrade(config, "0001_identity:base", sql=True)
        sql = buffer.getvalue()
        self.assertLess(sql.index("DROP TABLE sessions"),
                        sql.index("DROP TABLE users"))
        self.assertLess(sql.index("DROP TABLE verifications"),
                        sql.index("DROP TABLE users"))
        self.assertLess(sql.index("DROP TABLE verifications"),
                        sql.index("DROP TYPE verification_type"))
