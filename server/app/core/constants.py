import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr, ValidationError

from app.schemas.constants import (
    AppConstants,
    OtpConstants,
    AuthConstants,
    CorsConstants,
    LoggerConstants,
    QdrantConstants,
    GeminiConstants,
    RefreshConstants,
    DoclingConstants,
    EmbeddingDenseKey,
    PostgresConstants,
    EmbeddingConstants,
)

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def _values(schema: type[BaseModel]) -> dict[str, str]:
    """Read overrides, omitting absent or blank default-backed fields for validation."""
    values = {}
    for name, field in schema.model_fields.items():
        value = os.getenv(name)
        if value is None or (not field.is_required() and not value.strip()):
            continue

        values[name] = value

    return values


class Constants:
    """Expose validated settings through the established nested API."""

    @property
    def otp(self) -> OtpConstants:
        """Validate registration lifetime without consuming access settings."""
        try:
            return OtpConstants.model_validate(_values(OtpConstants))
        except ValidationError:
            raise ValueError(
                "Invalid OTP configuration: positive TTL required") from None

    @property
    def auth(self) -> AuthConstants:
        """Keep access-token configuration optional until explicitly consumed."""
        try:
            return AuthConstants.model_validate(_values(AuthConstants))
        except ValidationError:
            raise ValueError(
                "Invalid access-token configuration: signing secret and positive TTL required") from None

    @property
    def refresh(self) -> RefreshConstants:
        """Validate refresh lifetime and the explicitly configured Secure flag."""
        try:
            return RefreshConstants.model_validate(_values(RefreshConstants))
        except ValidationError:
            raise ValueError(
                "Invalid refresh configuration: positive TTL and explicit cookie Secure flag required") from None

    @property
    def gemini(self) -> "_Gemini":
        """Validate optional generation settings only when generation is prepared."""
        try:
            config = GeminiConstants.model_validate(_values(GeminiConstants))
        except ValidationError:
            raise ValueError(
                "Invalid Gemini configuration: key, model, and positive token limit required") from None

        return _Gemini(config)

    def __init__(self) -> None:
        """Load and validate settings before exposing the nested configuration groups."""
        app = AppConstants.model_validate(_values(AppConstants))
        cors = CorsConstants.model_validate(_values(CorsConstants))
        logger = LoggerConstants.model_validate(_values(LoggerConstants))
        docling = DoclingConstants.model_validate(_values(DoclingConstants))
        embedding = EmbeddingConstants.model_validate(
            _values(EmbeddingConstants))
        qdrant = QdrantConstants.model_validate(_values(QdrantConstants))
        postgres = PostgresConstants.model_validate(_values(PostgresConstants))

        self.app = _App(app.PORT)
        self.cors = _Cors(cors.CORS_ORIGINS)
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
        self.qdrant = _Qdrant(qdrant)
        self.postgres = _Postgres(postgres)


class _Postgres:
    """Expose validated PostgreSQL settings and retain the secret wrapper."""

    def __init__(self, config: PostgresConstants) -> None:
        """Expose the PostgreSQL application connection settings."""
        self.POSTGRES_HOST = config.POSTGRES_HOST
        self.POSTGRES_PORT = config.POSTGRES_PORT
        self.POSTGRES_DB = config.POSTGRES_DB
        self.POSTGRES_USER = config.POSTGRES_USER
        self.POSTGRES_PASSWORD = config.POSTGRES_PASSWORD


class _Gemini:
    """Expose lazily validated Gemini settings under the gemini group."""

    def __init__(self, config: GeminiConstants) -> None:
        """Expose the secret credential, explicit model, and output limit."""
        self.GEMINI_API_KEY: SecretStr = config.GEMINI_API_KEY
        self.GEMINI_MODEL = config.GEMINI_MODEL
        self.GEMINI_MAX_OUTPUT_TOKENS = config.GEMINI_MAX_OUTPUT_TOKENS


class _Cors:
    """Expose validated browser origins under the cors group."""

    def __init__(self, origins: list[str]) -> None:
        """Expose the explicit CORS allow-list."""
        self.CORS_ORIGINS = origins


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

    def __init__(self, config: QdrantConstants) -> None:
        """Expose the validated application endpoint, collection, and write settings."""
        self.QDRANT_URL = config.QDRANT_URL
        self.QDRANT_DISTANCE = config.QDRANT_DISTANCE
        self.QDRANT_COLLECTION = config.QDRANT_COLLECTION
        self.QDRANT_CLIENT_TIMEOUT = config.QDRANT_CLIENT_TIMEOUT
        self.QDRANT_WRITE_WAIT = config.QDRANT_WRITE_WAIT


constants = Constants()
