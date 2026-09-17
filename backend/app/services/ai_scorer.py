"""ИИ-оценка ответов менеджера через DeepSeek."""

import json
import re

from app.services.ai_client import ai_available, ask_ai

SCORER_SYSTEM_PROMPT = """Ты — опытный тренер по продажам в Университете
продвижения в Telegram. Твоя задача — оценить ответ менеджера
на вопрос о продукте.

Критерии оценки (0-10):
- 10 — ответ полный, точный, уверенный, упоминает ключевые моменты
- 7-9 — ответ в целом верный, но упускает детали
- 4-6 — ответ частично верный, есть пробелы
- 1-3 — ответ слабый, много ошибок
- 0 — ответ не по теме или «не знаю»

Отвечай СТРОГО в формате JSON, без текста до или после:
{
  "score": <число 0-10>,
  "feedback": "<краткая обратная связь на русском, 1-2 предложения>",
  "matched_keywords": ["<слово1>", "<слово2>"],
  "missed_keywords": ["<слово1>", "<слово2>"]
}
"""


def _extract_json(text: str) -> dict | None:
    """Извлекает JSON из ответа ИИ (может быть обёрнут в ```json ... ```).

    Args:
        text: Сырой текст ответа модели.

    Returns:
        Разобранный словарь или None.
    """
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def score_answer_ai(question: str, model_answer: str, answer: str) -> dict | None:
    """Оценивает ответ через DeepSeek.

    Args:
        question: Вопрос (текст задания).
        model_answer: Эталонный ответ (для сравнения).
        answer: Ответ менеджера.

    Returns:
        Словарь с score, feedback и ключевыми словами или None при ошибке.
    """
    if not ai_available():
        return None

    user_msg = (
        f"Вопрос: {question}\n\n"
        f"Эталонный ответ: {model_answer}\n\n"
        f"Ответ менеджера: {answer}\n\n"
        f"Оцени и верни JSON."
    )
    result_text = ask_ai(SCORER_SYSTEM_PROMPT, user_msg, temperature=0.3)
    if not result_text:
        return None

    data = _extract_json(result_text)
    if not data or "score" not in data:
        return None

    try:
        score = int(data["score"])
        score = max(0, min(10, score))
    except (ValueError, TypeError):
        return None

    return {
        "score": score,
        "feedback": str(data.get("feedback", "")),
        "matched_keywords": list(data.get("matched_keywords", [])),
        "missed_keywords": list(data.get("missed_keywords", [])),
    }


OBJECTION_SCORER_PROMPT = """Ты — опытный тренер по продажам. Оцени ответ менеджера
на возражение клиента в диалоге.

Критерии (0-10):
- 10 — менеджер уверенно обработал возражение, использовал технику
- 7-9 — ответ хороший, но есть недочёты
- 4-6 — частично обработал, слабые аргументы
- 1-3 — ответ неубедительный, возражение осталось
- 0 — ответ не по теме / «не знаю» / согласие с возражением

Отвечай СТРОГО в формате JSON:
{
  "score": <0-10>,
  "feedback": "<краткая обратная связь на русском, 1-2 предложения>",
  "matched_keywords": ["<что менеджер сказал правильно>", ...],
  "missed_keywords": ["<что стоило бы добавить>", ...]
}
"""

NEEDS_SCORER_PROMPT = """Ты — эксперт по продажам. Оцени, правильно ли менеджер
задаёт вопросы клиенту, чтобы выявить потребность.

Цели менеджера:
- Задавать ОТКРЫТЫЕ вопросы (что, как, какие, расскажите)
- Не называть цену в первые раунды
- Резюмировать услышанное в конце

Критерии (0-10):
- 10 — резюмирование после выяснения, менеджер показал понимание
- 7-9 — отличный открытый вопрос по теме
- 4-6 — вопрос задан, но не очень глубокий
- 1-3 — закрытый вопрос (да/нет) или преждевременная цена
- 0 — не вопрос, раздражающая реплика

Отвечай СТРОГО в формате JSON:
{
  "score": <0-10>,
  "feedback": "<краткая обратная связь на русском, 1-2 предложения>",
  "matched_keywords": [],
  "missed_keywords": []
}
"""


def _finalize_score(data: dict, *, empty_keywords: bool = False) -> dict | None:
    """Собирает словарь оценки из JSON ИИ."""
    try:
        score = int(data["score"])
        score = max(0, min(10, score))
    except (ValueError, TypeError, KeyError):
        return None
    if empty_keywords:
        matched: list[str] = []
        missed: list[str] = []
    else:
        matched = list(data.get("matched_keywords", []))
        missed = list(data.get("missed_keywords", []))
    return {
        "score": score,
        "feedback": str(data.get("feedback", "")),
        "matched_keywords": matched,
        "missed_keywords": missed,
    }


def score_objection_answer_ai(
    objection_title: str,
    manager_answer: str,
    round_index: int,
) -> dict | None:
    """Оценивает ответ менеджера на возражение через DeepSeek.

    Args:
        objection_title: Название возражения (например, «Дорого»).
        manager_answer: Ответ менеджера.
        round_index: Номер раунда (0-4).

    Returns:
        Оценка 0-10 и feedback или None при ошибке / USE_AI=false.
    """
    if not ai_available():
        return None

    user_msg = (
        f"Возражение: {objection_title}\n"
        f"Раунд: {round_index + 1}\n"
        f"Ответ менеджера: {manager_answer}\n\n"
        f"Оцени и верни JSON."
    )
    result_text = ask_ai(OBJECTION_SCORER_PROMPT, user_msg, temperature=0.3)
    if not result_text:
        return None
    data = _extract_json(result_text)
    if not data or "score" not in data:
        return None
    return _finalize_score(data)


def score_needs_answer_ai(
    scenario_title: str,
    manager_answer: str,
    round_index: int,
) -> dict | None:
    """Оценивает вопрос менеджера в режиме «Выявление потребностей».

    Args:
        scenario_title: Название сценария.
        manager_answer: Ответ (вопрос) менеджера.
        round_index: Номер раунда (0-6).

    Returns:
        Оценка 0-10 и feedback или None при ошибке / USE_AI=false.
    """
    if not ai_available():
        return None

    user_msg = (
        f"Ситуация: {scenario_title}\n"
        f"Раунд: {round_index + 1} из 7\n"
        f"Реплика менеджера: {manager_answer}\n\n"
        f"Оцени и верни JSON."
    )
    result_text = ask_ai(NEEDS_SCORER_PROMPT, user_msg, temperature=0.3)
    if not result_text:
        return None
    data = _extract_json(result_text)
    if not data or "score" not in data:
        return None
    return _finalize_score(data, empty_keywords=True)
