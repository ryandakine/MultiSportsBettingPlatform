"""add_parlay_legs_table

Revision ID: f7959b8a8c61
Revises: fd654b46c064
Create Date: 2025-12-17 18:49:08.847230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7959b8a8c61'
down_revision: Union[str, None] = 'fd654b46c064'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create parlay_legs table
    op.create_table(
        'parlay_legs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('parlay_bet_id', sa.String(), nullable=False),
        sa.Column('sport', sa.String(), nullable=False),
        sa.Column('game_id', sa.String(), nullable=False),
        sa.Column('home_team', sa.String(), nullable=True),
        sa.Column('away_team', sa.String(), nullable=True),
        sa.Column('bet_type', sa.String(), nullable=False),
        sa.Column('team', sa.String(), nullable=True),
        sa.Column('line', sa.Float(), nullable=True),
        sa.Column('odds', sa.Float(), nullable=False),
        sa.Column('predicted_probability', sa.Float(), nullable=True),
        sa.Column('predicted_edge', sa.Float(), nullable=True),
        sa.Column('result', sa.String(), nullable=True),
        sa.Column('actual_outcome', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['parlay_bet_id'], ['bets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parlay_legs_parlay_bet_id'), 'parlay_legs', ['parlay_bet_id'], unique=False)
    
    # Create parlay_cards table
    op.create_table(
        'parlay_cards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('num_legs', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('min_odds', sa.Float(), nullable=False),
        sa.Column('max_odds', sa.Float(), nullable=False),
        sa.Column('recommended_amount', sa.Float(), nullable=True),
        sa.Column('expected_value', sa.Float(), nullable=True),
        sa.Column('combined_probability', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('legs_json', sa.JSON(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parlay_cards_user_id'), 'parlay_cards', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_parlay_cards_user_id'), table_name='parlay_cards')
    op.drop_table('parlay_cards')
    op.drop_index(op.f('ix_parlay_legs_parlay_bet_id'), table_name='parlay_legs')
    op.drop_table('parlay_legs')
