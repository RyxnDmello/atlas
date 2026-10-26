from typing import Literal

from pydantic import BaseModel

from app.errors.api import ErrorCode


class CollectionHealth(BaseModel):
    """Describe an accessible collection using Qdrant's reported metadata."""

    status: str
    name: str
    points: int | None


class DiagnosticError(BaseModel):
    """Describe a supplementary diagnostic failure without raw transport details."""

    error: str
    code: ErrorCode


class QdrantHealth(BaseModel):
    """Report connectivity and optional Qdrant metadata independently."""

    version: str | None = None
    status: Literal["Qdrant Healthy", "unhealthy"]
    uptime: str | None = None
    started: str | None = None
    collection: CollectionHealth | None = None
    diagnostics_error: DiagnosticError | None = None
    error: str | None = None
    code: ErrorCode | None = None


class PostgresHealth(BaseModel):
    """Report minimal PostgreSQL connectivity without connection details."""

    status: Literal["PostgreSQL Healthy", "PostgreSQL Unhealthy"]
    version: str | None = None
    error: str | None = None
    code: ErrorCode | None = None


class DatabaseHealth(BaseModel):
    """Represent independent Qdrant and PostgreSQL diagnostics."""

    qdrant: QdrantHealth
    postgres: PostgresHealth
