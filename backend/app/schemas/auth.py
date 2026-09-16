"""Pydantic-схемы регистрации, входа и JWT-ответа."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    created_at: datetime | None


class TokenOut(BaseModel):
    """JWT и данные пользователя после входа или регистрации."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
