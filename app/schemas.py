from pydantic import BaseModel, ConfigDict, Field


class ChecklistItemCreate(BaseModel):
    """Schema used to create a new checklist item."""

    title: str = Field(..., min_length=1, max_length=255)
    completed: bool = False


class ChecklistItemRead(ChecklistItemCreate):
    """Schema used to return a checklist item."""

    id: int
    todo_id: int

    model_config = ConfigDict(from_attributes=True)


class ChecklistItemUpdate(BaseModel):
    """Schema used to update an existing checklist item."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    completed: bool | None = None


class FolderCreate(BaseModel):
    """Schema used to create a new folder."""

    name: str = Field(..., min_length=1, max_length=255)


class FolderRead(FolderCreate):
    """Schema used to return a folder."""

    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class FolderUpdate(BaseModel):
    """Schema used to update a folder."""

    name: str = Field(..., min_length=1, max_length=255)


class TodoCreate(BaseModel):
    """Schema used to create a new todo item."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    completed: bool = False
    folder_id: int | None = None


class TodoRead(TodoCreate):
    """Schema used to return a todo item."""

    id: int
    checklist_items: list[ChecklistItemRead] = []

    model_config = ConfigDict(from_attributes=True)


class TodoUpdate(BaseModel):
    """Schema used to update an existing todo item."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None
    folder_id: int | None = None


class TodoListQuery(BaseModel):
    """Optional query parameters for filtering and paginating todos."""

    completed: bool | None = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class UserCreate(BaseModel):
    """Schema used to register a new user."""

    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)


class UserLogin(BaseModel):
    """Schema used to log in an existing user."""

    email: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)


class UserRead(BaseModel):
    """Schema used to return a user profile."""

    id: int
    email: str


class TokenResponse(BaseModel):
    """Schema used to return JWT tokens."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class RefreshTokenRequest(BaseModel):
    """Schema used to request a new access token from a refresh token."""

    refresh_token: str = Field(..., min_length=1)


class PasswordChange(BaseModel):
    """Schema used to change an authenticated user's password."""

    current_password: str = Field(..., min_length=6, max_length=255)
    new_password: str = Field(..., min_length=6, max_length=255)
