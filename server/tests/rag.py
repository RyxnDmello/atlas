"""Local canonical RAG fixtures; never connect to configured PostgreSQL or Qdrant."""
from uuid import UUID
from typing import Literal
from datetime import datetime, timezone

from app.db.postgres import Database

from app.models.postgres import File


def seed(database: Database, owner: UUID, identifier: UUID,
         status: Literal["processing", "ready", "deleting"] = "ready") -> None:
    """Create explicit canonical state for synthetic HTTP retrieval fixtures."""
    now = datetime.now(timezone.utc)
    with database.session() as session:
        session.add(File(id=identifier, owner_id=owner, name="Synthetic",
                         original_name="synthetic.md", extension=".md", size_bytes=1,
                         status=status, created_at=now, updated_at=now))
        session.commit()
