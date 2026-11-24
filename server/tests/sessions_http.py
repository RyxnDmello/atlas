"""Opt-in live HTTP rotation/logout/CORS acceptance; clean only generated users."""
import sys
import json
import secrets
import subprocess
from uuid import uuid4
from pathlib import Path
from threading import Barrier
from http.cookies import SimpleCookie
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, delete, select

from app.core.constants import constants
from app.db.postgres import Database, url

from app.models.postgres import User, Verification, Session

from app.pipeline.auth.access import Access
from app.pipeline.auth.refresh import digest

from tests.login_live import snapshot
from tests.login_http import authenticated
from tests.registration_http import request


def invalid(token: str | None, origin: str | None = None) -> dict[str, str]:
    headers = {} if token is None else {'Cookie': 'atlas_refresh=' + token}
    if origin is not None:
        headers['Origin'] = origin
    status, body, metadata = request(
        '/auth/refresh', method='POST', headers=headers)
    assert status == 401 and body == {
        'error': 'Invalid refresh token', 'code': 'INVALID_REFRESH_TOKEN'}
    assert 'set-cookie' not in metadata
    return metadata


def cleared(token: str | None) -> None:
    status, body, headers = request('/auth/logout', method='POST', headers=(
        {} if token is None else {'Cookie': 'atlas_refresh=' + token}))
    assert status == 204 and body is None
    cookie = SimpleCookie(headers['set-cookie'])['atlas_refresh']
    assert cookie.value == '' and cookie['max-age'] == '0'
    assert parsedate_to_datetime(
        cookie['expires']) <= datetime.now(timezone.utc)
    assert cookie['path'] == '/auth' and cookie['httponly'] and cookie['samesite'] == 'lax'
    assert bool(cookie['secure']) == constants.refresh.AUTH_COOKIE_SECURE


