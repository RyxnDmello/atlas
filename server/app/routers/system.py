import time

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])

TIME = time.monotonic()


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
