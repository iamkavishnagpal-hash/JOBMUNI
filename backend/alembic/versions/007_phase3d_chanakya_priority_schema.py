"""Phase 3D: CHANAKYA Opportunity Prioritization schema migration

Revision ID: 007_phase3d_chanakya_priority_schema
Revises: 006_phase3c_compensation_schema
Create Date: 2026-08-30 03:33:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '007_phase3d_chanakya_priority_schema'
down_revision: Union[str, None] = '006_phase3c_compensation_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority_score', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('urgency_score', sa.Integer(), server_default='50', nullable=False))
        batch_op.add_column(sa.Column('actionability', sa.String(length=50), server_default='NEEDS_REVIEW', nullable=False))
        batch_op.add_column(sa.Column('effort_level', sa.String(length=50), server_default='MEDIUM', nullable=False))
        batch_op.add_column(sa.Column('recommended_action', sa.String(length=50), server_default='REVIEW', nullable=False))
        batch_op.add_column(sa.Column('lifecycle_status', sa.String(length=50), server_default='EVALUATED', nullable=False))
        batch_op.add_column(sa.Column('chanakya_json', sa.JSON(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_column('chanakya_json')
        batch_op.drop_column('lifecycle_status')
        batch_op.drop_column('recommended_action')
        batch_op.drop_column('effort_level')
        batch_op.drop_column('actionability')
        batch_op.drop_column('urgency_score')
        batch_op.drop_column('priority_score')
