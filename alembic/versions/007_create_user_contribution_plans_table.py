"""create user_contribution_plans table

Revision ID: 007
Revises: 006
Create Date: 2025-12-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_contribution_plans table (using String instead of Enum)
    op.create_table(
        'user_contribution_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('frequency', sa.Enum('weekly', 'biweekly', 'monthly', 'quarterly', name='contribution_frequency'), nullable=False),
        sa.Column('currency', sa.String(length=8), server_default='USD', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_contribution_plans_user_id')
    )


def downgrade() -> None:
    # Drop user_contribution_plans table
    op.drop_table('user_contribution_plans')
