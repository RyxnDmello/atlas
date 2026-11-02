from collections.abc import Iterator
from contextlib import contextmanager

from app.db.postgres import Database

from app.pipeline.storage import Storage

from app.errors.api import ApiError

_storage: Storage | None = None
_postgres: Database | None = None


@contextmanager
def activate(storage: Storage, postgres: Database) -> Iterator[None]:
    """Publish both lifespan-owned datastores and restore the prior runtime scope."""
    global _storage, _postgres

    previous = _storage, _postgres
    _storage = storage
    _postgres = postgres

    try:
        yield
    finally:
        _storage, _postgres = previous


def postgres() -> Database:
    """Return the lifespan-owned database without constructing an engine or Session."""
    if _postgres is None:
        raise ApiError("PostgreSQL is not initialized",
                       "INTERNAL_SERVER_ERROR")

    return _postgres


def storage() -> Storage:
    """Return ready services without constructing a model or collection."""
    if _storage is None:
        raise ApiError("Upload storage is not initialized",
                       "INTERNAL_SERVER_ERROR")

    return _storage
