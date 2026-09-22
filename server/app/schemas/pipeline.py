from pydantic import BaseModel


class Chunk(BaseModel):
    """Represent one pipeline chunk and its token count."""

    id: str
    text: str
    index: int
    count: int
