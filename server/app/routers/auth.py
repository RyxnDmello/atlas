from typing import Any
from collections.abc import Callable, Coroutine

from fastapi.routing import APIRoute
from fastapi import APIRouter, Request, Response
from fastapi.exceptions import RequestValidationError

from app.core.constants import constants

from app.pipeline.auth.registration import register
from app.pipeline.auth.verify import resend, verify

from app.schemas.auth.registration import RegistrationRequest, RegistrationResponse
from app.schemas.auth.verification import ResendRequest, VerifyRequest, VerifyResponse

from app.errors.api import ApiError


class AuthRoute(APIRoute):
    """Prevent validation diagnostics from echoing any submitted credential input."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def validate(request: Request) -> Response:
            try:
                return await handler(request)
            except RequestValidationError:
                message = ("Invalid registration input" if request.url.path.endswith("/register")
                           else "Invalid verification input")
                raise ApiError(message,
                               "UNPROCESSABLE_ENTITY") from None

        return validate


router = APIRouter(
    prefix="/auth", tags=["auth"], route_class=AuthRoute)


@router.post("/register", status_code=201, response_model=RegistrationResponse)
def registration(request: RegistrationRequest) -> RegistrationResponse:
    """Keep password hashing and synchronous database work off the event loop."""
    register(request)

    return RegistrationResponse()


@router.post("/verify", response_model=VerifyResponse)
def verification(request: VerifyRequest, response: Response) -> VerifyResponse:
    """Set the refresh cookie only after verification persistence commits."""
    config = constants.refresh
    result = verify(request)
    response.set_cookie(
        key="atlas_refresh", value=result.credentials.refresh,
        max_age=config.AUTH_REFRESH_TOKEN_TTL_SECONDS,
        path="/auth", httponly=True, samesite="lax",
        secure=config.AUTH_COOKIE_SECURE,
    )

    return VerifyResponse(access_token=result.credentials.access, user=result.user)


@router.post("/resend", response_model=RegistrationResponse)
def resending(request: ResendRequest) -> RegistrationResponse:
    """Replace the auth verification without issuing credentials."""
    resend(request)

    return RegistrationResponse()
