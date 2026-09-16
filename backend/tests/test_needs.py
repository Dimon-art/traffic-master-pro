"""Тесты режима «Выявление потребностей»: вопросы, раунды, права."""

from pathlib import Path

import pytest

from app.core.config import settings
from app.services.question_loader import load_needs_scenarios

DOCKER_KB = Path("/app/knowledge_base")
REPO_KB = Path(__file__).resolve().parents[2] / "knowledge_base_volume"

OPEN_QUESTION = "Расскажите о вашем проекте"
CLOSED_QUESTION = "Вам нужно дёшево?"
PRICE_PREMATURE = "Стоимость 50000"
SUMMARY_QUESTION = "Правильно ли я понял, что вам нужны заявки?"
NOT_A_QUESTION = "Да, хорошо"


def _knowledge_base_path() -> Path:
    """Путь к банку знаний: в контейнере или в репозитории."""
    docker_file = DOCKER_KB / "client_search_methods" / "needs.json"
    if docker_file.is_file():
        return DOCKER_KB
    return REPO_KB


@pytest.fixture
def needs_bank(monkeypatch):
    """Подключает реальный needs.json и сбрасывает кэш загрузчика."""
    monkeypatch.setattr(settings, "knowledge_base_path", str(_knowledge_base_path()))
    load_needs_scenarios.cache_clear()
    yield
    load_needs_scenarios.cache_clear()


def _generic_scenario() -> dict:
    """Сценарий generic_inquiry из банка."""
    for scenario in load_needs_scenarios():
        if scenario["id"] == "generic_inquiry":
            return scenario
    raise AssertionError("Сценарий generic_inquiry не найден")


def _start_needs(client, headers, topic="generic_inquiry"):
    """Стартует тренировку выявления потребностей."""
    return client.post(
        "/api/trainings",
        json={"mode": "needs", "topic": topic},
        headers=headers,
    )


def _answer(client, headers, training_id, content):
    """Отправляет реплику менеджера."""
    return client.post(
        f"/api/trainings/{training_id}/answers",
        json={"content": content},
        headers=headers,
    )


def test_start_needs_requires_topic(client, auth_headers_user, needs_bank):
    resp = client.post(
        "/api/trainings",
        json={"mode": "needs", "topic": None},
        headers=auth_headers_user,
    )
    assert resp.status_code == 400


def test_start_needs_invalid_topic(client, auth_headers_user, needs_bank):
    resp = _start_needs(client, auth_headers_user, topic="nope")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Сценарий не найден"


def test_start_needs_success(client, auth_headers_user, needs_bank):
    scenario = _generic_scenario()
    resp = _start_needs(client, auth_headers_user)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "needs"
    assert data["topic"] == "generic_inquiry"
    assert data["status"] == "started"
    assert data["messages"][0]["role"] == "ai"
    assert data["messages"][0]["content"] == scenario["opening"]


def test_answer_open_question(client, auth_headers_user, needs_bank):
    created = _start_needs(client, auth_headers_user).json()
    resp = _answer(client, auth_headers_user, created["id"], OPEN_QUESTION)
    assert resp.status_code == 200
    assert resp.json()["score"] >= 7


def test_answer_closed_question(client, auth_headers_user, needs_bank):
    created = _start_needs(client, auth_headers_user).json()
    resp = _answer(client, auth_headers_user, created["id"], CLOSED_QUESTION)
    assert resp.status_code == 200
    assert resp.json()["score"] <= 3


def test_answer_price_premature(client, auth_headers_user, needs_bank):
    created = _start_needs(client, auth_headers_user).json()
    resp = _answer(client, auth_headers_user, created["id"], PRICE_PREMATURE)
    assert resp.status_code == 200
    assert resp.json()["score"] <= 3


def test_answer_summary(client, auth_headers_user, needs_bank):
    created = _start_needs(client, auth_headers_user).json()
    resp = _answer(client, auth_headers_user, created["id"], SUMMARY_QUESTION)
    assert resp.status_code == 200
    assert resp.json()["score"] >= 8


def test_answer_not_question(client, auth_headers_user, needs_bank):
    created = _start_needs(client, auth_headers_user).json()
    resp = _answer(client, auth_headers_user, created["id"], NOT_A_QUESTION)
    assert resp.status_code == 200
    assert resp.json()["score"] <= 2


def test_7_rounds_complete(client, auth_headers_user, needs_bank):
    scenario = _generic_scenario()
    created = _start_needs(client, auth_headers_user).json()
    last = None
    for _round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, created["id"], OPEN_QUESTION)
        assert last.status_code == 200
    assert last.json()["training"]["status"] == "completed"


def test_final_score_0_100(client, auth_headers_user, needs_bank):
    scenario = _generic_scenario()
    created = _start_needs(client, auth_headers_user).json()
    last = None
    for _round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, created["id"], OPEN_QUESTION)
    score = last.json()["training"]["score"]
    assert score is not None
    assert 0 <= score <= 100


def test_client_ready_if_avg_high(client, auth_headers_user, needs_bank):
    scenario = _generic_scenario()
    created = _start_needs(client, auth_headers_user).json()
    last = None
    for _round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, created["id"], OPEN_QUESTION)
    assert last.json()["next_question"] == scenario["final_good"]


def test_client_not_ready_if_avg_low(client, auth_headers_user, needs_bank):
    scenario = _generic_scenario()
    created = _start_needs(client, auth_headers_user).json()
    last = None
    for _round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, created["id"], CLOSED_QUESTION)
    assert last.json()["next_question"] == scenario["final_bad"]


def test_list_needs_scenarios_public(client, needs_bank):
    resp = client.get("/api/trainings/needs/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 4
    assert {"id", "title", "description"} <= set(data[0].keys())
    assert "generic_inquiry" in {item["id"] for item in data}


def test_user_sees_only_own_needs_trainings(
    client, auth_headers_user, auth_headers_admin, needs_bank
):
    _start_needs(client, auth_headers_user)
    _start_needs(client, auth_headers_admin)
    resp = client.get("/api/trainings", headers=auth_headers_user)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
