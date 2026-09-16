"""Добавляет роль пользователя и таблицу заявок.

Revision ID: e2324c6c58e8
Revises: f24641cbf5c5
Create Date: 2026-09-16 11:06:48.044474
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e2324c6c58e8"
down_revision: Union[str, None] = "f24641cbf5c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role_enum = postgresql.ENUM("user", "admin", name="user_role", create_type=False)
lead_status_enum = postgresql.ENUM(
    "new",
    "in_progress",
    "done",
    "rejected",
    name="lead_status",
    create_type=False,
)


def upgrade() -> None:
    """Создаёт ENUM-типы, таблицу leads и колонку users.role."""
    bind = op.get_bind()
    postgresql.ENUM("user", "admin", name="user_role").create(bind, checkfirst=True)
    postgresql.ENUM("new", "in_progress", "done", "rejected", name="lead_status").create(
        bind,
        checkfirst=True,
    )
    op.create_table(
        "leads",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", lead_status_enum, server_default="new", nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "users",
        sa.Column("role", user_role_enum, server_default="user", nullable=False),
    )
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)


def downgrade() -> None:
    """Удаляет роль, таблицу leads и связанные ENUM-типы."""
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_column("users", "role")
    op.drop_table("leads")
    bind = op.get_bind()
    postgresql.ENUM(name="user_role").drop(bind, checkfirst=True)
    postgresql.ENUM(name="lead_status").drop(bind, checkfirst=True)
