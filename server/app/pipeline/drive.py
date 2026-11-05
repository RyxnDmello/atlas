from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import postgres

from app.schemas.drive.file import FileResponse
from app.schemas.drive.folder import FolderResponse
from app.schemas.drive.listing import DriveResponse
from app.schemas.drive.requests import FolderCreate, FolderPatch

from app.models.postgres import File, Folder

from app.errors.folder import FolderNotFoundError
from app.errors.postgres import PostgresOperationError


def owned(session: Session, folder_id: UUID, owner_id: UUID) -> Folder:
    """Resolve identity and owner together so foreign and missing are indistinguishable."""
    folder = session.scalar(select(Folder).where(
        Folder.id == folder_id, Folder.owner_id == owner_id))
    if folder is None:
        raise FolderNotFoundError()

    return folder


def listing(owner_id: UUID, folder_id: UUID | None = None) -> DriveResponse:
    """Read only the owner's direct children; preserve every canonical file status."""
    try:
        with postgres().session() as session:
            folder = owned(session, folder_id,
                           owner_id) if folder_id is not None else None
            folders = session.scalars(select(Folder).where(
                Folder.owner_id == owner_id, Folder.parent_id == folder_id))
            files = session.scalars(select(File).where(
                File.owner_id == owner_id, File.folder_id == folder_id))

            return DriveResponse(
                folder=FolderResponse.model_validate(
                    folder) if folder is not None else None,
                folders=[FolderResponse.model_validate(
                    item) for item in folders],
                files=[FileResponse.model_validate(item) for item in files],
            )
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def create(owner_id: UUID, request: FolderCreate) -> FolderResponse:
    """Authorize the optional parent before writing, then commit one canonical folder."""
    try:
        with postgres().session() as session:
            if request.parent_id is not None:
                owned(session, request.parent_id, owner_id)

            now = datetime.now(timezone.utc)
            folder = Folder(owner_id=owner_id, parent_id=request.parent_id,
                            name=request.name, description=request.description,
                            created_at=now, updated_at=now)
            session.add(folder)
            session.flush()
            result = FolderResponse.model_validate(folder)
            session.commit()

            return result
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def update(owner_id: UUID, folder_id: UUID, request: FolderPatch) -> FolderResponse:
    """Patch only supplied metadata while preserving identity, ownership and location."""
    try:
        with postgres().session() as session:
            folder = owned(session, folder_id, owner_id)
            if request.name is not None:
                folder.name = request.name
            if "description" in request.model_fields_set:
                folder.description = request.description
            folder.updated_at = datetime.now(timezone.utc)
            session.flush()
            result = FolderResponse.model_validate(folder)
            session.commit()

            return result
    except SQLAlchemyError:
        raise PostgresOperationError() from None
