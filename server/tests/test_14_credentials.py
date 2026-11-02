import os
import jwt
import secrets
import hashlib
import unittest

from typing import Any
from pathlib import Path
from uuid import UUID, uuid4
from unittest.mock import patch
from dotenv import dotenv_values
from argon2 import PasswordHasher
from pydantic import ValidationError
from argon2.exceptions import HashingError
from datetime import datetime, timedelta, timezone

from app.core.constants import Constants

from app.pipeline.auth.access import Access
from app.pipeline.auth.password import Password
from app.pipeline.auth import refresh, verification

from app.schemas.constants import AuthConstants
from app.schemas.auth.access import AccessClaims

from app.errors.auth import CredentialError, InvalidAccessTokenError


def config(**values: object) -> AuthConstants:
    """Create isolated synthetic settings without reading or printing local secrets."""
    return AuthConstants.model_validate({
        "AUTH_ACCESS_TOKEN_SECRET": secrets.token_urlsafe(48), **values})


class AuthConfigurationTests(unittest.TestCase):
    """Prove lazy validation and byte-based secret constraints."""

    def setUp(self) -> None:
        values = {name: value for name, value in dotenv_values(
            Path(__file__).resolve().parents[1] / ".env.example").items() if value is not None}
        values["AUTH_ACCESS_TOKEN_SECRET"] = secrets.token_urlsafe(48)
        scope = patch.dict(os.environ, values, clear=True)
        scope.start()
        self.addCleanup(scope.stop)

    def test_secret_absent_until_access_is_prepared(self) -> None:
        os.environ.pop("AUTH_ACCESS_TOKEN_SECRET")
        Constants()
        with self.assertRaisesRegex(ValueError, "Invalid access-token configuration"):
            Access()

    def test_invalid_settings_do_not_break_unrelated_configuration(self) -> None:
        for value in ("", " " * 40, "short"):
            with self.subTest(case=len(value)), patch.dict(os.environ, {"AUTH_ACCESS_TOKEN_SECRET": value}):
                Constants()
                with self.assertRaises(ValueError):
                    Access()

    def test_utf8_byte_length_and_redaction(self) -> None:
        for value in ("a" * 32, "é" * 16):
            settings = config(AUTH_ACCESS_TOKEN_SECRET=value)
            self.assertNotIn(value, str(settings))
            self.assertNotIn(value, settings.model_dump_json())
            Access(settings)

        for value in ("a" * 31, "é" * 15):
            with self.assertRaises(ValidationError) as caught:
                config(AUTH_ACCESS_TOKEN_SECRET=value)

            self.assertNotIn(value, str(caught.exception))

    def test_ttl_default_override_and_rejection(self) -> None:
        self.assertEqual(config().AUTH_ACCESS_TOKEN_TTL_SECONDS, 900)
        self.assertEqual(
            config(AUTH_ACCESS_TOKEN_TTL_SECONDS="123").AUTH_ACCESS_TOKEN_TTL_SECONDS, 123)
        for value in (0, -1, "invalid", None):
            with self.subTest(case=str(value)), self.assertRaises(ValidationError):
                config(AUTH_ACCESS_TOKEN_TTL_SECONDS=value)

    def test_loader_uses_default_and_positive_override(self) -> None:
        os.environ.pop("AUTH_ACCESS_TOKEN_TTL_SECONDS")
        self.assertEqual(Constants().auth.AUTH_ACCESS_TOKEN_TTL_SECONDS, 900)
        os.environ["AUTH_ACCESS_TOKEN_TTL_SECONDS"] = "55"
        self.assertEqual(Constants().auth.AUTH_ACCESS_TOKEN_TTL_SECONDS, 55)
        for value in ("0", "-1", "invalid"):
            os.environ["AUTH_ACCESS_TOKEN_TTL_SECONDS"] = value
            with self.assertRaises(ValueError):
                Access()

    def test_loader_errors_hide_secret(self) -> None:
        sentinel = secrets.token_urlsafe(48)
        os.environ.update(AUTH_ACCESS_TOKEN_SECRET=sentinel,
                          AUTH_ACCESS_TOKEN_TTL_SECONDS="invalid")
        with self.assertRaises(ValueError) as caught:
            Access()

        self.assertNotIn(sentinel, str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)


