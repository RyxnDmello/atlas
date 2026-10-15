from pydantic import BaseModel


class ResponseChunk(BaseModel):
    """Represent one chunk and its source metadata in the upload response."""

    text: str
    index: int
    count: int
    page: int | None = None
    heading: str | None = None
    section: str | None = None


class UploadResponse(BaseModel):
    """Represent the upload endpoint response."""

    id: str
    name: str
    type: str
    total: int
    chunks: list[ResponseChunk]
