from app.errors.api import ApiError


class FolderNotFoundError(ApiError):
    """Give missing and inaccessible folders the same public privacy boundary."""

    def __init__(self) -> None:
        super().__init__("Folder not found", "FOLDER_NOT_FOUND")


class FolderScopeLimitError(ApiError):
    """Reject an oversized authorized scope without returning a partial search set."""

    def __init__(self) -> None:
        super().__init__("This folder exceeds the supported Ask scope.",
                         "FOLDER_SCOPE_LIMIT_EXCEEDED")
