"""add_performance_indexes

Revision ID: 004_add_performance_indexes
Revises: bc3d780fa14b
Create Date: 2025-12-11 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_performance_indexes'
down_revision: Union[str, None] = 'bc3d780fa14b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite indexes for prediction queries.
    
    These indexes dramatically improve performance for:
    - get_prediction_history(user_id) with ORDER BY timestamp DESC
    - Sport-based queries with time-based ordering
    """
    # Create composite index for user prediction history
    # This supports: WHERE user_id = X ORDER BY timestamp DESC
    op.create_index(
        'idx_predictions_user_timestamp', 
        'predictions',
        ['user_id', sa.text('timestamp DESC')],
        unique=False,
        postgresql_using='btree'  # PostgreSQL specific
    )
    
    # Create composite index for sport-based queries
    # This supports: WHERE sport = X ORDER BY timestamp DESC
    op.create_index(
        'idx_predictions_sport_timestamp',
        'predictions',
        ['sport', sa.text('timestamp DESC')],
        unique=False,
        postgresql_using='btree'  # PostgreSQL specific
    )
    
    # For SQLite, create simpler indexes without DESC clause
    # SQLite doesn't support DESC in index definition, but will still use these
    try:
        # Check if we're on PostgreSQL - if not, create simple indexes instead
        bind = op.get_bind()
        if 'sqlite' in bind.dialect.name.lower():
            # Drop the PostgreSQL-specific indexes and create SQLite-compatible ones
            op.drop_index('idx_predictions_user_timestamp', table_name='predictions')
            op.drop_index('idx_predictions_sport_timestamp', table_name='predictions')
            
            op.create_index(
                'idx_predictions_user_timestamp',
                'predictions',
                ['user_id', 'timestamp'],
                unique=False
            )
            
            op.create_index(
                'idx_predictions_sport_timestamp',
                'predictions',
                ['sport', 'timestamp'],
                unique=False
            )
    except Exception:
        # If we hit any issues, the PostgreSQL indexes will work
        pass


def downgrade() -> None:
    """Remove composite indexes."""
    op.drop_index('idx_predictions_sport_timestamp', table_name='predictions')
    op.drop_index('idx_predictions_user_timestamp', table_name='predictions')