class PasswordTests(unittest.TestCase):
    """Exercise real Argon2 defaults and sanitized operational failures."""

    def setUp(self) -> None:
        self.password = Password()
        self.plaintext = secrets.token_urlsafe(24)

    def test_argon2id_random_salts_and_verification(self) -> None:
        first = self.password.hash(self.plaintext)
        second = self.password.hash(self.plaintext)
        self.assertTrue(first.startswith("$argon2id$"))
        self.assertTrue(second.startswith("$argon2id$"))
        self.assertFalse(first == second)
        self.assertTrue(self.password.verify(first, self.plaintext))
        self.assertTrue(self.password.verify(second, self.plaintext))
        self.assertFalse(self.password.needs_rehash(first))
        self.assertFalse(self.password.verify(
            first, secrets.token_urlsafe(24)))

    def test_malformed_hash_is_internal_failure(self) -> None:
        for value in ("", "invalid", "$argon2id$invalid", "$unsupported$"):
            with self.subTest(case=len(value)), self.assertRaises(CredentialError):
                self.password.verify(value, self.plaintext)

        with self.assertRaises(CredentialError):
            self.password.needs_rehash("invalid")

    def test_rehash_decision_delegates(self) -> None:
        for expected in (False, True):
            with patch.object(PasswordHasher, "check_needs_rehash", return_value=expected) as check:
                self.assertEqual(self.password.needs_rehash(
                    "synthetic-encoded"), expected)
                check.assert_called_once_with("synthetic-encoded")

    def test_library_failures_are_sanitized(self) -> None:
        sentinel = secrets.token_urlsafe(48)
        for method, call in (("hash", lambda: self.password.hash(self.plaintext)),
                             ("verify", lambda: self.password.verify(
                                 "encoded", self.plaintext)),
                             ("check_needs_rehash", lambda: self.password.needs_rehash("encoded"))):
            with patch.object(PasswordHasher, method, side_effect=HashingError(sentinel)):
                with self.assertRaises(CredentialError) as caught:
                    call()

            self.assertEqual(caught.exception.code, "INTERNAL_SERVER_ERROR")
            self.assertNotIn(sentinel, str(caught.exception.to_dict()))
            self.assertTrue(caught.exception.__suppress_context__)

    def test_constructor_failure_is_sanitized(self) -> None:
        with patch("app.pipeline.auth.password.PasswordHasher", side_effect=RuntimeError("private")):
            with self.assertRaises(CredentialError):
                Password()


