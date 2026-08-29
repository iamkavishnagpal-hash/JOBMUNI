from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.evidence import (
    EvidenceItemResponse,
    EvidenceItemCreate,
    EvidenceItemUpdate,
    SkillsSummaryResponse,
)
from app.services.evidence_service import saraswati_service

evidence_router = APIRouter()
settings_router = APIRouter()

# --- EVIDENCE BANK ENDPOINTS ---

@evidence_router.get("", response_model=List[EvidenceItemResponse])
async def list_evidence_items(
    category: Optional[str] = None,
    skill_or_tool: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = True,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    return await saraswati_service.list_evidence(
        db,
        category=category,
        skill_or_tool=skill_or_tool,
        search=search,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )

@evidence_router.get("/skills/summary", response_model=SkillsSummaryResponse)
async def get_skills_summary(db: AsyncSession = Depends(get_db)):
    return await saraswati_service.get_skills_summary(db)

@evidence_router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_evidence_bank(db: AsyncSession = Depends(get_db)):
    return await saraswati_service.seed_default_evidence(db)

@evidence_router.get("/{evidence_id}", response_model=EvidenceItemResponse)
async def get_evidence_item(evidence_id: str, db: AsyncSession = Depends(get_db)):
    item = await saraswati_service.get_evidence_by_id(db, evidence_id)
    if not item:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    return item

@evidence_router.post("", response_model=EvidenceItemResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence_item(
    item_in: EvidenceItemCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await saraswati_service.create_evidence_item(db, item_in)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@evidence_router.put("/{evidence_id}", response_model=EvidenceItemResponse)
async def update_evidence_item(
    evidence_id: str,
    item_update: EvidenceItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated = await saraswati_service.update_evidence_item(db, evidence_id, item_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    return updated

@evidence_router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence_item(evidence_id: str, db: AsyncSession = Depends(get_db)):
    success = await saraswati_service.delete_evidence_item(db, evidence_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    return None

# --- SETTINGS / INTEGRATIONS ---
@settings_router.get("/integrations")
async def get_integrations_status():
    from app.core.config import settings
    return {
        "database": {
            "engine": "sqlite" if settings.is_sqlite else "postgresql",
            "url_configured": bool(settings.DATABASE_URL),
            "status": "connected"
        },
        "google_sheets": {
            "configured": bool(settings.GOOGLE_SHEETS_SPREADSHEET_ID),
            "spreadsheet_id": settings.GOOGLE_SHEETS_SPREADSHEET_ID or "Not configured yet",
            "status": "CONNECTED" if settings.GOOGLE_SHEETS_SPREADSHEET_ID else "NOT_CONFIGURED"
        },
        "ai_provider": {
            "provider": "Gemini" if settings.GEMINI_API_KEY else "Offline Rule Engine Fallback",
            "configured": bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY),
            "status": "READY"
        },
        "email_smtp": {
            "configured": bool(settings.SMTP_HOST),
            "host": settings.SMTP_HOST or "Not configured yet",
            "status": "READY" if settings.SMTP_HOST else "NOT_CONFIGURED"
        }
    }
