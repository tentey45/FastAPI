from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_authenticated_user, get_db
from app.exceptions import ChecklistItemNotFoundError, TodoNotFoundError
from app.models import ChecklistItem, Todo, User
from app.schemas import (
    ChecklistItemCreate,
    ChecklistItemRead,
    ChecklistItemUpdate,
    TodoCreate,
    TodoRead,
    TodoUpdate,
)

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> Todo:
    """Create a new todo item for the authenticated user."""
    db_todo = Todo(**todo.model_dump(), owner_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.get("", response_model=list[TodoRead])
async def list_todos(
    completed: bool | None = Query(default=None),
    folder_id: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> list[Todo]:
    """Return todo items for the authenticated user with optional filtering and pagination."""
    query = db.query(Todo).filter(Todo.owner_id == current_user.id)
    if completed is not None:
        query = query.filter(Todo.completed.is_(completed))
    if folder_id is not None:
        query = query.filter(Todo.folder_id == folder_id)

    return query.order_by(Todo.id).offset(offset).limit(limit).all()


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> Todo:
    """Return a single todo item by id for the authenticated user."""
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if todo is None:
        raise TodoNotFoundError()
    return todo


@router.put("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> Todo:
    """Update an existing todo item for the authenticated user."""
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if todo is None:
        raise TodoNotFoundError()

    for field, value in todo_update.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> None:
    """Delete a todo item by id for the authenticated user."""
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if todo is None:
        raise TodoNotFoundError()

    db.delete(todo)
    db.commit()


@router.post("/{todo_id}/checklist", response_model=ChecklistItemRead, status_code=status.HTTP_201_CREATED)
async def create_checklist_item(
    todo_id: int,
    item: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> ChecklistItem:
    """Create a new checklist item for a todo task."""
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if todo is None:
        raise TodoNotFoundError()

    db_item = ChecklistItem(**item.model_dump(), todo_id=todo_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{todo_id}/checklist/{item_id}", response_model=ChecklistItemRead)
async def update_checklist_item(
    todo_id: int,
    item_id: int,
    item_update: ChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> ChecklistItem:
    """Update a checklist item's title or completed status."""
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if todo is None:
        raise TodoNotFoundError()

    db_item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id, ChecklistItem.todo_id == todo_id).first()
    if db_item is None:
        raise ChecklistItemNotFoundError()

    for field, value in item_update.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{todo_id}/checklist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(
    todo_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> None:
    """Delete a checklist item."""
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if todo is None:
        raise TodoNotFoundError()

    db_item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id, ChecklistItem.todo_id == todo_id).first()
    if db_item is None:
        raise ChecklistItemNotFoundError()

    db.delete(db_item)
    db.commit()

