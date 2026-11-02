from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.pipeline.drive import create, update
from app.pipeline.auth.current import current

from app.models.postgres import User
from app.routers.drive import DriveRoute

from app.schemas.drive.query import FolderQuery
from app.schemas.drive.folder import FolderResponse
from app.schemas.drive.requests import FolderCreate, FolderPatch


router = APIRouter(prefix="/folders", tags=["folders"], route_class=DriveRoute)


@router.post("", status_code=201, response_model=FolderResponse)
def creation(request: FolderCreate, query: Annotated[FolderQuery, Query()],
             user: Annotated[User, Depends(current)]) -> FolderResponse:
    """Create metadata only after authentication and owner-scoped parent resolution."""
    return create(user.id, request)


@router.patch("/{folder_id}", response_model=FolderResponse)
def patch(folder_id: UUID, request: FolderPatch, query: Annotated[FolderQuery, Query()],
          user: Annotated[User, Depends(current)]) -> FolderResponse:
    """Delegate the allowed metadata update without accepting a new location or owner."""
    return update(user.id, folder_id, request)
