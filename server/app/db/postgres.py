from dataclasses import dataclass
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import Engine, URL, create_engine, text

from app.core.logging import logger
from app.core.constants import constants, _Postgres

from app.errors.postgres import PostgresConnectionError


def url(config: _Postgres) -> URL:
    """Build a driver URL from literal credentials without manual URL escaping."""
    return URL.create(
        "postgresql+psycopg",
        username=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD.get_secret_value(),
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        database=config.POSTGRES_DB,
    )


@dataclass
class Database:
    """Own one lifespan's engine and reusable factory, never a shared Session."""

    engine: Engine
    sessions: sessionmaker[Session]

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Close each operation's Session; callers explicitly commit successful work."""
        with self.sessions() as session:
            try:
                yield session
            except BaseException:
                session.rollback()
                raise

    def check(self) -> str:
        """Probe connectivity and version using read-only SQL on the existing pool."""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

                return str(connection.execute(text("SHOW server_version")).scalar_one())
        except Exception:
            raise PostgresConnectionError() from None

    def close(self) -> None:
        """Release the lifespan-owned pool after operation Sessions have closed."""
        self.engine.dispose()
        logger.info("PostgreSQL runtime closed")


def prepare() -> Database:
    """Construct and probe one engine, disposing it if preparation fails."""
    engine = None

    try:
        engine = create_engine(
            url(constants.postgres), pool_pre_ping=True, hide_parameters=True,
            connect_args={"connect_timeout": 5},
        )
        database = Database(engine, sessionmaker(bind=engine))
        version = database.check()
    except Exception:
        if engine is not None:
            engine.dispose()

        raise PostgresConnectionError() from None

    logger.info("PostgreSQL runtime prepared: version=%s", version)

    return database
