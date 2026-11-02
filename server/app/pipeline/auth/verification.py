import secrets

from app.errors.auth import CredentialError


def generate() -> str:
    """Generate six ASCII digits, preserving leading zeroes, without persistence."""
    try:
        return f"{secrets.randbelow(1_000_000):06d}"
    except Exception:
        raise CredentialError() from None
