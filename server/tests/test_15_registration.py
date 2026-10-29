import os
import json
import secrets
import inspect
import unittest
from uuid import uuid4
from pathlib import Path
from dotenv import dotenv_values
from types import SimpleNamespace
from pydantic import ValidationError
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.postgres import Database
from app.core.constants import Constants

from app.routers.auth import router
from app.pipeline.auth.registration import register

from app.schemas.constants import OtpConstants
from app.schemas.auth.registration import RegistrationRequest

from app.models.postgres import User, Verification

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error
from app.errors.postgres import PostgresOperationError
from app.errors.auth import AccountAlreadyExistsError, CredentialError


def request(**values: object) -> RegistrationRequest:
    """Use synthetic credentials without emitting them in assertion output."""
    return RegistrationRequest.model_validate({
        "name": "  Atlas  Tester  ", "email": "  Atlas.Test+Tag@EXAMPLE.COM  ",
        "password": secrets.token_urlsafe(18), **values,
    })


def application() -> FastAPI:
    """Exercise the actual auth router without preparing unrelated providers."""
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(ApiError, cast_handle_api_error())

    return app


def integrity(table: str | None = "users", constraint: str | None = "uq_users_email", state: str = "23505") -> IntegrityError:
    """Model driver metadata separately from deliberately sensitive diagnostics."""
    class DriverError(Exception):
        sqlstate = state
        diag = SimpleNamespace(table_name=table, constraint_name=constraint)

    original = DriverError("synthetic-private-database-diagnostic")

    return IntegrityError("synthetic-private-sql", {}, original)


class RegistrationSchemaTests(unittest.TestCase):
    """Prove canonical identity and literal password boundaries."""

    def test_canonicalization_and_password_preservation(self) -> None:
        plaintext = "  literal password  "
        value = request(password=plaintext)
        self.assertEqual(value.name, "Atlas  Tester")
        self.assertEqual(value.email, "atlas.test+tag@example.com")
        self.assertTrue(value.password.get_secret_value() == plaintext)
        self.assertNotIn(plaintext, repr(value))
        self.assertNotIn(plaintext, value.model_dump_json())

    def test_name_bounds_after_trim(self) -> None:
        for name in (" a ", " " + "a" * 100 + " "):
            request(name=name)
        for name in ("", " \t ", "a" * 101, None, 7):
            with self.subTest(length=len(name) if isinstance(name, str) else None):
                with self.assertRaises(ValidationError):
                    request(name=name)

    def test_password_bounds_without_composition_or_trim(self) -> None:
        for size in (8, 128):
            self.assertEqual(
                len(request(password=" " * size).password.get_secret_value()), size)
        for value in ("a" * 7, "a" * 129, None, 123):
            with self.assertRaises(ValidationError) as caught:
                request(password=value)
            if isinstance(value, str):
                self.assertNotIn(value, str(caught.exception))

    def test_invalid_email_and_exact_fields(self) -> None:
        for email in ("invalid", "a@", "a@localhost", "a@[127.0.0.1]", None):
            with self.assertRaises(ValidationError):
                request(email=email)
        with self.assertRaises(ValidationError):
            request(verified_at="unexpected")
        for name in ("name", "email", "password"):
            values = request().model_dump()
            values.pop(name)
            with self.assertRaises(ValidationError):
                RegistrationRequest.model_validate(values)

    def test_email_normalization_without_dns(self) -> None:
        with patch("email_validator.deliverability.validate_email_deliverability", side_effect=AssertionError("DNS forbidden")):
            self.assertEqual(
                request(email=" A@EXAMPLE.COM ").email, "a@example.com")
            self.assertEqual(request(email="A@bücher.de").email, "a@bücher.de")


class OtpConfigurationTests(unittest.TestCase):
    """Keep registration lifetime independent of access signing configuration."""

    def test_defaults_positive_override_and_rejection(self) -> None:
        self.assertEqual(OtpConstants().AUTH_OTP_TTL_SECONDS, 600)
        self.assertEqual(OtpConstants.model_validate(
            {"AUTH_OTP_TTL_SECONDS": "73"}).AUTH_OTP_TTL_SECONDS, 73)
        for value in (0, -1, "invalid", "1.5", None):
            with self.assertRaises(ValidationError):
                OtpConstants.model_validate({"AUTH_OTP_TTL_SECONDS": value})

    def test_lazy_independence_and_blank_defaults(self) -> None:
        values = {name: value for name, value in dotenv_values(
            Path(__file__).resolve().parents[1] / ".env.example").items() if value is not None}
        values.pop("AUTH_ACCESS_TOKEN_SECRET")
        with patch.dict(os.environ, values, clear=True):
            for value in (None, "", " "):
                os.environ.pop("AUTH_OTP_TTL_SECONDS", None)
                if value is not None:
                    os.environ["AUTH_OTP_TTL_SECONDS"] = value
                self.assertEqual(Constants().otp.AUTH_OTP_TTL_SECONDS, 600)
            os.environ["AUTH_OTP_TTL_SECONDS"] = "42"
            self.assertEqual(Constants().otp.AUTH_OTP_TTL_SECONDS, 42)
            for value in ("0", "-1", "invalid"):
                os.environ["AUTH_OTP_TTL_SECONDS"] = value
                Constants()
                with self.assertRaisesRegex(ValueError, "Invalid OTP configuration"):
                    _ = Constants().otp


