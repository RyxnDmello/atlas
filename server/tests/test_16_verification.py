import os
import unittest
from uuid import uuid4
from types import SimpleNamespace
from pydantic import ValidationError
from contextlib import contextmanager
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone

from app.core.constants import Constants
from app.models.postgres import User, Verification, Session

from app.pipeline.auth.verify import Verified, resend, verify
from app.pipeline.auth.initial_session import Credentials, issue

from app.schemas.constants import RefreshConstants
from app.schemas.auth.verification import ResendRequest, VerifyRequest, VerifiedUser

from app.errors.postgres import PostgresOperationError
from app.errors.auth import InvalidVerificationError, VerificationExpiredError

from tests.test_15_registration import application


class FakeDatabase:
    """Provide one local session seam without claiming PostgreSQL lock behavior."""

    def __init__(self, user: User | None, row: Verification | None) -> None:
        self.session_value = MagicMock()
        self.session_value.scalars.side_effect = [
            SimpleNamespace(one_or_none=lambda: user),
            SimpleNamespace(one_or_none=lambda: row),
        ]

    @contextmanager
    def session(self):
        try:
            yield self.session_value
        except BaseException:
            self.session_value.rollback()
            raise


def state(expired: bool = False) -> tuple[User, Verification]:
    now = datetime.now(timezone.utc)
    user = User(id=uuid4(), name="Test", email="test@example.com",
                password="synthetic", verified_at=None, created_at=now, updated_at=now)
    row = Verification(id=uuid4(), user_id=user.id, type="auth", otp="012345",
                       created_at=now, expires_at=now + timedelta(seconds=-1 if expired else 60))
    return user, row


