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
    canonical_url: Optional[str] = None
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

class SkillMatchItem(BaseModel):
    requirement: str
    normalized_skill: str
    matched: bool
    evidence_ids: List[str] = []
    evidence_count: int = 0
    confidence: float = 1.0
    top_metric: Optional[str] = None
    source_companies: List[str] = []
    verification_state: str = "NO_EVIDENCE"

class AlignmentReasoning(BaseModel):
    summary: str
    positive_factors: List[str] = []
    negative_factors: List[str] = []
    unknowns: List[str] = []
    recommended_action: str

class JobAlignmentResponse(BaseModel):
    job_id: str
    job_title: str
    company_name: str
    match_verdict: str  # STRONG_MATCH, PARTIAL_MATCH, WEAK_MATCH, INSUFFICIENT_EVIDENCE
    required_coverage_pct: float
    preferred_coverage_pct: float
    evidence_coverage_pct: float
    experience_alignment_pct: float
    matched_required: List[SkillMatchItem] = []
    missing_required: List[SkillMatchItem] = []
    matched_preferred: List[SkillMatchItem] = []
    missing_preferred: List[SkillMatchItem] = []
    unknown_requirements: List[str] = []
    reasoning: AlignmentReasoning

class JobResponse(JobBase):
    id: str
    company_id: Optional[str] = None
    source_id: Optional[str] = None
    posted_at: Optional[datetime] = None
    first_seen_at: datetime
    last_verified_at: datetime
    last_http_status: int = 200
    status: str = "ACTIVE"
    verification_status: str = "UNKNOWN"
    verification_error: Optional[str] = None
    verification_http_status: Optional[int] = None
    verification_reason: Optional[str] = None
    ghost_signal_score: int = 0
    ghost_signal_reasons: List[str] = []
    ghost_status: str = "ACTIVE"
    freshness_conf: float = 1.0
    hiring_signal_score: int = 75
    hiring_signal_tier: str = "HIGH"
    final_score: int = 0
    priority_tier: str = "NURTURE"
    score_breakdown: Dict[str, Any] = {}
    
    # Phase 3B Alignment fields
    match_verdict: str = "INSUFFICIENT_EVIDENCE"
    required_coverage_pct: float = 0.0
    preferred_coverage_pct: float = 0.0
    evidence_coverage_pct: float = 0.0
    experience_alignment_pct: float = 0.0
    alignment_json: Optional[Dict[str, Any]] = None

    created_at: datetime
    updated_at: datetime
    skills: List[JobSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)

class JobPaginationResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    limit: int
    pages: int
