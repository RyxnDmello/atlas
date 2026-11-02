"""Opt-in login acceptance; synthetic writes use a migrated disposable database."""

import sys
import json
import secrets
from uuid import uuid4
from threading import Barrier
from unittest.mock import patch
from argon2 import PasswordHasher
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import Session as OrmSession, sessionmaker

from app.core.constants import constants
from app.db.postgres import Database, url

from app.pipeline.auth.login import login
from app.pipeline.auth.access import Access
from app.pipeline.auth.refresh import digest
from app.pipeline.auth.password import Password

from app.schemas.auth.login import LoginRequest
from app.models.postgres import User, Verification, Session

from app.errors.postgres import PostgresOperationError
from app.errors.auth import CredentialError, InvalidCredentialsError, VerificationRequiredError

from tests.registration_live import counts
from tests.postgres_live import migrate, schema


def fixture(database: Database, *, verified: bool = True, verification: bool = False,
            outdated: bool = False) -> tuple[str, str]:
    """Generate private credentials, optionally with supported older Argon parameters."""
    now = datetime.now(timezone.utc)
    email = uuid4().hex + "@example.com"
    supplied = secrets.token_urlsafe(24)
    encoded = (PasswordHasher(time_cost=1, memory_cost=1024, parallelism=1).hash(supplied)
               if outdated else Password().hash(supplied))
    with database.session() as session:
        user = User(name="Synthetic", email=email, password=encoded,
                    verified_at=now if verified else None, created_at=now, updated_at=now)
        session.add(user)
        session.flush()
        if verification:
            session.add(Verification(user_id=user.id, type="auth", otp="012345",
                                     created_at=now, expires_at=now + timedelta(seconds=600)))
        session.commit()
    return email, supplied


def snapshot(database: Database, email: str) -> tuple[tuple, list[tuple], list[tuple]]:
    """Return private values for comparisons only; never include them in diagnostics."""
    with database.session() as session:
        user = session.scalars(select(User).where(User.email == email)).one()
        verifications = session.scalars(select(Verification).where(
            Verification.user_id == user.id).order_by(Verification.id)).all()
        sessions = session.scalars(select(Session).where(
            Session.user_id == user.id).order_by(Session.id)).all()
        return ((user.id, user.password, user.verified_at, user.created_at, user.updated_at),
                [(row.id, row.type, row.otp, row.created_at, row.expires_at)
                 for row in verifications],
                [(row.id, row.token_hash, row.created_at, row.expires_at) for row in sessions])


