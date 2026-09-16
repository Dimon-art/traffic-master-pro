"""Тесты админ-API пользователей."""


def test_user_cannot_list_users(client, auth_headers_user):
    resp = client.get("/api/users", headers=auth_headers_user)
    assert resp.status_code == 403


def test_admin_can_list_users(client, auth_headers_user, auth_headers_admin):
    resp = client.get("/api/users", headers=auth_headers_admin)
    assert resp.status_code == 200
    emails = [u["email"] for u in resp.json()]
    assert "user@test.com" in emails
    assert "admin@test.com" in emails


def test_admin_can_update_user_role(client, auth_headers_user, auth_headers_admin):
    resp = client.get("/api/users", headers=auth_headers_admin)
    users = resp.json()
    target = next(u for u in users if u["email"] == "user@test.com")
    resp = client.patch(
        f"/api/users/{target['id']}",
        json={"role": "admin"},
        headers=auth_headers_admin,
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_admin_cannot_change_email_via_patch(client, auth_headers_user, auth_headers_admin):
    resp = client.get("/api/users", headers=auth_headers_admin)
    target = next(u for u in resp.json() if u["email"] == "user@test.com")
    client.patch(
        f"/api/users/{target['id']}",
        json={"email": "hacked@test.com"},
        headers=auth_headers_admin,
    )
    resp = client.get(f"/api/users/{target['id']}", headers=auth_headers_admin)
    assert resp.json()["email"] == "user@test.com"


def test_admin_can_deactivate_user(client, auth_headers_user, auth_headers_admin):
    resp = client.get("/api/users", headers=auth_headers_admin)
    target = next(u for u in resp.json() if u["email"] == "user@test.com")
    resp = client.patch(
        f"/api/users/{target['id']}",
        json={"is_active": False},
        headers=auth_headers_admin,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
