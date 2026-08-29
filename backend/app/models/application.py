import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    recruiter_id: Mapped[str] = mapped_column(String(36), ForeignKey("recruiters.id", ondelete="SET NULL"), nullable=True)
    resume_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="DISCOVERED", index=True)
    jd_alignment_score: Mapped[int] = mapped_column(Integer, default=0)
    applied_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    referral_source: Mapped[str] = mapped_column(String(255), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    job = relationship("Job", back_populates="applications", lazy="selectin")
    recruiter = relationship("Recruiter", back_populates="applications", lazy="selectin")
    resume_version = relationship("ResumeVersion", back_populates="applications", lazy="selectin")
    outreach_messages = relationship("Outreach", back_populates="application", lazy="selectin")
    interviews = relationship("Interview", back_populates="application", lazy="selectin", cascade="all, delete-orphan")
    approval_requests = relationship("ApprovalRequest", back_populates="application", lazy="selectin", cascade="all, delete-orphan")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    autonomy_level: Mapped[int] = mapped_column(Integer, default=2)
    
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=True)
    recruiter_id: Mapped[str] = mapped_column(String(36), ForeignKey("recruiters.id", ondelete="SET NULL"), nullable=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    generated_content: Mapped[dict] = mapped_column(JSON, nullable=False)
    supporting_evidence: Mapped[list] = mapped_column(JSON, default=list)
    
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)
    decision_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    application = relationship("Application", back_populates="approval_requests", lazy="selectin")