class RegistrationDomainTests(unittest.TestCase):
    """Exercise the real Database context boundary with deterministic session seams.

    These checks prove orchestration and rollback calls, not PostgreSQL semantics;
    the opt-in real-service helper supplies that independent acceptance evidence.
    """

    def setUp(self) -> None:
        self.session = MagicMock()
        self.session.__enter__.return_value = self.session
        self.records = []
        self.session.add.side_effect = self.records.append

        def flush() -> None:
            for record in self.records:
                if record.id is None:
                    record.id = uuid4()

        self.session.flush.side_effect = flush
        factory = MagicMock(return_value=self.session)
        self.database = Database(MagicMock(), factory)
        postgres = patch("app.pipeline.auth.registration.postgres",
                         return_value=self.database)
        self.postgres: MagicMock = postgres.start()
        self.addCleanup(postgres.stop)

        password = patch("app.pipeline.auth.registration.Password")
        self.Password: MagicMock = password.start()
        self.addCleanup(password.stop)

        generate = patch("app.pipeline.auth.registration.generate",
                         return_value="000007")
        self.generate: MagicMock = generate.start()
        self.addCleanup(generate.stop)
        self.Password.return_value.hash.return_value = "synthetic-encoded-value"

    def test_success_reuses_primitives_and_commits_once(self) -> None:
        value = request()
        with patch.dict(os.environ, {"AUTH_OTP_TTL_SECONDS": "73", "AUTH_ACCESS_TOKEN_SECRET": ""}):
            self.assertIsNone(register(value))
        self.Password.return_value.hash.assert_called_once()
        self.assertTrue(
            self.Password.return_value.hash.call_args.args[0] == value.password.get_secret_value())
        self.generate.assert_called_once_with()
        self.assertEqual(len(self.records), 2)
        user, verification = self.records
        self.assertIsInstance(user, User)
        self.assertIsInstance(verification, Verification)
        self.assertEqual(user.name, value.name)
        self.assertEqual(user.email, value.email)
        self.assertIsNone(user.verified_at)
        self.assertTrue(user.password == "synthetic-encoded-value")
        self.assertEqual(verification.user_id, user.id)
        self.assertEqual(verification.type, "auth")
        self.assertTrue(verification.otp == "000007")
        self.assertEqual(verification.created_at, user.created_at)
        self.assertEqual(user.created_at, user.updated_at)
        self.assertIsNotNone(user.created_at.tzinfo)
        self.assertEqual((verification.expires_at -
                         user.created_at).total_seconds(), 73)
        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_not_called()
        self.session.execute.assert_not_called()
        self.assertEqual(self.session.flush.call_count, 2)
        self.session.__exit__.assert_called_once()

    def test_only_exact_email_conflict_maps_to_account_exists(self) -> None:
        self.session.flush.side_effect = integrity()
        with self.assertRaises(AccountAlreadyExistsError) as caught:
            register(request())
        self.assertEqual(caught.exception.status, 409)
        self.assertEqual(caught.exception.code, "ACCOUNT_ALREADY_EXISTS")
        self.assertTrue(caught.exception.__suppress_context__)
        self.session.rollback.assert_called_once()
        self.session.commit.assert_not_called()

    def test_unrelated_integrity_errors_are_safe_failures(self) -> None:
        for table, constraint, state in (
            ("verifications", "uq_verifications_user_id_type", "23505"),
            ("verifications", "fk_verifications_user_id_users", "23503"),
            ("users", "pk_users", "23505"),
            ("other", "uq_users_email", "23505"),
            ("users", "uq_users_email", "23503"),
            (None, None, "23505"),
        ):
            self.session.flush.side_effect = integrity(
                table, constraint, state)
            with self.assertRaises(PostgresOperationError) as caught:
                register(request())
            self.assertEqual(caught.exception.status, 500)
            self.assertNotIn("synthetic-private", str(caught.exception))
            self.assertTrue(caught.exception.__suppress_context__)

    def test_flush_and_commit_failures_rollback_and_close(self) -> None:
        for stage in ("user", "verification", "commit"):
            self.session.reset_mock()
            self.session.flush.side_effect = (
                SQLAlchemyError("synthetic-private") if stage == "user" else
                [None, SQLAlchemyError("synthetic-private")] if stage == "verification" else None)
            self.session.commit.side_effect = SQLAlchemyError(
                "synthetic-private") if stage == "commit" else None
            with self.assertRaises(PostgresOperationError):
                register(request())
            self.session.rollback.assert_called_once()
            self.session.__exit__.assert_called_once()
            self.assertEqual(self.session.commit.call_count,
                             int(stage == "commit"))

    def test_primitive_failures_do_not_open_transaction(self) -> None:
        for primitive in (self.Password.return_value.hash, self.generate):
            primitive.side_effect = CredentialError()
            with self.assertRaises(CredentialError):
                register(request())
            self.postgres.assert_not_called()
            primitive.side_effect = None

    def test_driver_failure_through_http_does_not_leak_or_log_credentials(self) -> None:
        plaintext = secrets.token_urlsafe(24)
        encoded = self.Password.return_value.hash.return_value
        otp = self.generate.return_value
        self.session.flush.side_effect = [None, IntegrityError(
            "synthetic-private-sql", {"password": plaintext,
                                      "hash": encoded, "otp": otp},
            Exception(plaintext + encoded + otp))]
        with TestClient(application()) as client, self.assertNoLogs(level="WARNING"):
            response = client.post("/auth/register", json={
                "name": "Test", "email": "test@example.com", "password": plaintext})
        self.assertEqual(response.status_code, 500)
        for value in (plaintext, encoded, otp, "synthetic-private-sql"):
            self.assertNotIn(value, response.text)
        self.session.rollback.assert_called_once()


