import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ScoringConfig(Base):
    __tablename__ = "scoring_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    config_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, default="Default Senior BI & Analytics")
    
    # Configurable Opportunity Scoring Weights (Sum = 1.00 / 100%)
    weight_skill_fit: Mapped[float] = mapped_column(Float, default=0.25)
    weight_seniority: Mapped[float] = mapped_column(Float, default=0.15)
    weight_domain: Mapped[float] = mapped_column(Float, default=0.15)
    weight_compensation: Mapped[float] = mapped_column(Float, default=0.15)
    weight_freshness: Mapped[float] = mapped_column(Float, default=0.10)
    weight_hiring_signal: Mapped[float] = mapped_column(Float, default=0.10)
    weight_recruiter: Mapped[float] = mapped_column(Float, default=0.10)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