def main() -> None:
    """Prove rotation, replay, concurrent loser cookie safety, isolation, logout and CORS."""
    engine = create_engine(url(constants.postgres), hide_parameters=True)
    database = Database(engine, sessionmaker(bind=engine))
    emails = ['sessions-http-' +
              uuid4().hex + '@example.com' for _ in range(2)]
    password = secrets.token_urlsafe(24)
    private = [password]
    try:
        issued = []
        for email in emails:
            status, _, _ = request(
                '/auth/register', {'name': 'Synthetic', 'email': email, 'password': password}, 'POST')
            assert status == 201
            with database.session() as session:
                user = session.scalars(
                    select(User).where(User.email == email)).one()
                otp = session.scalars(select(Verification).where(Verification.user_id == user.id,
                                      Verification.type == 'auth')).one().otp
                private.extend([otp, user.password])
            status, body, headers = request(
                '/auth/verify', {'email': email, 'otp': otp}, 'POST')
            assert status == 200
            authenticated(database, email, body, headers, 1, private)
            issued.append(
                (body, SimpleCookie(headers['set-cookie'])['atlas_refresh'].value))
        email = emails[0]
        first, token = issued[0]
        foreign = snapshot(database, emails[1])
        status, body, headers = request(
            '/auth/login', {'email': email, 'password': password}, 'POST')
        assert status == 200
        authenticated(database, email, body, headers, 2, private)
        independent = SimpleCookie(
            headers['set-cookie'])['atlas_refresh'].value
        baseline = snapshot(database, email)

        def rotate(old: str):
            status, body, headers = request(
                '/auth/refresh', method='POST', headers={'Cookie': 'atlas_refresh=' + old})
            assert status == 200
            authenticated(database, email, body, headers, 2, private)
            fresh = SimpleCookie(headers['set-cookie'])['atlas_refresh'].value
            assert fresh != old
            assert digest(old) not in {row[1]
                                       for row in snapshot(database, email)[2]}
            return body, fresh

        second, token_b = rotate(token)
        invalid(token)
        third, token_c = rotate(token_b)
        invalid(token_b)
        assert snapshot(database, email)[:2] == baseline[:2]
        assert snapshot(database, emails[1]) == foreign
        cleared(token_c)
        invalid(token_c)
        assert {row[1] for row in snapshot(database, email)[2]} == {
            digest(independent)}
        for body in (first, second, third):
            assert Access().decode(body['access_token']).user == baseline[0][0]

        for token_value in (None, '', '   ', secrets.token_urlsafe(48), token, token_b, token_c):
            state = snapshot(database, email)
            invalid(token_value)
            cleared(token_value)
            assert snapshot(database, email) == state

        def expired() -> str:
            raw = secrets.token_urlsafe(48)
            now = datetime.now(timezone.utc)
            with database.session() as session:
                session.add(Session(user_id=baseline[0][0], token_hash=digest(raw),
                                    created_at=now - timedelta(days=8), expires_at=now - timedelta(seconds=1)))
                session.commit()
            private.extend([raw, digest(raw)])
            return raw

        expired_refresh = expired()
        invalid(expired_refresh)
        invalid(expired_refresh)
        expired_logout = expired()
        cleared(expired_logout)
        assert {row[1] for row in snapshot(database, email)[2]} == {
            digest(independent)}

        gate = Barrier(2)

        def run(_: int):
            gate.wait(timeout=10)
            return request('/auth/refresh', method='POST', headers={'Cookie': 'atlas_refresh=' + independent})

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(run, (0, 1)))
        assert sorted(item[0] for item in results) == [200, 401]
        winner = next(item for item in results if item[0] == 200)
        loser = next(item for item in results if item[0] == 401)
        assert loser[1] == {'error': 'Invalid refresh token',
                            'code': 'INVALID_REFRESH_TOKEN'}
        assert 'set-cookie' not in loser[2]
        authenticated(database, email, winner[1], winner[2], 1, private)
        winning = SimpleCookie(winner[2]['set-cookie'])['atlas_refresh'].value
        state = snapshot(database, email)
        invalid(independent)
        assert snapshot(database, email) == state

        denied = 'https://denied-' + uuid4().hex + '.example'
        for origin in [*constants.cors.CORS_ORIGINS, denied]:
            allowed = origin in constants.cors.CORS_ORIGINS
            for path in ('/auth/refresh', '/auth/logout'):
                status, _, metadata = request(path, method='OPTIONS', headers={'Origin': origin,
                                                                               'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'Content-Type'})
                assert status == (200 if allowed else 400)
                assert metadata.get(
                    'access-control-allow-origin') == (origin if allowed else None)
                assert metadata.get(
                    'access-control-allow-credentials') == 'true'
            metadata = invalid(None, origin)
            assert metadata.get(
                'access-control-allow-origin') == (origin if allowed else None)
            assert metadata.get('access-control-allow-credentials') == 'true'
            status, body, metadata = request('/auth/refresh', method='POST', headers={'Origin': origin,
                                                                                      'Cookie': 'atlas_refresh=' + winning})
            assert status == 200
            authenticated(database, email, body, metadata, 1, private)
            winning = SimpleCookie(
                metadata['set-cookie'])['atlas_refresh'].value
            assert metadata.get(
                'access-control-allow-origin') == (origin if allowed else None)
            assert metadata.get('access-control-allow-credentials') == 'true'
            for method, header in (('PUT', 'Content-Type'), ('POST', 'X-Unapproved')):
                status, _, _ = request('/auth/refresh', method='OPTIONS', headers={'Origin': origin,
                                                                                   'Access-Control-Request-Method': method, 'Access-Control-Request-Headers': header})
                assert status == 400
        cleared(winning)
        assert snapshot(database, email)[2] == []
        assert snapshot(database, emails[1]) == foreign
        assert Access().decode(
            winner[1]['access_token']).user == baseline[0][0]
        status, spec, _ = request('/openapi.json')
        assert status == 200
        paths = {path for path in spec['paths'] if path.startswith('/auth')}
        assert paths - {'/auth'} == {
            '/auth/' + name for name in ('register', 'verify', 'resend', 'login', 'refresh', 'logout')}
        assert set(spec['paths']['/auth']) == {'get'}
        assert all(set(spec['paths'][path]) == {
                   'post'} for path in paths - {'/auth'})
        logs = subprocess.run(['docker', 'compose', '--env-file', str(Path(__file__).resolve().parents[1] / '.env'),
                               '-f', str(Path(__file__).resolve()
                                         .parents[2] / 'compose.yml'),
                               'logs', '--no-color', 'server'], capture_output=True, text=True, check=True)
        assert all(value not in logs.stdout + logs.stderr for value in private)
        print(json.dumps({'sessions_http': 'passed', 'rotation_replay': 'passed', 'concurrency': 'one_winner_one_loser',
                          'loser_cookie': 'untouched', 'logout': 'passed', 'cors': 'passed',
                          'session_isolation': 'passed', 'private_log_scan': 'passed'}))
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
        print(json.dumps({'sessions_http': 'failed', 'category': type(error).__name__,
                          'diagnostics': 'suppressed to protect credentials'}), file=sys.stderr)
        sys.exit(1)
