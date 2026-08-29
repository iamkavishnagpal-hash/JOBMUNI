from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(description="APPROVE | REJECT | EDIT_AND_APPROVE")
    modified_content: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None

class ApprovalRequestResponse(BaseModel):
    id: str
    action_type: str
    autonomy_level: int = 2
    application_id: Optional[str] = None
    recruiter_id: Optional[str] = None
    job_id: Optional[str] = None
    title: str
    reason: str
    generated_content: Dict[str, Any]
    supporting_evidence: List[Any] = []
    status: str = "PENDING"
    decision_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DashboardSummaryResponse(BaseModel):
    urgent_opportunities_count: int = 0
    recruiter_replies_count: int = 0
    followups_due_count: int = 0
    approvals_pending_count: int = 0
    interviews_this_week_count: int = 0
    active_applications_count: int = 0
    funnel_bottleneck: Optional[str] = "No bottlenecks detected. Keep applying to high-signal opportunities."
    career_gps_top_action: Optional[Dict[str, Any]] = None
