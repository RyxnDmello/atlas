from uuid import UUID
from math import isfinite
from time import perf_counter

from app.core.logging import logger
from app.core.runtime import storage

from app.db.qdrant import query

from app.schemas.retrieval import QueryRequest, RetrievedChunk

from app.errors.api import ApiError


def retrieve(question: str, file_id: UUID, top_k: int = 5) -> list[RetrievedChunk]:
    """Embed one validated question and map ranked matches within the requested file."""
    request = QueryRequest(question=question, top_k=top_k)
    services = storage()
    started = perf_counter()

    try:
        with services.encoding():
            entered = perf_counter()
            vectors = services.provider.embed([request.question])
            embedded = perf_counter() - entered

        if (
            len(vectors) != 1
            or len(vectors[0]) != services.provider.dimension
            or not all(isfinite(value) for value in vectors[0])
            or not any(vectors[0])
        ):
            raise ValueError(
                "Query embedding violates the dense vector contract")
    except Exception as error:
        logger.error(
            "Query embedding failed: file_id=%s top_k=%d reason=%s",
            file_id, request.top_k, type(error).__name__,
        )

        raise ApiError("Unable to embed retrieval question",
                       "INTERNAL_SERVER_ERROR") from error

    entered = perf_counter()
    points = query(services.client, services.collection,
                   vectors[0], file_id, request.top_k)
    queried = perf_counter() - entered

    try:
        results = []

        for point in points:
            if point.payload is None:
                raise ValueError("Retrieved point has no payload")

            result = RetrievedChunk.model_validate(
                {**point.payload, "score": point.score})

            if result.file_id != file_id:
                raise ValueError("Retrieved point violates file scope")

            results.append(result)
    except Exception as error:
        logger.error(
            "Retrieval payload invalid: file_id=%s top_k=%d reason=%s",
            file_id, request.top_k, type(error).__name__,
        )

        raise ApiError("Invalid retrieved chunk payload or file scope",
                       "INTERNAL_SERVER_ERROR") from error

    logger.info(
        "Retrieved file: file_id=%s top_k=%d count=%d scores=%s "
        "embedding_seconds=%.3f query_seconds=%.3f total_seconds=%.3f",
        file_id, request.top_k, len(
            results), [result.score for result in results],
        embedded, queried, perf_counter() - started,
    )

    return results
