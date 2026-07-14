from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.exceptions import ChecklistItemNotFoundError, FolderNotFoundError, TodoNotFoundError


async def todo_not_found_handler(request: Request, exc: TodoNotFoundError) -> JSONResponse:
    """Return a consistent JSON response for missing todos."""
    return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": exc.message})


async def folder_not_found_handler(request: Request, exc: FolderNotFoundError) -> JSONResponse:
    """Return a consistent JSON response for missing folders."""
    return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": exc.message})


async def checklist_item_not_found_handler(request: Request, exc: ChecklistItemNotFoundError) -> JSONResponse:
    """Return a consistent JSON response for missing checklist items."""
    return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": exc.message})


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return a readable response for request validation errors."""
    return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"detail": exc.errors()})

