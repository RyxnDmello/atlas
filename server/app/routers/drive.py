from typing import Annotated, Any
from collections.abc import Callable, Coroutine

from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi import APIRouter, Depends, Query, Request, Response

from app.pipeline.drive import listing
from app.pipeline.auth.current import current

from app.schemas.drive.query import DriveQuery
from app.schemas.drive.listing import DriveResponse

from app.models.postgres import User

from app.errors.api import ApiError


class DriveRoute(APIRoute):
    """Keep malformed drive input and internal validation details out of public errors."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def validate(request: Request) -> Response:
            try:
                return await handler(request)
            except RequestValidationError:
                raise ApiError("Invalid drive input",
                               "UNPROCESSABLE_ENTITY") from None

        return validate


router = APIRouter(tags=["drive"], route_class=DriveRoute)


@router.get("/drive", response_model=DriveResponse)
def browse(query: Annotated[DriveQuery, Query()], user: Annotated[User, Depends(current)]) -> DriveResponse:
    """Authenticate before synchronous, owner-scoped PostgreSQL browsing."""
    return listing(user.id, query.folder_id)
