"""Add document_type to evaluation_prompts

Revision ID: a1b2c3d4e5f6
Revises: d2a897ab49dc
Create Date: 2026-01-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'd2a897ab49dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'evaluation_prompts',
        sa.Column('document_type', sa.String(100), nullable=True)
    )

    op.execute("UPDATE evaluation_prompts SET document_type = '主治医意見書' WHERE document_type IS NULL")

    op.alter_column('evaluation_prompts', 'document_type', nullable=False)

    # ユニーク制約を追加
    op.create_unique_constraint(
        'unique_evaluation_prompt_per_document_type',
        'evaluation_prompts',
        ['document_type']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('unique_evaluation_prompt_per_document_type', 'evaluation_prompts', type_='unique')
    op.drop_column('evaluation_prompts', 'document_type')
