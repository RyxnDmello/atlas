from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as OrmSession

from app.core.constants import constants
from app.models.postgres import Session, User

from app.pipeline.auth.access import Access
from app.pipeline.auth.refresh import digest, generate


@dataclass(frozen=True, slots=True)
class Credentials:
    """Transient credentials retained only until a committed HTTP response is built."""

    access: str
    refresh: str


def issue(session: OrmSession, user: User, now: datetime) -> Credentials:
    """Stage one hashed refresh session in the caller's transaction."""
    ttl = constants.refresh.AUTH_REFRESH_TOKEN_TTL_SECONDS
    access = Access().issue(user.id)
    refresh = generate()
    session.add(Session(
        user_id=user.id, token_hash=digest(refresh),
        created_at=now, expires_at=now + timedelta(seconds=ttl),
    ))

    return Credentials(access=access, refresh=refresh)
