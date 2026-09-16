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
    NeedsScenarioOut,
    ObjectionScenarioOut,
    TrainingDetailOut,
    TrainingOut,
    TrainingStartIn,
)
from app.services.needs_scorer import (
    classify_question,
    client_ready,
    final_score_from_answers as needs_final_score,
    is_good_round,
)
from app.services.objection_scorer import (
    client_accepts,
    final_score_from_answers,
    pick_client_reply,
    score_objection_answer,
)
from app.services.question_loader import (
    load_needs_scenarios,
    load_objection_scenarios,
    load_questions,
)
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


def _find_objection_scenario(topic: str) -> dict:
    """Ищет сценарий возражения по id или отдаёт HTTP-ошибку.

    Args:
        topic: Идентификатор сценария.

    Returns:
        Словарь сценария.
    """
    try:
        scenarios = load_objection_scenarios()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    scenario = next((item for item in scenarios if item.get("id") == topic), None)
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сценарий не найден",
        )
    return scenario


def _find_needs_scenario(topic: str) -> dict:
    """Ищет сценарий выявления потребностей по id или отдаёт HTTP-ошибку.

    Args:
        topic: Идентификатор сценария.

    Returns:
        Словарь сценария.
    """
    try:
        scenarios = load_needs_scenarios()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    scenario = next((item for item in scenarios if item.get("id") == topic), None)
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сценарий не найден",
        )
    return scenario


def _start_product_knowledge(
    payload: TrainingStartIn,
    db: Session,
    current_user: User,
) -> Training:
    """Стартует режим «Знание продукта»."""
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


def _start_objections(
    payload: TrainingStartIn,
    db: Session,
    current_user: User,
) -> Training:
    """Стартует режим «Работа с возражениями»."""
    if payload.topic is None or not str(payload.topic).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите сценарий",
        )
    scenario = _find_objection_scenario(str(payload.topic).strip())
    training = Training(
        user_id=current_user.id,
        mode=payload.mode,
        topic=str(scenario.get("id", payload.topic)).strip(),
        status=TrainingStatus.STARTED,
        current_question_index=0,
    )
    db.add(training)
    db.flush()
    db.add(
        Message(
            training_id=training.id,
            role=MessageRole.AI,
            content=str(scenario.get("opening", "")),
        )
    )
    db.commit()
    return _get_training_or_404(db, training.id)


def _start_needs(
    payload: TrainingStartIn,
    db: Session,
    current_user: User,
) -> Training:
    """Стартует режим «Выявление потребностей»."""
    if payload.topic is None or not str(payload.topic).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите сценарий",
        )
    scenario = _find_needs_scenario(str(payload.topic).strip())
    training = Training(
        user_id=current_user.id,
        mode=payload.mode,
        topic=str(scenario.get("id", payload.topic)).strip(),
        status=TrainingStatus.STARTED,
        current_question_index=0,
    )
    db.add(training)
    db.flush()
    db.add(
        Message(
            training_id=training.id,
            role=MessageRole.AI,
            content=str(scenario.get("opening", "")),
        )
    )
    db.commit()
    return _get_training_or_404(db, training.id)


def _collect_user_scores(training: Training, current_score: int) -> list[int]:
    """Собирает оценки пользователя вместе с только что посчитанной."""
    scores = [
        int(message.score)
        for message in training.messages
        if message.role == MessageRole.USER and message.score is not None
    ]
    if len(scores) < training.current_question_index:
        scores.append(current_score)
    return scores


def _submit_objection_answer(
    training: Training,
    payload: AnswerIn,
    db: Session,
) -> AnswerOut:
    """Принимает ответ в режиме возражений и двигает раунд."""
    scenario = _find_objection_scenario(str(training.topic or ""))
    rounds = scenario.get("rounds") or []
    index = training.current_question_index
    if index >= len(rounds) or index >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тренировка уже завершена",
        )
    round_data = rounds[index]
    score_data = score_objection_answer(payload.content, round_data)
    current_score = int(score_data["score"])
    db.add(
        Message(
            training_id=training.id,
            role=MessageRole.USER,
            content=payload.content,
            score=current_score,
        )
    )
    is_good = bool(score_data["is_good"])
    client_reply = pick_client_reply(is_good, round_data)
    training.current_question_index = index + 1
    if training.current_question_index < 5:
        training.status = TrainingStatus.IN_PROGRESS
        next_question = client_reply
        db.add(
            Message(
                training_id=training.id,
                role=MessageRole.AI,
                content=next_question,
            )
        )
    else:
        user_scores = _collect_user_scores(training, current_score)
        training.score = final_score_from_answers(user_scores)
        accepted = client_accepts(user_scores)
        final_text = str(scenario["final_good"] if accepted else scenario["final_bad"])
        db.add(
            Message(
                training_id=training.id,
                role=MessageRole.AI,
                content=final_text,
            )
        )
        training.status = TrainingStatus.COMPLETED
        training.completed_at = datetime.now(timezone.utc)
        next_question = final_text
    db.commit()
    training = _get_training_or_404(db, training.id)
    return AnswerOut(
        score=current_score,
        feedback=str(score_data["feedback"]),
        matched_keywords=list(score_data["matched_keywords"]),
        missed_keywords=list(score_data["missed_keywords"]),
        next_question=next_question,
        training=TrainingOut.model_validate(training),
    )


