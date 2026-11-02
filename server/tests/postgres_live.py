"""Run opt-in PostgreSQL acceptance against the configured real service.

Pipe this file into the running server container after an explicit Alembic upgrade.
The configured database is inspected only. Writes and migration reversal use a
uniquely named disposable database with cleanup in finally. Keep PostgreSQL
available until the command exits so that cleanup can drop that database.
"""
import os
import sys
import json
import subprocess
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata

from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.orm import Session as OrmSession, sessionmaker
from sqlalchemy import DateTime, Engine, create_engine, inspect, text

from app.core.constants import constants

from app.db.postgres import Database, prepare, url

from app.models.postgres import Base, User, Verification, Session


def schema(engine: Engine) -> None:
    """Assert the live identity schema, including migration/model agreement."""
    inspector = inspect(engine)
    assert isinstance(inspector, PGInspector)
    assert set(inspector.get_table_names()) == {
        "alembic_version", "users", "verifications", "sessions",
    }
    expected = {
        "users": {
            "id": "UUID", "name": "TEXT", "email": "TEXT", "password": "TEXT",
            "verified_at": "TIMESTAMP", "created_at": "TIMESTAMP", "updated_at": "TIMESTAMP",
        },
        "verifications": {
            "id": "UUID", "user_id": "UUID", "type": "VARCHAR(6)",
            "otp": "VARCHAR(6)", "expires_at": "TIMESTAMP", "created_at": "TIMESTAMP",
        },
        "sessions": {
            "id": "UUID", "user_id": "UUID", "token_hash": "CHAR(64)",
            "expires_at": "TIMESTAMP", "created_at": "TIMESTAMP",
        },
    }
    for table, columns in expected.items():
        actual = inspector.get_columns(table)
        assert {column["name"]: str(column["type"])
                for column in actual} == columns
        for column in actual:
            assert column["nullable"] == (
                table == "users" and column["name"] == "verified_at")
            if column["name"].endswith("_at"):
                kind = column["type"]
                assert isinstance(kind, DateTime)
                assert kind.timezone is True
        assert inspector.get_pk_constraint(
            table)["constrained_columns"] == ["id"]
    enums = {item["name"]: item["labels"] for item in inspector.get_enums()}
    assert enums == {"verification_type": ["auth", "reset", "forgot"]}
    for table, columns in (("users", ["email"]), ("verifications", ["user_id", "type"]), ("sessions", ["token_hash"])):
        assert [item["column_names"]
                for item in inspector.get_unique_constraints(table)] == [columns]
    for table in ("verifications", "sessions"):
        foreign = inspector.get_foreign_keys(table)
        assert len(foreign) == 1
        assert foreign[0]["constrained_columns"] == ["user_id"]
        assert foreign[0]["referred_table"] == "users"
        assert foreign[0]["referred_columns"] == ["id"]
        assert foreign[0].get("options", {}).get("ondelete") == "CASCADE"
    indexes = inspector.get_indexes("sessions")
    assert any(item["name"] == "ix_sessions_user_id" and item["column_names"] == [
               "user_id"] and not item["unique"] for item in indexes)
    with engine.connect() as connection:
        assert connection.execute(
            text("SELECT version_num FROM alembic_version")).scalar_one() == "0001_identity"
        assert compare_metadata(MigrationContext.configure(
            connection), Base.metadata) == []


def reject(session: OrmSession, record: Base, constraint: str) -> None:
    """Require a named PostgreSQL constraint to reject a synthetic write."""
    try:
        with session.begin_nested():
            session.add(record)
            session.flush()
    except IntegrityError as error:
        assert getattr(getattr(error.orig, "diag", None),
                       "constraint_name", None) == constraint
    else:
        raise AssertionError(f"Constraint did not reject write: {constraint}")


def constraints(database: Database) -> None:
    """Exercise ORM defaults, uniqueness, foreign keys, rollback, and DB cascades."""
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=10)
    with database.session() as session:
        user = User(name="Synthetic acceptance", email="acceptance@example.invalid",
                    password="synthetic-placeholder", created_at=now, updated_at=now)
        session.add(user)
        session.flush()
        assert user.id is not None
        verification = dict(user_id=user.id, type="auth",
                            otp="000000", expires_at=expiry, created_at=now)
        credential = dict(user_id=user.id, token_hash="0" *
                          64, expires_at=expiry, created_at=now)
        session.add_all([Verification(**verification), Session(**credential)])
        session.flush()
        reject(session, User(name="Duplicate", email=user.email,
               password="synthetic-placeholder", created_at=now, updated_at=now), "uq_users_email")
        reject(session, Verification(**verification),
               "uq_verifications_user_id_type")
        reject(session, Session(**credential), "uq_sessions_token_hash")
        reject(session, Verification(
            **{**verification, "user_id": uuid4()}), "fk_verifications_user_id_users")
        reject(session, Session(**{**credential, "user_id": uuid4(),
               "token_hash": "1" * 64}), "fk_sessions_user_id_users")
        session.add_all([Verification(
            **{**verification, "type": purpose}) for purpose in ("reset", "forgot")])
        session.flush()
        session.delete(user)
        session.flush()
        for table in ("users", "verifications", "sessions"):
            assert session.execute(
                text(f"SELECT count(*) FROM {table}")).scalar_one() == 0
        session.commit()
    try:
        with database.session() as session:
            session.add(User(name="Rollback", email="rollback@example.invalid",
                        password="synthetic-placeholder", created_at=now, updated_at=now))
            session.flush()
            raise RuntimeError("Synthetic rollback")
    except RuntimeError:
        pass
    with database.session() as session:
        assert session.execute(
            text("SELECT count(*) FROM users")).scalar_one() == 0


def migrate(name: str, target: str) -> None:
    """Run the packaged explicit Alembic command without printing configuration."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade" if target ==
            "head" else "downgrade", target],
        env={**os.environ, "POSTGRES_DB": name}, capture_output=True, text=True,
    )
    assert result.returncode == 0, "Disposable migration failed; inspect safely"


def main() -> None:
    """Inspect the development DB and isolate destructive acceptance elsewhere."""
    database = prepare()
    admin = create_engine(url(constants.postgres).set(
        database="postgres"), isolation_level="AUTOCOMMIT", hide_parameters=True)
    name = "atlas_verify_" + uuid4().hex
    disposable = None
    created = False
    try:
        version = database.check()
        assert version.startswith("18.")
        schema(database.engine)
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migrate(name, "head")
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        disposable = Database(engine, sessionmaker(bind=engine))
        schema(disposable.engine)
        constraints(disposable)
        disposable.close()
        migrate(name, "base")
        inspector = inspect(disposable.engine)
        assert isinstance(inspector, PGInspector)
        assert set(inspector.get_table_names()) <= {"alembic_version"}
        assert inspector.get_enums() == []
        disposable.close()
        migrate(name, "head")
        schema(disposable.engine)
        print(json.dumps({"postgres_version": version, "schema": "passed", "migration_model_diff": "empty", "unique_constraints": 3,
              "foreign_key_rejections": 2, "cascade": "passed", "rollback": "passed", "disposable_upgrade_downgrade_upgrade": "passed"}))
    finally:
        if disposable is not None:
            disposable.close()
        database.close()
        if created:
            with admin.connect() as connection:
                connection.execute(
                    text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


if __name__ == "__main__":
    main()
