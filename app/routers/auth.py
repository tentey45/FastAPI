from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_user_by_email, hash_password, verify_password
from app.database import SessionLocal
from app.dependencies import get_current_authenticated_user
from app.models import User
from app.schemas import UserCreate, UserLogin, UserRead

router = APIRouter(tags=["auth"])


def get_db() -> Session:
    """Create a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user."""
    existing_user = get_user_by_email(db, user.email)
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(email=user.email, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)) -> dict[str, str]:
    """Authenticate a user and return a JWT access token."""
    db_user = get_user_by_email(db, user.email)
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=db_user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_authenticated_user)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user
