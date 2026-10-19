from pydantic import BaseModel, ConfigDict, Field

from app.schemas.retrieval import QueryRequest


class AskRequest(QueryRequest):
    """Use the same trimmed question and bounded top-k contract as retrieval."""


class Citation(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=0)
    page: int | None
    heading: str | None
    section: str | None
    excerpt: str
