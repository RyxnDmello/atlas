from app.errors.api import ApiError


class InvalidAccessTokenError(ApiError):
    """Reject untrusted access credentials without library diagnostics."""

    def __init__(self) -> None:
        super().__init__("Invalid access token", "INVALID_ACCESS_TOKEN")


class CredentialError(ApiError):
    """Distinguish internal credential failures from ordinary password mismatch."""

    def __init__(self) -> None:
        super().__init__("Unable to process credentials", "INTERNAL_SERVER_ERROR")
