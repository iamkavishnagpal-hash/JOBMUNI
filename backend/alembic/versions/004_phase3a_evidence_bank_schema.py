"""Phase 3A: SARASWATI Evidence Bank schema enhancement

Revision ID: 004_phase3a_evidence_bank_schema
Revises: 003_phase2_1_verification_hardening
Create Date: 2026-08-30 03:04:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_phase3a_evidence_bank_schema'
down_revision: Union[str, None] = '003_phase2_1_verification_hardening'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table('evidence_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('situation', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('task', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('action', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('result', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('timeframe_start', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('timeframe_end', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('tags', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('verified_by_user', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))

def downgrade() -> None:
    with op.batch_alter_table('evidence_items', schema=None) as batch_op:
        batch_op.drop_column('is_active')
        batch_op.drop_column('verified_by_user')
        batch_op.drop_column('tags')
        batch_op.drop_column('timeframe_end')
        batch_op.drop_column('timeframe_start')
        batch_op.drop_column('result')
        batch_op.drop_column('action')
        batch_op.drop_column('task')
        batch_op.drop_column('situation')
