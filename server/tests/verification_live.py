"""Opt-in Amendment 04 acceptance in a migrated disposable PostgreSQL database."""

import sys
import json
from uuid import uuid4
from threading import Barrier
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as OrmSession, sessionmaker
from sqlalchemy import create_engine, event, func, select, text

from app.core.constants import constants
from app.db.postgres import Database, url

from app.pipeline.auth.access import Access
from app.pipeline.auth.refresh import digest
from app.pipeline.auth.verify import resend, verify

from app.models.postgres import User, Verification, Session
from app.schemas.auth.verification import ResendRequest, VerifyRequest

from app.errors.postgres import PostgresOperationError

from app.errors.auth import (
    AccountNotFoundError, InvalidVerificationError,
    VerificationExpiredError, VerificationNotRequiredError,
)

from tests.registration_live import counts
from tests.postgres_live import migrate, schema


def fixture(database: Database, *, expired: bool = False) -> tuple[str, str]:
    """Create one synthetic unverified account and private development OTP."""
    now = datetime.now(timezone.utc)
    email = uuid4().hex + "@example.com"
    otp = "012345"
    with database.session() as session:
        user = User(name="Synthetic", email=email, password="synthetic",
                    verified_at=None, created_at=now, updated_at=now)
        session.add(user)
        session.flush()
        session.add(Verification(
            user_id=user.id, type="auth", otp=otp, created_at=now,
            expires_at=now + timedelta(seconds=-1 if expired else 600),
        ))
        session.commit()
    return email, otp


def totals(database: Database, email: str) -> tuple[bool, int, int]:
    """Check one account's final state without returning credential material."""
    with database.session() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        verifications = session.execute(select(func.count()).select_from(Verification).where(
            Verification.user_id == user.id, Verification.type == "auth")).scalar_one()
        sessions = session.execute(select(func.count()).select_from(Session).where(
            Session.user_id == user.id)).scalar_one()
        return user.verified_at is not None, int(verifications), int(sessions)


def race(database: Database, first: str, second: str) -> tuple[list[str], tuple[bool, int, int]]:
    """Start independent PostgreSQL transactions against the same user."""
    email, otp = fixture(database)
    barrier = Barrier(2, timeout=15)

    def run(action: str) -> str:
        barrier.wait()
        try:
            if action == "verify":
                verify(VerifyRequest(email=email, otp=otp))
            else:
                resend(ResendRequest(email=email))
            return "success"
        except (InvalidVerificationError, VerificationNotRequiredError) as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = sorted(pool.map(run, (first, second)))
    final = totals(database, email)
    if (first, second) == ("verify", "verify"):
        assert outcomes == ["VERIFICATION_NOT_REQUIRED", "success"]
        assert final == (True, 0, 1)
    elif (first, second) == ("verify", "resend"):
        assert final in ((True, 0, 1), (False, 1, 0))
        assert final != (False, 1, 0) or "INVALID_VERIFICATION" in outcomes
    else:
        assert outcomes == ["success", "success"]
        assert final == (False, 1, 0)
    return outcomes, final


