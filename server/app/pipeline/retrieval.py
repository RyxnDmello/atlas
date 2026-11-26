from uuid import UUID
from math import isfinite
from time import perf_counter

from qdrant_client.http.models import ScoredPoint

from app.core.logging import logger
from app.core.runtime import storage

from app.pipeline.storage import Storage
from app.db.qdrant import query, query_scoped

from app.schemas.scope import AuthorizedFileScope, FileSource
from app.schemas.retrieval import QueryRequest, RetrievedChunk

from app.errors.api import ApiError


def retrieve(question: str, file_id: UUID, top_k: int = 5) -> list[RetrievedChunk]:
    """Embed one validated question and map ranked matches within the requested file."""
    request = QueryRequest(question=question, top_k=top_k)
    services = storage()
    started = perf_counter()

    try:
        vector, embedded = _embed(services, request.question)
    except Exception as error:
        logger.error(
            "Query embedding failed: file_id=%s top_k=%d reason=%s",
            file_id, request.top_k, type(error).__name__,
        )

        raise ApiError("Unable to embed retrieval question",
                       "INTERNAL_SERVER_ERROR") from error

    entered = perf_counter()
    points = query(services.client, services.collection,
                   vector, file_id, request.top_k)
    queried = perf_counter() - entered

    try:
        results = _results(points, frozenset({file_id}))
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


def retrieve_scoped(question: str, scope: AuthorizedFileScope, top_k: int) -> list[RetrievedChunk]:
    """Search one complete server-authorized snapshot without rechecking canonical state."""
    if not isinstance(scope, AuthorizedFileScope) or not isinstance(scope.files, tuple):
        raise ValueError("An immutable authorized file scope is required")
    if any(not isinstance(source, FileSource)
           or not isinstance(source.file_id, UUID)
           or not isinstance(source.file_name, str) for source in scope.files):
        raise ValueError("Authorized scope contains invalid source metadata")
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise ValueError("top_k must be an integer in 1..20")

    request = QueryRequest(question=question, top_k=top_k)
    identifiers = scope.file_ids
    if not identifiers:
        return []

    services = storage()
    started = perf_counter()
    try:
        vector, embedded = _embed(services, request.question)
    except Exception as error:
        logger.error("Scoped query embedding failed: files=%d top_k=%d reason=%s",
                     len(identifiers), request.top_k, type(error).__name__)

        raise ApiError("Unable to embed retrieval question",
                       "INTERNAL_SERVER_ERROR") from error

    entered = perf_counter()
    points = query_scoped(services.client, services.collection,
                          vector, scope, request.top_k)
    queried = perf_counter() - entered
    try:
        results = _results(points, identifiers)
    except Exception as error:
        logger.error("Scoped retrieval payload invalid: files=%d top_k=%d reason=%s",
                     len(identifiers), request.top_k, type(error).__name__)

        raise ApiError("Invalid retrieved chunk payload or file scope",
                       "INTERNAL_SERVER_ERROR") from error

    logger.info(
        "Retrieved scope: files=%d top_k=%d count=%d scores=%s "
        "embedding_seconds=%.3f query_seconds=%.3f total_seconds=%.3f",
        len(identifiers), request.top_k, len(
            results), [item.score for item in results],
        embedded, queried, perf_counter() - started,
    )

    return results


def _embed(services: Storage, question: str) -> tuple[list[float], float]:
    """Reuse prepared inference and its ingestion lock; reject unsafe dense vectors."""
    with services.encoding():
        entered = perf_counter()
        vectors = services.provider.embed([question])
        elapsed = perf_counter() - entered

    if (len(vectors) != 1 or len(vectors[0]) != services.provider.dimension
            or not all(isfinite(value) for value in vectors[0]) or not any(vectors[0])):
        raise ValueError("Query embedding violates the dense vector contract")

    return vectors[0], elapsed


def _results(points: list[ScoredPoint], identifiers: frozenset[UUID]) -> list[RetrievedChunk]:
    """Validate every candidate before returning the original ranked sequence."""
    results = []
    for point in points:
        if point.payload is None:
            raise ValueError("Retrieved point has no payload")

        result = RetrievedChunk.model_validate(
            {**point.payload, "score": point.score})
        if result.file_id not in identifiers:
            raise ValueError("Retrieved point violates file scope")

        results.append(result)

    return results