def _submit_needs_answer(
    training: Training,
    payload: AnswerIn,
    db: Session,
) -> AnswerOut:
    """Принимает вопрос менеджера в режиме выявления потребностей."""
    scenario = _find_needs_scenario(str(training.topic or ""))
    rounds = scenario.get("rounds") or []
    index = training.current_question_index
    if index >= len(rounds) or index >= 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тренировка уже завершена",
        )
    round_data = rounds[index]
    classification = classify_question(payload.content, index)
    current_score = int(classification["score"])
    db.add(
        Message(
            training_id=training.id,
            role=MessageRole.USER,
            content=payload.content,
            score=current_score,
        )
    )
    is_good = is_good_round(classification)
    client_reply = str(
        round_data["good_reply"] if is_good else round_data["bad_reply"]
    )
    training.current_question_index = index + 1
    if training.current_question_index < 7:
        training.status = TrainingStatus.IN_PROGRESS
        next_question = client_reply
        db.add(
            Message(
                training_id=training.id,
                role=MessageRole.AI,
                content=next_question,
            )
        )
    else:
        user_scores = _collect_user_scores(training, current_score)
        training.score = needs_final_score(user_scores)
        ready = client_ready(user_scores)
        final_text = str(scenario["final_good"] if ready else scenario["final_bad"])
        db.add(
            Message(
                training_id=training.id,
                role=MessageRole.AI,
                content=final_text,
            )
        )
        training.status = TrainingStatus.COMPLETED
        training.completed_at = datetime.now(timezone.utc)
        next_question = final_text
    db.commit()
    training = _get_training_or_404(db, training.id)
    return AnswerOut(
        score=current_score,
        feedback=str(classification["feedback"]),
        matched_keywords=[],
        missed_keywords=[],
        next_question=next_question,
        training=TrainingOut.model_validate(training),
    )


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
    if payload.mode == TrainingMode.PRODUCT_KNOWLEDGE:
        return _start_product_knowledge(payload, db, current_user)
    if payload.mode == TrainingMode.OBJECTIONS:
        return _start_objections(payload, db, current_user)
    if payload.mode == TrainingMode.NEEDS:
        return _start_needs(payload, db, current_user)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Режим ещё не реализован",
    )


@router.get("/objections/scenarios", response_model=list[ObjectionScenarioOut])
def list_objection_scenarios() -> list[ObjectionScenarioOut]:
    """Публичный список сценариев режима «Работа с возражениями»."""
    try:
        scenarios = load_objection_scenarios()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    return [
        ObjectionScenarioOut(
            id=str(item.get("id", "")),
            title=str(item.get("title", "")),
            description=str(item.get("description", "")),
        )
        for item in scenarios
    ]


@router.get("/needs/scenarios", response_model=list[NeedsScenarioOut])
def list_needs_scenarios() -> list[NeedsScenarioOut]:
    """Публичный список сценариев режима «Выявление потребностей»."""
    try:
        scenarios = load_needs_scenarios()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Банк сценариев недоступен",
        ) from exc
    return [
        NeedsScenarioOut(
            id=str(item.get("id", "")),
            title=str(item.get("title", "")),
            description=str(item.get("description", "")),
        )
        for item in scenarios
    ]


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


@router.delete("/{training_id}")
def delete_training(
    training_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Удаляет сессию тренировки владельцем или админом."""
    training = db.query(Training).filter(Training.id == training_id).first()
    if training is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена")
    _ensure_owner_or_admin(training, current_user)
    db.delete(training)
    db.commit()
    return {"status": "deleted"}


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
    if training.mode == TrainingMode.OBJECTIONS:
        return _submit_objection_answer(training, payload, db)
    if training.mode == TrainingMode.NEEDS:
        return _submit_needs_answer(training, payload, db)
    if training.mode != TrainingMode.PRODUCT_KNOWLEDGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Режим ещё не реализован",
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
