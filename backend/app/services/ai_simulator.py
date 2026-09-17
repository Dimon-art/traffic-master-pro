"""ИИ-симулятор клиента для режимов objections и needs."""

from app.services.ai_client import ai_available, ask_ai

OBJECTION_CLIENT_PROMPT = """Ты — клиент в диалоге продаж.
Тебе нужно купить продвижение в Telegram для своего бизнеса, но
у тебя есть возражение: «{objection}».

Веди себя как реальный клиент:
- Отвечай коротко (1-2 предложения).
- Если менеджер работает с возражением грамотно — смягчайся.
- Если менеджер давит, уходит от ответа, называет цену раньше
  времени — усили возражение или раздражайся.
- Не давай прямых подсказок менеджеру.
- Если менеджер полностью обработал возражение — согласись
  («Хорошо, давайте попробуем»).

Твоя история диалога:
{history}

Ответь только репликой клиента, без пояснений.
"""

NEEDS_CLIENT_PROMPT = """Ты — клиент в диалоге продаж. Ты оставил
заявку на продвижение в Telegram, но пока не раскрыл свою цель.

Начальная ситуация: «{opening}»

Веди себя как реальный клиент:
- Отвечай коротко (1-2 предложения).
- Если менеджер задаёт открытые вопросы (расскажите, какие, что, как) —
  постепенно раскрывай потребность.
- Если менеджер задаёт закрытые вопросы или называет цену раньше
  времени — отвечай односложно или раздражайся.
- Не давай прямых подсказок менеджеру.
- Если менеджер выявил потребность полностью — согласись на
  предложение («Хорошо, расскажите подробнее»).

Твоя история диалога:
{history}

Ответь только репликой клиента, без пояснений.
"""


def _message_role(message) -> str:
    """Возвращает строковое значение роли сообщения."""
    role = getattr(message, "role", "")
    if hasattr(role, "value"):
        return str(role.value)
    return str(role)


def _format_history(messages: list) -> str:
    """Форматирует историю сообщений в текст для промпта.

    Args:
        messages: Список объектов Message (с полями role, content).

    Returns:
        Строка вида «Клиент: ... / Менеджер: ...».
    """
    lines = []
    for message in messages[-10:]:
        speaker = "Клиент" if _message_role(message) == "ai" else "Менеджер"
        content = getattr(message, "content", "")
        lines.append(f"{speaker}: {content}")
    return "\n".join(lines)


def get_objection_client_reply(
    objection_title: str,
    history_messages: list,
    manager_answer: str,
) -> str | None:
    """Получает реплику клиента через DeepSeek для режима objections.

    Args:
        objection_title: Название возражения из сценария.
        history_messages: История диалога.
        manager_answer: Текущая реплика менеджера.

    Returns:
        Текст реплики клиента или None при ошибке / USE_AI=false.
    """
    if not ai_available():
        return None

    history = _format_history(history_messages)
    system = OBJECTION_CLIENT_PROMPT.format(
        objection=objection_title,
        history=history,
    )
    return ask_ai(system, manager_answer, temperature=0.8, max_tokens=200)


def get_needs_client_reply(
    opening: str,
    history_messages: list,
    manager_answer: str,
) -> str | None:
    """Реплика клиента для режима needs.

    Args:
        opening: Стартовая реплика клиента.
        history_messages: История диалога.
        manager_answer: Текущая реплика менеджера.

    Returns:
        Текст реплики или None при ошибке / USE_AI=false.
    """
    if not ai_available():
        return None

    history = _format_history(history_messages)
    system = NEEDS_CLIENT_PROMPT.format(
        opening=opening,
        history=history,
    )
    return ask_ai(system, manager_answer, temperature=0.8, max_tokens=200)
