"""Добавление таблицы chats для отслеживания групповых чатов бота

Revision ID: 002_add_chats
Revises: 001_initial
Create Date: 2026-04-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002_add_chats'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('chats',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('chat_type', sa.String(length=20), nullable=False, server_default='group'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('chats')