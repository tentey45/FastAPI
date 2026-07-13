from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    """Schema used to create a new todo item."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    completed: bool = False


class TodoRead(TodoCreate):
    """Schema used to return a todo item."""

    id: int


class TodoUpdate(BaseModel):
    """Schema used to update an existing todo item."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = None


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
