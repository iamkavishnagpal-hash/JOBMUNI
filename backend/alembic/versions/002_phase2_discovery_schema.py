"""Phase 2 Discovery & Verification Schema Migration

Revision ID: 002_phase2_discovery_schema
Revises: 001_initial_schema
Create Date: 2026-08-30 02:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_phase2_discovery_schema'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Job table additions
    with op.batch_alter_table('jobs') as batch_op:
        batch_op.add_column(sa.Column('canonical_url', sa.String(1024), nullable=True))
        batch_op.add_column(sa.Column('verification_status', sa.String(50), server_default='UNKNOWN', nullable=False))
        batch_op.add_column(sa.Column('verification_error', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('verification_http_status', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ghost_signal_score', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('ghost_signal_reasons', sa.JSON(), server_default='[]', nullable=True))
        batch_op.add_column(sa.Column('ghost_status', sa.String(50), server_default='ACTIVE', nullable=False))
        batch_op.add_column(sa.Column('raw_description_hash', sa.String(64), nullable=True))
        
        batch_op.create_index('ix_jobs_canonical_url', ['canonical_url'])
        batch_op.create_index('ix_jobs_source_job_id', ['source_job_id'])
        batch_op.create_index('ix_jobs_verification_status', ['verification_status'])
        batch_op.create_index('ix_jobs_ghost_status', ['ghost_status'])
        batch_op.create_index('ix_jobs_raw_description_hash', ['raw_description_hash'])

    # 2. AutomationRun table additions
    with op.batch_alter_table('automation_runs') as batch_op:
        batch_op.add_column(sa.Column('task_name', sa.String(100), server_default='GENERIC_TASK', nullable=False))
        batch_op.add_column(sa.Column('agent_name', sa.String(100), server_default='BRAHMASTRA', nullable=False))
        batch_op.add_column(sa.Column('records_processed', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('records_created', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('records_updated', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('records_failed', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False))
        
        batch_op.create_index('ix_automation_runs_task_name', ['task_name'])
        batch_op.create_index('ix_automation_runs_agent_name', ['agent_name'])

def downgrade() -> None:
    with op.batch_alter_table('jobs') as batch_op:
        batch_op.drop_index('ix_jobs_raw_description_hash')
        batch_op.drop_index('ix_jobs_ghost_status')
        batch_op.drop_index('ix_jobs_verification_status')
        batch_op.drop_index('ix_jobs_source_job_id')
        batch_op.drop_index('ix_jobs_canonical_url')
        
        batch_op.drop_column('raw_description_hash')
        batch_op.drop_column('ghost_status')
        batch_op.drop_column('ghost_signal_reasons')
        batch_op.drop_column('ghost_signal_score')
        batch_op.drop_column('verification_http_status')
        batch_op.drop_column('verification_error')
        batch_op.drop_column('verification_status')
        batch_op.drop_column('canonical_url')

    with op.batch_alter_table('automation_runs') as batch_op:
        batch_op.drop_index('ix_automation_runs_agent_name')
        batch_op.drop_index('ix_automation_runs_task_name')
        
        batch_op.drop_column('retry_count')
        batch_op.drop_column('records_failed')
        batch_op.drop_column('records_updated')
        batch_op.drop_column('records_created')
        batch_op.drop_column('records_processed')
        batch_op.drop_column('agent_name')
        batch_op.drop_column('task_name')
