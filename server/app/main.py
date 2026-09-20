from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.constants import constants

from app.routers.system import router as system
from app.routers.documents import router as documents

from app.errors.api import ApiError

app = FastAPI(title=constants.app.APP_NAME)

app.include_router(system)
app.include_router(documents)


@app.exception_handler(ApiError)
async def handle(request: Request, error: ApiError) -> JSONResponse:
    """Serialize an ApiError into its stable JSON response shape.

    Args:
        request: The request that produced the exception.
        error: The structured API error raised by a router.

    Returns:
        A JSON response containing the error message and code.
    """
    del request
    return JSONResponse(status_code=error.status, content=error.to_dict())
