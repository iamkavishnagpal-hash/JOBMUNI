import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    version_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[str] = mapped_column(String(255), nullable=True)
    tailored_summary: Mapped[str] = mapped_column(Text, nullable=True)
    tailored_highlights: Mapped[list] = mapped_column(JSON, default=list)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=True)
    ats_score: Mapped[int] = mapped_column(Integer, default=90)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    profile = relationship("CandidateProfile", back_populates="resume_versions", lazy="selectin")
    applications = relationship("Application", back_populates="resume_version", lazy="selectin")

class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    round_type: Mapped[str] = mapped_column(String(50), default="SCREEN")
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    interviewer_names: Mapped[str] = mapped_column(String(255), nullable=True)
    prep_notes: Mapped[str] = mapped_column(Text, nullable=True)
    feedback_notes: Mapped[str] = mapped_column(Text, nullable=True)
    outcome: Mapped[str] = mapped_column(String(50), default="SCHEDULED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    application = relationship("Application", back_populates="interviews", lazy="selectin")
    questions = relationship("InterviewQuestion", back_populates="interview", lazy="selectin", cascade="all, delete-orphan")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="SQL_TECHNICAL")
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_answer_points: Mapped[list] = mapped_column(JSON, default=list)
    user_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    interview = relationship("Interview", back_populates="questions", lazy="selectin")
