from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Return the API readiness state including database availability."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    finally:
        db.close()
