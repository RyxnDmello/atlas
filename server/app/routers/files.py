from uuid import UUID
from typing import Annotated
from collections.abc import Generator
from starlette.concurrency import run_in_threadpool

from fastapi import APIRouter, Depends
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.models.postgres import User
from app.core.logging import get_logger

from app.pipeline.files import ready
from app.pipeline.retrieval import retrieve
from app.pipeline.auth.current import current
from app.pipeline.generation.prompt import FALLBACK
from app.pipeline.generation.grounded import GroundedStream
from app.pipeline.generation.gemini import GeminiFlashProvider

from app.schemas.generation import AskRequest
from app.schemas.retrieval import QueryRequest, QueryResponse, ScoredChunk

from app.errors.generation import GenerationError

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


def authorized(file_id: UUID, user: Annotated[User, Depends(current)]) -> UUID:
    """Resolve an owned ready UUID before retrieval or request-scoped SSE preparation."""
    return ready(user.id, file_id)


@router.post("/{file_id}/query", response_model=QueryResponse)
async def query(file: Annotated[UUID, Depends(authorized)], request: QueryRequest) -> QueryResponse:
    """Return scored file chunks while running blocking inference/search off the event loop."""
    chunks = await run_in_threadpool(retrieve, request.question, file, request.top_k)

    results = [
        ScoredChunk(
            score=chunk.score,
            text=chunk.text,
            index=chunk.chunk_index,
            count=chunk.token_count,
            page=chunk.page,
            heading=chunk.heading,
            section=chunk.section,
        )
        for chunk in chunks
    ]

    return QueryResponse(results=results)


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


@router.post("/{file_id}/ask", response_class=EventSourceResponse)
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
