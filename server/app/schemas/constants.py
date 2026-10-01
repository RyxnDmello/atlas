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


class QdrantConstants(BaseModel):
    """Validate Qdrant connection and health-check settings."""

    QDRANT_URL: str = Field(min_length=1)
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
