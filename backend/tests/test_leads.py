"""Тесты CRUD заявок и разграничения прав."""


def test_create_lead_requires_auth(client):
    resp = client.post("/api/leads", json={"name": "Иван", "phone": "+79001234567"})
    assert resp.status_code == 401


def test_create_lead_success(client, auth_headers_user):
    resp = client.post(
        "/api/leads",
        json={"name": "Иван", "phone": "+79001234567", "comment": "Хочу тренировку"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Иван"
    assert data["status"] == "new"
    assert data["created_by"]


def test_create_lead_requires_phone_or_email(client, auth_headers_user):
    resp = client.post("/api/leads", json={"name": "Иван"}, headers=auth_headers_user)
    assert resp.status_code == 422


def test_user_sees_only_own_leads(client, auth_headers_user, auth_headers_admin):
    client.post(
        "/api/leads",
        json={"name": "Юзер", "phone": "+7900"},
        headers=auth_headers_user,
    )
    client.post(
        "/api/leads",
        json={"name": "Админ", "phone": "+7999"},
        headers=auth_headers_admin,
    )

    resp = client.get("/api/leads", headers=auth_headers_user)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Юзер"

    resp = client.get("/api/leads", headers=auth_headers_admin)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_user_cannot_edit_other_lead(client, auth_headers_user, auth_headers_admin):
    resp = client.post(
        "/api/leads",
        json={"name": "Лид", "phone": "+7900"},
        headers=auth_headers_admin,
    )
    lead_id = resp.json()["id"]
    resp = client.patch(
        f"/api/leads/{lead_id}",
        json={"status": "rejected"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 403


def test_user_can_cancel_own_lead(client, auth_headers_user):
    resp = client.post(
        "/api/leads",
        json={"name": "Лид", "phone": "+7900"},
        headers=auth_headers_user,
    )
    lead_id = resp.json()["id"]
    resp = client.patch(
        f"/api/leads/{lead_id}",
        json={"status": "rejected"},
        headers=auth_headers_user,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"


def test_admin_can_edit_any_lead(client, auth_headers_user, auth_headers_admin):
    resp = client.post(
        "/api/leads",
        json={"name": "Лид", "phone": "+7900"},
        headers=auth_headers_user,
    )
    lead_id = resp.json()["id"]
    resp = client.patch(
        f"/api/leads/{lead_id}",
        json={"name": "Изменено", "status": "in_progress"},
        headers=auth_headers_admin,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Изменено"
    assert resp.json()["status"] == "in_progress"


def test_user_cannot_delete_lead(client, auth_headers_user):
    resp = client.post(
        "/api/leads",
        json={"name": "Лид", "phone": "+7900"},
        headers=auth_headers_user,
    )
    lead_id = resp.json()["id"]
    resp = client.delete(f"/api/leads/{lead_id}", headers=auth_headers_user)
    assert resp.status_code == 403


def test_admin_can_delete_lead(client, auth_headers_user, auth_headers_admin):
    resp = client.post(
        "/api/leads",
        json={"name": "Лид", "phone": "+7900"},
        headers=auth_headers_user,
    )
    lead_id = resp.json()["id"]
    resp = client.delete(f"/api/leads/{lead_id}", headers=auth_headers_admin)
    assert resp.status_code == 200
    resp = client.get(f"/api/leads/{lead_id}", headers=auth_headers_admin)
    assert resp.status_code == 404
