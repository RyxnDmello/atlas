from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FolderResponse(BaseModel):
    """Expose canonical folder metadata without ownership or hierarchy expansion."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    parent_id: UUID | None
    created_at: datetime
    updated_at: datetime
