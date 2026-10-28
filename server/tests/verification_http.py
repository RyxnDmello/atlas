"""Opt-in live API acceptance; clean up only generated synthetic accounts."""

import sys
import json
import secrets
from uuid import uuid4

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, delete, select

from app.core.constants import constants

from app.db.postgres import Database, url
from app.models.postgres import User, Verification, Session

from app.pipeline.auth.access import Access
from app.pipeline.auth.refresh import digest

from tests.registration_http import request


def main() -> None:
    """Prove register, resend, verify, cookie and persistence over packaged HTTP."""
    engine = create_engine(url(constants.postgres), hide_parameters=True)
    database = Database(engine, sessionmaker(bind=engine))
    emails = ["verification-http-" +
              uuid4().hex + "@example.com" for _ in range(2)]
    try:
        for index, email in enumerate(emails):
            status, body, headers = request("/auth/register", {
                "name": "Synthetic", "email": email,
                "password": secrets.token_urlsafe(24),
            }, "POST")
            assert status == 201 and body == {
                "status": "verification_required"}
            assert "set-cookie" not in headers

            with database.session() as session:
                user = session.scalar(select(User).where(User.email == email))
                assert user is not None
                row = session.scalar(select(Verification).where(
                    Verification.user_id == user.id, Verification.type == "auth"))
                assert row is not None
                prior = row.otp

            if index == 1:
                status, body, headers = request(
                    "/auth/resend", {"email": email}, "POST")
                assert status == 200 and body == {
                    "status": "verification_required"}
                assert "set-cookie" not in headers
                status, body, headers = request("/auth/verify", {
                    "email": email, "otp": prior}, "POST")
                assert status == 400 and body["code"] == "INVALID_VERIFICATION"
                assert "set-cookie" not in headers

            with database.session() as session:
                user = session.scalar(select(User).where(User.email == email))
                assert user is not None
                row = session.scalar(select(Verification).where(
                    Verification.user_id == user.id, Verification.type == "auth"))
                assert row is not None
                if index == 1:
                    assert row.otp != prior
                    assert (
                        row.expires_at - row.created_at).total_seconds() == constants.otp.AUTH_OTP_TTL_SECONDS
                current = row.otp

            status, body, headers = request("/auth/verify", {
                "email": email, "otp": current}, "POST")
            assert status == 200 and set(
                body) == {"access_token", "token_type", "user"}
            assert body["token_type"] == "bearer"
            assert set(body["user"]) == {"id", "name", "email"}
            assert body["user"]["email"] == email
            assert Access().decode(body["access_token"]).user == user.id
            cookie = headers["set-cookie"]
            for attribute in ("atlas_refresh=", "HttpOnly", "Path=/auth", "SameSite=lax",
                              f"Max-Age={constants.refresh.AUTH_REFRESH_TOKEN_TTL_SECONDS}"):
                assert attribute.lower() in cookie.lower()
            assert ("secure" in cookie.lower()
                    ) == constants.refresh.AUTH_COOKIE_SECURE
            refresh = cookie.split("atlas_refresh=", 1)[1].split(";", 1)[0]
            assert refresh not in json.dumps(body)

            with database.session() as session:
                user = session.scalar(select(User).where(User.email == email))
                assert user is not None and user.verified_at is not None
                assert session.scalar(select(Verification).where(
                    Verification.user_id == user.id, Verification.type == "auth")) is None
                rows = session.scalars(select(Session).where(
                    Session.user_id == user.id)).all()
                assert len(rows) == 1 and rows[0].token_hash == digest(refresh)
                assert rows[0].token_hash != refresh

            status, body, headers = request("/auth/verify", {
                "email": email, "otp": current}, "POST")
            assert status == 409 and body["code"] == "VERIFICATION_NOT_REQUIRED"
            assert "set-cookie" not in headers
            status, body, headers = request(
                "/auth/resend", {"email": email}, "POST")
            assert status == 409 and body["code"] == "VERIFICATION_NOT_REQUIRED"
            assert "set-cookie" not in headers

        absent = uuid4().hex + "@example.com"
        for path, payload in (("/auth/verify", {"email": absent, "otp": "012345"}),
                              ("/auth/resend", {"email": absent})):
            status, body, headers = request(path, payload, "POST")
            assert status == 404 and body["code"] == "ACCOUNT_NOT_FOUND"
            assert "set-cookie" not in headers

        print(json.dumps({"live_http": "passed", "register_verify": "passed",
                          "resend_old_otp": "rejected", "resend_new_otp": "accepted",
                          "hashed_session": "passed", "cleanup": "synthetic_only"}))
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
        print(json.dumps({"verification_http": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
