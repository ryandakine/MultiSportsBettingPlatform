"""add_indexes_for_performance

Revision ID: bc3d780fa14b
Revises: 
Create Date: 2024-12-11 01:28:12.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc3d780fa14b'
down_revision = '28fd181dc829'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Indexes for predictions table
    op.create_index('idx_predictions_user_sport', 'predictions', ['user_id', 'sport'])
    op.create_index('idx_predictions_timestamp', 'predictions', ['timestamp'])
    
    # Indexes for notifications table
    # Check if table exists first (good practice)
    # Note: SQLite doesn't support IF NOT EXISTS for indexes in older versions but SQLAlchemy handles it well usually
    op.create_index('idx_notifications_user_unread', 'notifications', ['user_id', 'delivered'])
    
    # Indexes for mobile_devices table
    op.create_index('idx_mobile_devices_user', 'mobile_devices', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_mobile_devices_user', table_name='mobile_devices')
    op.drop_index('idx_notifications_user_unread', table_name='notifications')
    op.drop_index('idx_predictions_timestamp', table_name='predictions')
    op.drop_index('idx_predictions_user_sport', table_name='predictions')
