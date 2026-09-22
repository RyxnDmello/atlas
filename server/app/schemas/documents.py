from pydantic import BaseModel


class ResponseChunk(BaseModel):
    """Represent one chunk returned by the upload endpoint."""

    text: str
    index: int
    count: int


class UploadResponse(BaseModel):
    """Represent the upload endpoint response."""

    name: str
    type: str
    total: int
    chunks: list[ResponseChunk]
