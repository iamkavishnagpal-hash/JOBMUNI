from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.recruiter import Recruiter
from app.models.application import Application
from app.schemas.recruiter import RecruiterResponse, RecruiterCreate
from app.schemas.application import ApplicationResponse, ApplicationCreate

recruiters_router = APIRouter()
applications_router = APIRouter()

# --- RECRUITERS ---
@recruiters_router.get("", response_model=List[RecruiterResponse])
async def list_recruiters(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recruiter).order_by(desc(Recruiter.created_at)))
    return result.scalars().all()

@recruiters_router.post("", response_model=RecruiterResponse, status_code=status.HTTP_201_CREATED)
async def create_recruiter(recruiter_in: RecruiterCreate, db: AsyncSession = Depends(get_db)):
    recruiter = Recruiter(**recruiter_in.model_dump())
    db.add(recruiter)
    await db.commit()
    await db.refresh(recruiter)
    return recruiter

# --- APPLICATIONS ---
@applications_router.get("", response_model=List[ApplicationResponse])
async def list_applications(status_filter: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Application).order_by(desc(Application.created_at))
    if status_filter:
        query = query.where(Application.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()

@applications_router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(app_in: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    application = Application(**app_in.model_dump())
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application
