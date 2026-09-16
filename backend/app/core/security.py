"""Хеширование паролей и работа с JWT."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль алгоритмом bcrypt.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Хеш пароля.
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Проверяет пароль против хеша.

    Args:
        password: Пароль в открытом виде.
        hashed: Сохранённый bcrypt-хеш.

    Returns:
        True, если пароль совпадает.
    """
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict, expires_minutes: int) -> str:
    """Создаёт подписанный JWT access-токен.

    Args:
        data: Полезная нагрузка токена.
        expires_minutes: Срок жизни токена в минутах.

    Returns:
        Строка JWT.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict | None:
    """Декодирует JWT и возвращает payload.

    Args:
        token: Строка JWT.

    Returns:
        Словарь полезной нагрузки или None, если токен невалиден.
    """
    try:
        payload: dict = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        return None
