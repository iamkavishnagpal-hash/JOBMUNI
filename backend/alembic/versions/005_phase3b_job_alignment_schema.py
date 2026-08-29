"""Phase 3B: ARJUNA JD Alignment schema migration

Revision ID: 005_phase3b_job_alignment_schema
Revises: 004_phase3a_evidence_bank_schema
Create Date: 2026-08-30 03:16:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005_phase3b_job_alignment_schema'
down_revision: Union[str, None] = '004_phase3a_evidence_bank_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('match_verdict', sa.String(length=50), server_default='INSUFFICIENT_EVIDENCE', nullable=False))
        batch_op.add_column(sa.Column('required_coverage_pct', sa.Float(), server_default='0.0', nullable=False))
        batch_op.add_column(sa.Column('preferred_coverage_pct', sa.Float(), server_default='0.0', nullable=False))
        batch_op.add_column(sa.Column('evidence_coverage_pct', sa.Float(), server_default='0.0', nullable=False))
        batch_op.add_column(sa.Column('experience_alignment_pct', sa.Float(), server_default='0.0', nullable=False))
        batch_op.add_column(sa.Column('alignment_json', sa.JSON(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_column('alignment_json')
        batch_op.drop_column('experience_alignment_pct')
        batch_op.drop_column('evidence_coverage_pct')
        batch_op.drop_column('preferred_coverage_pct')
        batch_op.drop_column('required_coverage_pct')
        batch_op.drop_column('match_verdict')
