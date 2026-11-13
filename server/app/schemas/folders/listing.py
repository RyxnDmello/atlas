from pydantic import BaseModel

from app.schemas.files.response import FileResponse
from app.schemas.folders.response import FolderResponse


class FolderListingResponse(BaseModel):
    """Return one selected location and only its immediate contents."""

    folder: FolderResponse | None
    folders: list[FolderResponse]
    files: list[FileResponse]
