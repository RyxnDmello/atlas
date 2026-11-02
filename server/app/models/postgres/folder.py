from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Index, Text, UniqueConstraint

from app.models.postgres.base import Base


class Folder(Base):
    """Persist owner-scoped adjacency and metadata without hierarchy operations."""

    __tablename__ = "folders"
    __table_args__ = (
        UniqueConstraint("id", "owner_id", name="uq_folders_id_owner_id"),
        ForeignKeyConstraint(
            ["parent_id", "owner_id"], ["folders.id", "folders.owner_id"],
            ondelete="RESTRICT", name="fk_folders_parent_id_owner_id_folders"),
        Index("ix_folders_owner_id_parent_id", "owner_id", "parent_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"))
    parent_id: Mapped[UUID | None] = mapped_column()
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
