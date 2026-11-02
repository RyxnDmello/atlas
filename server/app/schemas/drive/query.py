from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FolderQuery(BaseModel):
    """Folder mutations accept no query parameters, including ownership input."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class DriveQuery(FolderQuery):
    """Select an optional folder by UUID, never by client-supplied ownership."""

    folder_id: UUID | None = None
