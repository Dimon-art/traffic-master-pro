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
