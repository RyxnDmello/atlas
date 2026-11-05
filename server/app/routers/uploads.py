from typing import Annotated, Any
from collections.abc import Callable, Coroutine
from starlette.concurrency import run_in_threadpool
from fastapi import APIRouter, Form, Request, Response

from app.routers.drive import DriveRoute

from app.pipeline.upload import upload
from app.pipeline.auth.current import current

from app.schemas.drive.file import FileResponse
from app.schemas.drive.upload import FileUpload

from app.errors.api import ApiError


class UploadRoute(DriveRoute):
    """Resolve the verified current user before FastAPI parses multipart input."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def authenticated(request: Request) -> Response:
            request.state.upload_user = await run_in_threadpool(current, request)

            return await handler(request)

        return authenticated


router = APIRouter(prefix="/files", tags=["files"], route_class=UploadRoute)


@router.post("", status_code=201, response_model=FileResponse)
async def creation(request: Request, form: Annotated[FileUpload, Form(media_type="multipart/form-data")]) -> FileResponse:
    """Read transient input, delegate lifecycle orchestration, and always close the upload."""
    try:
        try:
            content = await form.file.read()
        except Exception:
            raise ApiError("Unable to read uploaded file",
                           "FILE_UPLOAD_FAILED") from None

        return await run_in_threadpool(upload, request.state.upload_user.id,
                                       form, content, form.file.filename or "")
    finally:
        await form.file.close()
