import re
import hashlib
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, Company, JobSkill, JobSource
from app.models.automation_run import AutomationRun
from app.services.ats_connectors.base import NormalizedJob
from app.services.ats_connectors.greenhouse import GreenhouseConnector
from app.services.ats_connectors.lever import LeverConnector
from app.services.scoring_service import OpportunityScorer

logger = logging.getLogger("jobmuni.discovery")

def normalize_canonical_url(raw_url: Optional[str]) -> Optional[str]:
    """Clean tracking query parameters (utm_*, gh_src, lever-source, etc.) to get canonical URL."""
    if not raw_url:
        return None
    try:
        parsed = urlparse(raw_url)
        # Strip trailing slashes and common tracking parameters
        clean_path = parsed.path.rstrip("/")
        query_params = parse_qsl(parsed.query)
        filtered_params = [
            (k, v) for k, v in query_params
            if not k.lower().startswith("utm_") and k.lower() not in {"gh_src", "lever-source", "ref", "source", "fbclid"}
        ]
        clean_query = urlencode(filtered_params)
        return urlunparse((parsed.scheme, parsed.netloc.lower(), clean_path, parsed.params, clean_query, ""))
    except Exception:
        return raw_url

def compute_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

class NaradaDiscoveryService:
    """
    NARADA Discovery & Information Acquisition Engine.
    Handles public ATS feed ingestion, normalization, deterministic deduplication,
    and idempotent persistence into PostgreSQL / SQLite.
    """

    def __init__(self):
        self.connectors = {
            "GREENHOUSE": GreenhouseConnector(),
            "LEVER": LeverConnector(),
        }

    async def ingest_normalized_jobs(
        self,
        db: AsyncSession,
        normalized_jobs: List[NormalizedJob],
        task_name: str = "NARADA_ATS_INGESTION"
    ) -> Dict[str, Any]:
        """
        Ingest a list of NormalizedJob objects into the database with deterministic deduplication.
        Returns execution statistics.
        """
        start_time = time.time()
        records_processed = len(normalized_jobs)
        records_created = 0
        records_updated = 0
        records_failed = 0
        errors: List[str] = []

        for item in normalized_jobs:
            try:
                # 1. Deduplication key checking
                canonical_url = normalize_canonical_url(item.canonical_url or item.url)
                desc_hash = compute_hash(item.raw_description)

                # Search by (source, source_job_id) OR canonical_url
                stmt = select(Job).where(
                    or_(
                        and_(Job.source_url == item.source, Job.source_job_id == item.source_job_id),
                        and_(Job.source_job_id == item.source_job_id, Job.company_name.ilike(item.company_name)),
                        Job.canonical_url == canonical_url,
                        Job.source_url == item.url,
                    )
                )
                res = await db.execute(stmt)
                existing_job = res.scalars().first()

                if existing_job:
                    # Idempotent update
                    existing_job.last_verified_at = datetime.now(timezone.utc)
                    existing_job.last_http_status = 200
                    existing_job.verification_status = "ACTIVE"
                    existing_job.verification_reason = "EXACT_JOB_FOUND"
                    
                    # Update fields if refreshed
                    if item.raw_description and existing_job.raw_description_hash != desc_hash:
                        existing_job.raw_description = item.raw_description
                        existing_job.raw_description_hash = desc_hash
                    if item.salary_min and not existing_job.salary_min:
                        existing_job.salary_min = item.salary_min
                        existing_job.salary_max = item.salary_max
                    
                    records_updated += 1
                else:
                    # Find or create company
                    comp_stmt = select(Company).where(Company.name.ilike(item.company_name))
                    comp_res = await db.execute(comp_stmt)
                    company = comp_res.scalars().first()

                    if not company:
                        company = Company(
                            name=item.company_name,
                            domain=None,
                            industry="Technology",
                            hiring_urgency="NORMAL",
                        )
                        db.add(company)
                        await db.flush()

                    # Compute opportunity score
                    score_res = OpportunityScorer.calculate_score(
                        title=item.title,
                        raw_description=item.raw_description,
                        location=item.location or "",
                        remote_status=item.remote_status,
                        salary_min=item.salary_min,
                        salary_max=item.salary_max,
                        posted_at=item.posted_at,
                        is_active=True,
                        company_urgency=company.hiring_urgency,
                    )

                    new_job = Job(
                        company_id=company.id,
                        company_name=company.name,
                        title=item.title,
                        location=item.location,
                        remote_type=item.remote_status,
                        source_url=item.url,
                        canonical_url=canonical_url,
                        source_job_id=item.source_job_id,
                        posted_at=item.posted_at,
                        first_seen_at=datetime.now(timezone.utc),
                        last_verified_at=datetime.now(timezone.utc),
                        last_http_status=200,
                        status="ACTIVE",
                        verification_status="ACTIVE",
                        verification_reason="EXACT_JOB_FOUND",
                        ghost_signal_score=0,
                        ghost_signal_reasons=[],
                        ghost_status="ACTIVE",
                        freshness_conf=1.0,
                        salary_min=item.salary_min,
                        salary_max=item.salary_max,
                        salary_currency=item.salary_currency,
                        seniority_level=item.seniority_level,
                        domain_category=item.domain_category,
                        raw_description=item.raw_description,
                        raw_description_hash=desc_hash,
                        hiring_signal_score=score_res["hiring_signal_score"],
                        hiring_signal_tier="HIGH" if score_res["hiring_signal_score"] >= 75 else "MEDIUM",
                        final_score=score_res["total_score"],
                        priority_tier=score_res["priority_tier"],
                        score_breakdown=score_res["breakdown"],
                    )
                    db.add(new_job)
                    await db.flush()

                    # Add skill associations
                    for s in item.required_skills:
                        db.add(JobSkill(job_id=new_job.id, skill_name=s, is_required=True, weight=1.0))
                    for s in item.preferred_skills:
                        if s not in item.required_skills:
                            db.add(JobSkill(job_id=new_job.id, skill_name=s, is_required=False, weight=0.6))

                    records_created += 1

            except Exception as exc:
                logger.error(f"[Narada Ingest Error] Failed item {item.title}: {exc}")
                records_failed += 1
                errors.append(str(exc))

        await db.commit()

        duration_ms = int((time.time() - start_time) * 1000)
        overall_status = "SUCCESS" if records_failed == 0 else ("PARTIAL" if records_created + records_updated > 0 else "FAILED")

        # Record Automation Run
        run_record = AutomationRun(
            task_name=task_name,
            task_type="JOB_DISCOVERY",
            agent_name="NARADA",
            status=overall_status,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            items_processed=records_processed,
            records_processed=records_processed,
            records_created=records_created,
            records_updated=records_updated,
            records_failed=records_failed,
            error_message="; ".join(errors) if errors else None,
            metadata_json={"task_name": task_name, "errors_count": len(errors)},
        )
        db.add(run_record)
        await db.commit()

        return {
            "status": overall_status,
            "records_processed": records_processed,
            "records_created": records_created,
            "records_updated": records_updated,
            "records_failed": records_failed,
            "duration_ms": duration_ms,
        }

    async def ingest_board(
        self,
        db: AsyncSession,
        source_type: str,
        company_slug: str,
    ) -> Dict[str, Any]:
        """Fetch from official ATS connector and ingest."""
        connector = self.connectors.get(source_type.upper())
        if not connector:
            raise ValueError(f"Unsupported source type: {source_type}. Supported: {list(self.connectors.keys())}")

        jobs = await connector.fetch_jobs(company_slug)
        task_name = f"NARADA_FETCH_{source_type.upper()}_{company_slug.upper()}"
        return await self.ingest_normalized_jobs(db, jobs, task_name=task_name)
