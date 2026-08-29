from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EvidenceItemBase(BaseModel):
    category: str = Field(description="METRIC, PROJECT, LEADERSHIP, TECH_STACK, CERTIFICATION")
    skill_or_tool: str = Field(description="e.g. Snowflake, dbt, Looker, SQL")
    title: str
    evidence_text: str
    quant_metric: Optional[str] = None
    source_company: Optional[str] = None
    confidence: float = 1.0

class EvidenceItemCreate(EvidenceItemBase):
    pass

class EvidenceItemResponse(EvidenceItemBase):
    id: str
    profile_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileBase(BaseModel):
    full_name: str
    email: str
    target_title: str = "Senior / Lead BI & Analytics Engineer"
    target_seniority: str = "SENIOR"
    target_comp_min: int = 160000
    target_comp_max: int = 230000
    work_auth_status: str = "US_CITIZEN"
    preferred_locations: List[str] = ["Remote US", "San Francisco, CA", "New York, NY"]
    raw_bio: Optional[str] = None

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileResponse(CandidateProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime
    evidence_items: List[EvidenceItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
