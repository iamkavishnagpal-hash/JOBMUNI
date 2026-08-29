from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.job import Job
from app.models.recruiter import Recruiter, Outreach, Followup
from app.models.application import Application, ApprovalRequest
from app.models.interview import Interview
from app.schemas.approval import DashboardSummaryResponse

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    # 1. Urgent Opportunities count (priority_tier == ACT_NOW and status == ACTIVE)
    urgent_q = await db.execute(
        select(func.count(Job.id)).where(Job.priority_tier == "ACT_NOW", Job.status == "ACTIVE")
    )
    urgent_count = urgent_q.scalar() or 0

    # 2. Recruiter replies count
    replies_q = await db.execute(
        select(func.count(Outreach.id)).where(Outreach.status == "REPLIED")
    )
    replies_count = replies_q.scalar() or 0

    # 3. Followups due count
    followups_q = await db.execute(
        select(func.count(Followup.id)).where(Followup.status == "READY")
    )
    followups_count = followups_q.scalar() or 0

    # 4. Approvals pending count
    approvals_q = await db.execute(
        select(func.count(ApprovalRequest.id)).where(ApprovalRequest.status == "PENDING")
    )
    approvals_count = approvals_q.scalar() or 0

    # 5. Interviews scheduled count
    interviews_q = await db.execute(
        select(func.count(Interview.id)).where(Interview.outcome == "SCHEDULED")
    )
    interviews_count = interviews_q.scalar() or 0

    # 6. Active applications count
    apps_q = await db.execute(
        select(func.count(Application.id)).where(Application.status.in_(["APPLIED", "SCREEN", "INTERVIEWING"]))
    )
    active_apps_count = apps_q.scalar() or 0

    return DashboardSummaryResponse(
        urgent_opportunities_count=urgent_count,
        recruiter_replies_count=replies_count,
        followups_due_count=followups_count,
        approvals_pending_count=approvals_count,
        interviews_this_week_count=interviews_count,
        active_applications_count=active_apps_count,
        funnel_bottleneck="No bottlenecks detected. Prioritize high-signal opportunities.",
        career_gps_top_action={
            "title": "Ingest and evaluate active Senior BI opportunities",
            "reason": "Configure job sources or paste target job descriptions to calculate alignment.",
            "cta_label": "Go to Job Radar",
            "cta_route": "/jobs"
        } if urgent_count == 0 else {
            "title": f"Review {urgent_count} urgent Act-Now opportunities",
            "reason": "Recent active postings with >85% alignment score.",
            "cta_label": "Review Jobs",
            "cta_route": "/jobs"
        }
    )
