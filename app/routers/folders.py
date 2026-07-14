from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_authenticated_user, get_db
from app.exceptions import FolderNotFoundError
from app.models import Folder, User
from app.schemas import FolderCreate, FolderRead, FolderUpdate

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> Folder:
    """Create a new folder for the authenticated user."""
    db_folder = Folder(name=folder.name, owner_id=current_user.id)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder


@router.get("", response_model=list[FolderRead])
async def list_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> list[Folder]:
    """Return all folders belonging to the authenticated user."""
    return db.query(Folder).filter(Folder.owner_id == current_user.id).order_by(Folder.name).all()


@router.put("/{folder_id}", response_model=FolderRead)
async def update_folder(
    folder_id: int,
    folder_update: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> Folder:
    """Update folder name."""
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == current_user.id).first()
    if folder is None:
        raise FolderNotFoundError()

    folder.name = folder_update.name
    db.commit()
    db.refresh(folder)
    return folder


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> None:
    """Delete a folder by ID. This deletes all tasks inside it due to cascade delete."""
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == current_user.id).first()
    if folder is None:
        raise FolderNotFoundError()

    db.delete(folder)
    db.commit()
