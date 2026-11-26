from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import postgres

from app.schemas.files.response import FileResponse
from app.schemas.folders.response import FolderResponse
from app.schemas.scope import AuthorizedFileScope, FileSource
from app.schemas.folders.listing import FolderListingResponse
from app.schemas.folders.requests import FolderCreate, FolderPatch

from app.models.postgres import File, Folder

from app.errors.postgres import PostgresOperationError
from app.errors.folder import FolderNotFoundError, FolderScopeLimitError


def owned(session: Session, folder_id: UUID, owner_id: UUID) -> Folder:
    """Resolve identity and owner together so foreign and missing are indistinguishable."""
    folder = session.scalar(select(Folder).where(
        Folder.id == folder_id, Folder.owner_id == owner_id))
    if folder is None:
        raise FolderNotFoundError()

    return folder


def resolve(owner_id: UUID, folder_id: UUID, *, max_files: int) -> AuthorizedFileScope:
    """Authorize a direct ready-file snapshot in one bounded, unlocked SQL read."""
    if not isinstance(owner_id, UUID) or not isinstance(folder_id, UUID):
        raise TypeError("Owner and folder must be UUIDs")
    if not isinstance(max_files, int) or isinstance(max_files, bool):
        raise TypeError("File ceiling must be an integer")
    if max_files <= 0:
        raise ValueError("File ceiling must be positive")

    try:
        with postgres().session() as session:
            rows = session.execute(
                select(Folder.id, File.id, File.name)
                .select_from(Folder)
                .outerjoin(File, and_(File.folder_id == Folder.id,
                                      File.owner_id == owner_id,
                                      File.status == "ready"))
                .where(Folder.id == folder_id, Folder.owner_id == owner_id)
                .order_by(File.id)
                .limit(max_files + 1)
                .execution_options(autoflush=False)
            ).all()
            if not rows:
                raise FolderNotFoundError()
            if len(rows) > max_files:
                raise FolderScopeLimitError()

            result = AuthorizedFileScope(tuple(
                FileSource(file_id, name) for _, file_id, name in rows
                if file_id is not None
            ))
    except SQLAlchemyError:
        raise PostgresOperationError() from None

    return result


def listing(owner_id: UUID, folder_id: UUID | None = None) -> FolderListingResponse:
    """Read only the owner's direct children; preserve every canonical file status."""
    try:
        with postgres().session() as session:
            folder = owned(session, folder_id,
                           owner_id) if folder_id is not None else None
            folders = session.scalars(select(Folder).where(
                Folder.owner_id == owner_id, Folder.parent_id == folder_id))
            files = session.scalars(select(File).where(
                File.owner_id == owner_id, File.folder_id == folder_id))

            return FolderListingResponse(
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
