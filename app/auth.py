import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy.orm import Session

from app.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

password_hasher = PasswordHash((BcryptHasher(),))


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return password_hasher.verify(plain_password, hashed_password)


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    """Create a signed JWT with the requested token type."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire, "type": token_type}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "access")


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT refresh token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_token(subject, expires_delta, "refresh")


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return a user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_current_user(db: Session, token: str, expected_type: str = "access") -> User:
    """Decode and validate a JWT token, then return the user."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if email is None:
            raise ValueError("Missing subject")
        if token_type != expected_type:
            raise ValueError("Invalid token type")
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    user = get_user_by_email(db, email)
    if user is None:
        raise ValueError("User not found")
    return user
