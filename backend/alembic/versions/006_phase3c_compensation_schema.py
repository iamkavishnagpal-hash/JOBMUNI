"""Phase 3C: KUBERA Compensation Intelligence schema migration

Revision ID: 006_phase3c_compensation_schema
Revises: 005_phase3b_job_alignment_schema
Create Date: 2026-08-30 03:24:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '006_phase3c_compensation_schema'
down_revision: Union[str, None] = '005_phase3b_job_alignment_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Update candidate_profiles table
    with op.batch_alter_table('candidate_profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('target_comp_preferred', sa.Integer(), server_default='195000', nullable=False))
        batch_op.add_column(sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False))
        batch_op.add_column(sa.Column('remote_preference', sa.String(length=50), server_default='REMOTE_FIRST', nullable=False))
        batch_op.add_column(sa.Column('international_preference', sa.String(length=50), server_default='US_ONLY', nullable=False))
        batch_op.add_column(sa.Column('visa_sponsorship_required', sa.String(length=50), server_default='NO', nullable=False))
        batch_op.add_column(sa.Column('employment_type_preference', sa.String(length=50), server_default='FULL_TIME', nullable=False))

    # 2. Update jobs table
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('compensation_tier', sa.String(length=50), server_default='UNKNOWN', nullable=False))
        batch_op.add_column(sa.Column('total_compensation_score', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('compensation_json', sa.JSON(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_column('compensation_json')
        batch_op.drop_column('total_compensation_score')
        batch_op.drop_column('compensation_tier')

    with op.batch_alter_table('candidate_profiles', schema=None) as batch_op:
        batch_op.drop_column('employment_type_preference')
        batch_op.drop_column('visa_sponsorship_required')
        batch_op.drop_column('international_preference')
        batch_op.drop_column('remote_preference')
        batch_op.drop_column('currency')
        batch_op.drop_column('target_comp_preferred')
