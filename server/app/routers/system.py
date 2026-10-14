import time

from fastapi import APIRouter

from app.core.logging import logger
from app.core.runtime import storage

from app.db.qdrant import check, details

from app.schemas.system import DatabaseHealth, DiagnosticError, QdrantHealth

from app.errors.api import ApiError

router = APIRouter(prefix="/system", tags=["system"])

TIME = time.monotonic()


@router.get("/health/databases", response_model=DatabaseHealth, response_model_exclude_unset=True)
def databases() -> DatabaseHealth:
    """Report collection access and minimal metadata with startup resources and HTTP 200."""
    try:
        services = storage()
        collection = check(services.client, services.collection)
    except ApiError as error:
        logger.exception(
            "Qdrant health check: status=unhealthy code=%s", error.code)

        return DatabaseHealth(qdrant=QdrantHealth(status="unhealthy", error=error.message, code=error.code))

    try:
        version, started, uptime = details(services.client)

        result = QdrantHealth(
            version=version, status="Qdrant Healthy",
            uptime=f"Running For {uptime:.2f}s",
            started=started.strftime("%Y-%m-%d, %H:%M:%S"), collection=collection,
        )
    except ApiError as error:
        logger.warning(
            "Qdrant telemetry failed: status=healthy code=%s", error.code, exc_info=True
        )

        result = QdrantHealth(
            version=None, status="Qdrant Healthy", uptime=None, started=None,
            collection=collection,
            diagnostics_error=DiagnosticError(
                error=error.message, code=error.code),
        )

    logger.info("Qdrant health check: status=healthy collection=%s",
                services.collection)

    return DatabaseHealth(qdrant=result)


@router.get("/health")
def health() -> dict[str, str]:
    """Return a liveness response for the running API process.

    Returns:
        The version, status, and uptime of the server.
    """
    uptime = round(time.monotonic() - TIME, 2)

    return {
        "version": "1.0.0",
        "status": "Server Healthy",
        "uptime": f"Running For {uptime}s",
    }
