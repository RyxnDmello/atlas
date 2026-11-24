from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import logger
from app.core.runtime import postgres, storage

from app.pipeline.folders import owned
from app.pipeline.ingestion import ingest, validate

from app.schemas.files.upload import FileUpload
from app.schemas.files.response import FileResponse

from app.models.postgres import File

from app.errors.api import ApiError
from app.errors.postgres import PostgresOperationError


def processing(owner_id: UUID, request: FileUpload, filename: str,
               extension: str, size: int) -> UUID:
    """Authorize location and durably create canonical state before cross-store work."""
    try:
        with postgres().session() as session:
            if request.folder_id is not None:
                owned(session, request.folder_id, owner_id)

            identifier = uuid4()
            now = datetime.now(timezone.utc)
            session.add(File(id=identifier, owner_id=owner_id, folder_id=request.folder_id,
                             name=request.name, description=request.description,
                             original_name=filename, extension=extension, size_bytes=size,
                             status="processing", created_at=now, updated_at=now))
            session.commit()

        return identifier
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def ready(identifier: UUID, owner_id: UUID) -> FileResponse:
    """Publish ready metadata only after a fresh finalization transaction commits."""
    try:
        with postgres().session() as session:
            file = session.scalar(select(File).where(
                File.id == identifier, File.owner_id == owner_id,
                File.status == "processing").with_for_update())
            if file is None:
                raise PostgresOperationError()

            file.status = "ready"
            file.updated_at = datetime.now(timezone.utc)
            session.flush()
            result = FileResponse.model_validate(file)
            session.commit()

        return result
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def compensate(identifier: UUID, owner_id: UUID, finalizing: bool) -> None:
    """Retain a non-ready recovery marker until exact derived cleanup is confirmed.

    Reconcile even an ambiguous ready-commit acknowledgement before deleting vectors:
    the UUID is private to this upload, so a committed ready row can be restored to
    processing safely. If that cannot be confirmed, leave the index intact.
    """
    try:
        if finalizing:
            with postgres().session() as session:
                file = session.scalar(select(File).where(
                    File.id == identifier, File.owner_id == owner_id).with_for_update())
                if file is not None:
                    if file.status not in {"processing", "ready"}:
                        raise PostgresOperationError()
                    file.status = "processing"
                    file.updated_at = datetime.now(timezone.utc)
                session.commit()

        storage().delete(identifier)

        with postgres().session() as session:
            session.execute(delete(File).where(
                File.id == identifier, File.owner_id == owner_id, File.status == "processing"))
            session.commit()
    except Exception as error:
        logger.error("Upload compensation incomplete: file_id=%s category=%s",
                     identifier, type(error).__name__)


def upload(owner_id: UUID, request: FileUpload, content: bytes, filename: str) -> FileResponse:
    """Coordinate short PostgreSQL transactions around the existing synchronous RAG pipeline."""
    extension = validate(content, filename)
    identifier = processing(owner_id, request, filename,
                            extension, len(content))
    finalizing = False

    try:
        ingest(content, filename, extension, identifier)
        finalizing = True

        return ready(identifier, owner_id)
    except Exception as error:
        compensate(identifier, owner_id, finalizing)
        logger.error("Upload failed: file_id=%s category=%s",
                     identifier, type(error).__name__)
        if isinstance(error, ApiError):
            raise

        raise ApiError("Unable to ingest uploaded file",
                       "INTERNAL_SERVER_ERROR") from None
