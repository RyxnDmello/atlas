from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.pipeline.auth.current import current
from app.pipeline.folders import create, listing, update

from app.schemas.folders.query import FolderQuery
from app.schemas.folders.response import FolderResponse
from app.schemas.folders.listing import FolderListingResponse
from app.schemas.folders.requests import FolderCreate, FolderPatch

from app.models.postgres import User
from app.routers.validation import ValidationRoute

router = APIRouter(prefix="/folders",
                   tags=["folders"], route_class=ValidationRoute)


@router.get("", response_model=FolderListingResponse)
def root(query: Annotated[FolderQuery, Query()], user: Annotated[User, Depends(current)]) -> FolderListingResponse:
    """List the authenticated owner's logical root without accepting query selectors."""
    return listing(user.id)


@router.get("/{folder_id}", response_model=FolderListingResponse)
def browse(folder_id: UUID, query: Annotated[FolderQuery, Query()],
           user: Annotated[User, Depends(current)]) -> FolderListingResponse:
    """Resolve an owned folder and its direct children from canonical state."""
    return listing(user.id, folder_id)


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
