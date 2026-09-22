import os
from pathlib import Path

from dotenv import load_dotenv

from app.schemas.constants import AppConstants, LoggerConstants, QdrantConstants

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def _value(name: str) -> str | None:
    """Return one environment-backed setting."""

    return os.getenv(name)


class Constants:
    """Expose validated settings through the established nested API."""

    def __init__(self) -> None:
        app = AppConstants.model_validate(
            {
                "PORT": _value("PORT"),
            }
        )
        logger = LoggerConstants.model_validate(
            {
                "LOG_LEVEL": _value("LOG_LEVEL"),
            }
        )
        qdrant = QdrantConstants.model_validate(
            {
                "QDRANT_URL": _value("QDRANT_URL"),
                "QDRANT_HEALTHCHECK_RETRIES": _value("QDRANT_HEALTHCHECK_RETRIES"),
                "QDRANT_HEALTHCHECK_TIMEOUT": _value("QDRANT_HEALTHCHECK_TIMEOUT"),
                "QDRANT_HEALTHCHECK_INTERVAL": _value("QDRANT_HEALTHCHECK_INTERVAL"),
                "QDRANT_HEALTHCHECK_START_PERIOD": _value(
                    "QDRANT_HEALTHCHECK_START_PERIOD"
                ),
            }
        )

        self.app = _App(app.PORT)
        self.logger = _Logger(logger.LOG_LEVEL)
        self.qdrant = _Qdrant(
            qdrant.QDRANT_URL,
            qdrant.QDRANT_HEALTHCHECK_RETRIES,
            qdrant.QDRANT_HEALTHCHECK_TIMEOUT,
            qdrant.QDRANT_HEALTHCHECK_INTERVAL,
            qdrant.QDRANT_HEALTHCHECK_START_PERIOD,
        )


class _App:
    """Expose application settings under the app group."""

    def __init__(self, port: int) -> None:
        self.PORT = port


class _Logger:
    """Expose logging settings under the logger group."""

    def __init__(self, level: str) -> None:
        self.LOG_LEVEL = level


class _Qdrant:
    """Expose Qdrant settings under the qdrant group."""

    def __init__(
        self,
        url: str,
        retries: int,
        timeout: int,
        interval: int,
        start_period: int,
    ) -> None:
        self.QDRANT_URL = url
        self.QDRANT_HEALTHCHECK_RETRIES = retries
        self.QDRANT_HEALTHCHECK_TIMEOUT = timeout
        self.QDRANT_HEALTHCHECK_INTERVAL = interval
        self.QDRANT_HEALTHCHECK_START_PERIOD = start_period


constants = Constants()
