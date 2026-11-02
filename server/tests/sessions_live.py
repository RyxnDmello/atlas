"""Opt-in rotation/logout PostgreSQL acceptance in a UUID-named disposable database."""
import sys
import json
import secrets
from uuid import uuid4
from threading import Barrier
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import Session as OrmSession, sessionmaker

from app.core.constants import constants
from app.db.postgres import Database, url

from app.pipeline.auth.access import Access
from app.pipeline.auth.logout import logout
from app.pipeline.auth.refresh import digest
from app.pipeline.auth.rotation import refresh

from app.models.postgres import Session, User

from app.errors.postgres import PostgresOperationError
from app.errors.auth import CredentialError, InvalidRefreshTokenError

from tests.registration_live import counts
from tests.login_live import fixture, snapshot
from tests.postgres_live import migrate, schema


def credential(database: Database, email: str, expires: datetime | None = None) -> str:
    """Seed a private opaque session only in the disposable acceptance database."""
    token = secrets.token_urlsafe(48)
    now = datetime.now(timezone.utc)
    with database.session() as session:
        user = session.scalars(select(User).where(User.email == email)).one()
        session.add(Session(user_id=user.id, token_hash=digest(token), created_at=now,
                            expires_at=expires if expires is not None else now + timedelta(days=7)))
        session.commit()
    return token


def invalid(token: str | None) -> None:
    try:
        refresh(token)
        raise AssertionError('Invalid refresh accepted')
    except InvalidRefreshTokenError as error:
        assert error.status == 401
        assert error.to_dict() == {
            'error': 'Invalid refresh token', 'code': 'INVALID_REFRESH_TOKEN'}


