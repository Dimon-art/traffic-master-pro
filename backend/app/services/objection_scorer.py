"""Оценка ответов в режиме «Работа с возражениями»."""

from app.services.ai_client import ai_available
from app.services.scorer import score_answer

GOOD_SCORE_THRESHOLD = 6


def _score_objection_answer_mock(answer: str, round_data: dict) -> dict:
    """Мок-оценка по ключевым словам раунда."""
    question = {
        "keywords": list(round_data.get("expected_keywords", [])),
        "min_keywords": int(round_data.get("min_keywords", 1)),
    }
    result = score_answer(answer, question, use_ai=False)
    score = int(result["score"])
    result["is_good"] = score >= GOOD_SCORE_THRESHOLD
    return result


def score_objection_answer(
    answer: str,
    round_data: dict,
    objection_title: str = "",
    round_index: int = 0,
    use_ai: bool = True,
) -> dict:
    """Оценивает ответ. При доступном ИИ — через DeepSeek, иначе мок.

    Args:
        answer: Текст ответа менеджера.
        round_data: Раунд сценария с expected_keywords и min_keywords.
        objection_title: Название возражения для промпта ИИ.
        round_index: Номер раунда с нуля.
        use_ai: Пытаться ли вызвать DeepSeek.

    Returns:
        Оценка 0-10, ключевые слова, feedback и флаг is_good.
    """
    if use_ai and ai_available():
        from app.services.ai_scorer import score_objection_answer_ai

        result = score_objection_answer_ai(
            objection_title=objection_title,
            manager_answer=answer,
            round_index=round_index,
        )
        if result is not None:
            result["is_good"] = int(result["score"]) >= GOOD_SCORE_THRESHOLD
            return result

    return _score_objection_answer_mock(answer, round_data)


def pick_client_reply(is_good: bool, round_data: dict) -> str:
    """Выбирает реплику клиента в зависимости от качества ответа.

    Args:
        is_good: True, если ответ менеджера набрал порог.
        round_data: Раунд сценария с client_reply_if_good / client_reply_if_bad.

    Returns:
        Текст реплики клиента.
    """
    if is_good:
        return str(round_data.get("client_reply_if_good", ""))
    return str(round_data.get("client_reply_if_bad", ""))


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


def client_accepts(scores: list[int]) -> bool:
    """Клиент принимает предложение, если средний балл не ниже порога.

    Args:
        scores: Оценки отдельных раундов по шкале 0-10.

    Returns:
        True, если средний балл >= GOOD_SCORE_THRESHOLD.
    """
    if not scores:
        return False
    return (sum(scores) / len(scores)) >= GOOD_SCORE_THRESHOLD
