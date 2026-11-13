from uuid import UUID
from typing import Annotated, Any
from starlette.concurrency import run_in_threadpool
from collections.abc import Callable, Coroutine, Generator

from fastapi.sse import EventSourceResponse, ServerSentEvent
from fastapi import APIRouter, Depends, Form, Request, Response

from app.core.logging import get_logger

from app.pipeline.upload import upload
from app.pipeline.retrieval import retrieve
from app.pipeline.auth.current import current
from app.pipeline.generation.prompt import FALLBACK
from app.pipeline.files import delete, read, ready, update
from app.pipeline.generation.grounded import GroundedStream
from app.pipeline.generation.gemini import GeminiFlashProvider

from app.schemas.generation import AskRequest
from app.schemas.files.upload import FileUpload
from app.schemas.files.metadata import FilePatch
from app.schemas.files.response import FileResponse

from app.models.postgres import User

from app.routers.validation import ValidationRoute

from app.errors.api import ApiError
from app.errors.generation import GenerationError


logger = get_logger(__name__)


class FileRoute(ValidationRoute):
    """Authenticate once before FastAPI parses file paths or JSON input."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def authenticated(request: Request) -> Response:
            request.state.file_user = await run_in_threadpool(current, request)

            return await handler(request)

        return authenticated


class UploadRoute(ValidationRoute):
    """Resolve the verified current user before FastAPI parses multipart input."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()

        async def authenticated(request: Request) -> Response:
            request.state.upload_user = await run_in_threadpool(current, request)

            return await handler(request)

        return authenticated


router = APIRouter(prefix="/files", tags=["files"])


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


def detail(request: Request, file_id: UUID) -> FileResponse:
    """Read owned canonical metadata independently of retrieval readiness."""
    return read(request.state.file_user.id, file_id)


def metadata(request: Request, file_id: UUID, body: FilePatch) -> FileResponse:
    """Delegate a ready-only canonical metadata transaction."""
    return update(request.state.file_user.id, file_id, body)


def removal(request: Request, file_id: UUID) -> Response:
    """Return an empty success only after the final canonical delete commits."""
    delete(request.state.file_user.id, file_id)

    return Response(status_code=204)


def authorized(file_id: UUID, user: Annotated[User, Depends(current)]) -> UUID:
    """Resolve an owned ready UUID before retrieval or request-scoped SSE preparation."""
    return ready(user.id, file_id)


def prepare(file: Annotated[UUID, Depends(authorized)], request: AskRequest) -> Generator[GroundedStream | None, None, None]:
    """Retrieve before commitment and own grounded cleanup for the entire request."""
    chunks = retrieve(request.question, file, request.top_k)

    if not chunks:
        yield None

        return

    try:
        stream = GroundedStream(
            GeminiFlashProvider(), request.question, chunks,
        )
    except ValueError:
        raise GenerationError() from None

    try:
        yield stream
    finally:
        stream.close()


def ask(
    stream: Annotated[GroundedStream | None, Depends(prepare, scope="request")],
) -> Generator[ServerSentEvent, None, None]:
    """Stream provisional clean deltas, then trusted citations and one success terminal."""
    try:
        if stream is None:
            yield ServerSentEvent(event="answer", data={"text": FALLBACK})
            citations = []
        else:
            for delta in stream:
                if delta:
                    yield ServerSentEvent(event="answer", data={"text": delta})

            citations = stream.citations
    except GenerationError:
        logger.warning("Ask stream category=generation_failed")

        yield ServerSentEvent(
            event="error",
            data={"error": "Generation failed.", "code": "GENERATION_FAILED"},
        )

        return
    except Exception as error:
        logger.error(
            "Ask stream category=unexpected type=%s", type(error).__name__,
        )

        yield ServerSentEvent(
            event="error",
            data={"error": "Generation failed.", "code": "GENERATION_FAILED"},
        )

        return

    yield ServerSentEvent(event="citations", data={"citations": citations})
    yield ServerSentEvent(event="done", data={"status": "completed"})


router.add_api_route(
    "", creation, methods=["POST"], status_code=201,
    response_model=FileResponse, route_class_override=UploadRoute,
)
router.add_api_route(
    "/{file_id}", detail, methods=["GET"],
    response_model=FileResponse, route_class_override=FileRoute,
)
router.add_api_route(
    "/{file_id}", metadata, methods=["PATCH"],
    response_model=FileResponse, route_class_override=FileRoute,
)
router.add_api_route(
    "/{file_id}", removal, methods=["DELETE"], status_code=204,
    response_class=Response, route_class_override=FileRoute,
)
router.add_api_route(
    "/{file_id}/ask", ask, methods=["POST"], response_class=EventSourceResponse,
)
