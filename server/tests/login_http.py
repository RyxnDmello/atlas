"""Opt-in packaged HTTP acceptance; remove only generated synthetic accounts."""

import sys
import json
import secrets
import subprocess
from uuid import uuid4

from argon2 import PasswordHasher
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, delete, select

from app.core.constants import constants
from app.db.postgres import Database, url

from app.pipeline.auth.access import Access
from app.pipeline.auth.refresh import digest
from app.pipeline.auth.password import Password

from app.models.postgres import User, Verification

from tests.login_live import snapshot
from tests.registration_http import request


def authenticated(database: Database, email: str, body: dict, headers: dict[str, str],
                  total: int, private: list[str]) -> None:
    """Inspect returned credentials privately and verify exact cookie/persistence shape."""
    assert set(body) == {"access_token", "user"}
    assert set(body["user"]) == {"id", "name", "email"}
    assert body["user"]["email"] == email
    cookie = headers["set-cookie"]
    parts = cookie.split("; ")
    assert parts[0].startswith("atlas_refresh=")
    assert set(parts[1:]) == {"HttpOnly", "Path=/auth", "SameSite=lax",
                              f"Max-Age={constants.refresh.AUTH_REFRESH_TOKEN_TTL_SECONDS}"} | (
                                  {"Secure"} if constants.refresh.AUTH_COOKIE_SECURE else set())
    refresh = parts[0].removeprefix("atlas_refresh=")
    assert refresh not in json.dumps(body)
    state, _, sessions = snapshot(database, email)
    assert len(sessions) == total
    assert sum(row[1] == digest(refresh) for row in sessions) == 1
    assert all(row[1] != refresh for row in sessions)
    assert Access().decode(body["access_token"]).user == state[0]
    assert str(state[0]) == body["user"]["id"]
    private.extend([body["access_token"], refresh, digest(refresh), state[1]])


def main() -> None:
    """Prove login, rehash, verify compatibility and sanitized logs over live HTTP."""
    engine = create_engine(url(constants.postgres), hide_parameters=True)
    database = Database(engine, sessionmaker(bind=engine))
    emails = ["login-http-" + uuid4().hex + "@example.com" for _ in range(3)]
    passwords = [secrets.token_urlsafe(24) for _ in emails]
    private = passwords.copy()
    try:
        for email, password in zip(emails, passwords):
            status, body, headers = request("/auth/register", {
                "name": "Synthetic", "email": email, "password": password,
            }, "POST")
            assert status == 201 and body == {
                "status": "verification_required"}
            assert "set-cookie" not in headers

        email, password = emails[0], passwords[0]
        with database.session() as session:
            user = session.scalars(
                select(User).where(User.email == email)).one()
            row = session.scalars(select(Verification).where(
                Verification.user_id == user.id, Verification.type == "auth")).one()
            otp = row.otp
            private.extend([otp, user.password])
        status, body, headers = request(
            "/auth/verify", {"email": email, "otp": otp}, "POST")
        assert status == 200
        authenticated(database, email, body, headers, 1, private)
        assert snapshot(database, email)[1] == []

        invalid = []
        for identity, supplied in ((uuid4().hex + "@example.com", password),
                                   (email, password + "wrong"), (emails[1], passwords[1] + "wrong")):
            before = [snapshot(database, identity) for identity in emails]
            status, body, headers = request(
                "/auth/login", {"email": identity, "password": supplied}, "POST")
            invalid.append((status, body))
            assert "set-cookie" not in headers
            assert [snapshot(database, identity)
                    for identity in emails] == before
        assert invalid == [
            (401, {"error": "Invalid credentials", "code": "INVALID_CREDENTIALS"})] * 3

        for index in (1, 2):
            identity, supplied = emails[index], passwords[index]
            with database.session() as session:
                user = session.scalars(select(User).where(
                    User.email == identity)).one()
                user.password = PasswordHasher(
                    time_cost=1, memory_cost=1024, parallelism=1).hash(supplied)
                if index == 2:
                    session.execute(delete(Verification).where(
                        Verification.user_id == user.id))
                session.commit()
            before = snapshot(database, identity)
            assert Password().needs_rehash(before[0][1])
            private.append(before[0][1])
            private.extend(row[2] for row in before[1])
            status, body, headers = request(
                "/auth/login", {"email": identity, "password": supplied}, "POST")
            assert (status, body) == (
                403, {"error": "Verification required", "code": "VERIFICATION_REQUIRED"})
            assert "set-cookie" not in headers
            assert snapshot(database, identity) == before

        with database.session() as session:
            user = session.scalars(
                select(User).where(User.email == email)).one()
            user.password = PasswordHasher(
                time_cost=1, memory_cost=1024, parallelism=1).hash(password)
            session.commit()
        before = snapshot(database, email)
        private.append(before[0][1])
        assert Password().needs_rehash(before[0][1])
        status, body, headers = request(
            "/auth/login", {"email": " " + email.upper() + " ", "password": password}, "POST")
        assert status == 200
        authenticated(database, email, body, headers, 2, private)
        after = snapshot(database, email)
        assert after[0][1] != before[0][1]
        assert Password().verify(after[0][1], password)
        assert not Password().needs_rehash(after[0][1])
        assert all(row in after[2] for row in before[2])
        status, body, headers = request(
            "/auth/login", {"email": email, "password": password}, "POST")
        assert status == 200
        authenticated(database, email, body, headers, 3, private)
        assert snapshot(database, email)[0] == after[0]

        logs = subprocess.run(["docker", "compose", "--env-file", ".env", "-f",
                               "docker-compose.yml", "logs", "--no-color", "server"],
                              capture_output=True, text=True, check=True)
        assert not any(value in logs.stdout + logs.stderr for value in private)
        print(json.dumps({"live_login": "passed", "invalid_credentials": "identical",
                          "unverified_unchanged": "passed", "live_rehash": "passed",
                          "verify_response": "passed", "log_scan": "passed",
                          "cleanup": "synthetic_only"}, sort_keys=True))
    finally:
        try:
            with database.session() as session:
                session.execute(delete(User).where(User.email.in_(emails)))
                session.commit()
        finally:
            database.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"login_http": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
