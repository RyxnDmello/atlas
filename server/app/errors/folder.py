from app.errors.api import ApiError


class FolderNotFoundError(ApiError):
    """Give missing and inaccessible folders the same public privacy boundary."""

    def __init__(self) -> None:
        super().__init__("Folder not found", "FOLDER_NOT_FOUND")
