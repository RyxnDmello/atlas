from typing import Callable, cast
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """Load and validate the environment-backed application settings."""

    APP_NAME: str = Field(min_length=1)
    LOG_LEVEL: str = Field(min_length=1)
    QDRANT_URL: str = Field(min_length=1)

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8",
    )

    @classmethod
    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, value: str) -> str:
        """Validate that the configured logging level is supported."""

        levels = {
            "INFO",
            "WARN",
            "FATAL",
            "DEBUG",
            "ERROR",
            "NOTSET",
            "WARNING",
            "CRITICAL",
        }

        if value.upper() not in levels:
            raise ValueError("LOG_LEVEL must be a supported logging level")

        return value

    @classmethod
    @field_validator("QDRANT_URL")
    def validate_qdrant_url(cls, value: str) -> str:
        """Validate that the Qdrant endpoint is an HTTP(S) URL."""

        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("QDRANT_URL must be a valid HTTP(S) URL")

        return value


def _load_settings() -> _Settings:
    """Create validated settings from the process environment and `.env`."""
    factory = cast(Callable[[], _Settings], _Settings)
    return factory()


class Constants:
    """Expose validated settings through the established nested API."""

    def __init__(self) -> None:
        settings = _load_settings()

        self.app = _App(settings.APP_NAME)
        self.logger = _Logger(settings.LOG_LEVEL)
        self.qdrant = _Qdrant(settings.QDRANT_URL)


class _App:
    """Expose application settings under the app group."""

    def __init__(self, name: str) -> None:
        self.APP_NAME = name


class _Logger:
    """Expose logging settings under the logger group."""

    def __init__(self, level: str) -> None:
        self.LOG_LEVEL = level


class _Qdrant:
    """Expose Qdrant settings under the qdrant group."""

    def __init__(self, url: str) -> None:
        self.QDRANT_URL = url


constants = Constants()
