"""ORM-модели приложения."""

from app.db.base import Base
from app.models.lead import Lead, LeadStatus
from app.models.user import User, UserRole

__all__ = ["Base", "Lead", "LeadStatus", "User", "UserRole"]
