"""create investor memory table

Revision ID: 9f9c23a7efc6
Revises: 7824a8ece51e
Create Date: 2026-08-01 17:19:17.090295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9f9c23a7efc6'
down_revision: Union[str, Sequence[str], None] = '7824a8ece51e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP TABLE IF EXISTS investor_memory CASCADE")
    
    op.create_table(
        'investor_memory',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('risk_profile', sa.String(length=50), nullable=True),
        sa.Column('investment_horizon', sa.String(length=50), nullable=True),
        sa.Column('preferred_sectors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('avoided_sectors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_market_cap', sa.String(length=50), nullable=True),
        sa.Column('preferred_industries', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_assets', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('investment_style', sa.String(length=50), nullable=True),
        sa.Column('dividend_preference', sa.String(length=50), nullable=True),
        sa.Column('esg_preference', sa.Boolean(), nullable=True),
        sa.Column('preferred_hold_period', sa.String(length=50), nullable=True),
        sa.Column('memory_summary', sa.Text(), nullable=True),
        sa.Column('memory_facts', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('memory_source', sa.String(length=50), nullable=False, server_default='conversation'),
        sa.Column('source_message_id', sa.UUID(), nullable=True),
        sa.Column('source_conversation_id', sa.UUID(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('memory_version', sa.String(length=20), nullable=False, server_default='v1'),
        sa.Column('last_confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated_from_chat', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_investor_memory_user_id'), 'investor_memory', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_investor_memory_user_id'), table_name='investor_memory')
    op.drop_table('investor_memory')
