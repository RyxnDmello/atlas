from pydantic import BaseModel, Field, field_validator

from app.models.qdrant.chunk import Chunk as Payload


class QueryRequest(BaseModel):
    """Validate a trimmed question and the bounded dense retrieval limit."""

    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def trim(cls, question: str) -> str:
        """Reject questions with no content after surrounding whitespace is removed."""
        question = question.strip()

        if not question:
            raise ValueError("Question must not be empty")

        return question


class RetrievedChunk(Payload):
    """Preserve the complete stored payload and raw score for downstream use."""

    page: int | None = Field(...)
    heading: str | None = Field(...)
    section: str | None = Field(...)
    score: float = Field(allow_inf_nan=False)