class VerificationTests(unittest.TestCase):
    def test_schema_accepts_leading_zero_and_normalizes_email(self) -> None:
        value = VerifyRequest.model_validate(
            {"email": " TEST@EXAMPLE.COM ", "otp": "012345"})
        self.assertEqual((value.email, value.otp),
                         ("test@example.com", "012345"))
        for otp in (123456, "12345", "1234567", "12345a", "１２３４５６"):
            with self.subTest(kind=type(otp).__name__), self.assertRaises(ValidationError):
                VerifyRequest.model_validate(
                    {"email": "test@example.com", "otp": otp})
        with self.assertRaises(ValidationError):
            ResendRequest.model_validate({"email": "invalid"})

    def test_refresh_config_is_explicit_and_positive(self) -> None:
        self.assertEqual(RefreshConstants(
            AUTH_COOKIE_SECURE=False).AUTH_REFRESH_TOKEN_TTL_SECONDS, 604800)
        with patch.dict(os.environ, {"AUTH_COOKIE_SECURE": "true", "AUTH_REFRESH_TOKEN_TTL_SECONDS": "73"}):
            config = Constants().refresh
            self.assertTrue(config.AUTH_COOKIE_SECURE)
            self.assertEqual(config.AUTH_REFRESH_TOKEN_TTL_SECONDS, 73)
        for value in ("0", "-1", "invalid"):
            with patch.dict(os.environ, {"AUTH_COOKIE_SECURE": "false", "AUTH_REFRESH_TOKEN_TTL_SECONDS": value}):
                with self.assertRaises(ValueError):
                    _ = Constants().refresh
        with patch.dict(os.environ):
            os.environ.pop("AUTH_COOKIE_SECURE", None)
            with self.assertRaises(ValueError):
                _ = Constants().refresh

    def test_wrong_otp_preserves_row(self) -> None:
        user, row = state()
        database = FakeDatabase(user, row)
        with patch("app.pipeline.auth.verify.postgres", return_value=database):
            with self.assertRaises(InvalidVerificationError):
                verify(VerifyRequest(email=user.email, otp="999999"))
        database.session_value.delete.assert_not_called()
        database.session_value.commit.assert_not_called()
        self.assertIsNone(user.verified_at)
        self.assertEqual(row.otp, "012345")

    def test_expired_row_commits_before_error(self) -> None:
        user, row = state(expired=True)
        database = FakeDatabase(user, row)
        with patch("app.pipeline.auth.verify.postgres", return_value=database):
            with self.assertRaises(VerificationExpiredError):
                verify(VerifyRequest(email=user.email, otp=row.otp))
        database.session_value.delete.assert_called_once_with(row)
        database.session_value.commit.assert_called_once()
        self.assertIsNone(user.verified_at)

    def test_expired_cleanup_failure_is_database_error(self) -> None:
        user, row = state(expired=True)
        database = FakeDatabase(user, row)
        database.session_value.commit.side_effect = SQLAlchemyError("private")
        with patch("app.pipeline.auth.verify.postgres", return_value=database):
            with self.assertRaises(PostgresOperationError):
                verify(VerifyRequest(email=user.email, otp=row.otp))

    def test_success_stages_one_session_and_commits(self) -> None:
        user, row = state()
        database = FakeDatabase(user, row)
        credentials = Credentials(
            access="synthetic-access", refresh="synthetic-refresh")
        with patch("app.pipeline.auth.verify.postgres", return_value=database), patch(
                "app.pipeline.auth.verify.issue", return_value=credentials) as issuer:
            result = verify(VerifyRequest(email=user.email, otp=row.otp))
        self.assertEqual(result.user.id, user.id)
        self.assertEqual(result.credentials, credentials)
        self.assertIsNotNone(user.verified_at)
        database.session_value.delete.assert_called_once_with(row)
        database.session_value.commit.assert_called_once()
        issuer.assert_called_once()

    def test_initial_session_persists_hash_only(self) -> None:
        user, _ = state()
        session = MagicMock()
        now = datetime.now(timezone.utc)
        with patch("app.pipeline.auth.initial_session.Access") as access, patch(
                "app.pipeline.auth.initial_session.generate", return_value="synthetic-refresh"), patch(
                "app.pipeline.auth.initial_session.constants") as config:
            config.refresh.AUTH_REFRESH_TOKEN_TTL_SECONDS = 71
            access.return_value.issue.return_value = "synthetic-access"
            credentials = issue(session, user, now)
        stored = session.add.call_args.args[0]
        self.assertIsInstance(stored, Session)
        self.assertEqual(stored.user_id, user.id)
        self.assertEqual(stored.expires_at - now, timedelta(seconds=71))
        self.assertEqual(len(stored.token_hash), 64)
        self.assertNotEqual(stored.token_hash, credentials.refresh)
        self.assertEqual(credentials.access, "synthetic-access")

    def test_resend_replaces_existing_otp_without_session(self) -> None:
        user, row = state()
        database = FakeDatabase(user, row)
        with patch("app.pipeline.auth.verify.postgres", return_value=database), patch(
                "app.pipeline.auth.verify.generate", side_effect=["012345", "654321"]):
            resend(ResendRequest(email=user.email))
        self.assertEqual(row.otp, "654321")
        self.assertEqual(row.expires_at - row.created_at,
                         timedelta(seconds=Constants().otp.AUTH_OTP_TTL_SECONDS))
        database.session_value.add.assert_not_called()
        database.session_value.commit.assert_called_once()

    def test_resend_creates_missing_row(self) -> None:
        user, _ = state()
        database = FakeDatabase(user, None)
        with patch("app.pipeline.auth.verify.postgres", return_value=database), patch(
                "app.pipeline.auth.verify.generate", return_value="654321"):
            resend(ResendRequest(email=user.email))
        row = database.session_value.add.call_args.args[0]
        self.assertIsInstance(row, Verification)
        self.assertEqual((row.user_id, row.type), (user.id, "auth"))

    def test_http_cookie_and_error_contract(self) -> None:
        user, _ = state()
        result = Verified(VerifiedUser(id=user.id, name=user.name, email=user.email),
                          Credentials(access="synthetic-access", refresh="synthetic-refresh"))
        with TestClient(application()) as client, patch("app.routers.auth.verify", return_value=result):
            response = client.post(
                "/auth/verify", json={"email": user.email, "otp": "012345"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {
                         "access_token", "token_type", "user"})
        cookie = response.headers["set-cookie"]
        for attribute in ("atlas_refresh=", "HttpOnly", "Path=/auth", "SameSite=lax", "Max-Age=604800"):
            self.assertIn(attribute, cookie)
        self.assertNotIn("synthetic-refresh", response.text)
        with TestClient(application()) as client, patch(
                "app.routers.auth.verify", side_effect=InvalidVerificationError()):
            failure = client.post(
                "/auth/verify", json={"email": user.email, "otp": "012345"})
        self.assertEqual((failure.status_code, failure.json()[
                         "code"]), (400, "INVALID_VERIFICATION"))
        self.assertNotIn("set-cookie", failure.headers)

    def test_http_auth_errors_and_validation_are_safe(self) -> None:
        from app.errors.auth import (
            AccountNotFoundError, VerificationNotRequiredError, VerificationExpiredError,
        )

        cases = (
            (AccountNotFoundError(), 404, "ACCOUNT_NOT_FOUND"),
            (VerificationNotRequiredError(), 409, "VERIFICATION_NOT_REQUIRED"),
            (InvalidVerificationError(), 400, "INVALID_VERIFICATION"),
            (VerificationExpiredError(), 400, "VERIFICATION_EXPIRED"),
        )
        with TestClient(application()) as client:
            for error, status, code in cases:
                for path, payload, symbol in (
                    ("/auth/verify",
                     {"email": "test@example.com", "otp": "012345"}, "verify"),
                    ("/auth/resend", {"email": "test@example.com"}, "resend"),
                ):
                    with self.subTest(path=path, code=code), patch(
                            "app.routers.auth." + symbol, side_effect=error):
                        response = client.post(path, json=payload)
                        self.assertEqual(
                            (response.status_code, response.json()["code"]), (status, code))
                        self.assertNotIn("set-cookie", response.headers)

            for path, payload in (
                ("/auth/verify",
                 {"email": "test@example.com", "otp": "private-invalid"}),
                ("/auth/resend", {"email": "private-invalid"}),
            ):
                response = client.post(path, json=payload)
                self.assertEqual((response.status_code, response.json()[
                                 "code"]), (422, "UNPROCESSABLE_ENTITY"))
                self.assertNotIn("private-invalid", response.text)


if __name__ == "__main__":
    unittest.main()
