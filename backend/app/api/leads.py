"""Эндпоинты заявок на консультацию."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.lead import Lead
from app.models.user import User, UserRole
from app.schemas.lead import LeadCreateIn, LeadOut, LeadUpdateIn

router = APIRouter(prefix="/api/leads", tags=["leads"])


def _get_lead_or_404(db: Session, lead_id: UUID) -> Lead:
    """Возвращает заявку или поднимает 404.

    Args:
        db: Сессия SQLAlchemy.
        lead_id: Идентификатор заявки.

    Returns:
        Найденная заявка.
    """
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")
    return lead


def _ensure_owner_or_admin(lead: Lead, current_user: User) -> None:
    """Запрещает доступ, если пользователь не владелец и не админ.

    Args:
        lead: Заявка.
        current_user: Текущий пользователь.
    """
    if current_user.role != UserRole.ADMIN and lead.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")


@router.post("/", response_model=LeadOut)
def create_lead(
    payload: LeadCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lead:
    """Создаёт заявку от текущего пользователя.

    Args:
        payload: Данные заявки.
        db: Сессия SQLAlchemy.
        current_user: Автор заявки.

    Returns:
        Созданная заявка.
    """
    lead = Lead(
        name=payload.name,
        phone=payload.phone,
        email=str(payload.email) if payload.email else None,
        comment=payload.comment,
        created_by=current_user.id,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/", response_model=list[LeadOut])
def list_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Lead]:
    """Возвращает заявки: все для админа, свои — для остальных.

    Args:
        db: Сессия SQLAlchemy.
        current_user: Текущий пользователь.

    Returns:
        Список заявок, новые сверху.
    """
    query = db.query(Lead)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Lead.created_by == current_user.id)
    return query.order_by(Lead.created_at.desc()).all()


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lead:
    """Возвращает одну заявку.

    Args:
        lead_id: Идентификатор заявки.
        db: Сессия SQLAlchemy.
        current_user: Текущий пользователь.

    Returns:
        Заявка.
    """
    lead = _get_lead_or_404(db, lead_id)
    _ensure_owner_or_admin(lead, current_user)
    return lead


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: UUID,
    payload: LeadUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Lead:
    """Обновляет заявку: владелец — только статус, админ — все поля.

    Args:
        lead_id: Идентификатор заявки.
        payload: Изменяемые поля.
        db: Сессия SQLAlchemy.
        current_user: Текущий пользователь.

    Returns:
        Обновлённая заявка.
    """
    lead = _get_lead_or_404(db, lead_id)
    _ensure_owner_or_admin(lead, current_user)
    updates = payload.model_dump(exclude_unset=True)
    if current_user.role != UserRole.ADMIN:
        extra_fields = set(updates.keys()) - {"status"}
        if extra_fields:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Владелец может менять только статус",
            )
    for field_name, value in updates.items():
        setattr(lead, field_name, value)
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> dict[str, str]:
    """Удаляет заявку. Только для администратора.

    Args:
        lead_id: Идентификатор заявки.
        db: Сессия SQLAlchemy.

    Returns:
        Подтверждение удаления.
    """
    lead = _get_lead_or_404(db, lead_id)
    db.delete(lead)
    db.commit()
    return {"status": "deleted"}
