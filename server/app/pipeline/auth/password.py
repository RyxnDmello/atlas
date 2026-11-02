from argon2.low_level import Type
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.errors.auth import CredentialError


class Password:
    """Wrap current Argon2id defaults without owning password policy or storage."""

    def __init__(self) -> None:
        try:
            self._hasher = PasswordHasher(type=Type.ID)
        except Exception:
            raise CredentialError() from None

    def hash(self, password: str) -> str:
        """Hash validated input using a fresh library-generated salt."""
        try:
            return self._hasher.hash(password)
        except Exception:
            raise CredentialError() from None

    def verify(self, encoded: str, password: str) -> bool:
        """Return False only for ordinary mismatch; fail safely for invalid hashes."""
        try:
            return self._hasher.verify(encoded, password)
        except VerifyMismatchError:
            return False
        except Exception:
            raise CredentialError() from None

    def needs_rehash(self, encoded: str) -> bool:
        """Compare stored parameters after successful verification; never persist."""
        try:
            return self._hasher.check_needs_rehash(encoded)
        except Exception:
            raise CredentialError() from None
