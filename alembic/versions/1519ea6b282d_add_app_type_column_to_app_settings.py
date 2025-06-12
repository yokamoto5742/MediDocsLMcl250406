"""Add app_type column to app_settings

Revision ID: 1519ea6b282d
Revises: 4f669dcc8bff
Create Date: 2025-06-03 XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1519ea6b282d'
down_revision: Union[str, None] = '4f669dcc8bff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. まずNULL許可でカラムを追加
    op.add_column('app_settings', sa.Column('app_type', sa.String(length=50), nullable=True))

    # 2. 既存のレコードにデフォルト値を設定
    op.execute("UPDATE app_settings SET app_type = 'opinion_letter' WHERE app_type IS NULL")

    # 3. NOT NULL制約を追加
    op.alter_column('app_settings', 'app_type', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('app_settings', 'app_type')