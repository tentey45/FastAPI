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
    """Schema used to return a JWT access token."""

    access_token: str
    token_type: str = "bearer"


class PasswordChange(BaseModel):
    """Schema used to change an authenticated user's password."""

    current_password: str = Field(..., min_length=6, max_length=255)
    new_password: str = Field(..., min_length=6, max_length=255)
