"""add_betting_tables_manual

Revision ID: add_betting_manual
Revises: 53eefc7f20cc
Create Date: 2025-12-11 22:35:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'add_betting_manual'
down_revision = '53eefc7f20cc'
branch_labels = None
depends_on = None


def upgrade():
    # Create bets table
    op.create_table('bets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('is_autonomous', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('sportsbook', sa.String(), nullable=False),
        sa.Column('sportsbook_bet_id', sa.String(), nullable=True),
        sa.Column('sport', sa.String(), nullable=False),
        sa.Column('game_id', sa.String(), nullable=False),
        sa.Column('game_date', sa.DateTime(), nullable=True),
        sa.Column('home_team', sa.String(), nullable=True),
        sa.Column('away_team', sa.String(), nullable=True),
        sa.Column('bet_type', sa.String(), nullable=False),
        sa.Column('team', sa.String(), nullable=True),
        sa.Column('line', sa.Float(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('odds', sa.Float(), nullable=False),
       sa.Column('predicted_probability', sa.Float(), nullable=True),
        sa.Column('predicted_edge', sa.Float(), nullable=True),
        sa.Column('model_confidence', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('actual_result', sa.String(), nullable=True),
        sa.Column('payout', sa.Float(), nullable=True),
        sa.Column('roi', sa.Float(), nullable=True),
        sa.Column('placed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('settled_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create bankrolls table  
    op.create_table('bankrolls',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('sportsbook', sa.String(), nullable=False, server_default='paper_trading'),
        sa.Column('current_balance', sa.Float(), nullable=False),
        sa.Column('initial_deposit', sa.Float(), nullable=False),
        sa.Column('total_wagered', sa.Float(), nullable=False, server_default='0'),
        sa.Column('total_won', sa.Float(), nullable=False, server_default='0'),
        sa.Column('total_lost', sa.Float(), nullable=False, server_default='0'),
        sa.Column('total_bets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('roi_percentage', sa.Float(), nullable=False, server_default='0'),
        sa.Column('win_rate', sa.Float(), nullable=False, server_default='0'),
        sa.Column('average_edge', sa.Float(), nullable=True),
        sa.Column('sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('active_bets_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_bets_amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('available_balance', sa.Float(), nullable=False),
        sa.Column('max_bet_amount', sa.Float(), nullable=True),
        sa.Column('daily_loss_limit', sa.Float(), nullable=True),
        sa.Column('daily_losses_today', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('last_bet_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create daily_performance table
    op.create_table('daily_performance',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('bets_placed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('amount_wagered', sa.Float(), nullable=False, server_default='0'),
        sa.Column('amount_won', sa.Float(), nullable=False, server_default='0'),
        sa.Column('amount_lost', sa.Float(), nullable=False, server_default='0'),
        sa.Column('roi_percentage', sa.Float(), nullable=False, server_default='0'),
        sa.Column('bets_won', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bets_lost', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bets_pushed', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.Column('tier', sa.String(), nullable=False, server_default='free'),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('price_monthly', sa.Float(), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(), nullable=False, server_default='usd'),
        sa.Column('predictions_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('predictions_limit', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create usage_logs table
    op.create_table('usage_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('subscription_id', sa.String(), nullable=False),
        sa.Column('predictions_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('endpoint', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('usage_logs')
    op.drop_table('subscriptions')
    op.drop_table('daily_performance')
    op.drop_table('bankrolls')
    op.drop_table('bets')
