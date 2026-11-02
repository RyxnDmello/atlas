from app.errors.api import ApiError


class PostgresOperationError(ApiError):
    """Keep SQL, parameters, and driver diagnostics outside public errors/logs."""

    def __init__(self) -> None:
        super().__init__("Unable to complete database operation", "POSTGRES_OPERATION_FAILED")


class PostgresConnectionError(ApiError):
    """Report PostgreSQL unavailability without exposing driver details."""

    def __init__(self) -> None:
        """Use the same safe message for startup and connectivity diagnostics."""
        super().__init__("Unable to connect to PostgreSQL", "POSTGRES_CONNECTION_FAILED")
