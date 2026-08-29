from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class RecruiterBase(BaseModel):
    company_name: str
    name: str
    role: Optional[str] = "Technical Recruiter"
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    relationship_status: str = "NEW"
    notes: Optional[str] = None

class RecruiterCreate(RecruiterBase):
    company_id: Optional[str] = None

class RecruiterResponse(RecruiterBase):
    id: str
    company_id: Optional[str] = None
    first_contact: Optional[datetime] = None
    last_contact: Optional[datetime] = None
    followup_due_date: Optional[datetime] = None
    engagement_score: int = 50
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
