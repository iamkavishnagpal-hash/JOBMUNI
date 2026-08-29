"""Phase 2.1 verification hardening: add verification_reason

Revision ID: 003_phase2_1_verification_hardening
Revises: 002_phase2_discovery_schema
Create Date: 2026-08-30 02:58:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_phase2_1_verification_hardening'
down_revision: Union[str, None] = '002_phase2_discovery_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verification_reason', sa.String(length=100), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_column('verification_reason')
