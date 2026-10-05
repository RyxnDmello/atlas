from app.errors.api import ApiError


class QdrantConnectionError(ApiError):
    """Represent a failure to connect to or inspect Qdrant."""

    def __init__(self, message: str = "Qdrant connection failed") -> None:
        """Create a Qdrant connection failure.

        Args:
            message: A safe explanation of the connection failure.
        """
        super().__init__(message, "QDRANT_CONNECTION_FAILED")


class QdrantCollectionError(ApiError):
    """Represent a Qdrant collection creation, validation, or storage failure."""

    def __init__(self, message: str = "Qdrant collection error") -> None:
        """Create a Qdrant collection failure.

        Args:
            message: A safe explanation of the collection failure.
        """
        super().__init__(message, "QDRANT_COLLECTION_ERROR")


def qdrant_connection_error(message: str) -> QdrantConnectionError:
    """Return a Qdrant connection error for a specific failure message."""
    return QdrantConnectionError(message)


def qdrant_collection_error(message: str) -> QdrantCollectionError:
    """Return a Qdrant collection error for a specific failure message."""
    return QdrantCollectionError(message)
