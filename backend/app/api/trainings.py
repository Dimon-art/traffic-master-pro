"""Эндпоинты сессий тренировки и ответов менеджера."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.training import Message, MessageRole, Training, TrainingMode, TrainingStatus
from app.models.user import User, UserRole
from app.schemas.training import (
    AnswerIn,
    AnswerOut,
    TrainingDetailOut,
    TrainingOut,
    TrainingStartIn,
)
from app.services.question_loader import load_questions
from app.services.scorer import final_score, score_answer

router = APIRouter(prefix="/api/trainings", tags=["trainings"])


def _get_training_or_404(db: Session, training_id: UUID) -> Training:
    """Возвращает тренировку с сообщениями или 404.

    Args:
        db: Сессия SQLAlchemy.
        training_id: Идентификатор сессии.

    Returns:
        Тренировка.
    """
    training = (
        db.query(Training)
        .options(joinedload(Training.messages))
        .filter(Training.id == training_id)
        .first()
    )
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена")
    return training


def _ensure_owner_or_admin(training: Training, current_user: User) -> None:
    """Запрещает доступ, если пользователь не владелец и не админ."""
    if current_user.role != UserRole.ADMIN and training.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")


def _load_bank(mode: TrainingMode) -> list[dict]:
    """Загружает банк вопросов или отдаёт ошибку API.

    Args:
        mode: Режим тренировки.

    Returns:
        Список вопросов.
    """
    try:
        return load_questions(mode)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк вопросов недоступен",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк вопросов пуст",
        ) from exc


@router.post("/", response_model=TrainingDetailOut)
def start_training(
    payload: TrainingStartIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Training:
    """Стартует сессию и кладёт первый вопрос ИИ.

    Args:
        payload: Режим и необязательная тема.
        db: Сессия SQLAlchemy.
        current_user: Автор сессии.

    Returns:
        Созданная тренировка с первым сообщением.
    """
    if payload.mode != TrainingMode.PRODUCT_KNOWLEDGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот режим тренировки пока недоступен",
        )
    questions = _load_bank(payload.mode)
    training = Training(
        user_id=current_user.id,
        mode=payload.mode,
        topic=payload.topic,
        status=TrainingStatus.STARTED,
        current_question_index=0,
    )
    db.add(training)
    db.flush()
    first_question = str(questions[0].get("question", ""))
    db.add(
        Message(
            training_id=training.id,
            role=MessageRole.AI,
            content=first_question,
        )
    )
    db.commit()
    return _get_training_or_404(db, training.id)


@router.get("/", response_model=list[TrainingOut])
def list_trainings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Training]:
    """Список тренировок: свои или все для админа."""
    if current_user.role == UserRole.ADMIN:
        query = db.query(Training)
    else:
        query = db.query(Training).filter(Training.user_id == current_user.id)
    return query.order_by(Training.created_at.desc()).all()


@router.get("/{training_id}", response_model=TrainingDetailOut)
def get_training(
    training_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Training:
    """Возвращает сессию с историей сообщений."""
    training = _get_training_or_404(db, training_id)
    _ensure_owner_or_admin(training, current_user)
    return training


@router.post("/{training_id}/answers", response_model=AnswerOut)
def submit_answer(
    training_id: UUID,
    payload: AnswerIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnswerOut:
    """Принимает ответ, оценивает его и выдаёт следующий вопрос.

    Args:
        training_id: Идентификатор сессии.
        payload: Текст ответа менеджера.
        db: Сессия SQLAlchemy.
        current_user: Автор ответа.

    Returns:
        Оценка, разбор и следующий вопрос либо None.
    """
    training = _get_training_or_404(db, training_id)
    _ensure_owner_or_admin(training, current_user)
    if training.status == TrainingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тренировка уже завершена",
        )
    questions = _load_bank(training.mode)
    index = training.current_question_index
    if index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тренировка уже завершена",
        )
    question = questions[index]
    result = score_answer(payload.content, question)
    db.add(
        Message(
            training_id=training.id,
            role=MessageRole.USER,
            content=payload.content,
            score=int(result["score"]),
        )
    )
    next_index = index + 1
    training.current_question_index = next_index
    next_question: str | None = None
    if next_index < len(questions):
        training.status = TrainingStatus.IN_PROGRESS
        next_question = str(questions[next_index].get("question", ""))
        db.add(
            Message(
                training_id=training.id,
                role=MessageRole.AI,
                content=next_question,
            )
        )
    else:
        user_scores = [
            message.score
            for message in training.messages
            if message.role == MessageRole.USER and message.score is not None
        ]
        user_scores.append(int(result["score"]))
        training.status = TrainingStatus.COMPLETED
        training.score = final_score(user_scores)
        training.completed_at = datetime.now(timezone.utc)
    db.commit()
    training = _get_training_or_404(db, training.id)
    return AnswerOut(
        score=int(result["score"]),
        feedback=str(result["feedback"]),
        matched_keywords=list(result["matched_keywords"]),
        missed_keywords=list(result["missed_keywords"]),
        next_question=next_question,
        training=TrainingOut.model_validate(training),
    )
