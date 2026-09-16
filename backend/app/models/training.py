"""Модели сессии тренировки и сообщений диалога."""

from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class TrainingMode(str, Enum):
    """Режим тренировки."""

    PRODUCT_KNOWLEDGE = "product_knowledge"
    OBJECTIONS = "objections"
    NEEDS = "needs"
    SALES_CALL = "sales_call"
    PROPOSAL = "proposal"


class TrainingStatus(str, Enum):
    """Статус сессии тренировки."""

    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MessageRole(str, Enum):
    """Роль автора сообщения в диалоге."""

    AI = "ai"
    USER = "user"


class Training(Base):
    """Сессия тренировки менеджера."""

    __tablename__ = "trainings"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode = Column(
        SAEnum(
            TrainingMode,
            name="training_mode",
            native_enum=False,
            values_callable=lambda items: [item.value for item in items],
        ),
        nullable=False,
    )
    topic = Column(String(200), nullable=True)
    status = Column(
        SAEnum(
            TrainingStatus,
            name="training_status",
            native_enum=False,
            values_callable=lambda items: [item.value for item in items],
        ),
        default=TrainingStatus.STARTED,
        nullable=False,
    )
    current_question_index = Column(Integer, default=0, nullable=False)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship(
        "Message",
        back_populates="training",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    """Сообщение в диалоге тренировки: вопрос ИИ или ответ пользователя."""

    __tablename__ = "messages"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    training_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("trainings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(
        SAEnum(
            MessageRole,
            name="message_role",
            native_enum=False,
            values_callable=lambda items: [item.value for item in items],
        ),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    training = relationship("Training", back_populates="messages")
