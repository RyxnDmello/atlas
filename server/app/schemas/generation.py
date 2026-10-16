from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=0)
    page: int | None
    heading: str | None
    section: str | None
    excerpt: str
