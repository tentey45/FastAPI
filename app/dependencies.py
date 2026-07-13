from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import SessionLocal
from app.models import User

security = HTTPBearer()


def get_db() -> Session:
    """Create a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Return the authenticated user from the Authorization header."""
    token = credentials.credentials
    try:
        user = get_current_user(db, token, expected_type="access")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials") from exc
    return user
