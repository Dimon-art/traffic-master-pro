"""Pydantic-схемы регистрации, входа и JWT-ответа."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class RegisterIn(BaseModel):
    """Тело запроса регистрации."""

    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None


class LoginIn(BaseModel):
    """Тело запроса входа."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Публичные данные пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime | None


class UserUpdateIn(BaseModel):
    """Частичное обновление пользователя администратором."""

    name: str | None = Field(default=None, max_length=100)
    role: UserRole | None = None
    is_active: bool | None = None


class TokenOut(BaseModel):
    """JWT и данные пользователя после входа или регистрации."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
