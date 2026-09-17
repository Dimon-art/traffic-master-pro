"""Клиент DeepSeek API (совместим с OpenAI SDK)."""

import logging
from functools import lru_cache
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_ai_client() -> Any:
    """Возвращает клиент DeepSeek или None, если ключ не задан.

    Returns:
        OpenAI-совместимый клиент или None.
    """
    if not settings.deepseek_api_key:
        return None
    from openai import OpenAI

    return OpenAI(
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com",
    )


def ai_available() -> bool:
    """Проверяет, доступен ли ИИ (ключ есть и USE_AI=true)."""
    return bool(settings.use_ai and settings.deepseek_api_key)


def ask_ai(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    max_tokens: int = 800,
) -> str | None:
    """Отправляет запрос к DeepSeek.

    Args:
        system_prompt: Системный промпт (роль ИИ).
        user_message: Сообщение пользователя.
        temperature: Степень креативности (0-1).
        max_tokens: Максимум токенов в ответе.

    Returns:
        Ответ ИИ или None при ошибке (для fallback на мок).
    """
    client = get_ai_client()
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception:
        logger.exception("Ошибка запроса к DeepSeek")
        return None
