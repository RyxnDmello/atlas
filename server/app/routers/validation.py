from typing import Any
from collections.abc import Callable, Coroutine

from fastapi.routing import APIRoute
from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError

from app.errors.api import ApiError


class ValidationRoute(APIRoute):
    """Keep malformed request input and internal validation details out of public errors."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def validate(request: Request) -> Response:
            try:
                return await handler(request)
            except RequestValidationError:
                raise ApiError("Invalid request input",
                               "UNPROCESSABLE_ENTITY") from None

        return validate
