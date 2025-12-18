"""add_game_date_to_parlay_legs

Revision ID: 89d84adaeed7
Revises: f7959b8a8c61
Create Date: 2025-12-18 01:49:34.686905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89d84adaeed7'
down_revision: Union[str, None] = 'f7959b8a8c61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add game_date column to parlay_legs table
    op.add_column('parlay_legs', sa.Column('game_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove game_date column from parlay_legs table
    op.drop_column('parlay_legs', 'game_date')
