"""add_license_applications_table

Revision ID: fd654b46c064
Revises: add_betting_manual
Create Date: 2025-12-17 12:46:03.602297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd654b46c064'
down_revision: Union[str, None] = 'add_betting_manual'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create license_applications table
    op.create_table('license_applications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('experience', sa.Text(), nullable=True),
        sa.Column('interest', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', sa.String(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('payment_status', sa.String(), nullable=False, server_default='not_started'),
        sa.Column('payment_id', sa.String(), nullable=True),
        sa.Column('monero_address', sa.String(), nullable=True),
        sa.Column('payment_amount', sa.String(), nullable=True),
        sa.Column('license_key', sa.String(), nullable=True),
        sa.Column('license_activated', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('license_activation_date', sa.DateTime(), nullable=True),
        sa.Column('monero_acknowledged', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('nda_signed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('nda_signed_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_license_applications_email'), 'license_applications', ['email'], unique=False)
    op.create_index(op.f('ix_license_applications_status'), 'license_applications', ['status'], unique=False)
    op.create_index(op.f('ix_license_applications_license_key'), 'license_applications', ['license_key'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_license_applications_license_key'), table_name='license_applications')
    op.drop_index(op.f('ix_license_applications_status'), table_name='license_applications')
    op.drop_index(op.f('ix_license_applications_email'), table_name='license_applications')
    
    # Drop table
    op.drop_table('license_applications')
