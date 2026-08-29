import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AutomationRun(Base):
    __tablename__ = "automation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # JOB_DISCOVERY, FRESHNESS_VERIFY, SCORING_REFRESH, SHEETS_SYNC, CAREER_GPS_EVAL, FOLLOWUP_CHECK
    
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS", index=True)  # SUCCESS, RUNNING, FAILED, PARTIAL
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    items_processed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # JOB_DISCOVERED, JOB_QUALIFIED, APPLICATION_CREATED, OUTREACH_SENT, REPLY_RECEIVED, INTERVIEW_SCHEDULED, OFFER_RECEIVED
    
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # job, application, recruiter, interview
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=True)
    variant: Mapped[str] = mapped_column(String(50), nullable=True)  # for A/B testing
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
