from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import postgres

from app.pipeline.auth.refresh import digest

from app.models.postgres import Session

from app.errors.postgres import PostgresOperationError


def logout(token: str | None) -> None:
    """Delete only the presented session, including an expired one; absence is success."""
    if token is None or not token.strip():
        return

    hashed = digest(token)
    try:
        with postgres().session() as session:
            removed = session.execute(delete(Session).where(
                Session.token_hash == hashed).returning(Session.id)).scalar_one_or_none()
            if removed is not None:
                session.commit()
    except SQLAlchemyError:
        raise PostgresOperationError() from None
