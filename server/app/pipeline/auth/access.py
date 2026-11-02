from jwt import PyJWT
from math import isfinite
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

from app.core.constants import constants

from app.schemas.constants import AuthConstants
from app.schemas.auth.access import AccessClaims

from app.errors.auth import CredentialError, InvalidAccessTokenError


class Access:
    """Issue and validate HS256 access credentials without resolving database users."""

    def __init__(self, config: AuthConstants | None = None) -> None:
        """Validate configuration lazily and enforce PyJWT's HMAC minimum as well."""
        self._config = config if config is not None else constants.auth
        self._codec = PyJWT(options={"enforce_minimum_key_length": True})

    def issue(self, user: UUID) -> str:
        """Issue the five approved claims, with a fresh UUID for each token."""
        try:
            issued = datetime.now(timezone.utc)
            return self._codec.encode(
                {"sub": str(user), "type": "access", "iat": issued,
                 "exp": issued + timedelta(seconds=self._config.AUTH_ACCESS_TOKEN_TTL_SECONDS),
                 "jti": str(uuid4())},
                self._config.AUTH_ACCESS_TOKEN_SECRET.get_secret_value(),
                algorithm="HS256",
            )
        except Exception:
            raise CredentialError() from None

    def decode(self, token: str) -> AccessClaims:
        """Return trusted claims only after signature, registered-claim and UUID checks."""
        try:
            claims = self._codec.decode(
                token, self._config.AUTH_ACCESS_TOKEN_SECRET.get_secret_value(),
                algorithms=["HS256"],
                options={"require": ["sub", "type", "iat", "exp", "jti"]},
            )
            if claims["type"] != "access":
                raise ValueError

            for name in ("iat", "exp"):
                value = claims[name]
                if type(value) not in (int, float) or not isfinite(value):
                    raise ValueError

            return AccessClaims(
                user=UUID(claims["sub"]), jti=UUID(claims["jti"]),
                issued=datetime.fromtimestamp(claims["iat"], timezone.utc),
                expires=datetime.fromtimestamp(claims["exp"], timezone.utc),
            )
        except Exception:
            raise InvalidAccessTokenError() from None
