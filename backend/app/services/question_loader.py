"""Загрузка банка вопросов и сценариев тренировки из knowledge base."""

import json
from functools import lru_cache
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


def _objection_scenarios_path() -> Path:
    """Путь к JSON-файлу сценариев возражений."""
    return Path(settings.knowledge_base_path) / "sales_calls_and_objections" / "objections.json"


@lru_cache(maxsize=1)
def load_objection_scenarios() -> list[dict]:
    """Читает список сценариев режима «Работа с возражениями».

    Returns:
        Список словарей сценариев из objections.json.

    Raises:
        FileNotFoundError: Если файл отсутствует.
        ValueError: Если JSON некорректный или нет сценариев.
    """
    path = _objection_scenarios_path()
    if not path.is_file():
        raise FileNotFoundError(f"Файл сценариев не найден: {path}")
    try:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError("Некорректный JSON банка возражений") from exc
    if not isinstance(data, dict):
        raise ValueError("Некорректный JSON банка возражений")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("Банк сценариев пуст")
    return scenarios
