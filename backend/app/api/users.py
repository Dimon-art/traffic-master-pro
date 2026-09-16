"""Эндпоинты управления пользователями (только админ)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.models.user import User
from app.schemas.auth import UserOut, UserUpdateIn

router = APIRouter(prefix="/api/users", tags=["users"])


def _get_user_or_404(db: Session, user_id: UUID) -> User:
    """Возвращает пользователя или поднимает 404.

    Args:
        db: Сессия SQLAlchemy.
        user_id: Идентификатор пользователя.

    Returns:
        Найденный пользователь.
    """
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user


@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[User]:
    """Возвращает список всех пользователей.

    Args:
        db: Сессия SQLAlchemy.

    Returns:
        Пользователи, новые сверху.
    """
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> User:
    """Возвращает одного пользователя.

    Args:
        user_id: Идентификатор пользователя.
        db: Сессия SQLAlchemy.

    Returns:
        Пользователь.
    """
    return _get_user_or_404(db, user_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    payload: UserUpdateIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> User:
    """Обновляет имя, роль и активность. Email и пароль не меняются.

    Args:
        user_id: Идентификатор пользователя.
        payload: Разрешённые поля.
        db: Сессия SQLAlchemy.

    Returns:
        Обновлённый пользователь.
    """
    user = _get_user_or_404(db, user_id)
    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(user, field_name, value)
    db.commit()
    db.refresh(user)
    return user
