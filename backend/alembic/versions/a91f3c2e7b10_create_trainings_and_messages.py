"""Создаёт таблицы trainings и messages.

Revision ID: a91f3c2e7b10
Revises: e2324c6c58e8
Create Date: 2026-09-16 15:40:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a91f3c2e7b10"
down_revision: Union[str, None] = "e2324c6c58e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создаёт таблицы сессий тренировки и сообщений."""
    op.create_table(
        "trainings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(length=50), nullable=False),
        sa.Column("topic", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("current_question_index", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trainings_user_id"), "trainings", ["user_id"], unique=False)
    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("training_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["training_id"], ["trainings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_training_id"), "messages", ["training_id"], unique=False)


def downgrade() -> None:
    """Удаляет таблицы сообщений и тренировок."""
    op.drop_index(op.f("ix_messages_training_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_trainings_user_id"), table_name="trainings")
    op.drop_table("trainings")
