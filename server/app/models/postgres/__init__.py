"""Register canonical identity, folder and file tables for Alembic metadata discovery."""

from app.models.postgres.user import User
from app.models.postgres.base import Base
from app.models.postgres.file import File
from app.models.postgres.folder import Folder
from app.models.postgres.session import Session
from app.models.postgres.verification import Verification

__all__ = ["Base", "File", "Folder", "Session", "User", "Verification"]
