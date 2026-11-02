"""Opt-in canonical current-user acceptance in a migrated disposable database."""
import sys
import json
from uuid import uuid4
from hashlib import sha256
from unittest.mock import patch
from fastapi.testclient import TestClient

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, select, text, event

from app.core.constants import constants

from app.pipeline.auth.access import Access
from app.pipeline.auth.current import current

from app.db.postgres import Database, url
from app.models.postgres import User, Verification, Session

from app.errors.auth import InvalidAccessTokenError
from app.errors.postgres import PostgresOperationError

from tests.test_19_current import bearer
from tests.registration_live import counts
from tests.login_live import fixture, snapshot
from tests.postgres_live import migrate, schema
from tests.test_15_registration import application


def fingerprint(database: Database) -> str:
    """Compare all canonical rows privately so unchanged counts cannot hide changed values."""
    digest = sha256()
    with database.engine.connect() as connection:
        for model in (User, Verification, Session):
            rows = connection.execute(
                select(model.__table__).order_by(model.id)).all()
            digest.update(repr(rows).encode())
    return digest.hexdigest()


def acceptance(database: Database) -> dict[str, object]:
    """Prove canonical profiles, read-only authentication and safe operational failure."""
    email, _ = fixture(database, verification=True)
    unverified, _ = fixture(database, verified=False)
    with database.session() as session:
        user = session.scalars(select(User).where(User.email == email)).one()
        identity = user.id
        other = session.scalars(select(User).where(
            User.email == unverified)).one().id
    token = Access().issue(identity)
    baseline = snapshot(database, email)
    statements = []

    def capture(connection, cursor, statement, parameters, context, many):
        statements.append(statement)

    with patch('app.pipeline.auth.current.postgres', return_value=database):
        event.listen(database.engine, 'before_cursor_execute', capture)
        try:
            resolved = current(bearer('Bearer '+token))
            assert resolved.id == identity and resolved.email == email
        finally:
            event.remove(database.engine, 'before_cursor_execute', capture)
        assert len(statements) == 1
        assert statements[0].lstrip().upper().startswith('SELECT')
        assert 'sessions' not in statements[0] and 'verifications' not in statements[0]
        assert snapshot(database, email) == baseline
        with database.session() as session:
            user = session.get(User, identity)
            assert user is not None
            user.name = 'Updated Canonical'
            user.email = uuid4().hex+'@example.com'
            updated = user.email
            session.commit()
        with TestClient(application()) as client:
            response = client.get('/auth?name=Untrusted&user_id='+str(other),
                                  headers={'Authorization': 'Bearer '+token})
        assert response.status_code == 200
        assert response.json() == {'id': str(
            identity), 'name': 'Updated Canonical', 'email': updated}
        assert 'set-cookie' not in response.headers
        with patch.object(database, 'session', side_effect=SQLAlchemyError('private diagnostic')):
            try:
                current(bearer('Bearer '+token))
                raise AssertionError('Database failure accepted')
            except PostgresOperationError as error:
                assert error.status == 500 and 'private diagnostic' not in str(
                    error.to_dict())
        with database.session() as session:
            session.delete(session.get(User, identity))
            session.commit()
        for value in (token, Access().issue(other)):
            try:
                current(bearer('Bearer '+value))
                raise AssertionError('Missing/unverified user accepted')
            except InvalidAccessTokenError as error:
                assert error.status == 401
    return {'current_user': 'passed', 'canonical_profile': 'passed', 'read_only_lookup': 'passed',
            'deleted_unverified': 'passed', 'database_failure': 'sanitized'}


def main() -> None:
    """Inspect configured data read-only and always drop only the generated database."""
    source = create_engine(url(
        constants.postgres), hide_parameters=True, connect_args={'connect_timeout': 3})
    admin = create_engine(url(constants.postgres).set(database='postgres'),
                          isolation_level='AUTOCOMMIT', hide_parameters=True, connect_args={'connect_timeout': 3})
    name = 'atlas_current_' + uuid4().hex
    disposable = None
    created = False
    try:
        schema(source)
        configured = Database(source, sessionmaker(bind=source))
        baseline = counts(configured), fingerprint(configured)
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
        assert (counts(configured), fingerprint(configured)) == baseline
        print(json.dumps({**result, 'head': '0001_identity',
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
        print(json.dumps({'current_live': 'failed', 'category': type(error).__name__,
                          'diagnostics': 'suppressed to protect credentials'}), file=sys.stderr)
        sys.exit(1)
