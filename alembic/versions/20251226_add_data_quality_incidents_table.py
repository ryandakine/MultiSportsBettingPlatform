"""add_data_quality_incidents_table

Revision ID: a1b2c3d4e5f6
Revises: 89d84adaeed7
Create Date: 2025-12-26 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '89d84adaeed7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create data_quality_incidents table
    op.create_table(
        'data_quality_incidents',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('incident_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),  # critical, high, medium, low
        sa.Column('data_type', sa.String(), nullable=False),  # e.g., "odds", "game_data"
        sa.Column('data_source', sa.String(), nullable=False),  # e.g., "espn_api", "the_odds_api"
        sa.Column('missing_fields', sa.String(), nullable=True),  # JSON array of missing fields
        sa.Column('context', sa.String(), nullable=True),  # JSON object with additional context
        sa.Column('impact', sa.String(), nullable=False),  # What operation failed
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_quality_incidents_incident_id', 'data_quality_incidents', ['incident_id'], unique=True)
    op.create_index('ix_data_quality_incidents_timestamp', 'data_quality_incidents', ['timestamp'], unique=False)
    op.create_index('ix_data_quality_incidents_severity', 'data_quality_incidents', ['severity'], unique=False)
    op.create_index('ix_data_quality_incidents_data_type', 'data_quality_incidents', ['data_type'], unique=False)
    op.create_index('ix_data_quality_incidents_resolved', 'data_quality_incidents', ['resolved'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_data_quality_incidents_resolved', table_name='data_quality_incidents')
    op.drop_index('ix_data_quality_incidents_data_type', table_name='data_quality_incidents')
    op.drop_index('ix_data_quality_incidents_severity', table_name='data_quality_incidents')
    op.drop_index('ix_data_quality_incidents_timestamp', table_name='data_quality_incidents')
    op.drop_index('ix_data_quality_incidents_incident_id', table_name='data_quality_incidents')
    op.drop_table('data_quality_incidents')


