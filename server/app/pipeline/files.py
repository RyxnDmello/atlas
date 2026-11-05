from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.postgres import File
from app.core.runtime import postgres, storage

from app.schemas.drive.file import FileResponse
from app.schemas.drive.metadata import FilePatch

from app.errors.postgres import PostgresOperationError
from app.errors.file import FileNotFoundError, FileNotReadyError


def owned(session: Session, file_id: UUID, owner_id: UUID) -> File | None:
    """Lock an owner-scoped row so metadata writes cannot overwrite deletion state."""
    return session.scalar(select(File).where(
        File.id == file_id, File.owner_id == owner_id).with_for_update())


def ready(owner_id: UUID, file_id: UUID) -> UUID:
    """Authorize at request start and release the read session before any RAG work."""
    try:
        with postgres().session() as session:
            file = session.scalar(select(File).where(
                File.id == file_id, File.owner_id == owner_id))
            if file is None:
                raise FileNotFoundError()
            if file.status != "ready":
                raise FileNotReadyError()

            return file.id
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def update(owner_id: UUID, file_id: UUID, request: FilePatch) -> FileResponse:
    """Commit only supplied metadata on a ready file without consulting the index."""
    try:
        with postgres().session() as session:
            file = owned(session, file_id, owner_id)
            if file is None:
                raise FileNotFoundError()
            if file.status != "ready":
                raise FileNotReadyError()

            if request.name is not None:
                file.name = request.name
            if "description" in request.model_fields_set:
                file.description = request.description
            file.updated_at = datetime.now(timezone.utc)
            session.flush()
            result = FileResponse.model_validate(file)
            session.commit()

            return result
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def deleting(owner_id: UUID, file_id: UUID) -> None:
    """Commit the durable recovery marker before any derived index cleanup."""
    try:
        with postgres().session() as session:
            file = owned(session, file_id, owner_id)
            if file is None:
                raise FileNotFoundError()
            if file.status == "processing":
                raise FileNotReadyError()

            if file.status == "ready":
                file.status = "deleting"
                file.updated_at = datetime.now(timezone.utc)
            session.commit()
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def finish(owner_id: UUID, file_id: UUID) -> None:
    """Finalize confirmed cleanup; another authorized in-flight delete may finish first."""
    try:
        with postgres().session() as session:
            file = owned(session, file_id, owner_id)
            if file is not None:
                if file.status != "deleting":
                    raise FileNotReadyError()

                session.delete(file)
            session.commit()
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def delete(owner_id: UUID, file_id: UUID) -> None:
    """Resume exact-file deletion with no PostgreSQL session spanning Qdrant."""
    deleting(owner_id, file_id)
    storage().delete(file_id)
    finish(owner_id, file_id)
