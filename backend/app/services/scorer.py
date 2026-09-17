"""Оценка ответов менеджера: DeepSeek с fallback на ключевые слова."""

import re

from app.services.ai_client import ai_available


def _normalize(text: str) -> str:
    """Приводит текст к нижнему регистру и убирает пунктуацию.

    Args:
        text: Исходный ответ менеджера.

    Returns:
        Нормализованная строка без знаков препинания.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _score_answer_mock(answer: str, question: dict) -> dict:
    """Мок-оценка 0-10 по совпадениям с keywords.

    Args:
        answer: Текст ответа менеджера.
        question: Словарь с ключами keywords (list) и min_keywords (int).

    Returns:
        Словарь со score, matched_keywords, missed_keywords и feedback.
    """
    keywords = [k.lower() for k in question.get("keywords", [])]
    min_kw = int(question.get("min_keywords", 1))
    normalized = _normalize(answer)

    matched = [k for k in keywords if k.lower() in normalized]
    missed = [k for k in keywords if k.lower() not in normalized]

    if not keywords:
        score = 5
    else:
        score = round(len(matched) / len(keywords) * 10)

    if len(matched) < min_kw:
        feedback = (
            f"Ответ слишком короткий или упускает ключевые моменты. "
            f"Найдено: {len(matched)} из {len(keywords)}. "
            f"Не хватает: {', '.join(missed[:3]) or '—'}."
        )
    else:
        extra = (
            f"Стоит добавить: {', '.join(missed[:3])}." if missed else "Всё по делу!"
        )
        feedback = (
            f"Хороший ответ. Упомянуто {len(matched)} из {len(keywords)} "
            f"ключевых моментов. {extra}"
        )

    return {
        "score": max(0, min(10, score)),
        "matched_keywords": matched,
        "missed_keywords": missed,
        "feedback": feedback,
    }


def score_answer(answer: str, question: dict, use_ai: bool = True) -> dict:
    """Оценивает ответ. При доступном ИИ — через DeepSeek, иначе мок.

    Args:
        answer: Текст ответа менеджера.
        question: Словарь вопроса (text/question, model_answer, keywords).
        use_ai: Пытаться ли вызвать DeepSeek (по умолчанию да).

    Returns:
        Словарь со score, matched_keywords, missed_keywords и feedback.
    """
    if use_ai and ai_available():
        from app.services.ai_scorer import score_answer_ai

        result = score_answer_ai(
            question=question.get("text") or question.get("question", ""),
            model_answer=question.get("model_answer", ""),
            answer=answer,
        )
        if result is not None:
            return result

    return _score_answer_mock(answer, question)


def final_score(scores: list[int]) -> int:
    """Считает итоговый балл 0-100 из списка оценок 0-10.

    Args:
        scores: Оценки отдельных ответов по шкале 0-10.

    Returns:
        Итоговый процент 0-100.
    """
    if not scores:
        return 0
    return round(sum(scores) / (len(scores) * 10) * 100)
