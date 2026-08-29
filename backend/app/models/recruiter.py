import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Recruiter(Base):
    __tablename__ = "recruiters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(255), nullable=True, default="Technical Recruiter")
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(512), nullable=True)
    relationship_status: Mapped[str] = mapped_column(String(50), default="NEW")
    first_contact: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_contact: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    followup_due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    engagement_score: Mapped[int] = mapped_column(Integer, default=50)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    company = relationship("Company", back_populates="recruiters", lazy="selectin")
    outreach_messages = relationship("Outreach", back_populates="recruiter", lazy="selectin", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="recruiter", lazy="selectin")

class Outreach(Base):
    __tablename__ = "outreach"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    recruiter_id: Mapped[str] = mapped_column(String(36), ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), default="EMAIL")
    template_type: Mapped[str] = mapped_column(String(50), default="COLD_OUTREACH")
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    reply_received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    reply_classification: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    recruiter = relationship("Recruiter", back_populates="outreach_messages", lazy="selectin")
    application = relationship("Application", back_populates="outreach_messages", lazy="selectin")
    followups = relationship("Followup", back_populates="outreach", lazy="selectin", cascade="all, delete-orphan")

class Followup(Base):
    __tablename__ = "followups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    outreach_id: Mapped[str] = mapped_column(String(36), ForeignKey("outreach.id", ondelete="CASCADE"), nullable=False)
    sequence_step: Mapped[int] = mapped_column(Integer, default=1)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING")
    generated_draft: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    outreach = relationship("Outreach", back_populates="followups", lazy="selectin")
