from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_authenticated_user, get_db
from app.exceptions import TodoNotFoundError
from app.models import Todo, User
from app.schemas import TodoCreate, TodoRead, TodoUpdate

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
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> list[Todo]:
    """Return todo items for the authenticated user with optional filtering and pagination."""
    query = db.query(Todo).filter(Todo.owner_id == current_user.id)
    if completed is not None:
        query = query.filter(Todo.completed.is_(completed))

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
