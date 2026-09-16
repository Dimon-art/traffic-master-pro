"""Pydantic-схемы сессий тренировки и ответов менеджера."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.training import MessageRole, TrainingMode, TrainingStatus


class TrainingStartIn(BaseModel):
    """Тело запроса на запуск тренировки."""

    mode: TrainingMode
    topic: str | None = Field(default=None, max_length=200)


class MessageOut(BaseModel):
    """Сообщение диалога в ответе API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: MessageRole
    content: str
    score: int | None = None
    created_at: datetime


class TrainingOut(BaseModel):
    """Краткие данные сессии тренировки."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    mode: TrainingMode
    topic: str | None
    status: TrainingStatus
    current_question_index: int
    score: int | None
    created_at: datetime
    completed_at: datetime | None


class TrainingDetailOut(TrainingOut):
    """Сессия тренировки вместе с историей сообщений."""

    messages: list[MessageOut] = []


class AnswerIn(BaseModel):
    """Ответ менеджера на текущий вопрос."""

    content: str = Field(min_length=1, max_length=4000)


class AnswerOut(BaseModel):
    """Ответ на вопрос: оценка и что ИИ понял."""

    score: int
    feedback: str
    matched_keywords: list[str]
    missed_keywords: list[str]
    next_question: str | None
    training: TrainingOut


class ObjectionScenarioOut(BaseModel):
    """Краткая карточка сценария возражения для каталога."""

    id: str
    title: str
    description: str
