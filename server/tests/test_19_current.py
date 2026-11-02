import os
import inspect
import secrets
import unittest
from jwt import encode
from uuid import uuid4
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone

from fastapi import Request
from fastapi.testclient import TestClient

from app.core.cors import configure_cors
from app.core.constants import constants

from app.pipeline.auth.access import Access
from app.pipeline.auth.logout import logout
from app.pipeline.auth.current import current
from app.pipeline.auth.rotation import refresh

from app.models.postgres import User
from app.schemas.constants import AuthConstants, CorsConstants

from app.errors.auth import InvalidAccessTokenError

from tests.test_17_login import FakeDatabase
from tests.test_15_registration import application


def bearer(value: str | None) -> Request:
    """Construct a dependency request without normalizing the header credential."""
    return Request({'type': 'http', 'headers': [] if value is None else [
        (b'authorization', value.encode('latin1'))]})


class CurrentTests(unittest.TestCase):
    def setUp(self):
        self.secret = secrets.token_urlsafe(48)
        scope = patch.dict(
            os.environ, {'AUTH_ACCESS_TOKEN_SECRET': self.secret})
        scope.start()
        self.addCleanup(scope.stop)
        self.user = User(id=uuid4(), name='Canonical', email='stored@example.com',
                         verified_at=datetime.now(timezone.utc))
        self.database = FakeDatabase(self.user)
        self.session = self.database.session_value
        self.session.get.return_value = self.user
        scope = patch('app.pipeline.auth.current.postgres',
                      return_value=self.database)
        self.postgres = scope.start()
        self.addCleanup(scope.stop)
        self.token = Access().issue(self.user.id)

    def get(self, header=None, **kwargs):
        with TestClient(application()) as client:
            return client.get('/auth', headers={} if header is None else {
                'Authorization': header}, **kwargs)

    def invalid(self, header):
        response = self.get(header)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'error': 'Invalid access token', 'code': 'INVALID_ACCESS_TOKEN'})
        self.assertNotIn('set-cookie', response.headers)

    def test_missing_wrong_blank_and_malformed_skip_database(self):
        for header in (None, '', 'Basic '+self.token, 'Bearer', 'Bearer ',
                       'Bearer    ', 'Bearer\t'+self.token, 'Bearer malformed'):
            with self.subTest(header_kind=header.split(' ')[0] if header else 'absent'):
                self.invalid(header)
        self.postgres.assert_not_called()

    def test_scheme_case_and_literal_decoder_input(self):
        for scheme in ('Bearer', 'bearer', 'bEaReR'):
            self.assertIs(current(bearer(scheme+' '+self.token)), self.user)
        with patch.object(Access, 'decode', side_effect=InvalidAccessTokenError()) as decode:
            self.invalid('Bearer  literal ')
        decode.assert_called_once_with(' literal ')

    def test_real_decoder_rejects_claim_signature_and_algorithm_failures(self):
        now = datetime.now(timezone.utc).timestamp()
        base = {'sub': str(self.user.id), 'jti': str(uuid4()), 'type': 'access',
                'iat': now-10, 'exp': now+60}
        cases = [{**base, 'exp': now-1}, {**base, 'type': 'refresh'},
                 {**base, 'sub': 'invalid'}, {**base, 'jti': 'invalid'},
                 {**base, 'iat': float('inf')}, {**base, 'exp': True},
                 {**base, 'iat': now+600}]
        for key in base:
            cases.append({k: v for k, v in base.items() if k != key})
        for claims in cases:
            self.invalid(
                'Bearer '+encode(claims, self.secret, algorithm='HS256'))
        for algorithm, secret in (('HS256', secrets.token_urlsafe(48)), ('HS384', self.secret)):
            self.invalid('Bearer '+encode(base, secret, algorithm=algorithm))
        self.invalid('Bearer '+self.token+'.altered')
        self.postgres.assert_not_called()

    def test_canonical_safe_response_and_read_only_lookup(self):
        response = self.get('Bearer '+self.token, params={
            'user_id': str(uuid4()), 'name': 'Attacker', 'email': 'attacker@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'id': str(self.user.id),
                                           'name': self.user.name, 'email': self.user.email})
        self.assertNotIn('set-cookie', response.headers)
        self.session.get.assert_called_once_with(User, self.user.id)
        for method in ('commit', 'add', 'delete', 'execute', 'scalars', 'flush'):
            getattr(self.session, method).assert_not_called()
        self.assertIs(current(bearer('Bearer '+self.token)), self.user)
        self.assertFalse(inspect.iscoroutinefunction(current))

    def test_refresh_cookie_and_query_cannot_authenticate(self):
        self.invalid(None)
        with TestClient(application()) as client:
            response = client.get('/auth?access_token=untrusted',
                                  headers={'Cookie': 'atlas_refresh='+self.token})
        self.assertEqual(response.status_code, 401)
        self.postgres.assert_not_called()

    def test_missing_deleted_and_unverified_are_same_generic_failure(self):
        for user in (None, User(id=self.user.id, verified_at=None)):
            self.session.get.return_value = user
            self.invalid('Bearer '+self.token)
        self.session.commit.assert_not_called()

    def test_operational_failure_is_sanitized_and_unlogged(self):
        private = 'private-driver-diagnostic'
        self.session.get.side_effect = SQLAlchemyError(private)
        with self.assertNoLogs('app', level='DEBUG'):
            response = self.get('Bearer '+self.token)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['code'], 'POSTGRES_OPERATION_FAILED')
        for value in (private, self.token, self.secret):
            self.assertNotIn(value, response.text)
        self.assertNotIn('set-cookie', response.headers)
        self.session.rollback.assert_called_once()

    def test_old_access_survives_real_rotation_logout_orchestration_then_expires(self):
        from types import SimpleNamespace
        self.session.execute.return_value.one_or_none.return_value = SimpleNamespace(
            id=uuid4(), user_id=self.user.id)
        with patch('app.pipeline.auth.rotation.postgres', return_value=self.database), patch(
                'app.pipeline.auth.logout.postgres', return_value=self.database):
            result = refresh(secrets.token_urlsafe(48))
            self.assertEqual(self.get('Bearer '+self.token).status_code, 200)
            logout(result.credentials.refresh)
            self.assertEqual(self.get('Bearer '+self.token).status_code, 200)
            self.assertEqual(
                self.get('Bearer '+result.credentials.access).status_code, 200)
        short = Access(AuthConstants.model_validate({
            'AUTH_ACCESS_TOKEN_SECRET': self.secret, 'AUTH_ACCESS_TOKEN_TTL_SECONDS': 3})).issue(self.user.id)
        self.assertEqual(self.get('Bearer '+short).status_code, 200)
        future = datetime.now(timezone.utc)+timedelta(seconds=4)
        with patch('jwt.api_jwt.datetime') as clock:
            clock.now.return_value = future
            self.invalid('Bearer '+short)

    def test_current_user_cors_and_contract(self):
        app = application()
        with patch.object(constants, 'cors', CorsConstants(CORS_ORIGINS=['https://atlas.example'])):
            configure_cors(app)
        with TestClient(app) as client:
            for origin, allowed in (('https://atlas.example', True), ('https://denied.example', False)):
                for method, header, supported in (('GET', 'Authorization', True),
                                                  ('POST', 'Content-Type', True),
                                                  ('PUT', 'Authorization', False),
                                                  ('PATCH', 'Authorization', True),
                                                  ('DELETE', 'Authorization', False),
                                                  ('GET', 'X-Unapproved', False)):
                    response = client.options('/auth', headers={'Origin': origin,
                                                                'Access-Control-Request-Method': method, 'Access-Control-Request-Headers': header})
                    self.assertEqual(response.status_code,
                                     200 if allowed and supported else 400)
                for token in (self.token, 'invalid'):
                    response = client.get(
                        '/auth', headers={'Origin': origin, 'Authorization': 'Bearer '+token})
                    self.assertEqual(response.headers.get(
                        'access-control-allow-origin'), origin if allowed else None)
                    self.assertEqual(response.headers.get(
                        'access-control-allow-credentials'), 'true')
        operation = app.openapi()['paths']['/auth']['get']
        self.assertNotIn('requestBody', operation)
        self.assertNotIn('parameters', operation)
        self.assertEqual(operation['responses']['200']['content']['application/json']['schema']['$ref'],
                         '#/components/schemas/AuthenticatedUser')


if __name__ == '__main__':
    unittest.main()
