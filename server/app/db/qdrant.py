from typing import Any
from uuid import uuid4
from httpx import TransportError

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.http.models import Distance, PointStruct, UpdateStatus, VectorParams

from app.core.logging import logger
from app.core.constants import constants

from app.models.qdrant.chunk import Chunk

from app.pipeline.embeddings.provider import EmbeddingProvider

from app.errors.qdrant import QdrantCollectionError, QdrantConnectionError


def create_client() -> QdrantClient:
    """Construct the configured remote client without a local fallback."""
    try:
        return QdrantClient(
            url=constants.qdrant.QDRANT_URL,
            timeout=constants.qdrant.QDRANT_CLIENT_TIMEOUT,
        )
    except Exception as error:
        raise QdrantConnectionError(
            "Unable to initialize Qdrant client") from error


def store(
    client: QdrantClient,
    collection: str,
    payloads: list[Chunk],
    vectors: list[list[float]],
) -> int:
    """Write matching payloads/vectors and require completed Qdrant storage."""
    if len(payloads) != len(vectors):
        raise QdrantCollectionError(
            "Qdrant payload and vector counts do not match")
    try:
        points = [
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload=payload.model_dump(mode="json"),
            )
            for payload, vector in zip(payloads, vectors, strict=True)
        ]
        result = client.upsert(
            collection_name=collection,
            points=points,
            wait=constants.qdrant.QDRANT_WRITE_WAIT,
        )
    except Exception as error:
        logger.exception(
            "Qdrant chunk storage failed: collection=%s", collection)
        source = error.source if isinstance(
            error, ResponseHandlingException) else error
        if isinstance(source, (TransportError, ConnectionError, TimeoutError)):
            raise QdrantConnectionError(
                "Unable to connect to Qdrant while storing chunks"
            ) from error
        raise QdrantCollectionError(
            "Unable to store chunks in Qdrant") from error
    if result.status != UpdateStatus.COMPLETED:
        logger.error(
            "Qdrant write not completed: collection=%s status=%s",
            collection,
            result.status,
        )
        raise QdrantCollectionError(
            "Qdrant did not confirm completed chunk storage")
    return len(points)


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    provider: EmbeddingProvider,
) -> None:
    """Create or validate a cosine collection for an embedding provider.

    Args:
        client: The injected Qdrant client to use.
        collection_name: The collection to create or inspect.
        provider: The active provider whose dimension sizes the collection.

    Raises:
        QdrantConnectionError: If Qdrant cannot be inspected.
        QdrantCollectionError: If creation fails or an existing collection
            does not match the provider dimension and cosine metric.
    """
    try:
        exists = client.collection_exists(collection_name)
    except Exception as error:
        raise QdrantConnectionError(
            f"Unable to inspect Qdrant collection '{collection_name}'"
        ) from error

    if exists:
        _validate_collection(client, collection_name, provider)
        return

    distance = _distance()
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=provider.dimension,
                distance=distance,
            ),
        )
    except Exception as error:
        raise QdrantCollectionError(
            f"Unable to create Qdrant collection '{collection_name}'"
        ) from error


def create_collection(
    client: QdrantClient,
    collection_name: str,
    provider: EmbeddingProvider,
) -> None:
    """Create or validate a provider-sized Qdrant collection."""
    ensure_collection(client, collection_name, provider)


def _validate_collection(
    client: QdrantClient,
    collection_name: str,
    provider: EmbeddingProvider,
) -> None:
    """Verify the existing collection matches the active vector contract."""
    try:
        info = client.get_collection(collection_name)
        vectors = info.config.params.vectors
        size, distance = _vector_config(vectors)
    except Exception as error:
        raise QdrantCollectionError(
            f"Unable to inspect Qdrant collection '{collection_name}'"
        ) from error

    if size != provider.dimension or distance != _distance():
        raise QdrantCollectionError(
            f"Qdrant collection '{collection_name}' does not match the active vector contract"
        )


def _vector_config(vectors: Any) -> tuple[int, Distance]:
    """Read unnamed vector configuration from a Qdrant collection response."""
    if isinstance(vectors, dict):
        raise ValueError(
            "Named Qdrant vectors are not supported for this collection")
    return vectors.size, vectors.distance


def _distance() -> Distance:
    """Return the configured Qdrant distance enum."""
    return Distance(constants.qdrant.QDRANT_DISTANCE)
