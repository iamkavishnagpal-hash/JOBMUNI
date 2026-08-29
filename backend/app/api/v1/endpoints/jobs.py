from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.job import Job, JobSkill
from app.models.scoring_config import ScoringConfig
from app.schemas.job import JobResponse, JobCreate, JobManualParseRequest
from app.services.scoring_service import scoring_service

router = APIRouter()

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Job).order_by(desc(Job.final_score), desc(Job.created_at))
    if status_filter:
        query = query.where(Job.status == status_filter)
    if priority_filter:
        query = query.where(Job.priority_tier == priority_filter)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/manual-parse", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def manual_parse_job(
    request: JobManualParseRequest,
    db: AsyncSession = Depends(get_db)
):
    # Fetch active scoring configuration
    config_q = await db.execute(select(ScoringConfig).where(ScoringConfig.is_active == True))
    config = config_q.scalars().first()
    if not config:
        config = ScoringConfig()  # default weights

    # Heuristic skill extraction from raw text
    skills_extracted = []
    text_lower = request.raw_text.lower()
    common_skills = [
        ("SQL", "CORE_TECH", 1.2),
        ("Snowflake", "WAREHOUSE", 1.0),
        ("dbt", "CORE_TECH", 1.0),
        ("Looker", "BI_TOOL", 1.0),
        ("Tableau", "BI_TOOL", 1.0),
        ("BigQuery", "WAREHOUSE", 1.0),
        ("Python", "CORE_TECH", 1.0),
        ("Data Modeling", "CORE_TECH", 1.0),
        ("Power BI", "BI_TOOL", 0.9),
    ]
    for skill_name, cat, weight in common_skills:
        if skill_name.lower() in text_lower:
            skills_extracted.append({"skill_name": skill_name, "category": cat, "weight": weight, "is_required": True})

    # Calculate scores
    job_payload = {
        "title": request.title,
        "remote_type": "REMOTE",
        "salary_max": 185000,
        "skills": skills_extracted,
        "status": "ACTIVE",
        "hiring_signal_score": 85
    }
    final_score, priority_tier, breakdown = scoring_service.calculate_score(job_payload, config)

    new_job = Job(
        company_name=request.company_name,
        title=request.title,
        location=request.location or "Remote, US",
        remote_type="REMOTE",
        source_url=request.source_url,
        raw_description=request.raw_text,
        status="ACTIVE",
        hiring_signal_score=85,
        hiring_signal_tier="HIGH",
        final_score=final_score,
        priority_tier=priority_tier,
        score_breakdown=breakdown
    )
    db.add(new_job)
    await db.flush()

    for s in skills_extracted:
        db.add(JobSkill(
            job_id=new_job.id,
            skill_name=s["skill_name"],
            category=s["category"],
            weight=s["weight"],
            is_required=s["is_required"]
        ))
    
    await db.commit()
    await db.refresh(new_job)
    return new_job

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
