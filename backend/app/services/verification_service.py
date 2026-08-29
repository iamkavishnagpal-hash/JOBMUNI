import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.automation_run import AutomationRun
from app.services.ats_connectors.base import USER_AGENT

logger = logging.getLogger("jobmuni.yama")

class YamaVerificationService:
    """
    YAMA Validation & Freshness Engine.
    Verifies that discovered jobs are still active and reachable on the web,
    handling 404, 410, redirects, timeouts, and 5xx errors conservatively.
    """

    def __init__(self, timeout_seconds: float = 8.0):
        self.timeout_seconds = timeout_seconds

    async def verify_url(self, client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        """
        Probe a job posting URL and classify reachability without false negatives.
        """
        if not url:
            return {
                "status": "UNKNOWN",
                "http_status": None,
                "error": "Missing URL",
                "is_active": False,
            }

        try:
            # Try HEAD first for performance, fall back to GET if 405 Method Not Allowed
            response = await client.head(url)
            if response.status_code == 405:
                response = await client.get(url)

            code = response.status_code

            if 200 <= code < 300:
                return {
                    "status": "ACTIVE",
                    "http_status": code,
                    "error": None,
                    "is_active": True,
                }
            elif code in (404, 410):
                return {
                    "status": "INACTIVE",
                    "http_status": code,
                    "error": f"HTTP {code} Page Gone/Not Found",
                    "is_active": False,
                }
            elif 300 <= code < 400:
                # Redirect handling: check final URL
                final_url = str(response.url).lower()
                # If redirected to generic careers or home page, posting is likely closed
                if any(x in final_url for x in ["/careers", "/jobs", "/search"]) and not any(char.isdigit() for char in final_url):
                    return {
                        "status": "INACTIVE",
                        "http_status": code,
                        "error": f"Redirected to generic portal: {final_url}",
                        "is_active": False,
                    }
                return {
                    "status": "ACTIVE",
                    "http_status": code,
                    "error": None,
                    "is_active": True,
                }
            elif 500 <= code < 600:
                # Server error - do NOT mark inactive (conservative policy)
                return {
                    "status": "UNKNOWN",
                    "http_status": code,
                    "error": f"Server 5xx error: HTTP {code}",
                    "is_active": True,  # Preserve active state during server outages
                }
            else:
                return {
                    "status": "UNKNOWN",
                    "http_status": code,
                    "error": f"Unexpected HTTP status: {code}",
                    "is_active": True,
                }

        except httpx.TimeoutException:
            # Timeout - conservative UNKNOWN (do not mark inactive)
            return {
                "status": "UNKNOWN",
                "http_status": None,
                "error": "Connection timeout",
                "is_active": True,
            }
        except httpx.RequestError as exc:
            return {
                "status": "ERROR",
                "http_status": None,
                "error": str(exc),
                "is_active": True,
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "http_status": None,
                "error": f"Unexpected validation error: {exc}",
                "is_active": True,
            }

    async def verify_job(self, db: AsyncSession, job: Job, client: Optional[httpx.AsyncClient] = None) -> Dict[str, Any]:
        """Verify a single job and update its DB record."""
        target_url = job.canonical_url or job.source_url

        if client:
            result = await self.verify_url(client, target_url)
        else:
            async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=self.timeout_seconds, follow_redirects=True) as c:
                result = await self.verify_url(c, target_url)

        job.last_verified_at = datetime.now(timezone.utc)
        job.verification_status = result["status"]
        job.verification_http_status = result["http_status"]
        job.verification_error = result["error"]
        job.last_http_status = result["http_status"] or job.last_http_status
        
        if result["status"] == "INACTIVE":
            job.status = "INACTIVE"

        await db.commit()
        return result

    async def verify_active_jobs(
        self,
        db: AsyncSession,
        limit: int = 50,
        task_name: str = "YAMA_FRESHNESS_VERIFICATION"
    ) -> Dict[str, Any]:
        """
        Batch verify reachable status of active jobs in the database.
        """
        start_time = time.time()
        stmt = select(Job).where(Job.status == "ACTIVE").limit(limit)
        res = await db.execute(stmt)
        jobs = res.scalars().all()

        records_processed = len(jobs)
        records_updated = 0
        records_failed = 0
        errors: List[str] = []

        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=self.timeout_seconds, follow_redirects=True) as client:
            for job in jobs:
                try:
                    await self.verify_job(db, job, client=client)
                    records_updated += 1
                except Exception as exc:
                    logger.error(f"[Yama Error] Verifying job {job.id}: {exc}")
                    records_failed += 1
                    errors.append(str(exc))

        duration_ms = int((time.time() - start_time) * 1000)
        overall_status = "SUCCESS" if records_failed == 0 else "PARTIAL"

        # Record Automation Run
        run_record = AutomationRun(
            task_name=task_name,
            task_type="FRESHNESS_VERIFY",
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
            metadata_json={"task_name": task_name, "verified_count": records_updated},
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
