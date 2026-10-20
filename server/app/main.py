from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.lifespan import lifespan
from app.core.constants import constants

from app.routers.files import router as files
from app.routers.system import router as system
from app.routers.documents import router as documents

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error, cast_handle_unexpected_error

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=constants.cors.CORS_ORIGINS,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)

app.include_router(files)
app.include_router(system)
app.include_router(documents)

app.add_exception_handler(ApiError, cast_handle_api_error())
app.add_exception_handler(Exception, cast_handle_unexpected_error())
