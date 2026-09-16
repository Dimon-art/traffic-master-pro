"""Мок-оценка ответов менеджера по ключевым словам."""

import re


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


def score_answer(answer: str, question: dict) -> dict:
    """Оценивает ответ 0-10 по совпадениям с keywords.

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