def acceptance(database: Database) -> dict[str, object]:
    """Prove canonical rollback, no unverified mutation, and independent concurrent sessions."""
    with patch("app.pipeline.auth.login.postgres", return_value=database):
        errors = []
        verified, supplied = fixture(database)
        for email, password in ((uuid4().hex + "@example.com", supplied),
                                (verified, supplied + "wrong")):
            before = snapshot(database, verified)
            try:
                login(LoginRequest.model_validate(
                    {"email": email, "password": password}))
                raise AssertionError("Invalid credentials accepted")
            except InvalidCredentialsError as error:
                errors.append((error.status, error.to_dict()))
            assert snapshot(database, verified) == before

        for present in (False, True):
            email, password = fixture(
                database, verified=False, verification=present, outdated=True)
            before = snapshot(database, email)
            try:
                login(LoginRequest.model_validate(
                    {"email": email, "password": password + "wrong"}))
                raise AssertionError("Unverified wrong password accepted")
            except InvalidCredentialsError as error:
                assert (error.status, error.to_dict()) == errors[0]
            with patch("app.pipeline.auth.verification.generate") as otp, patch.object(Password, "hash") as hashing:
                try:
                    login(LoginRequest.model_validate(
                        {"email": email, "password": password}))
                    raise AssertionError("Unverified account authenticated")
                except VerificationRequiredError as error:
                    assert error.status == 403
                otp.assert_not_called()
                hashing.assert_not_called()
            assert snapshot(database, email) == before
        assert errors[0] == errors[1]

        before = snapshot(database, verified)
        result = login(LoginRequest.model_validate(
            {"email": verified, "password": supplied}))
        after = snapshot(database, verified)
        assert after[0] == before[0] and after[1] == before[1]
        assert len(after[2]) == 1 and after[2][0][1] == digest(
            result.credentials.refresh)
        assert after[2][0][1] != result.credentials.refresh
        assert (after[2][0][3] - after[2][0][2]
                ).total_seconds() == constants.refresh.AUTH_REFRESH_TOKEN_TTL_SECONDS
        assert Access().decode(result.credentials.access).user == after[0][0]

        email, password = fixture(database, outdated=True)
        before = snapshot(database, email)
        assert Password().needs_rehash(before[0][1])
        login(LoginRequest.model_validate(
            {"email": email, "password": password}))
        after = snapshot(database, email)
        assert after[0][1] != before[0][1]
        assert Password().verify(after[0][1], password)
        assert not Password().needs_rehash(after[0][1])
        assert len(after[2]) == 1

        class FailingSession(OrmSession):
            def commit(self) -> None:
                assert any(isinstance(row, User) for row in self.dirty)
                assert any(isinstance(row, Session) for row in self.new)
                self.flush()
                raise SQLAlchemyError("Synthetic commit failure")

        def fail_session(session: OrmSession, context: object, instances: object) -> None:
            if any(isinstance(row, Session) for row in session.new):
                assert any(isinstance(row, User) for row in session.dirty)
                raise SQLAlchemyError("Synthetic session flush failure")

        for failure in ("flush", "commit"):
            email, password = fixture(database, outdated=True)
            before = snapshot(database, email)
            failing = (Database(database.engine, sessionmaker(bind=database.engine, class_=FailingSession))
                       if failure == "commit" else database)
            if failure == "flush":
                event.listen(OrmSession, "before_flush", fail_session)
            try:
                with patch("app.pipeline.auth.login.postgres", return_value=failing):
                    try:
                        login(LoginRequest.model_validate(
                            {"email": email, "password": password}))
                        raise AssertionError("Persistence failure accepted")
                    except PostgresOperationError:
                        pass
            finally:
                if failure == "flush":
                    event.remove(OrmSession, "before_flush", fail_session)
            assert snapshot(database, email) == before

        email, password = fixture(database)
        with database.session() as session:
            user = session.scalars(
                select(User).where(User.email == email)).one()
            user.password = "corrupt-synthetic-hash"
            session.commit()
        before = snapshot(database, email)
        try:
            login(LoginRequest.model_validate(
                {"email": email, "password": password}))
            raise AssertionError("Corrupt hash accepted")
        except CredentialError:
            pass
        assert snapshot(database, email) == before

        email, password = fixture(database, outdated=True)
        barrier = Barrier(2, timeout=15)

        def run(_: int):
            barrier.wait()
            return login(LoginRequest.model_validate({"email": email, "password": password}))

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(run, (0, 1)))
        final = snapshot(database, email)
        assert len(final[2]) == 2
        assert len({row[1] for row in final[2]}) == 2
        assert {row[1] for row in final[2]} == {
            digest(item.credentials.refresh) for item in results}
        assert Password().verify(final[0][1], password)
        assert not Password().needs_rehash(final[0][1])
        assert all(Access().decode(item.credentials.access).user ==
                   final[0][0] for item in results)

    return {"login": "passed", "unverified_unchanged": "passed", "rehash": "passed",
            "rollback": "passed", "concurrent_logins": 2, "independent_sessions": 2}


def main() -> None:
    """Inspect configured data read-only and drop only the UUID-named test database."""
    source = create_engine(url(constants.postgres), hide_parameters=True,
                           connect_args={"connect_timeout": 3})
    admin = create_engine(url(constants.postgres).set(database="postgres"),
                          isolation_level="AUTOCOMMIT", hide_parameters=True,
                          connect_args={"connect_timeout": 3})
    name = "atlas_login_" + uuid4().hex
    disposable = None
    created = False
    try:
        schema(source)
        baseline = counts(Database(source, sessionmaker(bind=source)))
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
        assert counts(Database(source, sessionmaker(bind=source))) == baseline
        print(json.dumps({**result, "head": "0001_identity",
              "configured_data": "preserved"}, sort_keys=True))
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
        print(json.dumps({"login_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
