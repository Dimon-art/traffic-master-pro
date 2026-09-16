"""Тесты регистрации, входа и эндпоинта /me."""


def test_register_success(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "new@test.com", "password": "secret12345", "name": "New"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "new@test.com"
    assert data["user"]["role"] == "user"


def test_register_duplicate_email(client, user_token):
    resp = client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "secret12345"},
    )
    assert resp.status_code == 400
    assert "уже занят" in resp.json()["detail"].lower()


def test_login_success(client, user_token):
    resp = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "secret12345"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, user_token):
    resp = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_me_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers_user):
    resp = client.get("/api/auth/me", headers=auth_headers_user)
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@test.com"
    assert resp.json()["role"] == "user"
