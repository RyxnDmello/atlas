from pydantic import BaseModel


class Chunk(BaseModel):
    id: str
    text: str
    index: int
    count: int


class ResponseChunk(BaseModel):
    text: str
    index: int
    count: int


class UploadResponse(BaseModel):
    name: str
    type: str
    total: int
    chunks: list[ResponseChunk]
