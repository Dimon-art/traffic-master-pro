"""Зависимости FastAPI: сессия БД и текущий пользователь."""

from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Отдаёт сессию SQLAlchemy и закрывает её после запроса.

    Yields:
        Сессия подключения к PostgreSQL.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Возвращает пользователя из JWT.

    Args:
        token: Bearer-токен из заголовка Authorization.
        db: Сессия SQLAlchemy.

    Returns:
        Найденный активный пользователь.

    Raises:
        HTTPException: Если токен недействителен или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    try:
        user_uuid = UUID(str(user_id))
    except ValueError as exc:
        raise credentials_exception from exc
    user = db.get(User, user_uuid)
    if user is None or not user.is_active:
        raise credentials_exception
    return user
