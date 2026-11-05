from uuid import UUID
from typing import Literal
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    """List canonical file metadata; visibility does not imply RAG readiness."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    original_name: str
    extension: str
    size_bytes: int
    status: Literal["processing", "ready", "deleting"]
    folder_id: UUID | None
    created_at: datetime
    updated_at: datetime
