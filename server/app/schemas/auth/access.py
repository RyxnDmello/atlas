from uuid import UUID
from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AccessClaims:
    """Carry verified access identity and timezone-aware UTC timestamps."""

    user: UUID
    jti: UUID
    issued: datetime
    expires: datetime
