from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints, field_validator


class ResendRequest(BaseModel):
    """Accept a canonical account email for auth verification replacement."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    email: EmailStr

    @field_validator("email")
    @classmethod
    def canonicalize(cls, value: str) -> str:
        return value.lower()


class VerifyRequest(ResendRequest):
    """Require an exact string OTP, including any leading zeroes."""

    otp: Annotated[str, StringConstraints(pattern=r"^[0-9]{6}$", strict=True)]


class VerifiedUser(BaseModel):
    id: UUID
    name: str
    email: str


class VerifyResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: VerifiedUser
