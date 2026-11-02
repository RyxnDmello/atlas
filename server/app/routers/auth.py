from typing import Any
from collections.abc import Callable, Coroutine

from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, Depends, Request, Response

from app.core.constants import constants

from app.pipeline.auth.login import login
from app.pipeline.auth.logout import logout
from app.pipeline.auth.current import current
from app.pipeline.auth.rotation import refresh
from app.pipeline.auth.verify import resend, verify
from app.pipeline.auth.registration import register

from app.schemas.auth.login import LoginRequest
from app.schemas.auth.verification import ResendRequest, VerifyRequest
from app.schemas.auth.authenticated import AuthenticatedResponse, AuthenticatedUser
from app.schemas.auth.registration import RegistrationRequest, RegistrationResponse

from app.models.postgres.user import User

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
                           else "Invalid login input" if request.url.path.endswith("/login")
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


def _cookie(response: Response, refresh: str | None = None) -> None:
    """Share refresh issuance and clearing attributes after successful domain outcomes."""
    config = constants.refresh
    response.set_cookie(
        key="atlas_refresh", value=refresh if refresh is not None else "",
        max_age=config.AUTH_REFRESH_TOKEN_TTL_SECONDS if refresh is not None else 0,
        expires=None if refresh is not None else 0,
        path="/auth", httponly=True, samesite="lax",
        secure=config.AUTH_COOKIE_SECURE,
    )


@router.post("/verify", response_model=AuthenticatedResponse)
def verification(request: VerifyRequest, response: Response) -> AuthenticatedResponse:
    """Set the refresh cookie only after verification persistence commits."""
    result = verify(request)
    _cookie(response, result.credentials.refresh)

    return AuthenticatedResponse(access_token=result.credentials.access, user=result.user)


@router.post("/login", response_model=AuthenticatedResponse)
def logging_in(request: LoginRequest, response: Response) -> AuthenticatedResponse:
    """Keep synchronous credential and database work off the event loop."""
    result = login(request)
    _cookie(response, result.credentials.refresh)

    return AuthenticatedResponse(access_token=result.credentials.access, user=result.user)


@router.post("/resend", response_model=RegistrationResponse)
def resending(request: ResendRequest) -> RegistrationResponse:
    """Replace the auth verification without issuing credentials."""
    resend(request)

    return RegistrationResponse()


@router.post("/refresh", response_model=AuthenticatedResponse)
def refreshing(request: Request, response: Response) -> AuthenticatedResponse:
    """Read only the refresh cookie and issue credentials after rotation commits."""
    result = refresh(request.cookies.get("atlas_refresh"))
    _cookie(response, result.credentials.refresh)

    return AuthenticatedResponse(access_token=result.credentials.access, user=result.user)


@router.post("/logout", status_code=204)
def logging_out(request: Request) -> Response:
    """Clear the cookie only after successful idempotent current-session logout."""
    logout(request.cookies.get("atlas_refresh"))
    response = Response(status_code=204)
    _cookie(response)

    return response


@router.get("", response_model=AuthenticatedUser)
def authenticated(user: User = Depends(current)) -> AuthenticatedUser:
    """Expose only the safe canonical profile supplied by the shared auth dependency."""
    return AuthenticatedUser(id=user.id, name=user.name, email=user.email)
