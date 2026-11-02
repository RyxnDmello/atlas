"""Register all canonical identity tables for Alembic metadata discovery."""

from app.models.postgres.base import Base
from app.models.postgres.session import Session
from app.models.postgres.user import User
from app.models.postgres.verification import Verification

__all__ = ["Base", "Session", "User", "Verification"]
