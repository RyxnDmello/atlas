from pydantic import BaseModel

from app.schemas.drive.file import FileResponse
from app.schemas.drive.folder import FolderResponse


class DriveResponse(BaseModel):
    """Return one selected location and only its immediate contents."""

    folder: FolderResponse | None
    folders: list[FolderResponse]
    files: list[FileResponse]
