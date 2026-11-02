from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.constants import constants


def configure_cors(app: FastAPI) -> None:
    """Register the configured browser-origin policy during application wiring."""
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["POST", "GET"],
        allow_headers=["Content-Type", "Authorization"],
        allow_origins=constants.cors.CORS_ORIGINS,
    )
