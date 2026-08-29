from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.recruiters import (
    recruiters_router,
    applications_router
)
from app.api.v1.endpoints.approvals import router as approvals_router
from app.api.v1.endpoints.scoring_config import router as scoring_config_router
from app.api.v1.endpoints.evidence_bank import (
    evidence_router,
    settings_router
)
from app.api.v1.endpoints.automation import router as automation_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(recruiters_router, prefix="/recruiters", tags=["Recruiters"])
api_router.include_router(applications_router, prefix="/applications", tags=["Applications"])
api_router.include_router(approvals_router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(evidence_router, prefix="/evidence-bank", tags=["Evidence Bank"])
api_router.include_router(scoring_config_router, prefix="/scoring-config", tags=["Scoring Config"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(automation_router, prefix="/automation-runs", tags=["Automation Runs"])