def acceptance(database: Database) -> dict[str, object]:
    """Prove real atomic consumption, committed cleanup, rollback and session isolation."""
    with patch('app.pipeline.auth.rotation.postgres', return_value=database), patch(
            'app.pipeline.auth.logout.postgres', return_value=database):
        email, _ = fixture(database, verification=True)
        other, _ = fixture(database)
        original = credential(database, email)
        independent = credential(database, email)
        foreign = credential(database, other)
        before = snapshot(database, email)
        untouched = snapshot(database, other)
        result = refresh(original)
        after = snapshot(database, email)
        assert after[:2] == before[:2]
        assert len(after[2]) == 2
        assert {row[1] for row in after[2]} == {
            digest(independent), digest(result.credentials.refresh)}
        replacement = next(row for row in after[2] if row[1] == digest(
            result.credentials.refresh))
        assert replacement[0] not in {row[0] for row in before[2]}
        assert replacement[2].tzinfo is not None
        assert (replacement[3] - replacement[2]).total_seconds(
        ) == constants.refresh.AUTH_REFRESH_TOKEN_TTL_SECONDS
        assert Access().decode(result.credentials.access).user == after[0][0]
        invalid(original)
        assert snapshot(database, email) == after
        assert snapshot(database, other) == untouched
        second = refresh(result.credentials.refresh)
        assert second.credentials.refresh != result.credentials.refresh
        invalid(result.credentials.refresh)

        boundary = datetime.now(timezone.utc)
        expired = credential(database, email, boundary)
        with patch('app.pipeline.auth.rotation.datetime') as clock:
            clock.now.return_value = boundary
            invalid(expired)
        assert digest(expired) not in {row[1]
                                       for row in snapshot(database, email)[2]}
        invalid(expired)
        for token in (None, '', '   ', secrets.token_urlsafe(48)):
            state = snapshot(database, email)
            invalid(token)
            assert snapshot(database, email) == state

        class FailingSession(OrmSession):
            def commit(self) -> None:
                self.flush()
                raise SQLAlchemyError('Synthetic commit failure')

        def fail_flush(session: OrmSession, context: object, instances: object) -> None:
            if any(isinstance(row, Session) for row in session.new):
                assert session.connection().execute(select(Session.id).where(
                    Session.token_hash == failed_hash)).first() is None
                raise SQLAlchemyError('Synthetic flush failure')

        for seam in ('flush', 'commit', 'issue'):
            token = credential(database, email)
            failed_hash = digest(token)
            state = snapshot(database, email)
            failing = Database(database.engine, sessionmaker(
                bind=database.engine, class_=FailingSession)) if seam == 'commit' else database
            if seam == 'flush':
                event.listen(OrmSession, 'before_flush', fail_flush)
            try:
                with patch('app.pipeline.auth.rotation.postgres', return_value=failing):
                    try:
                        if seam == 'issue':
                            with patch('app.pipeline.auth.rotation.issue', side_effect=CredentialError()):
                                refresh(token)
                        else:
                            refresh(token)
                        raise AssertionError('Injected failure accepted')
                    except (PostgresOperationError, CredentialError):
                        pass
            finally:
                if seam == 'flush':
                    event.remove(OrmSession, 'before_flush', fail_flush)
            assert snapshot(database, email) == state
            recovered = refresh(token)
            logout(recovered.credentials.refresh)

        unverified, _ = fixture(database, verified=False)
        token = credential(database, unverified)
        state = snapshot(database, unverified)
        try:
            refresh(token)
            raise AssertionError('Unverified owner accepted')
        except CredentialError:
            pass
        assert snapshot(database, unverified) == state

        concurrent, _ = fixture(database)
        token = credential(database, concurrent)
        gate = Barrier(2)

        def run(_: int):
            gate.wait(timeout=10)
            try:
                return refresh(token)
            except InvalidRefreshTokenError:
                return None

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(run, (0, 1)))
        winners = [outcome for outcome in outcomes if outcome is not None]
        assert len(winners) == 1 and outcomes.count(None) == 1
        state = snapshot(database, concurrent)
        assert len(state[2]) == 1 and state[2][0][1] == digest(
            winners[0].credentials.refresh)
        invalid(token)
        assert snapshot(database, concurrent) == state

        for token in (None, '', '   ', secrets.token_urlsafe(48), original, expired):
            state = snapshot(database, email)
            logout(token)
            assert snapshot(database, email) == state
        expired_logout = credential(database, email, boundary)
        logout(expired_logout)
        assert digest(expired_logout) not in {
            row[1] for row in snapshot(database, email)[2]}
        active = second.credentials.refresh
        state = snapshot(database, email)
        failing = Database(database.engine, sessionmaker(
            bind=database.engine, class_=FailingSession))
        with patch('app.pipeline.auth.logout.postgres', return_value=failing):
            try:
                logout(active)
                raise AssertionError('Failed logout accepted')
            except PostgresOperationError:
                pass
        assert snapshot(database, email) == state
        logout(active)
        invalid(active)
        assert {row[1] for row in snapshot(database, email)[2]} == {
            digest(independent)}
        assert snapshot(database, other) == untouched
        assert digest(foreign) == untouched[2][0][1]
        assert Access().decode(second.credentials.access).user == state[0][0]
        refreshed = refresh(independent)
        assert Access().decode(
            refreshed.credentials.access).user == state[0][0]
    return {'rotation': 'passed', 'expired_boundary_cleanup': 'passed', 'rollback': 'passed',
            'concurrent_winners': 1, 'concurrent_losers': 1, 'logout': 'passed',
            'session_isolation': 'passed', 'access_after_logout': 'valid_until_expiry'}


def main() -> None:
    """Inspect configured data read-only and always drop only the generated database."""
    source = create_engine(url(
        constants.postgres), hide_parameters=True, connect_args={'connect_timeout': 3})
    admin = create_engine(url(constants.postgres).set(database='postgres'),
                          isolation_level='AUTOCOMMIT', hide_parameters=True, connect_args={'connect_timeout': 3})
    name = 'atlas_sessions_' + uuid4().hex
    disposable = None
    created = False
    try:
        schema(source)
        baseline = counts(Database(source, sessionmaker(bind=source)))
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migrate(name, 'head')
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        disposable = Database(engine, sessionmaker(bind=engine))
        schema(engine)
        result = acceptance(disposable)
        schema(engine)
        schema(source)
        assert counts(Database(source, sessionmaker(bind=source))) == baseline
        print(json.dumps({**result, 'head': '0002_drive',
              'configured_data': 'preserved'}, sort_keys=True))
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


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'sessions_live': 'failed', 'category': type(error).__name__,
                          'diagnostics': 'suppressed to protect credentials'}), file=sys.stderr)
        sys.exit(1)
