from app.errors.api import ApiError


class FileNotFoundError(ApiError):
    """Keep missing and foreign file identities indistinguishable."""

    def __init__(self) -> None:
        super().__init__("File not found", "FILE_NOT_FOUND")


class FileNotReadyError(ApiError):
    """Reject operations that require an indexed, ready file."""

    def __init__(self) -> None:
        super().__init__("File is not ready", "FILE_NOT_READY")
