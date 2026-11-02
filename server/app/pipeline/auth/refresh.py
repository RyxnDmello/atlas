import hashlib
import secrets

from app.errors.auth import CredentialError


def generate() -> str:
    """Generate an opaque refresh credential from exactly 48 random bytes."""
    try:
        return secrets.token_urlsafe(48)
    except Exception:
        raise CredentialError() from None


def digest(token: str) -> str:
    """Return the lowercase SHA-256 key used by sessions.token_hash."""
    if not token.strip():
        raise ValueError("Refresh credential must be nonblank")

    try:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
    except Exception:
        raise CredentialError() from None
