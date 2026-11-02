from urllib.parse import urlparse
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, SecretStr, TypeAdapter, field_validator


class AppConstants(BaseModel):
    """Validate application server settings."""

    PORT: int = Field(ge=1, le=65535)


class CorsConstants(BaseModel):
    """Validate a comma-separated allow-list of exact browser origins."""

    CORS_ORIGINS: list[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def validate_origins(cls, value: object) -> list[str]:
        """Reject wildcard, credentialed, or non-origin URLs before startup."""
        origins = value.split(",") if isinstance(value, str) else value
        if not isinstance(origins, list):
            raise ValueError(
                "CORS_ORIGINS must be a comma-separated origin list")

        result = []
        for origin in origins:
            if not isinstance(origin, str):
                raise ValueError("CORS origins must be strings")

            origin = origin.strip()
            parsed = urlparse(origin)
            if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                    or "*" in origin or parsed.username is not None
                    or parsed.password is not None or parsed.path
                    or parsed.query or parsed.fragment or "?" in origin or "#" in origin
                    or any(character.isspace() for character in origin)):
                raise ValueError("CORS origins must be exact HTTP(S) origins")

            _ = parsed.port
            if origin not in result:
                result.append(origin)

        return result


class GeminiConstants(BaseModel):
    """Validate generation settings without displaying sensitive input values."""

    model_config = ConfigDict(hide_input_in_errors=True)

    GEMINI_API_KEY: SecretStr
    GEMINI_MODEL: str = Field(min_length=1)
    GEMINI_MAX_OUTPUT_TOKENS: int = Field(default=2048, gt=0)

    @field_validator("GEMINI_API_KEY", "GEMINI_MODEL")
    @classmethod
    def validate_nonblank(cls, value: SecretStr | str) -> SecretStr | str:
        """Reject whitespace-only credentials or model identifiers."""
        text = value.get_secret_value() if isinstance(value, SecretStr) else value

        if not text.strip():
            raise ValueError("Gemini settings must be nonblank")

        return value


class AuthConstants(BaseModel):
    """Validate access credentials only when the auth boundary is prepared."""

    model_config = ConfigDict(hide_input_in_errors=True, frozen=True)

    AUTH_ACCESS_TOKEN_SECRET: SecretStr
    AUTH_ACCESS_TOKEN_TTL_SECONDS: int = Field(default=900, gt=0)

    @field_validator("AUTH_ACCESS_TOKEN_SECRET")
    @classmethod
    def validate_secret(cls, value: SecretStr) -> SecretStr:
        """Measure the literal signing key in UTF-8 bytes without normalizing it."""
        text = value.get_secret_value()
        if not text.strip() or len(text.encode("utf-8")) < 32:
            raise ValueError(
                "Access signing secret must contain at least 32 UTF-8 bytes")

        return value


class OtpConstants(BaseModel):
    """Validate verification lifetime independently of access credentials."""

    model_config = ConfigDict(hide_input_in_errors=True, frozen=True)

    AUTH_OTP_TTL_SECONDS: int = Field(default=600, gt=0)


class RefreshConstants(BaseModel):
    """Validate initial refresh-session lifetime and cookie transport policy."""

    model_config = ConfigDict(hide_input_in_errors=True, frozen=True)

    AUTH_REFRESH_TOKEN_TTL_SECONDS: int = Field(default=604800, gt=0)
    AUTH_COOKIE_SECURE: bool


class PostgresConstants(BaseModel):
    """Validate required PostgreSQL settings without displaying sensitive input."""

    model_config = ConfigDict(hide_input_in_errors=True)

    POSTGRES_HOST: str
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535)
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr

    @field_validator("POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")
    @classmethod
    def validate_nonblank(cls, value: SecretStr | str) -> SecretStr | str:
        """Reject blank connection values while preserving literal credentials."""
        text = value.get_secret_value() if isinstance(value, SecretStr) else value

        if not text.strip():
            raise ValueError("PostgreSQL settings must be nonblank")

        return value


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

    DOCLING_MAX_CHUNK_TOKENS: int = Field(default=500, ge=1)
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
    """Validate Qdrant application connection and collection settings."""

    QDRANT_URL: str = Field(min_length=1)
    QDRANT_DISTANCE: Literal["Cosine"] = "Cosine"
    QDRANT_COLLECTION: str = Field(default="atlas-chunks", min_length=1)
    QDRANT_CLIENT_TIMEOUT: int = Field(default=10, ge=1)
    QDRANT_WRITE_WAIT: Literal[True] = True

    @field_validator("QDRANT_WRITE_WAIT", mode="before")
    @classmethod
    def parse_wait(cls, value: object) -> bool:
        """Parse an environment boolean before enforcing confirmed writes."""
        return TypeAdapter(bool).validate_python(value)

    @field_validator("QDRANT_URL")
    @classmethod
    def validate_qdrant_url(cls, value: str) -> str:
        """Validate that the Qdrant endpoint is an HTTP(S) URL."""
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("QDRANT_URL must be a valid HTTP(S) URL")

        return value
