import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, JSON, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)
    careers_url: Mapped[str] = mapped_column(String(512), nullable=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    size_range: Mapped[str] = mapped_column(String(50), nullable=True)
    data_stack_tags: Mapped[list] = mapped_column(JSON, default=list)
    hiring_urgency: Mapped[str] = mapped_column(String(50), default="NORMAL")
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    jobs = relationship("Job", back_populates="company", lazy="selectin", cascade="all, delete-orphan")
    recruiters = relationship("Recruiter", back_populates="company", lazy="selectin", cascade="all, delete-orphan")

class JobSource(Base):
    __tablename__ = "job_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    feed_url: Mapped[str] = mapped_column(String(512), nullable=True)
    reliability: Mapped[float] = mapped_column(Float, default=1.0)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=30)
    last_run: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    compliance_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    jobs = relationship("Job", back_populates="source", lazy="selectin")

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    remote_type: Mapped[str] = mapped_column(String(50), default="REMOTE")
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_sources.id", ondelete="SET NULL"), nullable=True)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=True, index=True)
    source_job_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_http_status: Mapped[int] = mapped_column(Integer, default=200)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True)
    freshness_conf: Mapped[float] = mapped_column(Float, default=1.0)
    
    salary_min: Mapped[int] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(10), default="USD")
    seniority_level: Mapped[str] = mapped_column(String(50), default="SENIOR")
    domain_category: Mapped[str] = mapped_column(String(100), default="BI_ANALYTICS")
    raw_description: Mapped[str] = mapped_column(Text, nullable=True)
    
    hiring_signal_score: Mapped[int] = mapped_column(Integer, default=75)
    hiring_signal_tier: Mapped[str] = mapped_column(String(50), default="HIGH")
    final_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    priority_tier: Mapped[str] = mapped_column(String(50), default="NURTURE", index=True)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    company = relationship("Company", back_populates="jobs", lazy="selectin")
    source = relationship("JobSource", back_populates="jobs", lazy="selectin")
    skills = relationship("JobSkill", back_populates="job", lazy="selectin", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", lazy="selectin", cascade="all, delete-orphan")

class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[str] = mapped_column(String(50), default="CORE_TECH")
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    job = relationship("Job", back_populates="skills", lazy="selectin")
