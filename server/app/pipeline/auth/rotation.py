from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import postgres

from app.pipeline.auth.refresh import digest
from app.pipeline.auth.initial_session import Credentials, issue

from app.models.postgres import Session, User
from app.schemas.auth.authenticated import AuthenticatedUser

from app.errors.postgres import PostgresOperationError
from app.errors.auth import CredentialError, InvalidRefreshTokenError


@dataclass(frozen=True, slots=True)
class Refreshed:
    user: AuthenticatedUser
    credentials: Credentials


def refresh(token: str | None) -> Refreshed:
    """Consume and replace one session atomically; invalid requests never issue cookies."""
    if token is None or not token.strip():
        raise InvalidRefreshTokenError()

    hashed = digest(token)
    now = datetime.now(timezone.utc)
    try:
        with postgres().session() as session:
            consumed = session.execute(delete(Session).where(
                Session.token_hash == hashed, Session.expires_at > now
            ).returning(Session.id, Session.user_id)).one_or_none()
            if consumed is None:
                expired = session.execute(delete(Session).where(
                    Session.token_hash == hashed, Session.expires_at <= now
                ).returning(Session.id)).scalar_one_or_none()
                if expired is not None:
                    session.commit()

                raise InvalidRefreshTokenError()

            user = session.get(User, consumed.user_id)
            if user is None or user.verified_at is None:
                raise CredentialError()

            credentials = issue(session, user, now)
            public = AuthenticatedUser(
                id=user.id, name=user.name, email=user.email)
            session.commit()

            return Refreshed(user=public, credentials=credentials)
    except SQLAlchemyError:
        raise PostgresOperationError() from None
