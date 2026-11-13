from fastapi import FastAPI

from app.core.cors import configure_cors
from app.core.lifespan import lifespan

from app.routers.auth import router as auth
from app.routers.files import router as files
from app.routers.system import router as system
from app.routers.folders import router as folders

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error, cast_handle_unexpected_error

app = FastAPI(lifespan=lifespan)

configure_cors(app)

app.include_router(auth)
app.include_router(files)
app.include_router(system)
app.include_router(folders)

app.add_exception_handler(ApiError, cast_handle_api_error())
app.add_exception_handler(Exception, cast_handle_unexpected_error())
