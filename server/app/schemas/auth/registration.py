from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, StringConstraints, field_validator


class RegistrationRequest(BaseModel):
    """Validate identity input while preserving the literal password."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    name: Annotated[str, StringConstraints(
        strip_whitespace=True, min_length=1, max_length=100)]
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def canonicalize(cls, value: str) -> str:
        """Lowercase the validator's normalized result without provider rewrites."""
        return value.lower()


class RegistrationResponse(BaseModel):
    """Registration requests verification without authenticating the account."""

    status: Literal["verification_required"] = "verification_required"
