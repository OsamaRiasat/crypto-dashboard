"""create user_onboarding table

Revision ID: 002
Revises: 001
Create Date: 2025-12-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_onboarding table (using String instead of Enum)
    op.create_table(
        'user_onboarding',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('portfolio_size', sa.Integer(), nullable=True),
        sa.Column('intent', sa.Enum('growth', 'tax', 'learning', 'fun', name='intent'), nullable=True),
        sa.Column('experience', sa.Enum('beginner', 'intermediate', 'advanced', name='experience_level'), nullable=True),
        sa.Column('allocation_preset', sa.Enum('Conservative', 'Moderate', 'Aggressive', 'YOLO', name='allocation_preset'), nullable=True),
        sa.Column('onboarding_completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade() -> None:
    # Drop user_onboarding table
    op.drop_table('user_onboarding')
