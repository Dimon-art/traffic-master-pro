"""Эндпоинты проверки состояния сервиса, PostgreSQL и Redis."""

from collections.abc import Generator

from fastapi import APIRouter, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

router = APIRouter()

_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def _get_session_local() -> sessionmaker[Session]:
    """Лениво создаёт фабрику сессий для health-проверок.

    Returns:
        sessionmaker, привязанный к PostgreSQL.
    """
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Отдаёт сессию SQLAlchemy и закрывает её после запроса.

    Yields:
        Сессия подключения к PostgreSQL.
    """
    db = _get_session_local()()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health() -> dict[str, str]:
    """Возвращает базовый статус сервиса.

    Returns:
        Словарь со статусом, именем сервиса и окружением.
    """
    return {
        "status": "ok",
        "service": "traffic-master-pro",
        "environment": settings.environment,
    }


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict[str, str]:
    """Проверяет доступность PostgreSQL.

    Args:
        db: Сессия SQLAlchemy, внедряемая через ``Depends``.

    Returns:
        Словарь со статусом БД или текстом ошибки.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "postgresql"}
    except Exception as exc:
        return {"status": "error", "database": "postgresql", "error": str(exc)}


@router.get("/health/redis")
def health_redis() -> dict[str, str]:
    """Проверяет доступность Redis через ping.

    Returns:
        Словарь со статусом Redis или текстом ошибки.
    """
    import redis

    client = None
    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        client.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception as exc:
        return {"status": "error", "redis": str(exc)}
    finally:
        if client is not None:
            client.close()
