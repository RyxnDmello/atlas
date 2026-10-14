import os
from pathlib import Path

from dotenv import load_dotenv

from app.schemas.constants import (
    AppConstants,
    LoggerConstants,
    QdrantConstants,
    DoclingConstants,
    EmbeddingDenseKey,
    EmbeddingConstants,
)

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def _value(name: str) -> str | None:
    """Return one environment-backed setting."""
    return os.getenv(name)


class Constants:
    """Expose validated settings through the established nested API."""

    def __init__(self) -> None:
        """Load and validate settings before exposing the nested configuration groups."""
        app = AppConstants.model_validate(
            {
                "PORT": _value("PORT"),
            }
        )
        logger = LoggerConstants.model_validate(
            {
                "LOG_LEVEL": _value("LOG_LEVEL"),
            }
        )
        docling = DoclingConstants.model_validate(
            {
                "DOCLING_MAX_CHUNK_TOKENS": _value("DOCLING_MAX_CHUNK_TOKENS"),
            }
        )
        embedding = EmbeddingConstants.model_validate({})
        qdrant = QdrantConstants.model_validate(
            {
                "QDRANT_URL": _value("QDRANT_URL"),
                **{
                    name: value
                    for name in ("QDRANT_COLLECTION", "QDRANT_CLIENT_TIMEOUT")
                    if (value := _value(name)) is not None
                },
                "QDRANT_HEALTHCHECK_RETRIES": _value("QDRANT_HEALTHCHECK_RETRIES"),
                "QDRANT_HEALTHCHECK_TIMEOUT": _value("QDRANT_HEALTHCHECK_TIMEOUT"),
                "QDRANT_HEALTHCHECK_INTERVAL": _value("QDRANT_HEALTHCHECK_INTERVAL"),
                "QDRANT_HEALTHCHECK_START_PERIOD": _value(
                    "QDRANT_HEALTHCHECK_START_PERIOD"
                ),
            }
        )

        self.app = _App(app.PORT)
        self.logger = _Logger(logger.LOG_LEVEL)
        self.docling = _Docling(
            docling.DOCLING_MAX_CHUNK_TOKENS,
            docling.DOCLING_MERGE_PEERS,
            docling.DOCLING_ALWAYS_EMIT_HEADINGS,
        )
        self.embedding = _Embedding(
            embedding.EMBEDDING_MODEL,
            embedding.EMBEDDING_DIMENSION,
            embedding.EMBEDDING_USE_FP16,
            embedding.EMBEDDING_RETURN_DENSE,
            embedding.EMBEDDING_RETURN_SPARSE,
            embedding.EMBEDDING_RETURN_COLBERT_VECS,
            embedding.EMBEDDING_DENSE_KEY,
        )
        self.qdrant = _Qdrant(
            qdrant.QDRANT_URL,
            qdrant.QDRANT_DISTANCE,
            qdrant.QDRANT_HEALTHCHECK_RETRIES,
            qdrant.QDRANT_HEALTHCHECK_TIMEOUT,
            qdrant.QDRANT_HEALTHCHECK_INTERVAL,
            qdrant.QDRANT_HEALTHCHECK_START_PERIOD,
            qdrant.QDRANT_COLLECTION,
            qdrant.QDRANT_CLIENT_TIMEOUT,
            qdrant.QDRANT_WRITE_WAIT,
        )


class _App:
    """Expose application settings under the app group."""

    def __init__(self, port: int) -> None:
        """Expose the validated application port."""
        self.PORT = port


class _Logger:
    """Expose logging settings under the logger group."""

    def __init__(self, level: str) -> None:
        """Expose the validated logging level."""
        self.LOG_LEVEL = level


class _Docling:
    """Expose Docling settings under the docling group."""

    def __init__(self, max_chunk_tokens: int, merge_peers: bool, headings: bool) -> None:
        """Expose the token limit, peer merging, and heading preservation settings."""
        self.DOCLING_MAX_CHUNK_TOKENS = max_chunk_tokens
        self.DOCLING_MERGE_PEERS = merge_peers
        self.DOCLING_ALWAYS_EMIT_HEADINGS = headings


class _Embedding:
    """Expose embedding settings under the embedding group."""

    def __init__(
        self,
        model: str,
        dimension: int,
        use_fp16: bool,
        return_dense: bool,
        return_sparse: bool,
        return_colbert_vecs: bool,
        dense_key: EmbeddingDenseKey,
    ) -> None:
        """Expose the fixed model, dimension, precision, and output settings."""
        self.EMBEDDING_MODEL = model
        self.EMBEDDING_DIMENSION = dimension
        self.EMBEDDING_USE_FP16 = use_fp16
        self.EMBEDDING_RETURN_DENSE = return_dense
        self.EMBEDDING_RETURN_SPARSE = return_sparse
        self.EMBEDDING_RETURN_COLBERT_VECS = return_colbert_vecs
        self.EMBEDDING_DENSE_KEY = dense_key


class _Qdrant:
    """Expose Qdrant settings under the qdrant group."""

    def __init__(
        self,
        url: str,
        distance: str,
        retries: int,
        timeout: int,
        interval: int,
        start_period: int,
        collection: str,
        client_timeout: int,
        wait: bool,
    ) -> None:
        """Expose the validated endpoint, collection, health, and write settings."""
        self.QDRANT_URL = url
        self.QDRANT_DISTANCE = distance
        self.QDRANT_HEALTHCHECK_RETRIES = retries
        self.QDRANT_HEALTHCHECK_TIMEOUT = timeout
        self.QDRANT_HEALTHCHECK_INTERVAL = interval
        self.QDRANT_HEALTHCHECK_START_PERIOD = start_period
        self.QDRANT_COLLECTION = collection
        self.QDRANT_CLIENT_TIMEOUT = client_timeout
        self.QDRANT_WRITE_WAIT = wait


constants = Constants()
