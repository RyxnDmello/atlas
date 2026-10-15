from uuid import UUID
from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from app.pipeline.retrieval import retrieve
from app.schemas.retrieval import QueryRequest, QueryResponse, ScoredChunk

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/{file_id}/query", response_model=QueryResponse)
async def query(file_id: UUID, request: QueryRequest) -> QueryResponse:
    """Return scored file chunks while running blocking inference/search off the event loop."""
    chunks = await run_in_threadpool(retrieve, request.question, file_id, request.top_k)

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
