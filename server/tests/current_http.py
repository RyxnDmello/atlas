"""Opt-in final live authentication flow; clean only the generated synthetic users."""
import sys
import json
import time
import secrets
import subprocess
from uuid import uuid4
from http.cookies import SimpleCookie

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, delete, select

from app.core.constants import constants
from app.db.postgres import Database, url

from app.schemas.constants import AuthConstants
from app.models.postgres import User, Verification

from app.pipeline.auth.access import Access

from tests.login_live import snapshot
from tests.login_http import authenticated
from tests.registration_http import request


def profile(token: str | None, expected=None, origin=None, scheme='Bearer'):
    """Assert the exact public profile/error without printing any credential."""
    headers = {} if token is None else {'Authorization': scheme+' '+token}
    if origin is not None:
        headers['Origin'] = origin
    status, body, metadata = request('/auth', headers=headers)
    assert status == (200 if expected is not None else 401)
    assert body == (expected if expected is not None else {
        'error': 'Invalid access token', 'code': 'INVALID_ACCESS_TOKEN'})
    assert 'set-cookie' not in metadata
    return metadata


def main() -> None:
    """Prove verify/login/current/refresh/logout, canonical guards, expiry and CORS."""
    engine = create_engine(url(constants.postgres), hide_parameters=True)
    database = Database(engine, sessionmaker(bind=engine))
    emails = ['current-http-'+uuid4().hex+'@example.com' for _ in range(2)]
    password = secrets.token_urlsafe(24)
    private = [password]
    try:
        for email in emails:
            status, _, _ = request('/auth/register', {
                'name': 'Synthetic Current', 'email': email, 'password': password}, 'POST')
            assert status == 201
        with database.session() as session:
            user = session.scalars(select(User).where(
                User.email == emails[0])).one()
            identity = user.id
            expected = {'id': str(identity),
                        'name': user.name, 'email': user.email}
            otp = session.scalars(select(Verification).where(
                Verification.user_id == identity, Verification.type == 'auth')).one().otp
            unverified = session.scalars(
                select(User).where(User.email == emails[1])).one().id
            private.extend([otp, user.password])
        status, verified, metadata = request(
            '/auth/verify', {'email': emails[0], 'otp': otp}, 'POST')
        assert status == 200
        authenticated(database, emails[0], verified, metadata, 1, private)
        profile(verified['access_token'], expected)
        status, logged, metadata = request(
            '/auth/login', {'email': emails[0], 'password': password}, 'POST')
        assert status == 200
        authenticated(database, emails[0], logged, metadata, 2, private)
        profile(logged['access_token'], expected, scheme='bEaReR')
        refresh = SimpleCookie(metadata['set-cookie'])['atlas_refresh'].value
        status, rotated, metadata = request(
            '/auth/refresh', method='POST', headers={'Cookie': 'atlas_refresh='+refresh})
        assert status == 200
        authenticated(database, emails[0], rotated, metadata, 2, private)
        profile(rotated['access_token'], expected)
        profile(logged['access_token'], expected)
        status, body, rejected = request(
            '/auth/refresh', method='POST', headers={'Cookie': 'atlas_refresh='+refresh})
        assert status == 401 and body['code'] == 'INVALID_REFRESH_TOKEN' and 'set-cookie' not in rejected
        fresh = SimpleCookie(metadata['set-cookie'])['atlas_refresh'].value
        status, body, cleared = request(
            '/auth/logout', method='POST', headers={'Cookie': 'atlas_refresh='+fresh})
        assert status == 204 and body is None
        assert SimpleCookie(cleared['set-cookie']
                            )['atlas_refresh']['max-age'] == '0'
        assert len(snapshot(database, emails[0])[2]) == 1
        profile(rotated['access_token'], expected)
        profile(logged['access_token'], expected)
        profile(verified['access_token'], expected)
        short = Access(AuthConstants.model_validate({
            'AUTH_ACCESS_TOKEN_SECRET': constants.auth.AUTH_ACCESS_TOKEN_SECRET,
            'AUTH_ACCESS_TOKEN_TTL_SECONDS': 3})).issue(identity)
        private.append(short)
        profile(short, expected)
        time.sleep(3.1)
        profile(short)
        for token, scheme in ((None, 'Bearer'), ('', 'Bearer'), ('   ', 'Bearer'),
                              ('malformed',
                               'Bearer'), (logged['access_token'], 'Basic'),
                              (Access().issue(uuid4()), 'Bearer'), (Access().issue(unverified), 'Bearer')):
            if token and token.strip():
                private.append(token)
            profile(token, scheme=scheme)
        denied = 'https://denied-'+uuid4().hex+'.example'
        for origin in [*constants.cors.CORS_ORIGINS, denied]:
            allowed = origin in constants.cors.CORS_ORIGINS
            for method, header in (('GET', 'Authorization'), ('POST', 'Content-Type')):
                status, _, headers = request('/auth', method='OPTIONS', headers={
                    'Origin': origin, 'Access-Control-Request-Method': method,
                    'Access-Control-Request-Headers': header})
                assert status == (200 if allowed else 400)
                assert headers.get(
                    'access-control-allow-origin') == (origin if allowed else None)
                assert headers.get(
                    'access-control-allow-credentials') == 'true'
            for token, value in ((logged['access_token'], expected), (None, None)):
                headers = profile(token, value, origin)
                assert headers.get(
                    'access-control-allow-origin') == (origin if allowed else None)
                assert headers.get(
                    'access-control-allow-credentials') == 'true'
        with database.session() as session:
            session.delete(session.get(User, identity))
            session.commit()
        profile(logged['access_token'])
        status, spec, _ = request('/openapi.json')
        assert status == 200
        routes = {path: set(value) for path, value in spec['paths'].items(
        ) if path.startswith('/auth')}
        assert routes == {'/auth': {'get'}, **{'/auth/'+name: {'post'} for name in (
            'register', 'verify', 'resend', 'login', 'refresh', 'logout')}}
        logs = subprocess.run(['docker', 'compose', '--env-file', '.env', '-f', 'docker-compose.yml',
                               'logs', '--no-color', 'server'], capture_output=True, text=True, check=True)
        assert all(value not in logs.stdout+logs.stderr for value in private)
        print(json.dumps({'current_http': 'passed', 'full_auth_flow': 'passed',
                          'stateless_access_expiry': 'passed', 'canonical_guards': 'passed',
                          'cors': 'passed', 'route_inventory': 7, 'private_log_scan': 'passed'}))
    finally:
        try:
            with database.session() as session:
                session.execute(delete(User).where(User.email.in_(emails)))
                session.commit()
                assert not session.scalars(
                    select(User).where(User.email.in_(emails))).all()
        finally:
            database.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'current_http': 'failed', 'category': type(error).__name__,
                          'diagnostics': 'suppressed to protect credentials'}), file=sys.stderr)
        sys.exit(1)