class RegistrationHttpTests(unittest.TestCase):
    """Verify actual routing, safe validation, and the exact credential-free API."""

    def setUp(self) -> None:
        self.client = TestClient(application())
        self.addCleanup(self.client.close)

    def test_exact_success_and_canonical_domain_input(self) -> None:
        plaintext = secrets.token_urlsafe(18)
        with patch("app.routers.auth.register") as domain:
            response = self.client.post("/auth/register", json={
                "name": " Test  Name ", "email": " Test@EXAMPLE.COM ", "password": plaintext})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"status": "verification_required"})
        self.assertNotIn("set-cookie", response.headers)
        value = domain.call_args.args[0]
        self.assertEqual(value.name, "Test  Name")
        self.assertEqual(value.email, "test@example.com")
        self.assertTrue(value.password.get_secret_value() == plaintext)

    def test_duplicate_response_never_includes_verification_state(self) -> None:
        bodies = []
        for email in ("TEST@example.com", " test@EXAMPLE.COM "):
            with patch("app.routers.auth.register", side_effect=AccountAlreadyExistsError()):
                response = self.client.post("/auth/register", json={
                    "name": "Test", "email": email, "password": secrets.token_urlsafe(18)})
            self.assertEqual(response.status_code, 409)
            self.assertNotIn("set-cookie", response.headers)
            bodies.append(response.json())
        self.assertEqual(bodies, [
                         {"error": "Account already exists", "code": "ACCOUNT_ALREADY_EXISTS"}] * 2)

    def test_validation_never_echoes_input_or_logs_credentials(self) -> None:
        sentinel = secrets.token_urlsafe(24)
        valid = {"name": "Test", "email": "test@example.com",
                 "password": sentinel}
        cases = [
            {**valid, "password": sentinel * 6}, {**valid, "email": sentinel},
            {**valid, "name": sentinel * 6}, {**valid, sentinel: sentinel},
            {"name": "Test", "password": sentinel}, [valid], None,
        ]
        with patch("app.routers.auth.register") as domain, self.assertNoLogs(level="WARNING"):
            for value in cases:
                response = self.client.post(
                    "/auth/register", content=json.dumps(value), headers={"Content-Type": "application/json"})
                self.assertEqual(response.status_code, 422)
                self.assertNotIn(sentinel, response.text)
                self.assertEqual(
                    response.json()["code"], "UNPROCESSABLE_ENTITY")
            response = self.client.post(
                "/auth/register", content='{"password":"' + sentinel, headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(sentinel, response.text)
        domain.assert_not_called()

    def test_database_failure_is_structured_and_not_logged_raw(self) -> None:
        with patch("app.routers.auth.register", side_effect=PostgresOperationError()), self.assertNoLogs(level="WARNING"):
            response = self.client.post("/auth/register", json={
                "name": "Test", "email": "test@example.com", "password": secrets.token_urlsafe(18)})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
                         "error": "Unable to complete database operation", "code": "POSTGRES_OPERATION_FAILED"})

    def test_auth_inventory_and_registration_handler_is_sync(self) -> None:
        from app.main import app
        from app.routers.auth import registration

        routes = {(path, method.upper()) for path, operations in app.openapi()["paths"].items()
                  for method in operations if path.startswith("/auth")}
        self.assertEqual(routes, {("/auth/register", "POST"),
                                  ("/auth/verify", "POST"), ("/auth/resend", "POST"),
                                  ("/auth/login", "POST"), ("/auth/refresh", "POST"),
                                  ("/auth/logout", "POST")})
        self.assertFalse(inspect.iscoroutinefunction(registration))
