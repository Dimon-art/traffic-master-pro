"""Загрузка банка вопросов тренировки из knowledge base."""

import json
from pathlib import Path

from app.core.config import settings
from app.models.training import TrainingMode

_MODE_FOLDERS: dict[TrainingMode, str] = {
    TrainingMode.PRODUCT_KNOWLEDGE: "product_knowledge",
}


def questions_file_path(mode: TrainingMode) -> Path:
    """Возвращает путь к JSON-файлу вопросов для режима.

    Args:
        mode: Режим тренировки.

    Returns:
        Путь к файлу questions.json.

    Raises:
        FileNotFoundError: Если для режима нет банка вопросов.
    """
    folder = _MODE_FOLDERS.get(mode)
    if folder is None:
        raise FileNotFoundError(f"Для режима {mode.value} банк вопросов не задан")
    return Path(settings.knowledge_base_path) / folder / "questions.json"


def load_questions(mode: TrainingMode) -> list[dict]:
    """Читает список вопросов из JSON.

    Args:
        mode: Режим тренировки.

    Returns:
        Список словарей с ключами question, keywords, min_keywords.

    Raises:
        FileNotFoundError: Если файл отсутствует.
        ValueError: Если JSON пустой или не список.
    """
    path = questions_file_path(mode)
    if not path.is_file():
        raise FileNotFoundError(f"Файл вопросов не найден: {path}")
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list) or not data:
        raise ValueError("Банк вопросов пуст")
    return data
