"""Opt-in acceptance against the running API; remove only its synthetic user."""
import sys
import json
import secrets
import traceback
import subprocess
from typing import Any
from uuid import uuid4
from urllib.error import HTTPError
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, delete, select

from app.core.constants import constants
from app.pipeline.auth.password import Password

from app.db.postgres import Database, url
from app.models.postgres import User, Verification, Session


def request(path: str, payload: object = None, method: str = "GET",
            headers: dict[str, str] | None = None) -> tuple[int, Any, dict[str, str]]:
    """Keep HTTP error bodies available for assertions without printing input."""
    data = None if payload is None else json.dumps(payload).encode()
    message = Request(f"http://127.0.0.1:{constants.app.PORT}{path}", data=data,
                      method=method, headers={"Content-Type": "application/json", **(headers or {})})
    try:
        response = urlopen(message, timeout=30)
    except HTTPError as error:
        response = error

    with response:
        body = response.read()
        status = response.status
        assert isinstance(status, int)
        metadata = {name.lower(): value for name,
                    value in response.headers.items()}
        return status, json.loads(body) if body and method != "OPTIONS" else None, metadata


def main() -> None:
    """Verify live persistence, duplicate safety, validation, CORS, and cleanup."""
    engine = create_engine(url(constants.postgres), hide_parameters=True)
    database = Database(engine, sessionmaker(bind=engine))
    email = "http-acceptance-" + uuid4().hex + "@example.com"
    plaintext = secrets.token_urlsafe(32)
    payload = {"name": "  HTTP  Acceptance  ", "email": " " + email.upper() + " ",
               "password": plaintext}
    identifier = None
    try:
        before = datetime.now(timezone.utc)
        status, body, headers = request("/auth/register", payload, "POST")
        assert status == 201 and body == {"status": "verification_required"}
        assert "set-cookie" not in headers
        with database.session() as session:
            user = session.scalars(
                select(User).where(User.email == email)).one()
            identifier = user.id
            verification = session.scalars(select(Verification).where(
                Verification.user_id == identifier)).one()
            assert user.email == email and user.name == "HTTP  Acceptance"
            assert user.verified_at is None and user.password.startswith(
                "$argon2id$")
            assert Password().verify(user.password, plaintext)
            assert verification.type == "auth"
            assert len(verification.otp) == 6 and verification.otp.isascii(
            ) and verification.otp.isdigit()
            assert user.created_at == user.updated_at == verification.created_at
            assert before <= user.created_at <= datetime.now(timezone.utc)
            assert (verification.expires_at -
                    verification.created_at).total_seconds() == constants.otp.AUTH_OTP_TTL_SECONDS
            assert session.scalars(select(Session).where(
                Session.user_id == identifier)).first() is None
            original = (user.password, user.created_at, user.updated_at,
                        verification.id, verification.otp, verification.expires_at)

        for verified in (False, True):
            if verified:
                with database.session() as session:
                    user = session.get(User, identifier)
                    assert user is not None
                    user.verified_at = datetime.now(timezone.utc)
                    session.commit()

            status, body, headers = request("/auth/register", payload, "POST")
            assert status == 409 and body == {
                "error": "Account already exists", "code": "ACCOUNT_ALREADY_EXISTS"}
            assert "set-cookie" not in headers
            with database.session() as session:
                user = session.get(User, identifier)
                assert user is not None and (
                    user.verified_at is not None) == verified
                verification = session.scalars(select(Verification).where(
                    Verification.user_id == identifier)).one()
                assert original == (user.password, user.created_at, user.updated_at,
                                    verification.id, verification.otp, verification.expires_at)

        for invalid in ({**payload, "password": "short"}, {**payload, "unexpected": plaintext},
                        {**payload, "email": "invalid"}, {**payload, "name": " "}):
            status, body, headers = request("/auth/register", invalid, "POST")
            assert status == 422 and body == {
                "error": "Invalid registration input", "code": "UNPROCESSABLE_ENTITY"}
            assert "set-cookie" not in headers

        origins = constants.cors.CORS_ORIGINS
        denied = "https://unapproved-" + uuid4().hex + ".example"
        for origin in [*origins, denied]:
            status, _, headers = request("/auth/register", method="OPTIONS", headers={
                "Origin": origin, "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"})
            assert status == (200 if origin in origins else 400)
            assert headers.get(
                "access-control-allow-origin") == (origin if origin in origins else None)
            assert headers.get("access-control-allow-credentials") == "true"

        status, body, _ = request("/openapi.json")
        assert status == 200 and isinstance(body, dict)
        assert {path for path in body["paths"] if path.startswith(
            "/auth")} == {"/auth/register", "/auth/verify", "/auth/resend", "/auth/login", "/auth/refresh", "/auth/logout", "/auth"}
        assert set(body["paths"]["/auth/register"]) == {"post"}
        assert {"/files", "/files/{file_id}/ask", "/files/{file_id}/query",
                "/system/health", "/system/health/databases"} <= set(body["paths"])
        logs = subprocess.run(["docker", "compose", "--env-file", ".env", "-f",
                               "docker-compose.yml", "logs", "--no-color", "server"],
                              capture_output=True, text=True, check=True)
        assert plaintext not in logs.stdout + \
            logs.stderr, "Synthetic password appeared in API logs"
        print(json.dumps({"live_http": "passed", "stored_state": "passed",
                          "verified_unverified_conflicts": "passed", "invalid_cases": 4,
                          "cors": "passed", "route_inventory": "passed", "password_log_scan": "passed"}))
    finally:
        try:
            with database.session() as session:
                session.execute(delete(User).where(User.email == email))
                session.commit()
                assert session.scalars(select(User).where(
                    User.email == email)).first() is None
                if identifier is not None:
                    assert session.scalars(select(Verification).where(
                        Verification.user_id == identifier)).first() is None
                    assert session.scalars(select(Session).where(
                        Session.user_id == identifier)).first() is None
        finally:
            database.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"registration_http": "failed", "category": type(error).__name__,
                          "line": traceback.extract_tb(error.__traceback__)[-1].lineno,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
