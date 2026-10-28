"""Opt-in registration acceptance against real PostgreSQL in a disposable DB.

Run from server with POSTGRES_HOST/PORT pointing to the available service. The
configured application database is inspected only; all writes use a UUID-named
database that is removed in finally. Output contains booleans/counts only.
"""
import sys
import json
import secrets
from uuid import uuid4
from threading import Barrier
from unittest.mock import patch
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.orm import Session as OrmSession, sessionmaker

from app.core.constants import constants
from app.pipeline.auth.password import Password

from app.db.postgres import Database, url
from app.models.postgres import User, Verification, Session

from app.routers.auth import router

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error

from tests.postgres_live import migrate, schema


def counts(database: Database) -> tuple[int, int, int]:
    """Measure identity row totals without reading or printing credentials."""
    with database.session() as session:
        totals = [int(session.execute(select(func.count()).select_from(model)).scalar_one())
                  for model in (User, Verification, Session)]

        return totals[0], totals[1], totals[2]


def acceptance(database: Database) -> dict[str, object]:
    """Exercise the actual HTTP/domain path with independent PostgreSQL sessions."""
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(ApiError, cast_handle_api_error())
    plaintext = secrets.token_urlsafe(24)
    identity = "registration-" + uuid4().hex
    email = identity + "@example.com"
    payload = {"name": "  Synthetic  Acceptance  ",
               "email": " " + email.upper() + " ", "password": plaintext}
    ttl = constants.otp.AUTH_OTP_TTL_SECONDS

    with patch("app.pipeline.auth.registration.postgres", return_value=database), TestClient(app) as client:
        before = datetime.now(timezone.utc)
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201, "Registration success status"
        assert response.json() == {"status": "verification_required"}
        assert "set-cookie" not in response.headers
        assert counts(database) == (1, 1, 0)
        with database.session() as session:
            user = session.scalars(
                select(User).where(User.email == email)).one()
            verification = session.scalars(select(Verification).where(
                Verification.user_id == user.id)).one()
            assert user.name == "Synthetic  Acceptance"
            assert user.email == email and user.verified_at is None
            assert user.password.startswith("$argon2id$")
            assert Password().verify(user.password, plaintext), "Stored password verification"
            assert verification.type == "auth"
            assert len(verification.otp) == 6 and verification.otp.isascii(
            ) and verification.otp.isdigit()
            assert user.created_at == user.updated_at == verification.created_at
            assert before <= user.created_at <= datetime.now(timezone.utc)
            assert (verification.expires_at -
                    verification.created_at).total_seconds() == ttl
            assert verification.expires_at > datetime.now(timezone.utc)
            original = (user.password, user.created_at, user.updated_at,
                        verification.id, verification.otp, verification.expires_at)
            identifier = user.id

        conflicts = []
        for verified in (False, True):
            if verified:
                with database.session() as session:
                    user = session.get(User, identifier)
                    assert user is not None
                    user.verified_at = datetime.now(timezone.utc)
                    session.commit()
            response = client.post(
                "/auth/register", json={**payload, "email": email})
            assert response.status_code == 409
            assert "set-cookie" not in response.headers
            conflicts.append(response.json())
            with database.session() as session:
                user = session.get(User, identifier)
                assert user is not None
                verification = session.scalars(select(Verification).where(
                    Verification.user_id == identifier)).one()
                assert original == (user.password, user.created_at, user.updated_at,
                                    verification.id, verification.otp, verification.expires_at), "Duplicate changed existing rows"
                assert (user.verified_at is not None) == verified
        assert conflicts == [
            {"error": "Account already exists", "code": "ACCOUNT_ALREADY_EXISTS"}] * 2

        for stage in ("verification", "commit"):
            class FailingSession(OrmSession):
                """Inject failures without changing the database schema."""

                def commit(self) -> None:
                    if stage == "commit":
                        raise SQLAlchemyError("Synthetic commit failure")

                    super().commit()

            def fail(session: OrmSession, context: object, instances: object) -> None:
                for row in session.new:
                    if isinstance(row, Verification):
                        row.user_id = uuid4()

            if stage == "verification":
                event.listen(FailingSession, "before_flush", fail)
            failing = Database(database.engine, sessionmaker(
                bind=database.engine, class_=FailingSession))
            failed_email = stage + "-" + uuid4().hex + "@example.com"
            try:
                with patch("app.pipeline.auth.registration.postgres", return_value=failing):
                    response = client.post(
                        "/auth/register", json={**payload, "email": failed_email})
                assert response.status_code == 500
                assert response.json()["code"] == "POSTGRES_OPERATION_FAILED"
                assert plaintext not in response.text
                with database.session() as session:
                    assert session.scalar(select(func.count()).select_from(
                        User).where(User.email == failed_email)) == 0
                assert counts(database) == (
                    1, 1, 0), "Partial registration survived rollback"
            finally:
                if stage == "verification":
                    event.remove(FailingSession, "before_flush", fail)

        concurrent = "concurrent-" + uuid4().hex + "@example.com"
        barrier = Barrier(2, timeout=15)

        def submit(uppercase: bool) -> int:
            with TestClient(app) as worker:
                barrier.wait()
                response = worker.post("/auth/register", json={
                    **payload, "email": " " + concurrent.upper() + " " if uppercase else concurrent})
                return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, (False, True)))
        assert statuses == [201, 409], "Concurrent registration outcome"
        with database.session() as session:
            assert session.scalar(select(func.count()).select_from(
                User).where(User.email == concurrent)) == 1
        assert counts(database) == (2, 2, 0)
        response = client.post(
            "/auth/register", json={**payload, "password": plaintext * 8})
        assert response.status_code == 422 and plaintext not in response.text

    return {"http": "passed", "stored_state": "passed", "duplicate_verified_unverified": "passed",
            "rollback_failures": 2, "concurrent_statuses": statuses, "sessions": 0}


def main() -> None:
    """Preserve normal data and always remove only the created acceptance DB."""
    source = create_engine(url(constants.postgres), hide_parameters=True,
                           connect_args={"connect_timeout": 3})
    admin = create_engine(url(constants.postgres).set(database="postgres"),
                          isolation_level="AUTOCOMMIT", hide_parameters=True,
                          connect_args={"connect_timeout": 3})
    name = "atlas_registration_" + uuid4().hex
    disposable = None
    created = False
    try:
        source_database = Database(source, sessionmaker(bind=source))
        schema(source)
        baseline = counts(source_database)
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migrate(name, "head")
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        disposable = Database(engine, sessionmaker(bind=engine))
        schema(engine)
        result = acceptance(disposable)
        schema(engine)
        schema(source)
        assert counts(
            source_database) == baseline, "Configured database row totals changed"
        print(json.dumps({**result, "schema": "unchanged", "head": "0001_identity",
                          "configured_database_counts": "preserved"}, sort_keys=True))
    finally:
        if disposable is not None:
            disposable.close()
        source.dispose()
        try:
            if created:
                with admin.connect() as connection:
                    connection.execute(
                        text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        finally:
            admin.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"registration_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
