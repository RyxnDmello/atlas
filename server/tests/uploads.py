"""Local upload fixtures; SQLite and test credentials never imply real PostgreSQL acceptance."""
import os
import secrets
from uuid import uuid4
from collections.abc import Iterator
from datetime import datetime, timezone
from contextlib import contextmanager, ExitStack

from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event

from app.db.postgres import Database

from app.models.postgres import Base, User

from app.pipeline.auth.access import Access


@contextmanager
def environment() -> Iterator[tuple[Database, User, dict[str, str]]]:
    """Provide real local SQLAlchemy sessions, a verified user and ephemeral Bearer headers."""
    from unittest.mock import patch
    with ExitStack() as scope:
        scope.enter_context(patch.dict(
            os.environ, {"AUTH_ACCESS_TOKEN_SECRET": secrets.token_urlsafe(48)}))
        engine = create_engine("sqlite://", poolclass=StaticPool,
                               connect_args={"check_same_thread": False}, hide_parameters=True)
        scope.callback(engine.dispose)

        @event.listens_for(engine, "connect")
        def constraints(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(engine)
        database = Database(engine, sessionmaker(bind=engine))
        now = datetime.now(timezone.utc)
        user = User(id=uuid4(), name="Synthetic", email="upload@example.invalid",
                    password="synthetic-placeholder", verified_at=now, created_at=now, updated_at=now)
        with database.session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            session.expunge(user)
        for target in ("app.pipeline.upload.postgres", "app.pipeline.auth.current.postgres"):
            scope.enter_context(patch(target, return_value=database))

        yield database, user, {"Authorization": "Bearer " + Access().issue(user.id)}
