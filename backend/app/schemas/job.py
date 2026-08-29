from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class JobSkillBase(BaseModel):
    skill_name: str
    is_required: bool = True
    category: str = "CORE_TECH"
    weight: float = 1.0

class JobSkillResponse(JobSkillBase):
    id: str
    job_id: str

    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    company_name: str
    title: str
    location: Optional[str] = "Remote, US"
    remote_type: str = "REMOTE"
    source_url: Optional[str] = None
    source_job_id: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    seniority_level: str = "SENIOR"
    domain_category: str = "BI_ANALYTICS"
    raw_description: Optional[str] = None

class JobCreate(JobBase):
    skills: List[JobSkillBase] = []

class JobManualParseRequest(BaseModel):
    company_name: str
    title: str
    raw_text: str
    source_url: Optional[str] = None
    location: Optional[str] = "Remote, US"

class JobResponse(JobBase):
    id: str
    company_id: Optional[str] = None
    source_id: Optional[str] = None
    posted_at: Optional[datetime] = None
    first_seen_at: datetime
    last_verified_at: datetime
    last_http_status: int = 200
    status: str = "ACTIVE"
    freshness_conf: float = 1.0
    hiring_signal_score: int = 75
    hiring_signal_tier: str = "HIGH"
    final_score: int = 0
    priority_tier: str = "NURTURE"
    score_breakdown: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    skills: List[JobSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)
