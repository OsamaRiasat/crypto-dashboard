"""create user_risk_allocations table

Revision ID: 004
Revises: 003
Create Date: 2025-12-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_risk_allocations table
    op.create_table(
        'user_risk_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('collateral_pct', sa.Integer(), nullable=False),
        sa.Column('growth_pct', sa.Integer(), nullable=False),
        sa.Column('wildcard_pct', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.CheckConstraint('collateral_pct BETWEEN 0 AND 100', name='ck_collateral_pct_range'),
        sa.CheckConstraint('growth_pct BETWEEN 0 AND 100', name='ck_growth_pct_range'),
        sa.CheckConstraint('wildcard_pct BETWEEN 0 AND 100', name='ck_wildcard_pct_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_risk_allocations_user_id')
    )


def downgrade() -> None:
    # Drop user_risk_allocations table
    op.drop_table('user_risk_allocations')
