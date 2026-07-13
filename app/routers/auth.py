from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, create_refresh_token, get_current_user, get_user_by_email, hash_password, verify_password
from app.database import SessionLocal
from app.dependencies import get_current_authenticated_user
from app.models import User
from app.schemas import PasswordChange, RefreshTokenRequest, TokenResponse, UserCreate, UserLogin, UserRead

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
    refresh_token = create_refresh_token(subject=db_user.email)
    return TokenResponse(access_token=token, refresh_token=refresh_token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current authenticated user",
    description="Return the profile of the currently authenticated user using a bearer token.",
)
async def get_me(current_user: User = Depends(get_current_authenticated_user)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user


@router.post(
    "/refresh-token",
    response_model=TokenResponse,
    summary="Refresh an access token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Issue a new access token from a valid refresh token."""
    try:
        user = get_current_user(db, token_data.refresh_token, expected_type="refresh")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

    access_token = create_access_token(subject=user.email)
    return TokenResponse(access_token=access_token)


@router.post(
    "/change-password",
    summary="Change the current user's password",
    description="Update the password for the authenticated user after verifying the current password.",
)
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_authenticated_user),
) -> dict[str, str]:
    """Change the authenticated user's password."""
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password_data.current_password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    db_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
