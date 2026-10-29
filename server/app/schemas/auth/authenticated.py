from uuid import UUID

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    id: UUID
    name: str
    email: str


class AuthenticatedResponse(BaseModel):
    access_token: str
    user: AuthenticatedUser
