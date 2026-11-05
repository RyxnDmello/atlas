from uuid import UUID
from typing import Any
from collections.abc import Callable, Coroutine

from fastapi import APIRouter, Request, Response
from starlette.concurrency import run_in_threadpool

from app.pipeline.files import delete, update
from app.pipeline.auth.current import current

from app.routers.drive import DriveRoute

from app.schemas.drive.file import FileResponse
from app.schemas.drive.metadata import FilePatch


class FileRoute(DriveRoute):
    """Authenticate once before FastAPI parses mutation paths or JSON input."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def authenticated(request: Request) -> Response:
            request.state.file_user = await run_in_threadpool(current, request)

            return await handler(request)

        return authenticated


router = APIRouter(prefix="/files", tags=["files"], route_class=FileRoute)


@router.patch("/{file_id}", response_model=FileResponse)
def metadata(request: Request, file_id: UUID, body: FilePatch) -> FileResponse:
    """Delegate a ready-only canonical metadata transaction."""
    return update(request.state.file_user.id, file_id, body)


@router.delete("/{file_id}", status_code=204, response_class=Response)
def removal(request: Request, file_id: UUID) -> Response:
    """Return an empty success only after the final canonical delete commits."""
    delete(request.state.file_user.id, file_id)

    return Response(status_code=204)