def acceptance(database: Database) -> dict[str, object]:
    """Prove lifecycle, rollback, and lock ordering with real PostgreSQL."""
    with patch("app.pipeline.auth.verify.postgres", return_value=database):
        email, otp = fixture(database)
        with database.session() as session:
            user = session.scalar(select(User).where(User.email == email))
            assert user is not None
            old = session.scalar(select(Verification).where(
                Verification.user_id == user.id))
            assert old is not None
            original = old.otp
        resend(ResendRequest(email=email))
        assert totals(database, email) == (False, 1, 0)
        try:
            verify(VerifyRequest(email=email, otp=original))
            raise AssertionError("Old OTP remained valid")
        except InvalidVerificationError:
            pass
        with database.session() as session:
            user = session.scalar(select(User).where(User.email == email))
            assert user is not None
            row = session.scalar(select(Verification).where(
                Verification.user_id == user.id))
            assert row is not None and row.otp != original
            current = row.otp
        result = verify(VerifyRequest(email=email, otp=current))
        assert Access().decode(result.credentials.access).user == result.user.id
        assert totals(database, email) == (True, 0, 1)
        with database.session() as session:
            stored = session.scalar(select(Session).where(
                Session.user_id == result.user.id))
            assert stored is not None
            assert stored.token_hash == digest(result.credentials.refresh)
            assert stored.token_hash != result.credentials.refresh
            assert stored.expires_at - stored.created_at == timedelta(
                seconds=constants.refresh.AUTH_REFRESH_TOKEN_TTL_SECONDS)

        expired, value = fixture(database, expired=True)
        try:
            verify(VerifyRequest(email=expired, otp=value))
            raise AssertionError("Expired OTP accepted")
        except VerificationExpiredError:
            pass
        assert totals(database, expired) == (False, 0, 0)
        try:
            verify(VerifyRequest(email=expired, otp=value))
            raise AssertionError("Deleted OTP remained valid")
        except InvalidVerificationError:
            pass

        absent = uuid4().hex + "@example.com"
        for action in (
            lambda: verify(VerifyRequest(email=absent, otp="012345")),
            lambda: resend(ResendRequest(email=absent)),
        ):
            try:
                action()
                raise AssertionError("Unknown account accepted")
            except AccountNotFoundError:
                pass
        for action in (
            lambda: verify(VerifyRequest(email=email, otp=current)),
            lambda: resend(ResendRequest(email=email)),
        ):
            try:
                action()
                raise AssertionError("Verified account accepted")
            except VerificationNotRequiredError:
                pass

        failed, valid = fixture(database)

        class FailingSession(OrmSession):
            def commit(self) -> None:
                raise SQLAlchemyError("Synthetic commit failure")

        failing = Database(database.engine, sessionmaker(
            bind=database.engine, class_=FailingSession))
        with patch("app.pipeline.auth.verify.postgres", return_value=failing):
            try:
                verify(VerifyRequest(email=failed, otp=valid))
                raise AssertionError("Commit failure accepted")
            except PostgresOperationError:
                pass
        assert totals(database, failed) == (False, 1, 0)

        flush_failed, flush_otp = fixture(database)

        def fail_session(session: OrmSession, context: object, instances: object) -> None:
            if any(isinstance(row, Session) for row in session.new):
                raise SQLAlchemyError("Synthetic session insertion failure")

        event.listen(OrmSession, "before_flush", fail_session)
        try:
            with patch("app.pipeline.auth.verify.postgres", return_value=database):
                try:
                    verify(VerifyRequest(email=flush_failed, otp=flush_otp))
                    raise AssertionError("Session insertion failure accepted")
                except PostgresOperationError:
                    pass
        finally:
            event.remove(OrmSession, "before_flush", fail_session)
        assert totals(database, flush_failed) == (False, 1, 0)

        verify_race = race(database, "verify", "verify")
        mixed_race = race(database, "verify", "resend")
        resend_race = race(database, "resend", "resend")

    return {"lifecycle": "passed", "rollback": "passed", "expired_cleanup": "passed",
            "verify_race": verify_race[0], "mixed_race": mixed_race[0],
            "resend_race": resend_race[0]}


def main() -> None:
    """Preserve configured data and remove only this helper's disposable database."""
    source = create_engine(url(constants.postgres), hide_parameters=True,
                           connect_args={"connect_timeout": 3})
    admin = create_engine(url(constants.postgres).set(database="postgres"),
                          isolation_level="AUTOCOMMIT", hide_parameters=True,
                          connect_args={"connect_timeout": 3})
    name = "atlas_verification_" + uuid4().hex
    disposable = None
    created = False
    try:
        schema(source)
        baseline = counts(Database(source, sessionmaker(bind=source)))
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migrate(name, "head")
        engine = create_engine(url(constants.postgres).set(database=name),
                               hide_parameters=True)
        disposable = Database(engine, sessionmaker(bind=engine))
        schema(engine)
        result = acceptance(disposable)
        schema(engine)
        schema(source)
        assert counts(Database(source, sessionmaker(bind=source))) == baseline
        print(json.dumps({**result, "head": "0002_drive",
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
        print(json.dumps({"verification_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
