"""Модель заявки (лида)."""

from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum as SqlEnum, ForeignKey, String, Text, Uuid, func

from app.db.base import Base


class LeadStatus(str, Enum):
    """Статус заявки."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    REJECTED = "rejected"


class Lead(Base):
    """Заявка на консультацию."""

    __tablename__ = "leads"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(
        SqlEnum(
            LeadStatus,
            name="lead_status",
            values_callable=lambda items: [item.value for item in items],
            native_enum=False,
        ),
        default=LeadStatus.NEW,
        server_default=LeadStatus.NEW.value,
        nullable=False,
    )
    created_by = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
