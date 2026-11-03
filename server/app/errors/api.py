from typing import Literal

from fastapi import HTTPException
from fastapi.responses import JSONResponse

CommonErrorCode = Literal[
    "BAD_REQUEST",
    "UNPROCESSABLE_ENTITY",
    "INTERNAL_SERVER_ERROR",
]
AuthErrorCode = Literal[
    "ACCOUNT_NOT_FOUND",
    "INVALID_CREDENTIALS",
    "INVALID_ACCESS_TOKEN",
    "INVALID_VERIFICATION",
    "VERIFICATION_EXPIRED",
    "INVALID_REFRESH_TOKEN",
    "VERIFICATION_REQUIRED",
    "ACCOUNT_ALREADY_EXISTS",
    "VERIFICATION_NOT_REQUIRED",
]
FileErrorCode = Literal[
    "FILE_NOT_FOUND",
    "FILE_NOT_READY",
    "INVALID_FILE_TYPE",
    "INVALID_FILE_SIZE",
    "FILE_UPLOAD_FAILED",
]
QdrantErrorCode = Literal[
    "QDRANT_COLLECTION_ERROR",
    "QDRANT_CONNECTION_FAILED",
]
PostgresErrorCode = Literal[
    "POSTGRES_OPERATION_FAILED",
    "POSTGRES_CONNECTION_FAILED",
]
GenerationErrorCode = Literal[
    "GENERATION_FAILED"
]
FolderErrorCode = Literal[
    "FOLDER_NOT_FOUND"
]

ErrorCode = CommonErrorCode | FileErrorCode | QdrantErrorCode | GenerationErrorCode | PostgresErrorCode | AuthErrorCode | FolderErrorCode

STATUS_BY_CODE: dict[ErrorCode, int] = {
    "BAD_REQUEST": 400,
    "FILE_NOT_READY": 409,
    "FILE_NOT_FOUND": 404,
    "FOLDER_NOT_FOUND": 404,
    "ACCOUNT_NOT_FOUND": 404,
    "INVALID_FILE_TYPE": 400,
    "INVALID_FILE_SIZE": 400,
    "GENERATION_FAILED": 502,
    "FILE_UPLOAD_FAILED": 400,
    "INVALID_CREDENTIALS": 401,
    "INVALID_VERIFICATION": 400,
    "VERIFICATION_EXPIRED": 400,
    "UNPROCESSABLE_ENTITY": 422,
    "INVALID_ACCESS_TOKEN": 401,
    "VERIFICATION_REQUIRED": 403,
    "INVALID_REFRESH_TOKEN": 401,
    "INTERNAL_SERVER_ERROR": 500,
    "ACCOUNT_ALREADY_EXISTS": 409,
    "QDRANT_COLLECTION_ERROR": 500,
    "QDRANT_CONNECTION_FAILED": 503,
    "VERIFICATION_NOT_REQUIRED": 409,
    "POSTGRES_OPERATION_FAILED": 500,
    "POSTGRES_CONNECTION_FAILED": 503,
}


class ApiError(HTTPException):
    """Represent a client-facing API failure with a stable code and status."""

    def __init__(self, message: str, code: ErrorCode) -> None:
        """Create an error from its message and error code.

        Args:
            message: A useful explanation safe to return to the client.
            code: The stable code used by clients and mapped to an HTTP status.
        """
        self.code: ErrorCode = code
        self.message = message
        self.status = STATUS_BY_CODE[code]

        super().__init__(status_code=self.status, detail=message)

    def to_dict(self) -> dict[str, str]:
        """Return the structured JSON representation of this API error."""
        return {"error": self.message, "code": self.code}

    def response(self) -> JSONResponse:
        """Return the API Response with proper error status and content."""
        return JSONResponse(status_code=self.status, content=self.to_dict())


def is_api_error(error: object) -> bool:
    """Return whether an object is an instance of ApiError.

    Args:
        error: The object to inspect.

    Returns:
        True when the object is an ApiError, otherwise False.
    """
    return isinstance(error, ApiError)
