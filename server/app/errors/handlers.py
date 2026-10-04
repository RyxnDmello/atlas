from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.types import HTTPExceptionHandler

from app.core.logging import logger
from app.errors.api import ApiError, STATUS_BY_CODE, is_api_error


def handle_api_error(request: Request, error: ApiError) -> JSONResponse:
    """Return the structured response for a known API error.

    Args:
        request: The request that produced the error.
        error: The known API error raised by application code.

    Returns:
        The error's structured JSON response with its mapped status code.
    """
    del request
    return error.response()


def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    """Log an unexpected exception and return a generic server error.

    Args:
        request: The request that produced the exception.
        error: The unexpected exception raised during request handling.

    Returns:
        A generic structured 500 response without internal exception details.
    """
    if is_api_error(error):
        return handle_api_error(request, cast(ApiError, error))

    logger.error(
        "Unhandled exception: %s",
        error,
        exc_info=(type(error), error, error.__traceback__),
    )
    return JSONResponse(
        status_code=STATUS_BY_CODE["INTERNAL_SERVER_ERROR"],
        content={
            "error": "Internal server error",
            "code": "INTERNAL_SERVER_ERROR",
        },
    )


def cast_handle_unexpected_error():
    return cast(HTTPExceptionHandler, handle_unexpected_error)


def cast_handle_api_error():
    return cast(HTTPExceptionHandler, handle_api_error)
