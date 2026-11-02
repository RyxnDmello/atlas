from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint

from app.models.postgres.base import Base


class Verification(Base):
    """Map one current verification per user and purpose without OTP behavior."""

    __tablename__ = "verifications"
    __table_args__ = (UniqueConstraint("user_id", "type",
                      name="uq_verifications_user_id_type"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[Literal["auth", "reset", "forgot"]] = mapped_column(
        ENUM("auth", "reset", "forgot", name="verification_type"),
    )
    otp: Mapped[str] = mapped_column(String(6))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
