"""add media_messages table

Revision ID: add_media_messages
Revises: 691baef6a85d
Create Date: 2026-04-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_media_messages'
down_revision: Union[str, None] = '691baef6a85d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'media_messages',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('person_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('media_type', sa.String(length=20), nullable=False),
        sa.Column('file_id', sa.String(length=255), nullable=False),
        sa.Column('file_unique_id', sa.String(length=255), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', 'chat_id'),
    )
    op.create_index(op.f('ix_media_messages_chat_id'), 'media_messages', ['chat_id'], unique=False)
    op.create_index(op.f('ix_media_messages_person_id'), 'media_messages', ['person_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_media_messages_person_id'), table_name='media_messages')
    op.drop_index(op.f('ix_media_messages_chat_id'), table_name='media_messages')
    op.drop_table('media_messages')
