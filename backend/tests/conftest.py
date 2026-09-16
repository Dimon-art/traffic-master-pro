"""Фикстуры pytest: SQLite in-memory, клиент FastAPI и JWT тестовых пользователей."""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import Lead, User  # noqa: F401

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Создаёт чистую in-memory БД на каждый тест."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """HTTP-клиент FastAPI с подменой get_db на тестовую сессию."""
    from app.api.deps import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_token(client) -> str:
    """Регистрирует обычного юзера и возвращает JWT."""
    resp = client.post(
        "/api/auth/register",
        json={"email": "user@test.com", "password": "secret12345", "name": "User"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def admin_token(client, db_session) -> str:
    """Создаёт админа напрямую в БД и возвращает JWT."""
    from app.core.config import settings
    from app.core.security import create_access_token, hash_password
    from app.models.user import User, UserRole

    user = User(
        email="admin@test.com",
        hashed_password=hash_password("secret12345"),
        name="Admin",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token({"sub": str(user.id)}, settings.access_token_expire_minutes)


@pytest.fixture
def auth_headers_user(user_token):
    """Заголовок Authorization для обычного пользователя."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def auth_headers_admin(admin_token):
    """Заголовок Authorization для администратора."""
    return {"Authorization": f"Bearer {admin_token}"}
