from uuid import UUID

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """Map one embedded chunk to its stored Qdrant payload."""

    file_id: UUID
    chunk_index: int = Field(ge=0)
    token_count: int = Field(ge=0)
    page: int | None = None
    heading: str | None = None
    section: str | None = None
    text: str
    display_text: str
