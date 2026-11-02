"""Opt-in synthetic primitive smoke; print safe metadata only."""
import json
import secrets
from uuid import uuid4

from app.pipeline.auth.access import Access
from app.pipeline.auth.password import Password
from app.pipeline.auth import refresh, verification

from app.schemas.constants import AuthConstants


def run() -> dict[str, object]:
    """Exercise credentials without databases, network calls, or persisted secrets."""
    password = Password()
    plain = secrets.token_urlsafe(24)
    encoded = password.hash(plain)
    verified = password.verify(encoded, plain)
    access = Access(AuthConstants.model_validate({
        "AUTH_ACCESS_TOKEN_SECRET": secrets.token_urlsafe(48)}))
    user = uuid4()
    trusted = access.decode(access.issue(user))
    token = refresh.generate()
    digest = refresh.digest(token)
    otp = verification.generate()
    assert encoded.startswith(
        "$argon2id$") and verified and trusted.user == user
    assert len(token) == 64 and len(digest) == 64 and len(
        otp) == 6 and otp.isascii() and otp.isdigit()

    return {"password_algorithm": "argon2id", "password_verified": verified,
            "access_algorithm": "HS256", "access_claims_valid": trusted.user == user,
            "refresh_token_chars": len(token), "refresh_hash_chars": len(digest), "otp_chars": len(otp)}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
