from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Index, Text

from app.models.postgres.base import Base


class File(Base):
    """Persist canonical file metadata and legal states without ingestion behavior."""

    __tablename__ = "files"
    __table_args__ = (
        ForeignKeyConstraint(
            ["folder_id", "owner_id"], ["folders.id", "folders.owner_id"],
            ondelete="RESTRICT", name="fk_files_folder_id_owner_id_folders"),
        CheckConstraint("size_bytes >= 0",
                        name="ck_files_size_bytes_nonnegative"),
        Index("ix_files_owner_id_folder_id", "owner_id", "folder_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"))
    folder_id: Mapped[UUID | None] = mapped_column()
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    original_name: Mapped[str] = mapped_column(Text)
    extension: Mapped[str] = mapped_column(Text)
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[Literal["processing", "ready", "deleting"]] = mapped_column(
        ENUM("processing", "ready", "deleting", name="file_status"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
