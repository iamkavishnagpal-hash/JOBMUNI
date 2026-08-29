from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

class EvidenceItemBase(BaseModel):
    category: str = Field(..., description="TECH_SKILL | BUSINESS_IMPACT | ARCHITECTURE_PROJECT | LEADERSHIP_MANAGEMENT | CERTIFICATION")
    skill_or_tool: str = Field(..., min_length=1, description="Primary skill or tool, e.g. SQL, Snowflake, dbt, Looker")
    title: str = Field(..., min_length=3, max_length=255, description="High-impact descriptive headline")
    evidence_text: str = Field(..., min_length=10, description="Full STAR description or claim")
    
    situation: Optional[str] = None
    task: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    
    quant_metric: Optional[str] = Field(None, description="Explicit quantified metric, e.g. 40% reduction, $1.2M savings")
    source_company: Optional[str] = Field(None, description="Employer or client where achievement occurred")
    timeframe_start: Optional[str] = None
    timeframe_end: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    verified_by_user: bool = True

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = {"TECH_SKILL", "BUSINESS_IMPACT", "ARCHITECTURE_PROJECT", "LEADERSHIP_MANAGEMENT", "CERTIFICATION"}
        upper_v = v.upper()
        if upper_v not in allowed:
            raise ValueError(f"Category must be one of {allowed}, got '{v}'")
        return upper_v

class EvidenceItemCreate(EvidenceItemBase):
    profile_id: Optional[str] = None

class EvidenceItemUpdate(BaseModel):
    category: Optional[str] = None
    skill_or_tool: Optional[str] = None
    title: Optional[str] = None
    evidence_text: Optional[str] = None
    situation: Optional[str] = None
    task: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    quant_metric: Optional[str] = None
    source_company: Optional[str] = None
    timeframe_start: Optional[str] = None
    timeframe_end: Optional[str] = None
    tags: Optional[List[str]] = None
    confidence: Optional[float] = None
    verified_by_user: Optional[bool] = None
    is_active: Optional[bool] = None

class EvidenceItemResponse(EvidenceItemBase):
    id: str
    profile_id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SkillSummaryItem(BaseModel):
    skill_name: str
    evidence_count: int
    categories: List[str]
    top_metrics: List[str]
    evidence_ids: List[str]

class SkillsSummaryResponse(BaseModel):
    total_skills: int
    total_evidence_items: int
    skills: List[SkillSummaryItem]
