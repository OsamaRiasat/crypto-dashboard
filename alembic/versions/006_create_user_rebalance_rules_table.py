"""create user_rebalance_rules table

Revision ID: 006
Revises: 005
Create Date: 2025-12-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_rebalance_rules table (using String instead of Enum)
    op.create_table(
        'user_rebalance_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.Enum('daily', 'weekly', 'monthly', 'quarterly', name='rebalance_frequency'), nullable=False),
        sa.Column('threshold_pct', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.CheckConstraint('threshold_pct BETWEEN 5 AND 25', name='ck_threshold_pct_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_rebalance_rules_user_id')
    )


def downgrade() -> None:
    # Drop user_rebalance_rules table
    op.drop_table('user_rebalance_rules')
