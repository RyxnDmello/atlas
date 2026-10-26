from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.core.constants import constants

from app.db.postgres import url

from app.models.postgres import Base

from app.errors.postgres import PostgresConnectionError

target_metadata = Base.metadata


def offline() -> None:
    """Render migration SQL without connecting or embedding credentials in output."""
    context.configure(
        dialect_name="postgresql", target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def online() -> None:
    """Run explicit migrations with literal credentials and no ConfigParser URL."""
    engine = create_engine(
        url(constants.postgres), poolclass=NullPool, hide_parameters=True,
        connect_args={"connect_timeout": 5},
    )

    try:
        try:
            connection = engine.connect()
        except Exception:
            raise PostgresConnectionError() from None

        with connection:
            context.configure(connection=connection,
                              target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    offline()
else:
    online()
