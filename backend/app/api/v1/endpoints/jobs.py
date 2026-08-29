from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_
from app.core.database import get_db
from app.models.job import Job, JobSkill, Company
from app.models.scoring_config import ScoringConfig
from app.schemas.job import JobResponse, JobCreate, JobManualParseRequest, JobPaginationResponse, JobAlignmentResponse, JobCompensationResponse
from app.services.jd_parser import JDParser
from app.services.scoring_service import OpportunityScorer
from app.services.verification_service import YamaVerificationService
from app.services.discovery_service import NaradaDiscoveryService

router = APIRouter()

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    verification_status: Optional[str] = None,
    ghost_status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Job).order_by(desc(Job.final_score), desc(Job.created_at))
    
    if status_filter:
        query = query.where(Job.status == status_filter)
    if priority_filter:
        query = query.where(Job.priority_tier == priority_filter)
    if verification_status:
        query = query.where(Job.verification_status == verification_status)
    if ghost_status:
        query = query.where(Job.ghost_status == ghost_status)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Job.title.ilike(search_pattern),
                Job.company_name.ilike(search_pattern),
                Job.location.ilike(search_pattern),
            )
        )
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/manual-parse", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def manual_parse_job(
    request: JobManualParseRequest,
    db: AsyncSession = Depends(get_db)
):
    # Parse with deterministic JDParser
    parsed = JDParser.parse(
        title=request.title,
        raw_description=request.raw_text,
        location_hint=request.location,
    )

    # Find or create company
    comp_q = await db.execute(select(Company).where(Company.name.ilike(request.company_name)))
    company = comp_q.scalars().first()
    if not company:
        company = Company(name=request.company_name, industry="Technology", hiring_urgency="NORMAL")
        db.add(company)
        await db.flush()

    # Calculate multi-factor score
    score_res = OpportunityScorer.calculate_score(
        title=request.title,
        raw_description=request.raw_text,
        location=parsed.location or "Remote, US",
        remote_status=parsed.remote_status,
        salary_min=parsed.salary_min,
        salary_max=parsed.salary_max,
        posted_at=None,
        is_active=True,
        company_urgency=company.hiring_urgency,
    )

    new_job = Job(
        company_id=company.id,
        company_name=company.name,
        title=request.title,
        location=parsed.location or "Remote, US",
        remote_type=parsed.remote_status,
        source_url=request.source_url,
        canonical_url=request.source_url,
        raw_description=request.raw_text,
        status="ACTIVE",
        verification_status="ACTIVE",
        verification_reason="EXACT_JOB_FOUND",
        ghost_signal_score=0,
        ghost_signal_reasons=[],
        ghost_status="ACTIVE",
        freshness_conf=1.0,
        salary_min=parsed.salary_min,
        salary_max=parsed.salary_max,
        salary_currency=parsed.salary_currency,
        seniority_level=parsed.seniority_level,
        domain_category=parsed.domain_category,
        hiring_signal_score=score_res["hiring_signal_score"],
        hiring_signal_tier="HIGH" if score_res["hiring_signal_score"] >= 75 else "MEDIUM",
        final_score=score_res["total_score"],
        priority_tier=score_res["priority_tier"],
        score_breakdown=score_res["breakdown"],
    )
    db.add(new_job)
    await db.flush()

    for s in parsed.required_skills:
        db.add(JobSkill(job_id=new_job.id, skill_name=s, is_required=True, weight=1.0))
    for s in parsed.preferred_skills:
        if s not in parsed.required_skills:
            db.add(JobSkill(job_id=new_job.id, skill_name=s, is_required=False, weight=0.6))
    
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

@router.post("/{job_id}/verify", response_model=JobResponse)
async def verify_job_endpoint(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    verifier = YamaVerificationService()
    await verifier.verify_job(db, job)
    await db.refresh(job)
    return job

@router.post("/ingest-feed", status_code=status.HTTP_200_OK)
async def ingest_feed_endpoint(
    source_type: str = Query(..., description="GREENHOUSE or LEVER"),
    company_slug: str = Query(..., description="Company slug e.g. snowflake, stripe"),
    db: AsyncSession = Depends(get_db)
):
    service = NaradaDiscoveryService()
    try:
        res = await service.ingest_board(db, source_type=source_type, company_slug=company_slug)
        return res
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/{job_id}/alignment", response_model=JobAlignmentResponse)
async def get_job_alignment_endpoint(job_id: str, db: AsyncSession = Depends(get_db)):
    from app.services.alignment_engine import arjuna_engine
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # If alignment is already cached in alignment_json and valid, return it; otherwise evaluate and persist
    if job.alignment_json and job.alignment_json.get("matched_required") is not None:
        return job.alignment_json

    alignment = await arjuna_engine.evaluate_and_persist_job_alignment(db, job_id)
    if not alignment:
        raise HTTPException(status_code=404, detail="Job not found")
    return alignment

@router.post("/{job_id}/alignment", response_model=JobAlignmentResponse)
async def evaluate_job_alignment_endpoint(job_id: str, db: AsyncSession = Depends(get_db)):
    from app.services.alignment_engine import arjuna_engine
    alignment = await arjuna_engine.evaluate_and_persist_job_alignment(db, job_id)
    if not alignment:
        raise HTTPException(status_code=404, detail="Job not found")
    return alignment

@router.get("/{job_id}/compensation", response_model=JobCompensationResponse)
async def get_job_compensation_endpoint(job_id: str, db: AsyncSession = Depends(get_db)):
    from app.services.compensation_service import kubera_service
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # If compensation is already cached in compensation_json and valid, return it; otherwise evaluate and persist
    if job.compensation_json and job.compensation_json.get("compensation_tier") is not None:
        return job.compensation_json

    comp_res = await kubera_service.evaluate_and_persist_job_compensation(db, job_id)
    if not comp_res:
        raise HTTPException(status_code=404, detail="Job not found")
    return comp_res

@router.post("/{job_id}/compensation", response_model=JobCompensationResponse)
async def evaluate_job_compensation_endpoint(job_id: str, db: AsyncSession = Depends(get_db)):
    from app.services.compensation_service import kubera_service
    comp_res = await kubera_service.evaluate_and_persist_job_compensation(db, job_id)
    if not comp_res:
        raise HTTPException(status_code=404, detail="Job not found")
    return comp_res


