from pydantic import Field, SecretStr

from app.schemas.auth.verification import ResendRequest


class LoginRequest(ResendRequest):
    """Keep the shared canonical email and preserve literal password input."""

    password: SecretStr = Field(min_length=8, max_length=128)
