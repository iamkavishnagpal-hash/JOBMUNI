from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ApplicationBase(BaseModel):
    job_id: str
    recruiter_id: Optional[str] = None
    status: str = "DISCOVERED"
    notes: Optional[str] = None
    referral_source: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationResponse(ApplicationBase):
    id: str
    resume_version_id: Optional[str] = None
    jd_alignment_score: int = 0
    applied_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
