from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import postgres

from app.pipeline.auth.password import Password
from app.pipeline.auth.initial_session import Credentials, issue

from app.schemas.auth.login import LoginRequest
from app.schemas.auth.authenticated import AuthenticatedUser

from app.models.postgres import User

from app.errors.postgres import PostgresOperationError
from app.errors.auth import InvalidCredentialsError, VerificationRequiredError


@dataclass(frozen=True, slots=True)
class LoggedIn:
    user: AuthenticatedUser
    credentials: Credentials


def login(request: LoginRequest) -> LoggedIn:
    """Commit optional password rehash and an independent session atomically."""
    try:
        with postgres().session() as session:
            user = session.scalars(select(User).where(
                User.email == request.email).with_for_update()).one_or_none()
            if user is None:
                raise InvalidCredentialsError()

            password = Password()
            supplied = request.password.get_secret_value()
            if not password.verify(user.password, supplied):
                raise InvalidCredentialsError()
            if user.verified_at is None:
                raise VerificationRequiredError()

            now = datetime.now(timezone.utc)
            if password.needs_rehash(user.password):
                user.password = password.hash(supplied)
                user.updated_at = now
            credentials = issue(session, user, now)
            public = AuthenticatedUser(
                id=user.id, name=user.name, email=user.email)
            session.commit()

            return LoggedIn(user=public, credentials=credentials)
    except SQLAlchemyError:
        raise PostgresOperationError() from None
