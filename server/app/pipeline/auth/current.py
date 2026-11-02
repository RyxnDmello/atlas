from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import postgres

from app.models.postgres.user import User
from app.pipeline.auth.access import Access

from app.errors.auth import InvalidAccessTokenError
from app.errors.postgres import PostgresOperationError


def current(request: Request) -> User:
    """Resolve a literal Bearer credential to a canonical verified user, without session state."""
    authorization = request.headers.get("Authorization")
    if authorization is None:
        raise InvalidAccessTokenError()

    scheme, separator, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not separator or not token.strip():
        raise InvalidAccessTokenError()

    claims = Access().decode(token)

    try:
        with postgres().session() as session:
            user = session.get(User, claims.user)
            if user is None or user.verified_at is None:
                raise InvalidAccessTokenError()

            return user
    except SQLAlchemyError:
        raise PostgresOperationError() from None
