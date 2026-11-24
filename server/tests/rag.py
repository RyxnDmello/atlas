"""Local canonical RAG fixtures; never connect to configured PostgreSQL or Qdrant."""
from uuid import UUID
from typing import Literal
from datetime import datetime, timezone

from app.db.postgres import Database
from app.core.runtime import activate

from app.pipeline.files import ready
from app.pipeline.storage import Storage
from app.pipeline.retrieval import retrieve

from app.models.postgres import File
from app.schemas.retrieval import QueryRequest, RetrievedChunk


def seed(database: Database, owner: UUID, identifier: UUID,
         status: Literal["processing", "ready", "deleting"] = "ready") -> None:
    """Create explicit canonical state for synthetic HTTP retrieval fixtures."""
    now = datetime.now(timezone.utc)
    with database.session() as session:
        session.add(File(id=identifier, owner_id=owner, name="Synthetic",
                         original_name="synthetic.md", extension=".md", size_bytes=1,
                         status=status, created_at=now, updated_at=now))
        session.commit()


def retrieved(database: Database, storage: Storage, owner: UUID, identifier: UUID,
              question: str = "question", top_k: int = 5) -> list[RetrievedChunk]:
    """Exercise canonical authorization and internal retrieval, never a public query alias."""
    request = QueryRequest(question=question, top_k=top_k)
    with activate(storage, database):
        ready(owner, identifier)

        return retrieve(request.question, identifier, request.top_k)
