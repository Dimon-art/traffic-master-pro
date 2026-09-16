"""Тесты режима «Работа с возражениями»: старт, раунды, финал, права."""

from pathlib import Path

import pytest

from app.core.config import settings
from app.services.question_loader import load_objection_scenarios

DOCKER_KB = Path("/app/knowledge_base")
REPO_KB = Path(__file__).resolve().parents[2] / "knowledge_base_volume"


def _knowledge_base_path() -> Path:
    """Путь к банку знаний: в контейнере или в репозитории."""
    docker_file = DOCKER_KB / "sales_calls_and_objections" / "objections.json"
    if docker_file.is_file():
        return DOCKER_KB
    return REPO_KB


@pytest.fixture
def objections_bank(monkeypatch):
    """Подключает реальный objections.json и сбрасывает кэш загрузчика."""
    monkeypatch.setattr(settings, "knowledge_base_path", str(_knowledge_base_path()))
    load_objection_scenarios.cache_clear()
    yield
    load_objection_scenarios.cache_clear()


def _price_scenario() -> dict:
    """Сценарий «Дорого» из банка."""
    for scenario in load_objection_scenarios():
        if scenario["id"] == "price":
            return scenario
    raise AssertionError("Сценарий price не найден")


def _start_objections(client, headers, topic="price"):
    """Стартует тренировку возражений."""
    return client.post(
        "/api/trainings",
        json={"mode": "objections", "topic": topic},
        headers=headers,
    )


def _answer(client, headers, training_id, content):
    """Отправляет реплику менеджера."""
    return client.post(
        f"/api/trainings/{training_id}/answers",
        json={"content": content},
        headers=headers,
    )


def _good_text(round_data: dict) -> str:
    """Собирает ответ со всеми ожидаемыми ключевыми словами."""
    return " ".join(round_data["expected_keywords"])


def test_start_objection_training_requires_topic(client, auth_headers_user, objections_bank):
    resp = client.post(
        "/api/trainings",
        json={"mode": "objections", "topic": None},
        headers=auth_headers_user,
    )
    assert resp.status_code == 400


def test_start_objection_training_invalid_topic(client, auth_headers_user, objections_bank):
    resp = _start_objections(client, auth_headers_user, topic="nonexistent")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Сценарий не найден"


def test_start_objection_training_success(client, auth_headers_user, objections_bank):
    scenario = _price_scenario()
    resp = _start_objections(client, auth_headers_user)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "objections"
    assert data["topic"] == "price"
    assert data["status"] == "started"
    assert data["current_question_index"] == 0
    assert len(data["messages"]) == 1
    assert data["messages"][0]["role"] == "ai"
    assert data["messages"][0]["content"] == scenario["opening"]


def test_answer_advances_round(client, auth_headers_user, objections_bank):
    created = _start_objections(client, auth_headers_user).json()
    resp = _answer(client, auth_headers_user, created["id"], "ценность результат")
    assert resp.status_code == 200
    data = resp.json()
    assert data["training"]["current_question_index"] == 1
    assert data["next_question"]
    detail = client.get(f"/api/trainings/{created['id']}", headers=auth_headers_user).json()
    assert len([msg for msg in detail["messages"] if msg["role"] == "ai"]) == 2


def test_good_answer_client_softens(client, auth_headers_user, objections_bank):
    scenario = _price_scenario()
    round_data = scenario["rounds"][0]
    created = _start_objections(client, auth_headers_user).json()
    answer = " ".join(round_data["expected_keywords"][:3])
    resp = _answer(client, auth_headers_user, created["id"], answer)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] >= 6
    assert data["next_question"] == round_data["client_reply_if_good"]


def test_bad_answer_client_pushes(client, auth_headers_user, objections_bank):
    scenario = _price_scenario()
    round_data = scenario["rounds"][0]
    created = _start_objections(client, auth_headers_user).json()
    resp = _answer(client, auth_headers_user, created["id"], "не знаю что сказать")
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] < 6
    assert data["next_question"] == round_data["client_reply_if_bad"]


def test_5_rounds_complete_training(client, auth_headers_user, objections_bank):
    scenario = _price_scenario()
    created = _start_objections(client, auth_headers_user).json()
    training_id = created["id"]
    last = None
    for round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, training_id, _good_text(round_data))
        assert last.status_code == 200
    data = last.json()
    assert data["training"]["status"] == "completed"
    assert data["next_question"] in (scenario["final_good"], scenario["final_bad"])
    detail = client.get(f"/api/trainings/{training_id}", headers=auth_headers_user).json()
    last_ai = [msg for msg in detail["messages"] if msg["role"] == "ai"][-1]
    assert last_ai["content"] in (scenario["final_good"], scenario["final_bad"])


def test_final_score_0_100(client, auth_headers_user, objections_bank):
    scenario = _price_scenario()
    created = _start_objections(client, auth_headers_user).json()
    training_id = created["id"]
    last = None
    for round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, training_id, _good_text(round_data))
    data = last.json()
    assert data["training"]["score"] is not None
    assert 0 <= data["training"]["score"] <= 100


def test_client_accepts_if_avg_high(client, auth_headers_user, objections_bank):
    scenario = _price_scenario()
    created = _start_objections(client, auth_headers_user).json()
    training_id = created["id"]
    last = None
    for round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, training_id, _good_text(round_data))
    data = last.json()
    assert data["training"]["status"] == "completed"
    assert data["next_question"] == scenario["final_good"]


def test_client_refuses_if_avg_low(client, auth_headers_user, objections_bank):
    scenario = _price_scenario()
    created = _start_objections(client, auth_headers_user).json()
    training_id = created["id"]
    last = None
    for _round_data in scenario["rounds"]:
        last = _answer(client, auth_headers_user, training_id, "не знаю")
    data = last.json()
    assert data["training"]["status"] == "completed"
    assert data["next_question"] == scenario["final_bad"]


def test_user_sees_only_own_objection_trainings(
    client, auth_headers_user, auth_headers_admin, objections_bank
):
    _start_objections(client, auth_headers_user)
    _start_objections(client, auth_headers_admin)
    resp = client.get("/api/trainings", headers=auth_headers_user)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_admin_sees_all_objection_trainings(
    client, auth_headers_user, auth_headers_admin, objections_bank
):
    _start_objections(client, auth_headers_user)
    _start_objections(client, auth_headers_admin)
    resp = client.get("/api/trainings", headers=auth_headers_admin)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_objection_scenarios_public(client, objections_bank):
    resp = client.get("/api/trainings/objections/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 8
    assert {"id", "title", "description"} <= set(data[0].keys())
    assert "price" in {item["id"] for item in data}


def test_delete_objection_training(client, auth_headers_user, objections_bank):
    created = _start_objections(client, auth_headers_user).json()
    resp = client.delete(f"/api/trainings/{created['id']}", headers=auth_headers_user)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"
    missing = client.get(f"/api/trainings/{created['id']}", headers=auth_headers_user)
    assert missing.status_code == 404
