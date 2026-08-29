import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.automation_run import AutomationRun

logger = logging.getLogger("jobmuni.ghost_detector")

class GhostDetectorService:
    """
    Conservative Ghost Job Detection Engine.
    Evaluates multi-factor signals to identify stale or abandoned postings without
    making baseless claims.
    """

    @classmethod
    def evaluate_job(cls, job: Job) -> Tuple[int, List[str], str]:
        """
        Evaluate a single job record and calculate:
        (ghost_signal_score [0..100], ghost_signal_reasons [List[str]], ghost_status [ACTIVE|STALE|LIKELY_INACTIVE|UNKNOWN])
        """
        score = 0
        reasons: List[str] = []
        now = datetime.now(timezone.utc)

        # Signal 1: Explicitly verified inactive (HTTP 404/410)
        if job.verification_status == "INACTIVE" or job.last_http_status in (404, 410):
            score += 60
            reasons.append("Job posting returned 404/410 (removed from source ATS)")

        # Signal 2: Age of job posting
        ref_date = job.posted_at or job.first_seen_at
        if ref_date:
            if ref_date.tzinfo is None:
                ref_date = ref_date.replace(tzinfo=timezone.utc)
            age_days = (now - ref_date).days
            if age_days > 90:
                score += 40
                reasons.append(f"Posting age exceeds 90 days ({age_days} days old)")
            elif age_days > 60:
                score += 25
                reasons.append(f"Posting age exceeds 60 days ({age_days} days old)")
            elif age_days > 30:
                score += 10
                reasons.append(f"Posting age exceeds 30 days ({age_days} days old)")

        # Signal 3: Missing essential job metadata
        desc_len = len(job.raw_description or "")
        if desc_len < 100:
            score += 20
            reasons.append("Missing detailed job description body")
        if not job.location and job.remote_type == "UNKNOWN":
            score += 10
            reasons.append("Missing location and remote workplace policy")

        # Signal 4: Verification errors
        if job.verification_status == "ERROR":
            score += 15
            reasons.append("Persistent network or gateway errors during verification")

        # Clamp score between 0 and 100
        final_score = min(100, max(0, score))

        # Classify status conservatively
        if final_score >= 70:
            ghost_status = "LIKELY_INACTIVE"
        elif final_score >= 40:
            ghost_status = "STALE"
        elif job.verification_status == "UNKNOWN" and not job.posted_at:
            ghost_status = "UNKNOWN"
        else:
            ghost_status = "ACTIVE"

        return final_score, reasons, ghost_status

    async def scan_and_tag_jobs(
        self,
        db: AsyncSession,
        limit: int = 100,
        task_name: str = "GHOST_JOB_SCAN"
    ) -> Dict[str, Any]:
        """
        Scan active jobs and update their ghost signals.
        """
        start_time = time.time()
        stmt = select(Job).limit(limit)
        res = await db.execute(stmt)
        jobs = res.scalars().all()

        records_processed = len(jobs)
        records_updated = 0
        records_failed = 0
        errors: List[str] = []

        for job in jobs:
            try:
                g_score, g_reasons, g_status = self.evaluate_job(job)
                job.ghost_signal_score = g_score
                job.ghost_signal_reasons = g_reasons
                job.ghost_status = g_status

                # If classified likely inactive, update job status
                if g_status == "LIKELY_INACTIVE" and job.status == "ACTIVE":
                    job.status = "INACTIVE"

                records_updated += 1
            except Exception as exc:
                logger.error(f"[GhostDetector Error] Job {job.id}: {exc}")
                records_failed += 1
                errors.append(str(exc))

        await db.commit()

        duration_ms = int((time.time() - start_time) * 1000)
        overall_status = "SUCCESS" if records_failed == 0 else "PARTIAL"

        # Record Automation Run
        run_record = AutomationRun(
            task_name=task_name,
            task_type="GHOST_DETECTION",
            agent_name="YAMA",
            status=overall_status,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            items_processed=records_processed,
            records_processed=records_processed,
            records_created=0,
            records_updated=records_updated,
            records_failed=records_failed,
            error_message="; ".join(errors) if errors else None,
            metadata_json={"task_name": task_name, "scanned_count": records_updated},
        )
        db.add(run_record)
        await db.commit()

        return {
            "status": overall_status,
            "records_processed": records_processed,
            "records_updated": records_updated,
            "records_failed": records_failed,
            "duration_ms": duration_ms,
        }
