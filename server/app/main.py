from fastapi import FastAPI

from app.core.lifespan import lifespan

from app.routers.documents import router as documents
from app.routers.system import router as system

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error, cast_handle_unexpected_error

app = FastAPI(lifespan=lifespan)

app.include_router(system)
app.include_router(documents)

app.add_exception_handler(ApiError, cast_handle_api_error())
app.add_exception_handler(Exception, cast_handle_unexpected_error())
