"""Тесты API тренировок: старт, ответы, права доступа."""

from pathlib import Path
import shutil

import pytest

from app.core.config import settings

FIXTURE_QUESTIONS = Path(__file__).parent / "fixtures" / "questions_sample.json"


@pytest.fixture
def product_bank(monkeypatch, tmp_path):
    """Подкладывает тестовый банк из двух вопросов."""
    dest = tmp_path / "product_knowledge"
    dest.mkdir()
    shutil.copy(FIXTURE_QUESTIONS, dest / "questions.json")
    monkeypatch.setattr(settings, "knowledge_base_path", str(tmp_path))
    return dest


def test_start_requires_auth(client, product_bank):
    resp = client.post("/api/trainings", json={"mode": "product_knowledge"})
    assert resp.status_code == 401


def test_start_product_knowledge_success(client, auth_headers_user, product_bank):
    resp = client.post(
        "/api/trainings",
        json={"mode": "product_knowledge"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "product_knowledge"
    assert data["status"] == "started"
    assert data["current_question_index"] == 0
    assert len(data["messages"]) == 1
    assert data["messages"][0]["role"] == "ai"


def test_start_unavailable_mode(client, auth_headers_user, product_bank):
    resp = client.post(
        "/api/trainings",
        json={"mode": "needs"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 400


def test_user_sees_only_own_trainings(client, auth_headers_user, auth_headers_admin, product_bank):
    client.post("/api/trainings", json={"mode": "product_knowledge"}, headers=auth_headers_user)
    client.post("/api/trainings", json={"mode": "product_knowledge"}, headers=auth_headers_admin)
    resp = client.get("/api/trainings", headers=auth_headers_user)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    resp = client.get("/api/trainings", headers=auth_headers_admin)
    assert len(resp.json()) == 2


def test_get_training_detail(client, auth_headers_user, product_bank):
    created = client.post(
        "/api/trainings",
        json={"mode": "product_knowledge"},
        headers=auth_headers_user,
    ).json()
    resp = client.get(f"/api/trainings/{created['id']}", headers=auth_headers_user)
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]
    assert resp.json()["messages"][0]["role"] == "ai"


def test_get_training_404(client, auth_headers_user, product_bank):
    resp = client.get(
        "/api/trainings/00000000-0000-0000-0000-000000000001",
        headers=auth_headers_user,
    )
    assert resp.status_code == 404


def test_user_cannot_view_other_training(client, auth_headers_user, auth_headers_admin, product_bank):
    created = client.post(
        "/api/trainings",
        json={"mode": "product_knowledge"},
        headers=auth_headers_admin,
    ).json()
    resp = client.get(f"/api/trainings/{created['id']}", headers=auth_headers_user)
    assert resp.status_code == 403


def test_answer_requires_auth(client, product_bank):
    resp = client.post(
        "/api/trainings/00000000-0000-0000-0000-000000000001/answers",
        json={"content": "Реклама в кабинете"},
    )
    assert resp.status_code == 401


def test_answer_success_and_next_question(client, auth_headers_user, product_bank):
    created = client.post(
        "/api/trainings",
        json={"mode": "product_knowledge"},
        headers=auth_headers_user,
    ).json()
    resp = client.post(
        f"/api/trainings/{created['id']}/answers",
        json={"content": "Это официальная реклама в кабинете с таргетом"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert 0 <= data["score"] <= 10
    assert data["next_question"]
    assert data["training"]["status"] == "in_progress"
    assert "реклама" in data["matched_keywords"]


def test_answer_other_users_training_forbidden(
    client, auth_headers_user, auth_headers_admin, product_bank
):
    created = client.post(
        "/api/trainings",
        json={"mode": "product_knowledge"},
        headers=auth_headers_admin,
    ).json()
    resp = client.post(
        f"/api/trainings/{created['id']}/answers",
        json={"content": "стандарт"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 403


def test_complete_training_sets_final_score(client, auth_headers_user, product_bank):
    created = client.post(
        "/api/trainings",
        json={"mode": "product_knowledge"},
        headers=auth_headers_user,
    ).json()
    training_id = created["id"]
    client.post(
        f"/api/trainings/{training_id}/answers",
        json={"content": "реклама кабинет таргет"},
        headers=auth_headers_user,
    )
    resp = client.post(
        f"/api/trainings/{training_id}/answers",
        json={"content": "стандарт или премиум"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["next_question"] is None
    assert data["training"]["status"] == "completed"
    assert data["training"]["score"] is not None
    assert 0 <= data["training"]["score"] <= 100


def test_cannot_answer_completed_training(client, auth_headers_user, product_bank):
    created = client.post(
        "/api/trainings",
        json={"mode": "product_knowledge"},
        headers=auth_headers_user,
    ).json()
    training_id = created["id"]
    client.post(
        f"/api/trainings/{training_id}/answers",
        json={"content": "реклама кабинет таргет"},
        headers=auth_headers_user,
    )
    client.post(
        f"/api/trainings/{training_id}/answers",
        json={"content": "стандарт премиум"},
        headers=auth_headers_user,
    )
    resp = client.post(
        f"/api/trainings/{training_id}/answers",
        json={"content": "ещё раз"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 400
