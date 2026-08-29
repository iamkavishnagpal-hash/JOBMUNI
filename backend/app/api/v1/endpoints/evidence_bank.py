from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.candidate_profile import CandidateProfile, EvidenceItem
from app.schemas.candidate import EvidenceItemResponse, EvidenceItemCreate, CandidateProfileResponse

evidence_router = APIRouter()
settings_router = APIRouter()

# --- EVIDENCE BANK ---
@evidence_router.get("", response_model=List[EvidenceItemResponse])
async def list_evidence_items(category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(EvidenceItem).order_by(desc(EvidenceItem.created_at))
    if category:
        query = query.where(EvidenceItem.category == category)
    result = await db.execute(query)
    return result.scalars().all()

@evidence_router.post("", response_model=EvidenceItemResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence_item(item_in: EvidenceItemCreate, db: AsyncSession = Depends(get_db)):
    # Ensure profile exists
    prof_q = await db.execute(select(CandidateProfile))
    profile = prof_q.scalars().first()
    if not profile:
        profile = CandidateProfile(
            full_name="Kavish",
            email="kavish@example.com",
            target_title="Senior / Lead BI & Analytics Engineer"
        )
        db.add(profile)
        await db.flush()

    item = EvidenceItem(profile_id=profile.id, **item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

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
            "configured": bool(settings.SMTP_HOST and settings.SMTP_USER),
            "host": settings.SMTP_HOST or "Not configured yet",
            "status": "CONFIGURED" if settings.SMTP_HOST else "NOT_CONFIGURED"
        }
    }
