from threading import Lock
from time import perf_counter
from uuid import UUID

from qdrant_client import QdrantClient

from app.db.qdrant import store
from app.core.logging import logger

from app.schemas.pipeline import Chunk
from app.models.qdrant.chunk import Chunk as Payload

from app.pipeline.embeddings.provider import EmbeddingProvider

from app.errors.api import ApiError


class Storage:
    """Embed and persist chunks using resources prepared during startup."""

    def __init__(
        self, provider: EmbeddingProvider, client: QdrantClient, collection: str
    ) -> None:
        """Bind an initialized provider and collection to the upload pipeline."""
        self.provider = provider
        self.client = client
        self.collection = collection
        self.ready = perf_counter()
        self._lock = Lock()

    def write(self, chunks: list[Chunk]) -> int:
        """Embed contextualized text and return the confirmed stored point count."""
        if not chunks:
            raise ApiError("No chunks to embed or store", "FILE_UPLOAD_FAILED")
        try:
            with self._lock:
                started = perf_counter()
                vectors = self.provider.embed([chunk.text for chunk in chunks])
                elapsed = perf_counter() - started
            if len(vectors) != len(chunks) or any(
                len(vector) != self.provider.dimension for vector in vectors
            ):
                raise ValueError(
                    "Embedding output does not match the chunk vector contract"
                )
        except Exception as error:
            logger.exception("Embedding failed: file_id=%s", chunks[0].id)
            raise ApiError(
                "Unable to embed uploaded file chunks", "INTERNAL_SERVER_ERROR"
            ) from error
        logger.info(
            "Embedded file: file_id=%s chunks=%d dimension=%d seconds=%.3f",
            chunks[0].id,
            len(chunks),
            self.provider.dimension,
            elapsed,
        )
        payloads = [
            Payload(
                file_id=UUID(chunk.id),
                chunk_index=chunk.index,
                token_count=chunk.count,
                page=chunk.page,
                heading=chunk.heading,
                section=chunk.section,
                text=chunk.text,
                display_text=chunk.display_text,
            )
            for chunk in chunks
        ]
        count = store(self.client, self.collection, payloads, vectors)
        logger.info("Stored file: file_id=%s points=%d", chunks[0].id, count)
        return count
