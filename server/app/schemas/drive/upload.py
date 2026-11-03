from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict

from app.schemas.drive.metadata import Name, Description


class FileUpload(BaseModel):
    """Accept only upload input; canonical identity and source facts are server-owned."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    file: UploadFile
    name: Name
    description: Description = None
    folder_id: UUID | None = None
