"""Initial schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-30 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Candidate Profiles & Evidence Items
    op.create_table(
        'candidate_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('target_title', sa.String(255), nullable=False),
        sa.Column('target_seniority', sa.String(50), nullable=False),
        sa.Column('target_comp_min', sa.Integer(), nullable=False),
        sa.Column('target_comp_max', sa.Integer(), nullable=False),
        sa.Column('work_auth_status', sa.String(100), nullable=False),
        sa.Column('preferred_locations', sa.JSON(), nullable=True),
        sa.Column('raw_bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'evidence_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('skill_or_tool', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('evidence_text', sa.Text(), nullable=False),
        sa.Column('quant_metric', sa.String(255), nullable=True),
        sa.Column('source_company', sa.String(255), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 2. Companies & Job Sources
    op.create_table(
        'companies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('careers_url', sa.String(512), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('size_range', sa.String(50), nullable=True),
        sa.Column('data_stack_tags', sa.JSON(), nullable=True),
        sa.Column('hiring_urgency', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'job_sources',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source_name', sa.String(100), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('feed_url', sa.String(512), nullable=True),
        sa.Column('reliability', sa.Float(), nullable=True),
        sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_success', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('compliance_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 3. Jobs & Job Skills
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False, index=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('remote_type', sa.String(50), nullable=True),
        sa.Column('source_id', sa.String(36), sa.ForeignKey('job_sources.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source_url', sa.String(1024), nullable=True, index=True),
        sa.Column('source_job_id', sa.String(255), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_http_status', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, index=True),
        sa.Column('freshness_conf', sa.Float(), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(10), nullable=True),
        sa.Column('seniority_level', sa.String(50), nullable=True),
        sa.Column('domain_category', sa.String(100), nullable=True),
        sa.Column('raw_description', sa.Text(), nullable=True),
        sa.Column('hiring_signal_score', sa.Integer(), nullable=True),
        sa.Column('hiring_signal_tier', sa.String(50), nullable=True),
        sa.Column('final_score', sa.Integer(), nullable=True, index=True),
        sa.Column('priority_tier', sa.String(50), nullable=True, index=True),
        sa.Column('score_breakdown', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'job_skills',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_name', sa.String(100), nullable=False, index=True),
        sa.Column('is_required', sa.Boolean(), default=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('weight', sa.Float(), default=1.0)
    )

    # 4. Recruiters, Outreach, Followups
    op.create_table(
        'recruiters',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('role', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('linkedin_url', sa.String(512), nullable=True),
        sa.Column('relationship_status', sa.String(50), nullable=True),
        sa.Column('first_contact', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_contact', sa.DateTime(timezone=True), nullable=True),
        sa.Column('followup_due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('engagement_score', sa.Integer(), default=50),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 5. Resume Versions, Applications, Approval Requests
    op.create_table(
        'resume_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_name', sa.String(255), nullable=False),
        sa.Column('target_role', sa.String(255), nullable=True),
        sa.Column('tailored_summary', sa.Text(), nullable=True),
        sa.Column('tailored_highlights', sa.JSON(), nullable=True),
        sa.Column('markdown_content', sa.Text(), nullable=True),
        sa.Column('ats_score', sa.Integer(), default=90),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'applications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recruiter_id', sa.String(36), sa.ForeignKey('recruiters.id', ondelete='SET NULL'), nullable=True),
        sa.Column('resume_version_id', sa.String(36), sa.ForeignKey('resume_versions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, index=True),
        sa.Column('jd_alignment_score', sa.Integer(), default=0),
        sa.Column('applied_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('referral_source', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'outreach',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('recruiter_id', sa.String(36), sa.ForeignKey('recruiters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', sa.String(36), sa.ForeignKey('applications.id', ondelete='SET NULL'), nullable=True),
        sa.Column('channel', sa.String(50), nullable=True),
        sa.Column('template_type', sa.String(50), nullable=True),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reply_received_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reply_classification', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'followups',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('outreach_id', sa.String(36), sa.ForeignKey('outreach.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sequence_step', sa.Integer(), default=1),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(50), default='PENDING'),
        sa.Column('generated_draft', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'approval_requests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('autonomy_level', sa.Integer(), default=2),
        sa.Column('application_id', sa.String(36), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=True),
        sa.Column('recruiter_id', sa.String(36), sa.ForeignKey('recruiters.id', ondelete='SET NULL'), nullable=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('generated_content', sa.JSON(), nullable=False),
        sa.Column('supporting_evidence', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(50), default='PENDING', index=True),
        sa.Column('decision_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 6. Interviews & Scoring Configs & Logs
    op.create_table(
        'interviews',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('application_id', sa.String(36), sa.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('round_number', sa.Integer(), default=1),
        sa.Column('round_type', sa.String(50), default='SCREEN'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interviewer_names', sa.String(255), nullable=True),
        sa.Column('prep_notes', sa.Text(), nullable=True),
        sa.Column('feedback_notes', sa.Text(), nullable=True),
        sa.Column('outcome', sa.String(50), default='SCHEDULED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'interview_questions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('interview_id', sa.String(36), sa.ForeignKey('interviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(50), default='SQL_TECHNICAL'),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('suggested_answer_points', sa.JSON(), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'scoring_configs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('config_name', sa.String(100), nullable=False, unique=True),
        sa.Column('weight_skill_fit', sa.Float(), default=0.25),
        sa.Column('weight_seniority', sa.Float(), default=0.15),
        sa.Column('weight_domain', sa.Float(), default=0.15),
        sa.Column('weight_compensation', sa.Float(), default=0.15),
        sa.Column('weight_freshness', sa.Float(), default=0.10),
        sa.Column('weight_hiring_signal', sa.Float(), default=0.10),
        sa.Column('weight_recruiter', sa.Float(), default=0.10),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.create_table(
        'automation_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('task_type', sa.String(100), nullable=False, index=True),
        sa.Column('status', sa.String(50), default='SUCCESS', index=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), default=0),
        sa.Column('items_processed', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True)
    )

    op.create_table(
        'analytics_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', sa.String(100), nullable=False, index=True),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('channel', sa.String(50), nullable=True),
        sa.Column('variant', sa.String(50), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True)
    )

def downgrade() -> None:
    op.drop_table('analytics_events')
    op.drop_table('automation_runs')
    op.drop_table('scoring_configs')
    op.drop_table('interview_questions')
    op.drop_table('interviews')
    op.drop_table('approval_requests')
    op.drop_table('followups')
    op.drop_table('outreach')
    op.drop_table('applications')
    op.drop_table('resume_versions')
    op.drop_table('recruiters')
    op.drop_table('job_skills')
    op.drop_table('jobs')
    op.drop_table('job_sources')
    op.drop_table('companies')
    op.drop_table('evidence_items')
    op.drop_table('candidate_profiles')
