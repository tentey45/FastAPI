from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_user_by_email, hash_password, verify_password
from app.database import SessionLocal
from app.dependencies import get_current_authenticated_user
from app.models import User
from app.schemas import TokenResponse, UserCreate, UserLogin, UserRead

router = APIRouter(tags=["auth"])


def get_db() -> Session:
    """Create a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with an email and password.",
)
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


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT",
    description="Authenticate a user and return a JWT access token for protected endpoints.",
)
async def login_user(user: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""
    db_user = get_user_by_email(db, user.email)
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=db_user.email)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user",
    description="Return the profile of the currently authenticated user using a bearer token.",
)
async def get_me(current_user: User = Depends(get_current_authenticated_user)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user
