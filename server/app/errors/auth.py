from app.errors.api import ApiError


class InvalidCredentialsError(ApiError):
    def __init__(self) -> None:
        super().__init__("Invalid credentials", "INVALID_CREDENTIALS")


class VerificationRequiredError(ApiError):
    def __init__(self) -> None:
        super().__init__("Verification required", "VERIFICATION_REQUIRED")


class InvalidRefreshTokenError(ApiError):
    def __init__(self) -> None:
        super().__init__("Invalid refresh token", "INVALID_REFRESH_TOKEN")


class InvalidAccessTokenError(ApiError):
    """Reject untrusted access credentials without library diagnostics."""

    def __init__(self) -> None:
        super().__init__("Invalid access token", "INVALID_ACCESS_TOKEN")


class AccountAlreadyExistsError(ApiError):
    """Expose account existence without disclosing verification state."""

    def __init__(self) -> None:
        super().__init__("Account already exists", "ACCOUNT_ALREADY_EXISTS")


class CredentialError(ApiError):
    """Distinguish internal credential failures from ordinary password mismatch."""

    def __init__(self) -> None:
        super().__init__("Unable to process credentials", "INTERNAL_SERVER_ERROR")


class AccountNotFoundError(ApiError):
    def __init__(self) -> None:
        super().__init__("Account not found", "ACCOUNT_NOT_FOUND")


class VerificationNotRequiredError(ApiError):
    def __init__(self) -> None:
        super().__init__("Verification not required", "VERIFICATION_NOT_REQUIRED")


class InvalidVerificationError(ApiError):
    def __init__(self) -> None:
        super().__init__("Invalid verification", "INVALID_VERIFICATION")


class VerificationExpiredError(ApiError):
    def __init__(self) -> None:
        super().__init__("Verification expired", "VERIFICATION_EXPIRED")
