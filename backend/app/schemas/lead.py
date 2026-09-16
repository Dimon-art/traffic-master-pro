"""Pydantic-схемы заявок."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.lead import LeadStatus


class LeadCreateIn(BaseModel):
    """Тело запроса на создание заявки."""

    name: str = Field(min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    comment: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def require_phone_or_email(self) -> "LeadCreateIn":
        """Требует хотя бы один контакт: телефон или email.

        Returns:
            Проверенная модель.

        Raises:
            ValueError: Если не указаны ни телефон, ни email.
        """
        phone = (self.phone or "").strip()
        if not phone and self.email is None:
            raise ValueError("Укажите телефон или email")
        return self


class LeadUpdateIn(BaseModel):
    """Частичное обновление заявки."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    comment: str | None = Field(default=None, max_length=2000)
    status: LeadStatus | None = None


class LeadOut(BaseModel):
    """Публичные данные заявки."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    phone: str | None
    email: str | None
    comment: str | None
    status: LeadStatus
    created_at: datetime | None
    updated_at: datetime | None
    created_by: UUID
