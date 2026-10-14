from collections.abc import Iterator
from contextlib import contextmanager

from app.pipeline.storage import Storage

from app.errors.api import ApiError

_storage: Storage | None = None


@contextmanager
def activate(storage: Storage) -> Iterator[None]:
    """Publish startup-ready storage for this lifespan and restore prior scope."""
    global _storage

    previous = _storage
    _storage = storage

    try:
        yield
    finally:
        _storage = previous


def storage() -> Storage:
    """Return ready services without constructing a model or collection."""
    if _storage is None:
        raise ApiError("Upload storage is not initialized",
                       "INTERNAL_SERVER_ERROR")

    return _storage
