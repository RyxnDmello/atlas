import os
import inspect
import secrets
import unittest
from uuid import uuid4
from unittest.mock import patch
from types import SimpleNamespace
from http.cookies import SimpleCookie
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

from app.core.cors import configure_cors
from app.core.constants import constants

from app.pipeline.auth.access import Access
from app.pipeline.auth.logout import logout
from app.pipeline.auth.refresh import digest
from app.pipeline.auth.rotation import refresh

from app.models.postgres import Session, User
from app.schemas.constants import CorsConstants

from app.errors.auth import CredentialError, InvalidRefreshTokenError

from tests.test_17_login import FakeDatabase
from tests.test_15_registration import application


class SessionTests(unittest.TestCase):
    """Deterministic orchestration/HTTP contracts; real transactions are opt-in."""

    def setUp(self):
        scope = patch.dict(os.environ, {
            'AUTH_ACCESS_TOKEN_SECRET': secrets.token_urlsafe(48),
            'AUTH_COOKIE_SECURE': 'false', 'AUTH_REFRESH_TOKEN_TTL_SECONDS': '73',
            'CORS_ORIGINS': 'https://atlas.example',
        })
        scope.start()
        self.addCleanup(scope.stop)
        self.token = secrets.token_urlsafe(48)
        self.now = datetime.now(timezone.utc)
        self.user = User(id=uuid4(), name='Canonical', email='canonical@example.com',
                         verified_at=self.now)
        self.database = FakeDatabase(self.user)
        self.session = self.database.session_value
        self.session.execute.return_value.one_or_none.return_value = SimpleNamespace(
            id=uuid4(), user_id=self.user.id)
        self.session.get.return_value = self.user
        for module in ('rotation', 'logout'):
            scope = patch('app.pipeline.auth.' + module +
                          '.postgres', return_value=self.database)
            scope.start()
            self.addCleanup(scope.stop)

    def post(self, path, token=None, **kwargs):
        headers = kwargs.pop('headers', {})
        if token is not None:
            headers['Cookie'] = 'atlas_refresh=' + token
        with TestClient(application()) as client:
            return client.post('/auth/' + path, headers=headers, **kwargs)

    def absent(self, expired=None):
        self.session.execute.return_value.one_or_none.return_value = None
        self.session.execute.return_value.scalar_one_or_none.return_value = expired

    def test_missing_and_blank_refresh_reject_without_database(self):
        with patch('app.pipeline.auth.rotation.postgres') as database:
            for token in (None, '', '   '):
                with self.assertRaises(InvalidRefreshTokenError):
                    refresh(token)
        database.assert_not_called()

    def test_atomic_consume_uses_literal_hash_and_one_aware_time(self):
        token = ' ' + self.token + ' '
        result = refresh(token)
        statement = self.session.execute.call_args.args[0]
        compiled = statement.compile(dialect=postgresql.dialect())
        self.assertIn('DELETE FROM sessions', str(compiled))
        self.assertIn('sessions.expires_at >', str(compiled))
        self.assertIn('RETURNING sessions.id, sessions.user_id', str(compiled))
        self.assertIn(digest(token), compiled.params.values())
        row = self.session.add.call_args.args[0]
        self.assertIsInstance(row, Session)
        self.assertEqual(row.token_hash, digest(result.credentials.refresh))
        self.assertNotEqual(row.token_hash, result.credentials.refresh)
        self.assertIn(row.created_at, compiled.params.values())
        self.assertIsNotNone(row.created_at.tzinfo)
        self.assertEqual((row.expires_at - row.created_at).total_seconds(), 73)
        self.assertEqual(Access().decode(
            result.credentials.access).user, self.user.id)
        self.session.commit.assert_called_once()
        self.session.get.assert_called_once_with(User, self.user.id)

    def test_expired_cleanup_uses_same_time_and_commits_before_rejection(self):
        self.absent(uuid4())
        with self.assertRaises(InvalidRefreshTokenError):
            refresh(self.token)
        first, second = [call.args[0].compile(dialect=postgresql.dialect())
                         for call in self.session.execute.call_args_list]
        self.assertIn('sessions.expires_at <=', str(second))
        self.assertEqual(first.params, second.params)
        self.session.commit.assert_called_once()
        self.session.add.assert_not_called()

    def test_unknown_or_replayed_has_no_commit_or_user_lookup(self):
        self.absent()
        response = self.post('refresh', self.token)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
                         'error': 'Invalid refresh token', 'code': 'INVALID_REFRESH_TOKEN'})
        self.assertNotIn('set-cookie', response.headers)
        self.session.commit.assert_not_called()
        self.session.get.assert_not_called()
        self.session.add.assert_not_called()

    def test_http_missing_cookie_ignores_body_and_authorization(self):
        with patch('app.pipeline.auth.rotation.postgres') as database:
            response = self.post('refresh', json={'refresh_token': self.token},
                                 headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(response.status_code, 401)
        self.assertNotIn('set-cookie', response.headers)
        database.assert_not_called()

    def test_success_shared_response_and_cookie_both_security_modes(self):
        for secure in ('true', 'false'):
            with patch.dict(os.environ, {'AUTH_COOKIE_SECURE': secure}):
                response = self.post('refresh', self.token,
                                     content='invalid-json')
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(set(body), {'access_token', 'user'})
            self.assertEqual(body['user'], {'id': str(
                self.user.id), 'name': self.user.name, 'email': self.user.email})
            cookie = SimpleCookie(
                response.headers['set-cookie'])['atlas_refresh']
            self.assertEqual(cookie['path'], '/auth')
            self.assertEqual(cookie['max-age'], '73')
            self.assertTrue(cookie['httponly'])
            self.assertEqual(cookie['samesite'], 'lax')
            self.assertEqual(bool(cookie['secure']), secure == 'true')
            self.assertNotIn(cookie.value, response.text)

    def test_inconsistent_user_rolls_back_and_never_issues(self):
        for user in (None, User(id=uuid4(), verified_at=None)):
            self.session.get.return_value = user
            with patch('app.pipeline.auth.rotation.issue') as issue:
                response = self.post('refresh', self.token)
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json()['code'], 'INTERNAL_SERVER_ERROR')
            self.assertNotIn('set-cookie', response.headers)
            issue.assert_not_called()
        self.session.commit.assert_not_called()
        self.assertEqual(self.session.rollback.call_count, 2)

    def test_issuance_and_database_failures_are_safe_without_cookies(self):
        for seam in ('execute', 'add', 'commit', 'issue'):
            target = ('app.pipeline.auth.rotation.issue' if seam ==
                      'issue' else None)
            scope = patch(target, side_effect=CredentialError()) if target else patch.object(
                self.session, seam, side_effect=SQLAlchemyError('private diagnostic'))
            with scope:
                response = self.post('refresh', self.token)
            self.assertEqual(response.status_code, 500)
            self.assertNotIn('set-cookie', response.headers)
            self.assertNotIn('private diagnostic', response.text)
            self.assertEqual(response.json()[
                             'code'], 'INTERNAL_SERVER_ERROR' if seam == 'issue' else 'POSTGRES_OPERATION_FAILED')
        self.assertEqual(self.session.rollback.call_count, 4)

    def test_expired_cleanup_commit_failure_is_operational(self):
        self.absent(uuid4())
        self.session.commit.side_effect = SQLAlchemyError('private diagnostic')
        response = self.post('refresh', self.token)
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('set-cookie', response.headers)
        self.session.rollback.assert_called_once()

    def test_logout_missing_blank_avoids_database_and_ignores_body(self):
        with patch('app.pipeline.auth.logout.postgres') as database:
            for token in (None, '', '   '):
                logout(token)
            response = self.post('logout', json={'refresh_token': self.token},
                                 headers={'Authorization': 'Bearer ' + self.token})
        database.assert_not_called()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')

    def test_logout_exact_delete_without_expiry_or_other_session_scope(self):
        for removed in (uuid4(), None):
            self.session.reset_mock()
            self.session.execute.return_value.scalar_one_or_none.return_value = removed
            logout(self.token)
            compiled = self.session.execute.call_args.args[0].compile(
                dialect=postgresql.dialect())
            self.assertEqual(list(compiled.params.values()),
                             [digest(self.token)])
            self.assertNotIn('expires_at', str(compiled))
            self.assertNotIn('user_id', str(compiled))
            self.assertEqual(self.session.commit.call_count,
                             int(removed is not None))

    def test_logout_clears_matching_cookie_in_both_security_modes(self):
        for secure in ('true', 'false'):
            with patch.dict(os.environ, {'AUTH_COOKIE_SECURE': secure}):
                response = self.post('logout', self.token)
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.content, b'')
            cookie = SimpleCookie(
                response.headers['set-cookie'])['atlas_refresh']
            self.assertEqual(cookie.value, '')
            self.assertEqual(cookie['max-age'], '0')
            self.assertTrue(cookie['expires'])
            self.assertEqual(cookie['path'], '/auth')
            self.assertTrue(cookie['httponly'])
            self.assertEqual(cookie['samesite'], 'lax')
            self.assertEqual(bool(cookie['secure']), secure == 'true')

    def test_logout_database_failure_is_not_success_or_cookie_clear(self):
        for seam in ('execute', 'commit'):
            with patch.object(self.session, seam, side_effect=SQLAlchemyError('private diagnostic')):
                response = self.post('logout', self.token)
            self.assertEqual(response.status_code, 500)
            self.assertEqual(
                response.json()['code'], 'POSTGRES_OPERATION_FAILED')
            self.assertNotIn('set-cookie', response.headers)
            self.assertNotIn('private diagnostic', response.text)

    def test_credentialed_cors_auth_success_failure_and_preflight(self):
        app = application()
        with patch.object(constants, "cors", CorsConstants(CORS_ORIGINS=["https://atlas.example"])):
            configure_cors(app)
        with TestClient(app) as client:
            for origin, allowed in (('https://atlas.example', True), ('https://denied.example', False)):
                for path in ('refresh', 'logout'):
                    response = client.options('/auth/' + path, headers={'Origin': origin,
                                                                        'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'Content-Type'})
                    self.assertEqual(response.status_code,
                                     200 if allowed else 400)
                    self.assertEqual(response.headers.get(
                        'access-control-allow-origin'), origin if allowed else None)
                    for cookie in (False, True):
                        headers = {'Origin': origin}
                        if cookie:
                            headers['Cookie'] = 'atlas_refresh=' + self.token
                        response = client.post(
                            '/auth/' + path, headers=headers)
                        self.assertEqual(response.headers.get(
                            'access-control-allow-origin'), origin if allowed else None)
                        self.assertEqual(response.headers.get(
                            'access-control-allow-credentials'), 'true')
                for method, header in (('GET', 'Content-Type'), ('POST', 'Authorization')):
                    response = client.options('/auth/refresh', headers={'Origin': origin,
                                                                        'Access-Control-Request-Method': method, 'Access-Control-Request-Headers': header})
                    self.assertEqual(response.status_code, 400)

    def test_route_inventory_has_six_post_only_and_no_bearer_dependency(self):
        from app.routers.auth import refreshing, logging_out
        paths = application().openapi()['paths']
        self.assertEqual(set(paths), {'/auth/' + path for path in (
            'register', 'verify', 'resend', 'login', 'refresh', 'logout')})
        for path, value in paths.items():
            self.assertEqual(set(value), {'post'})
            self.assertNotIn('security', value['post'])
        for path in ('refresh', 'logout'):
            operation = paths['/auth/' + path]['post']
            self.assertNotIn('requestBody', operation)
            self.assertNotIn('parameters', operation)
        self.assertEqual(paths['/auth/refresh']['post']['responses']['200']['content']['application/json']['schema']['$ref'],
                         '#/components/schemas/AuthenticatedResponse')
        for endpoint in (refreshing, logging_out):
            self.assertFalse(inspect.iscoroutinefunction(endpoint))


if __name__ == '__main__':
    unittest.main()
