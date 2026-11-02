import os
import json
import secrets
import inspect
import unittest
from uuid import uuid4
from copy import deepcopy
from argon2 import PasswordHasher
from pydantic import ValidationError
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from app.pipeline.auth.login import login
from app.pipeline.auth.access import Access
from app.pipeline.auth.refresh import digest
from app.pipeline.auth.password import Password

from app.models.postgres import User, Session
from app.schemas.auth.login import LoginRequest

from app.errors.auth import CredentialError, InvalidCredentialsError

from tests.test_15_registration import application


class FakeDatabase:
    """Exercise orchestration only; real rollback/locking belongs to login_live."""

    def __init__(self, user: User | None) -> None:
        self.session_value = MagicMock()
        self.session_value.scalars.return_value.one_or_none.return_value = user

    @contextmanager
    def session(self):
        try:
            yield self.session_value
        except BaseException:
            self.session_value.rollback()
            raise


class LoginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.supplied = secrets.token_urlsafe(24)
        cls.encoded = Password().hash(cls.supplied)

    def setUp(self) -> None:
        scope = patch.dict(os.environ, {
            "AUTH_ACCESS_TOKEN_SECRET": secrets.token_urlsafe(48),
            "AUTH_COOKIE_SECURE": "false", "AUTH_REFRESH_TOKEN_TTL_SECONDS": "73",
        })
        scope.start()
        self.addCleanup(scope.stop)
        now = datetime.now(timezone.utc)
        self.user = User(id=uuid4(), name="Stored Name", email="test@example.com",
                         password=self.encoded, verified_at=now, created_at=now, updated_at=now)
        self.database = FakeDatabase(self.user)
        scope = patch("app.pipeline.auth.login.postgres",
                      return_value=self.database)
        scope.start()
        self.addCleanup(scope.stop)

    def request(self, **values: object) -> LoginRequest:
        return LoginRequest.model_validate({"email": self.user.email,
                                            "password": self.supplied, **values})

    def http(self, **values: object):
        with TestClient(application()) as client:
            return client.post("/auth/login", json={"email": self.user.email,
                                                    "password": self.supplied, **values})

    def test_schema_exact_fields_canonical_email_and_literal_password(self) -> None:
        literal = "  Password  "
        value = self.request(email=" TEST@EXAMPLE.COM ", password=literal)
        self.assertEqual(value.email, "test@example.com")
        self.assertEqual(value.password.get_secret_value(), literal)
        self.assertNotIn(literal, repr(value))
        for length in (8, 128):
            self.assertEqual(
                len(self.request(password=" " * length).password.get_secret_value()), length)
        for length in (7, 129):
            with self.assertRaises(ValidationError) as caught:
                self.request(password="s" * length)
            self.assertNotIn("s" * length, str(caught.exception))
        for values in ({"email": "invalid"}, {"password": 12345678}, {"user_id": str(uuid4())}):
            with self.assertRaises(ValidationError):
                self.request(**values)
        for payload in ({"email": self.user.email}, {"password": self.supplied}):
            with self.assertRaises(ValidationError):
                LoginRequest.model_validate(payload)

    def test_invalid_http_input_is_safe_and_does_not_enter_domain(self) -> None:
        sentinel = secrets.token_urlsafe(24)
        with TestClient(application()) as client, patch("app.routers.auth.login") as domain:
            for payload in ({"email": sentinel, "password": sentinel},
                            {"email": self.user.email,
                                "password": sentinel, "extra": sentinel},
                            {"email": self.user.email, "password": "short"}):
                response = client.post("/auth/login", json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json(), {
                                 "error": "Invalid login input", "code": "UNPROCESSABLE_ENTITY"})
                self.assertNotIn(sentinel, response.text)
                self.assertNotIn("set-cookie", response.headers)
            response = client.post("/auth/login", content='{"password":"' + sentinel,
                                   headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(sentinel, response.text)
        domain.assert_not_called()

    def test_unknown_email_never_constructs_password_primitive(self) -> None:
        self.database.session_value.scalars.return_value.one_or_none.return_value = None
        with patch("app.pipeline.auth.login.Password") as password, patch("app.pipeline.auth.login.issue") as issuer:
            with self.assertRaises(InvalidCredentialsError):
                login(self.request())
        password.assert_not_called()
        issuer.assert_not_called()
        self.database.session_value.commit.assert_not_called()

    def test_three_invalid_credentials_http_results_are_identical(self) -> None:
        outcomes = []
        for exists, verified in ((False, False), (True, True), (True, False)):
            self.user.verified_at = datetime.now(
                timezone.utc) if verified else None
            self.database.session_value.scalars.return_value.one_or_none.return_value = self.user if exists else None
            response = self.http(password=self.supplied + "wrong")
            outcomes.append((response.status_code, response.json()))
            self.assertNotIn("set-cookie", response.headers)
        self.assertEqual(outcomes, [
                         (401, {"error": "Invalid credentials", "code": "INVALID_CREDENTIALS"})] * 3)
        self.database.session_value.add.assert_not_called()
        self.database.session_value.commit.assert_not_called()

    def test_unverified_correct_password_has_no_mutation_or_otp_path(self) -> None:
        self.user.verified_at = None
        prior = deepcopy((self.user.password, self.user.updated_at))
        with patch.object(Password, "needs_rehash", return_value=True) as rehash, patch.object(
                Password, "hash") as hashing, patch("app.pipeline.auth.login.issue") as issuer, patch(
                "app.pipeline.auth.verification.generate") as otp:
            response = self.http()
        self.assertEqual((response.status_code, response.json()),
                         (403, {"error": "Verification required", "code": "VERIFICATION_REQUIRED"}))
        self.assertNotIn("set-cookie", response.headers)
        self.assertEqual((self.user.password, self.user.updated_at), prior)
        for seam in (rehash, hashing, issuer, otp):
            seam.assert_not_called()
        self.database.session_value.add.assert_not_called()
        self.database.session_value.delete.assert_not_called()
        self.database.session_value.commit.assert_not_called()
        self.database.session_value.scalars.assert_called_once()

    def test_verified_success_uses_existing_jwt_and_hash_only_session(self) -> None:
        prior = self.user.password
        with self.assertNoLogs("app", level="DEBUG"):
            result = login(self.request())
        self.assertEqual(result.user.id, self.user.id)
        self.assertEqual(Access().decode(
            result.credentials.access).user, self.user.id)
        stored = self.database.session_value.add.call_args.args[0]
        self.assertIsInstance(stored, Session)
        self.assertEqual(stored.token_hash, digest(result.credentials.refresh))
        self.assertNotEqual(stored.token_hash, result.credentials.refresh)
        self.assertEqual(
            (stored.expires_at - stored.created_at).total_seconds(), 73)
        self.assertEqual(self.user.password, prior)
        self.database.session_value.commit.assert_called_once()
        statement = self.database.session_value.scalars.call_args.args[0]
        self.assertIn("FOR UPDATE", str(statement))

    def test_response_and_cookie_exact_for_secure_and_insecure_configuration(self) -> None:
        for secure in (False, True):
            with patch.dict(os.environ, {"AUTH_COOKIE_SECURE": str(secure).lower()}):
                response = self.http()
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(set(body), {"access_token", "user"})
            self.assertEqual(body["user"], {"id": str(
                self.user.id), "name": self.user.name, "email": self.user.email})
            cookie = response.headers["set-cookie"]
            parts = cookie.split("; ")
            self.assertEqual(set(parts[1:]), {
                             "HttpOnly", "Max-Age=73", "Path=/auth", "SameSite=lax"} | ({"Secure"} if secure else set()))
            refresh = parts[0].removeprefix("atlas_refresh=")
            self.assertTrue(parts[0].startswith("atlas_refresh="))
            self.assertNotIn(refresh, json.dumps(body))
            self.assertEqual(Access().decode(
                body["access_token"]).user, self.user.id)

    def test_no_rehash_keeps_hash_and_updated_timestamp(self) -> None:
        prior = (self.user.password, self.user.updated_at)
        with patch.object(Password, "needs_rehash", return_value=False), patch.object(Password, "hash") as hashing:
            login(self.request())
        hashing.assert_not_called()
        self.assertEqual((self.user.password, self.user.updated_at), prior)

    def test_rehash_uses_literal_verified_password_before_session_commit(self) -> None:
        old = PasswordHasher(time_cost=1, memory_cost=1024,
                             parallelism=1).hash(self.supplied)
        self.user.password = old
        self.assertTrue(Password().needs_rehash(old))
        login(self.request())
        self.assertTrue(self.user.password != old)
        self.assertTrue(Password().verify(self.user.password, self.supplied))
        self.assertFalse(Password().needs_rehash(self.user.password))
        self.database.session_value.commit.assert_called_once()

    def test_staging_and_commit_failure_roll_back_without_cookie(self) -> None:
        for failing in ("add", "commit"):
            self.database.session_value.reset_mock(side_effect=True)
            getattr(self.database.session_value, failing).side_effect = SQLAlchemyError(
                "private diagnostic")
            with patch.object(Password, "needs_rehash", return_value=True), patch.object(
                    Password, "hash", return_value=self.encoded), self.assertNoLogs("app", level="DEBUG"):
                response = self.http()
            self.assertEqual((response.status_code, response.json()),
                             (500, {"error": "Unable to complete database operation", "code": "POSTGRES_OPERATION_FAILED"}))
            self.assertNotIn("set-cookie", response.headers)
            self.database.session_value.rollback.assert_called_once()

    def test_corrupt_hash_is_internal_error_without_credentials(self) -> None:
        self.user.password = "corrupt-synthetic-hash"
        response = self.http()
        self.assertEqual((response.status_code, response.json()),
                         (500, {"error": "Unable to process credentials", "code": "INTERNAL_SERVER_ERROR"}))
        self.assertNotIn("set-cookie", response.headers)
        self.database.session_value.add.assert_not_called()
        self.database.session_value.commit.assert_not_called()

    def test_crypto_failures_do_not_commit_or_expose_diagnostics(self) -> None:
        for symbol in ("verify", "needs_rehash", "hash"):
            with patch.object(Password, "needs_rehash", return_value=True), patch.object(
                    Password, symbol, side_effect=CredentialError()):
                response = self.http()
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json()["code"], "INTERNAL_SERVER_ERROR")
            self.assertNotIn("set-cookie", response.headers)
        self.database.session_value.commit.assert_not_called()

    def test_multiple_successes_create_independent_sessions_without_deletion(self) -> None:
        first = login(self.request())
        second = login(self.request())
        rows = [call.args[0]
                for call in self.database.session_value.add.call_args_list]
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0].token_hash != rows[1].token_hash)
        self.assertTrue(first.credentials.access != second.credentials.access)
        self.database.session_value.delete.assert_not_called()

    def test_openapi_inventory_shared_response_and_cors(self) -> None:
        from app.main import app
        from app.routers.auth import logging_in

        specification = app.openapi()
        paths = specification["paths"]
        self.assertEqual({path for path in paths if path.startswith("/auth")},
                         {"/auth", "/auth/register", "/auth/verify", "/auth/resend", "/auth/login", "/auth/refresh", "/auth/logout"})
        for path in ("/auth/login", "/auth/verify"):
            self.assertEqual(set(paths[path]), {"post"})
            schema = paths[path]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
            self.assertEqual(
                schema["$ref"], "#/components/schemas/AuthenticatedResponse")
        self.assertEqual(set(specification["components"]["schemas"]["AuthenticatedResponse"]["properties"]), {
                         "access_token", "user"})
        self.assertFalse(inspect.iscoroutinefunction(logging_in))
        cors = next(
            middleware for middleware in app.user_middleware if middleware.cls is CORSMiddleware)
        self.assertTrue(cors.kwargs["allow_credentials"])


if __name__ == "__main__":
    unittest.main()
