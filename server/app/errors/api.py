from typing import Literal

from fastapi import HTTPException

CommonErrorCode = Literal[
    "BAD_REQUEST",
    "UNPROCESSABLE_ENTITY",
    "INTERNAL_SERVER_ERROR",
]

FileErrorCode = Literal[
    "INVALID_FILE_TYPE",
    "INVALID_FILE_SIZE",
    "FILE_UPLOAD_FAILED",
]

ErrorCode = CommonErrorCode | FileErrorCode

STATUS_BY_CODE: dict[ErrorCode, int] = {
    "BAD_REQUEST": 400,
    "INVALID_FILE_TYPE": 400,
    "INVALID_FILE_SIZE": 400,
    "FILE_UPLOAD_FAILED": 400,
    "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_SERVER_ERROR": 500,
}


class ApiError(HTTPException):
    """Represent a client-facing API failure with a stable code and status."""

    def __init__(self, message: str, code: ErrorCode) -> None:
        """Create an error from its message and error code.

        Args:
            message: A useful explanation safe to return to the client.
            code: The stable code used by clients and mapped to an HTTP status.
        """
        self.code = code
        self.message = message
        self.status = STATUS_BY_CODE[code]
        super().__init__(status_code=self.status, detail=message)

    def to_dict(self) -> dict[str, str]:
        """Return the structured JSON representation of this API error."""
        return {"error": self.message, "code": self.code}
