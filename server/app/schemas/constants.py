from typing import Literal, TypeAlias
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class AppConstants(BaseModel):
    """Validate application server settings."""

    PORT: int = Field(ge=1, le=65535)


class LoggerConstants(BaseModel):
    """Validate logging settings."""

    LOG_LEVEL: str = Field(min_length=1)

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Validate that the configured logging level is supported."""

        levels = {
            "INFO",
            "WARN",
            "FATAL",
            "DEBUG",
            "ERROR",
            "NOTSET",
            "WARNING",
            "CRITICAL",
        }

        if value.upper() not in levels:
            raise ValueError("LOG_LEVEL must be a supported logging level")

        return value


class DoclingConstants(BaseModel):
    """Validate Docling extraction and chunking settings."""

    DOCLING_MAX_CHUNK_TOKENS: int = Field(ge=1)
    DOCLING_MERGE_PEERS: bool = True
    DOCLING_ALWAYS_EMIT_HEADINGS: bool = True


EmbeddingDenseKey: TypeAlias = Literal["dense_vecs"]


class EmbeddingConstants(BaseModel):
    """Validate fixed BGE-M3 embedding pipeline settings."""

    EMBEDDING_MODEL: str = Field(default="BAAI/bge-m3", min_length=1)
    EMBEDDING_DIMENSION: int = Field(default=1024, ge=1)
    EMBEDDING_USE_FP16: bool = False
    EMBEDDING_RETURN_DENSE: bool = True
    EMBEDDING_RETURN_SPARSE: bool = False
    EMBEDDING_RETURN_COLBERT_VECS: bool = False
    EMBEDDING_DENSE_KEY: EmbeddingDenseKey = "dense_vecs"


class QdrantConstants(BaseModel):
    """Validate Qdrant connection and health-check settings."""

    QDRANT_URL: str = Field(min_length=1)
    QDRANT_DISTANCE: Literal["Cosine"] = "Cosine"
    QDRANT_COLLECTION: str = Field(default="atlas-chunks", min_length=1)
    QDRANT_CLIENT_TIMEOUT: int = Field(default=10, ge=1)
    QDRANT_WRITE_WAIT: Literal[True] = True
    QDRANT_HEALTHCHECK_RETRIES: int = Field(ge=1)
    QDRANT_HEALTHCHECK_TIMEOUT: int = Field(ge=1)
    QDRANT_HEALTHCHECK_INTERVAL: int = Field(ge=1)
    QDRANT_HEALTHCHECK_START_PERIOD: int = Field(ge=0)

    @field_validator("QDRANT_URL")
    @classmethod
    def validate_qdrant_url(cls, value: str) -> str:
        """Validate that the Qdrant endpoint is an HTTP(S) URL."""

        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("QDRANT_URL must be a valid HTTP(S) URL")

        return value