class AccessTests(unittest.TestCase):
    """Verify real signatures and all token rejection categories."""

    def setUp(self) -> None:
        self.config = config(AUTH_ACCESS_TOKEN_TTL_SECONDS=120)
        self.access = Access(self.config)
        self.key = self.config.AUTH_ACCESS_TOKEN_SECRET.get_secret_value()
        self.user = uuid4()
        issued = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.claims: dict[str, Any] = {
            "sub": str(self.user), "type": "access", "iat": int(issued.timestamp()),
            "exp": int((issued + timedelta(seconds=120)).timestamp()), "jti": str(uuid4())}

    def reject(self, token: str) -> None:
        with self.assertRaises(InvalidAccessTokenError) as caught:
            self.access.decode(token)

        self.assertEqual(caught.exception.to_dict(), {
            "error": "Invalid access token", "code": "INVALID_ACCESS_TOKEN"})
        self.assertEqual(caught.exception.status, 401)
        self.assertTrue(caught.exception.__suppress_context__)

    def test_exact_claims_and_typed_roundtrip(self) -> None:
        token = self.access.issue(self.user)
        payload = jwt.decode(token, self.key, algorithms=["HS256"])
        self.assertEqual(set(payload), {"sub", "type", "iat", "exp", "jti"})
        self.assertEqual(payload["sub"], str(self.user))
        self.assertEqual(payload["type"], "access")
        self.assertEqual(payload["exp"] - payload["iat"], 120)
        self.assertIsInstance(UUID(payload["jti"]), UUID)
        self.assertEqual(jwt.get_unverified_header(token)["alg"], "HS256")
        trusted = self.access.decode(token)
        self.assertIsInstance(trusted, AccessClaims)
        self.assertEqual(trusted.user, self.user)
        self.assertEqual(trusted.jti, UUID(payload["jti"]))
        self.assertEqual(trusted.issued.tzinfo, timezone.utc)
        self.assertEqual(trusted.expires - trusted.issued,
                         timedelta(seconds=120))
        other = self.access.decode(self.access.issue(self.user))
        self.assertNotEqual(trusted.jti, other.jti)

    def test_missing_each_required_claim(self) -> None:
        for name in self.claims:
            payload = {key: value for key,
                       value in self.claims.items() if key != name}
            with self.subTest(claim=name):
                self.reject(jwt.encode(payload, self.key, algorithm="HS256"))

    def test_expired_wrong_type_and_invalid_uuids(self) -> None:
        for name, value in (("exp", 1), ("type", "refresh"), ("sub", "invalid"),
                            ("jti", "invalid"), ("sub", 5), ("jti", [])):
            with self.subTest(claim=name):
                self.reject(jwt.encode(
                    {**self.claims, name: value}, self.key, algorithm="HS256"))

    def test_invalid_temporal_claims(self) -> None:
        for name in ("iat", "exp"):
            for value in ("invalid", None, [], True, float("nan"), float("inf")):
                with self.subTest(claim=name, kind=type(value).__name__):
                    self.reject(jwt.encode(
                        {**self.claims, name: value}, self.key, algorithm="HS256"))

        self.reject(jwt.encode(
            {**self.claims, "iat": self.claims["exp"] + 3600}, self.key, algorithm="HS256"))

    def test_wrong_secret_and_algorithm(self) -> None:
        self.reject(jwt.encode(
            self.claims, secrets.token_urlsafe(48), algorithm="HS256"))
        for algorithm in ("HS384", "HS512"):
            self.reject(jwt.encode(
                self.claims, secrets.token_urlsafe(96), algorithm=algorithm))

        self.reject(jwt.encode(self.claims, "", algorithm="none"))

    def test_tampered_and_malformed(self) -> None:
        token = self.access.issue(self.user)
        parts = token.split(".")
        parts[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
        self.reject(".".join(parts))
        for value in ("", "not-a-token", "a.b.c"):
            self.reject(value)

    def test_library_failure_and_issuance_failure_are_sanitized(self) -> None:
        with patch.object(jwt.PyJWT, "decode", side_effect=RuntimeError(self.key)):
            self.reject("synthetic")

        with patch.object(jwt.PyJWT, "encode", side_effect=RuntimeError(self.key)):
            with self.assertRaises(CredentialError) as caught:
                self.access.issue(self.user)

        self.assertNotIn(self.key, str(caught.exception.to_dict()))

    def test_minimum_key_enforcement_enabled(self) -> None:
        codec = self.access._codec
        with self.assertRaises(jwt.InvalidKeyError):
            codec.encode(self.claims, "short", algorithm="HS256")

        with self.assertRaises(jwt.InvalidKeyError):
            codec.decode(self.access.issue(self.user),
                         "short", algorithms=["HS256"])


class RefreshTests(unittest.TestCase):
    """Prove opaque entropy requests and exact future session-key representation."""

    def test_generator_requests_48_bytes(self) -> None:
        with patch("app.pipeline.auth.refresh.secrets.token_urlsafe", return_value="opaque") as source:
            self.assertEqual(refresh.generate(), "opaque")
            source.assert_called_once_with(48)

    def test_real_tokens_are_urlsafe_and_distinct(self) -> None:
        tokens = [refresh.generate() for _ in range(4)]
        self.assertEqual(len(set(tokens)), 4)
        for token in tokens:
            self.assertRegex(token, r"^[A-Za-z0-9_-]{64}$")

    def test_sha256_mapping_and_blank_rejection(self) -> None:
        token = "synthetic-é-refresh"
        result = refresh.digest(token)
        self.assertTrue(result == hashlib.sha256(
            token.encode("utf-8")).hexdigest())
        self.assertRegex(result, r"^[a-f0-9]{64}$")
        for value in ("", " \t\n"):
            with self.assertRaises(ValueError):
                refresh.digest(value)

    def test_random_source_failure_is_sanitized(self) -> None:
        with patch("app.pipeline.auth.refresh.secrets.token_urlsafe", side_effect=RuntimeError("private")):
            with self.assertRaises(CredentialError):
                refresh.generate()


class VerificationTests(unittest.TestCase):
    """Prove secure OTP bounds, ASCII formatting, and leading zero preservation."""

    def test_bound_and_leading_zeroes(self) -> None:
        for value, expected in ((0, "000000"), (1, "000001"), (999999, "999999")):
            with patch("app.pipeline.auth.verification.secrets.randbelow", return_value=value) as source:
                otp = verification.generate()
                self.assertTrue(otp == expected)
                self.assertRegex(otp, r"^[0-9]{6}$")
                source.assert_called_once_with(1_000_000)

    def test_random_source_failure_is_sanitized(self) -> None:
        with patch("app.pipeline.auth.verification.secrets.randbelow", side_effect=RuntimeError("private")):
            with self.assertRaises(CredentialError):
                verification.generate()


class CredentialLoggingTests(unittest.TestCase):
    """Observe successful credential work without emitting its sensitive values."""

    def test_primitives_emit_no_logs(self) -> None:
        with self.assertNoLogs(level="DEBUG"):
            password = Password()
            plain = secrets.token_urlsafe(24)
            encoded = password.hash(plain)
            password.verify(encoded, plain)
            password.needs_rehash(encoded)
            access = Access(config())
            access.decode(access.issue(uuid4()))
            refresh.digest(refresh.generate())
            verification.generate()
