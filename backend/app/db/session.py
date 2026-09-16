"""Синхронная сессия SQLAlchemy для FastAPI-зависимостей."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


class _SessionFactory:
    """Ленивая фабрика сессий: engine создаётся при первом вызове."""

    def __init__(self) -> None:
        self._maker: sessionmaker[Session] | None = None

    def __call__(self) -> Session:
        """Создаёт новую сессию SQLAlchemy.

        Returns:
            Открытая сессия.
        """
        if self._maker is None:
            engine = create_engine(settings.database_url, pool_pre_ping=True)
            self._maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return self._maker()


SessionLocal = _SessionFactory()
