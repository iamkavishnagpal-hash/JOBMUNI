import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, JSON, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    target_title: Mapped[str] = mapped_column(String(255), nullable=False, default="Senior / Lead BI & Analytics Engineer")
    target_seniority: Mapped[str] = mapped_column(String(50), nullable=False, default="SENIOR")
    target_comp_min: Mapped[int] = mapped_column(Integer, nullable=False, default=160000)
    target_comp_max: Mapped[int] = mapped_column(Integer, nullable=False, default=230000)
    work_auth_status: Mapped[str] = mapped_column(String(100), nullable=False, default="US_CITIZEN")
    preferred_locations: Mapped[list] = mapped_column(JSON, default=lambda: ["Remote US", "San Francisco, CA", "New York, NY"])
    raw_bio: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    evidence_items = relationship("EvidenceItem", back_populates="profile", lazy="selectin", cascade="all, delete-orphan")
    resume_versions = relationship("ResumeVersion", back_populates="profile", lazy="selectin", cascade="all, delete-orphan")

class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # TECH_SKILL, BUSINESS_IMPACT, ARCHITECTURE_PROJECT, LEADERSHIP_MANAGEMENT, CERTIFICATION
    skill_or_tool: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # e.g. SQL, Snowflake, dbt, Looker, Python, Power BI, Databricks, Azure, AWS, BigQuery, Tableau, Data Modeling
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Structured STAR breakdown
    situation: Mapped[str] = mapped_column(Text, nullable=True)
    task: Mapped[str] = mapped_column(Text, nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(Text, nullable=True)
    
    quant_metric: Mapped[str] = mapped_column(String(255), nullable=True)  # e.g. "$140k/yr compute cost reduction"
    source_company: Mapped[str] = mapped_column(String(255), nullable=True)
    timeframe_start: Mapped[str] = mapped_column(String(50), nullable=True)
    timeframe_end: Mapped[str] = mapped_column(String(50), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    verified_by_user: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    profile = relationship("CandidateProfile", back_populates="evidence_items", lazy="selectin")
