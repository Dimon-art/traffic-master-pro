"""Эндпоинты регистрации, входа и текущего пользователя."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _issue_token(user: User) -> TokenOut:
    """Выпускает JWT и собирает ответ TokenOut.

    Args:
        user: Пользователь, для которого выпускается токен.

    Returns:
        Токен и публичные данные пользователя.
    """
    access_token = create_access_token(
        {"sub": str(user.id)},
        settings.access_token_expire_minutes,
    )
    return TokenOut(access_token=access_token, user=UserOut.model_validate(user))


@router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    """Регистрирует нового пользователя и возвращает токен.

    Args:
        payload: Email, пароль и необязательное имя.
        db: Сессия SQLAlchemy.

    Returns:
        JWT и данные созданного пользователя.

    Raises:
        HTTPException: Если email уже занят.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже занят",
        )
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_token(user)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    """Проверяет учётные данные и возвращает токен.

    Args:
        payload: Email и пароль.
        db: Сессия SQLAlchemy.

    Returns:
        JWT и данные пользователя.

    Raises:
        HTTPException: Если email или пароль неверны.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _issue_token(user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Возвращает текущего авторизованного пользователя.

    Args:
        current_user: Пользователь из JWT.

    Returns:
        Публичные данные пользователя.
    """
    return current_user
