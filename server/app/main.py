from fastapi import FastAPI

from app.core.constants import constants

from app.routers.system import router as system
from app.routers.documents import router as documents

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error, cast_handle_unexpected_error

app = FastAPI(title=constants.app.APP_NAME)

app.include_router(system)
app.include_router(documents)

app.add_exception_handler(ApiError, cast_handle_api_error())
app.add_exception_handler(Exception, cast_handle_unexpected_error())
