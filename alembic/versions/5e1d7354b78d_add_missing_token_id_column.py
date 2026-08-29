"""add missing token_id column to refresh_tokens

Revision ID: 5e1d7354b78d
Revises: 1802ca32555f
Create Date: 2026-08-29 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e1d7354b78d'
down_revision: Union[str, Sequence[str], None] = '1802ca32555f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('refresh_tokens', sa.Column('token_id', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_refresh_tokens_token_id'), 'refresh_tokens', ['token_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_tokens_token_id'), table_name='refresh_tokens')
    op.drop_column('refresh_tokens', 'token_id')
