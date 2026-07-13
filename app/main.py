import logging

from fastapi import FastAPI

from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.error_handlers import todo_not_found_handler, validation_exception_handler
from app.exceptions import TodoNotFoundError
from app.logging_config import setup_logging
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.todos import router as todos_router

settings = get_settings()
setup_logging(settings.log_level)

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(todos_router)
app.add_exception_handler(TodoNotFoundError, todo_not_found_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/")
async def read_root() -> dict[str, str]:
    """Return a welcome message for the API."""
    logger.info("Root endpoint was called")
    return {"message": f"Welcome to the {settings.app_name}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
