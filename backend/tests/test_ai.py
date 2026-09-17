"""Тесты клиента DeepSeek и fallback на мок-оценку."""

import pytest

from app.core.config import settings
from app.services import ai_client
from app.services.ai_client import ai_available, ask_ai, get_ai_client
from app.services.ai_scorer import score_answer_ai, score_needs_answer_ai, score_objection_answer_ai
from app.services.ai_simulator import get_needs_client_reply, get_objection_client_reply
from app.services.needs_scorer import classify_question
from app.services.objection_scorer import score_objection_answer
from app.services.scorer import score_answer


@pytest.fixture(autouse=True)
def _clear_ai_client_cache():
    """Сбрасывает кэш клиента между тестами."""
    get_ai_client.cache_clear()
    yield
    get_ai_client.cache_clear()


def test_ai_available_false_when_no_key(monkeypatch):
    monkeypatch.setattr(settings, "deepseek_api_key", "")
    monkeypatch.setattr(settings, "use_ai", True)
    assert ai_available() is False


def test_ai_available_false_when_use_ai_false(monkeypatch):
    monkeypatch.setattr(settings, "use_ai", False)
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test")
    assert ai_available() is False


def test_ai_available_true(monkeypatch):
    monkeypatch.setattr(settings, "use_ai", True)
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test")
    assert ai_available() is True


def test_ask_ai_returns_none_on_error(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            raise RuntimeError("api down")

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeClient:
        def __init__(self):
            self.chat = FakeChat()

    monkeypatch.setattr(ai_client, "get_ai_client", lambda: FakeClient())
    assert ask_ai("система", "вопрос") is None


def test_score_answer_ai_extracts_json(monkeypatch):
    monkeypatch.setattr("app.services.ai_scorer.ai_available", lambda: True)
    monkeypatch.setattr(
        "app.services.ai_scorer.ask_ai",
        lambda *args, **kwargs: '{"score": 8, "feedback": "Хорошо", "matched_keywords": ["реклама"], "missed_keywords": []}',
    )
    result = score_answer_ai("Что такое Ads?", "Официальная реклама", "реклама")
    assert result is not None
    assert result["score"] == 8
    assert result["feedback"] == "Хорошо"
    assert result["matched_keywords"] == ["реклама"]


def test_score_answer_falls_back_on_ai_error(monkeypatch):
    monkeypatch.setattr("app.services.scorer.ai_available", lambda: True)
    monkeypatch.setattr("app.services.ai_scorer.score_answer_ai", lambda **kwargs: None)
    question = {
        "question": "Что такое Telegram Ads?",
        "keywords": ["реклама", "кабинет"],
        "min_keywords": 1,
    }
    result = score_answer("официальная реклама в кабинете", question)
    assert "matched_keywords" in result
    assert "missed_keywords" in result
    assert "feedback" in result
    assert 0 <= result["score"] <= 10
    assert "реклама" in result["matched_keywords"]


def test_objection_client_reply_returns_none_when_no_ai(monkeypatch):
    monkeypatch.setattr(settings, "use_ai", False)
    assert get_objection_client_reply("Дорого", [], "Это инвестиция") is None


def test_objection_client_reply_uses_ai(monkeypatch):
    monkeypatch.setattr(settings, "use_ai", True)
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test")
    monkeypatch.setattr(
        "app.services.ai_simulator.ask_ai",
        lambda *args, **kwargs: "Ну хорошо, уговорили",
    )
    result = get_objection_client_reply("Дорого", [], "Это инвестиция в навык")
    assert result == "Ну хорошо, уговорили"


def test_needs_client_reply_fallback(monkeypatch):
    monkeypatch.setattr(settings, "use_ai", False)
    assert get_needs_client_reply("Хочу продвижение", [], "Расскажите о цели") is None


def test_score_objection_answer_ai_extracts_json(monkeypatch):
    monkeypatch.setattr("app.services.ai_scorer.ai_available", lambda: True)
    monkeypatch.setattr(
        "app.services.ai_scorer.ask_ai",
        lambda *args, **kwargs: '{"score": 8, "feedback": "Уверенно", "matched_keywords": ["ценность"], "missed_keywords": []}',
    )
    result = score_objection_answer_ai("Дорого", "Это инвестиция в навык", 0)
    assert result is not None
    assert result["score"] == 8
    assert result["feedback"] == "Уверенно"


def test_score_needs_answer_ai_extracts_json(monkeypatch):
    monkeypatch.setattr("app.services.ai_scorer.ai_available", lambda: True)
    monkeypatch.setattr(
        "app.services.ai_scorer.ask_ai",
        lambda *args, **kwargs: '{"score": 7, "feedback": "Открытый вопрос"}',
    )
    result = score_needs_answer_ai("Хочу продвижение", "Расскажите о цели", 0)
    assert result is not None
    assert result["score"] == 7
    assert result["matched_keywords"] == []
    assert result["missed_keywords"] == []


def test_objection_scorer_falls_back_on_ai_error(monkeypatch):
    monkeypatch.setattr("app.services.objection_scorer.ai_available", lambda: True)
    monkeypatch.setattr("app.services.ai_scorer.score_objection_answer_ai", lambda **kwargs: None)
    round_data = {
        "expected_keywords": ["ценность", "результат"],
        "min_keywords": 1,
    }
    result = score_objection_answer(
        "ценность и результат",
        round_data,
        objection_title="Дорого",
        round_index=0,
    )
    assert result["is_good"] is True
    assert "ценность" in result["matched_keywords"]
    assert 0 <= result["score"] <= 10


def test_needs_classifier_falls_back_on_ai_error(monkeypatch):
    monkeypatch.setattr("app.services.needs_scorer.ai_available", lambda: True)
    monkeypatch.setattr("app.services.ai_scorer.score_needs_answer_ai", lambda **kwargs: None)
    result = classify_question(
        "Расскажите о вашем проекте",
        0,
        scenario_title="Хочу продвижение в Telegram",
    )
    assert result["score"] >= 7
    assert result["is_open"] is True
    assert "feedback" in result
