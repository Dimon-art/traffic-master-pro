"""Классификация вопросов менеджера в режиме «Выявление потребностей»."""

from app.services.ai_client import ai_available

GOOD_SCORE_THRESHOLD = 6

_SUMMARY_MARKERS = (
    "правильно ли я понял",
    "правильно понял",
    "верно ли",
    "если я правильно",
    "то есть вы",
    "итак",
    "получается",
)

_OPEN_STEMS = (
    "что",
    "как",
    "какой",
    "какая",
    "какие",
    "почему",
    "зачем",
    "расскаж",
    "опиш",
    "подел",
    "подскаж",
    "объясн",
    "уточн",
    "раскро",
)

_PRICE_MARKERS = ("цена", "стоимость", "стоит", "сколько")


def _normalize(text: str) -> str:
    """Приводит текст к нижнему регистру для поиска маркеров."""
    return text.lower()


def _classify_question_mock(text: str, round_index: int = 0) -> dict:
    """Мок-классификация по типу вопроса (открытый / закрытый / цена).

    Args:
        text: Текст реплики менеджера.
        round_index: Номер раунда с нуля (цена рано — до третьего раунда).

    Returns:
        Словарь с флагами, оценкой 0-10 и feedback на русском.
    """
    lowered = _normalize(text)
    has_question_mark = "?" in text
    is_summary = any(marker in lowered for marker in _SUMMARY_MARKERS)
    has_open_stem = any(stem in lowered for stem in _OPEN_STEMS)
    # Стем открытого вопроса достаточен: в речи часто нет «?», см. «Расскажите…».
    is_open = has_open_stem and (has_question_mark or has_open_stem)
    is_closed = has_question_mark and not is_open
    has_price = any(marker in lowered for marker in _PRICE_MARKERS)
    is_price_premature = (
        round_index < 3 and has_price and not is_open and not is_summary
    )

    if is_summary:
        score = 9
        feedback = "Отличное резюмирование — клиент видит, что вы слушаете."
    elif is_open:
        score = 7
        feedback = "Хороший открытый вопрос — клиент раскрывается."
    elif is_closed:
        score = 3
        feedback = (
            "Закрытый вопрос — клиент даёт односложный ответ. Попробуйте открытый."
        )
    elif is_price_premature:
        score = 2
        feedback = "Цену рано называть — сначала выясните потребность."
    else:
        score = 1
        feedback = "Это не вопрос. Задайте открытый вопрос."

    return {
        "is_open": is_open,
        "is_closed": is_closed,
        "is_summary": is_summary,
        "is_price_premature": is_price_premature,
        "score": score,
        "feedback": feedback,
    }


def classify_question(
    text: str,
    round_index: int = 0,
    scenario_title: str = "",
    use_ai: bool = True,
) -> dict:
    """Классифицирует вопрос. При доступном ИИ — через DeepSeek, иначе мок.

    Args:
        text: Текст реплики менеджера.
        round_index: Номер раунда с нуля.
        scenario_title: Название сценария для промпта ИИ.
        use_ai: Пытаться ли вызвать DeepSeek.

    Returns:
        Словарь с флагами, оценкой 0-10 и feedback на русском.
    """
    if use_ai and ai_available():
        from app.services.ai_scorer import score_needs_answer_ai

        result = score_needs_answer_ai(
            scenario_title=scenario_title,
            manager_answer=text,
            round_index=round_index,
        )
        if result is not None:
            score = int(result["score"])
            return {
                "is_open": score >= 6,
                "is_closed": 2 <= score < 6,
                "is_summary": score >= 9,
                "is_price_premature": False,
                "score": score,
                "feedback": str(result.get("feedback", "")),
            }

    return _classify_question_mock(text, round_index)


def is_good_round(classification: dict) -> bool:
    """Раунд хороший, если оценка не ниже порога.

    Args:
        classification: Результат classify_question.

    Returns:
        True, если score >= 6.
    """
    return int(classification.get("score", 0)) >= GOOD_SCORE_THRESHOLD


def final_score_from_answers(scores: list[int]) -> int:
    """Считает итоговый балл 0-100 как средний балл раундов, умноженный на 10.

    Args:
        scores: Оценки отдельных раундов по шкале 0-10.

    Returns:
        Итог 0-100.
    """
    if not scores:
        return 0
    average = sum(scores) / len(scores)
    return max(0, min(100, round(average * 10)))


def client_ready(scores: list[int]) -> bool:
    """Клиент готов к предложению, если средний балл не ниже порога.

    Args:
        scores: Оценки отдельных раундов по шкале 0-10.

    Returns:
        True, если средний балл >= GOOD_SCORE_THRESHOLD.
    """
    if not scores:
        return False
    return (sum(scores) / len(scores)) >= GOOD_SCORE_THRESHOLD
