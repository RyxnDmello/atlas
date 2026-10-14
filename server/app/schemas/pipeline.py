from pydantic import BaseModel


class Chunk(BaseModel):
    """Represent one Docling chunk and its source metadata."""

    id: str
    text: str
    display_text: str
    index: int
    count: int
    page: int | None = None
    heading: str | None = None
    section: str | None = None
