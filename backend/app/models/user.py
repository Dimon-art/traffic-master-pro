"""Модель пользователя."""

from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SqlEnum, String, Uuid, func

from app.db.base import Base


class UserRole(str, Enum):
    """Роль учётной записи."""

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """Учётная запись пользователя."""

    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(
        SqlEnum(
            UserRole,
            name="user_role",
            values_callable=lambda items: [item.value for item in items],
            native_enum=False,
        ),
        default=UserRole.USER,
        server_default=UserRole.USER.value,
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
