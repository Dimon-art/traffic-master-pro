"""Оценка ответов в режиме «Работа с возражениями»."""

from app.services.scorer import score_answer

GOOD_SCORE_THRESHOLD = 6


def score_objection_answer(answer: str, round_data: dict) -> dict:
    """Оценивает реплику менеджера в текущем раунде возражения.

    Args:
        answer: Текст ответа менеджера.
        round_data: Раунд сценария с expected_keywords и min_keywords.

    Returns:
        Оценка 0-10, ключевые слова, feedback и флаг is_good.
    """
    question = {
        "keywords": list(round_data.get("expected_keywords", [])),
        "min_keywords": int(round_data.get("min_keywords", 1)),
    }
    result = score_answer(answer, question)
    score = int(result["score"])
    result["is_good"] = score >= GOOD_SCORE_THRESHOLD
    return result


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
