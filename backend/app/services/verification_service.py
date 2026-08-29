import re
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.automation_run import AutomationRun
from app.services.ats_connectors.base import USER_AGENT

logger = logging.getLogger("jobmuni.yama")

# Known generic job search / career paths that indicate a job posting redirect
GENERIC_CAREER_PATHS = {
    "/careers", "/careers/", "/jobs", "/jobs/", "/search", "/search/",
    "/jobs/search", "/careers/search", "/careers/search/redirect",
    "/all-jobs", "/open-positions", "/work-with-us", "/join-us"
}

# Explicit job closed / expiration markers in page body
JOB_EXPIRED_PHRASES = [
    "this job has expired",
    "job is no longer available",
    "position has been closed",
    "no longer accepting applications",
    "this posting is closed",
    "this listing is no longer active",
    "job listing has expired",
    "job not found",
    "requisition has been closed",
]

class YamaVerificationService:
    """
    YAMA Validation & Freshness Engine (Hardened Phase 2.1).
    Distinguishes exact job existence from generic domain/careers portal 200s,
    using specialized ATS API probes where supported and deep content/redirect analysis.
    """

    def __init__(self, timeout_seconds: float = 8.0):
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def extract_greenhouse_identifiers(url: str, source_job_id: Optional[str] = None, company_name: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Extract (company_slug, job_id) from Greenhouse URL or metadata."""
        if not url:
            return company_name.lower() if company_name else None, source_job_id

        # e.g. https://boards.greenhouse.io/snowflake/jobs/123456
        # or https://job-boards.greenhouse.io/stripe/jobs/gh_stripe_202
        match = re.search(r"greenhouse\.io/(?:embed/job_board/|v1/boards/)?([^/?#]+)/jobs/([^/?#]+)", url, re.IGNORECASE)
        if match:
            return match.group(1).lower(), match.group(2)

        # e.g. https://boards.greenhouse.io/snowflake?gh_jid=123456
        match_query = re.search(r"greenhouse\.io/([^/?#]+).*?[?&]gh_jid=([^&#]+)", url, re.IGNORECASE)
        if match_query:
            return match_query.group(1).lower(), match_query.group(2)

        comp = company_name.lower() if company_name else None
        return comp, source_job_id

    @staticmethod
    def extract_lever_identifiers(url: str, source_job_id: Optional[str] = None, company_name: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """Extract (company_slug, posting_id) from Lever URL or metadata."""
        if not url:
            return company_name.lower() if company_name else None, source_job_id

        # e.g. https://jobs.lever.co/netflix/lever_db_303
        match = re.search(r"jobs\.lever\.co/([^/?#]+)/([^/?#]+)", url, re.IGNORECASE)
        if match:
            return match.group(1).lower(), match.group(2)

        comp = company_name.lower() if company_name else None
        return comp, source_job_id

    async def verify_greenhouse_exact(
        self,
        client: httpx.AsyncClient,
        company_slug: str,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Verify exact Greenhouse job existence via public board API endpoint:
        https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}
        """
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs/{job_id}"
        try:
            resp = await client.get(api_url)
            if resp.status_code == 200:
                return {
                    "status": "ACTIVE",
                    "reason": "EXACT_JOB_FOUND",
                    "http_status": 200,
                    "error": None,
                    "is_active": True,
                }
            elif resp.status_code in (404, 410):
                return {
                    "status": "INACTIVE",
                    "reason": "EXACT_JOB_NOT_FOUND",
                    "http_status": resp.status_code,
                    "error": f"Greenhouse returned HTTP {resp.status_code} for job ID {job_id}",
                    "is_active": False,
                }
            elif 500 <= resp.status_code < 600:
                return {
                    "status": "UNKNOWN",
                    "reason": "TEMPORARY_SERVER_ERROR",
                    "http_status": resp.status_code,
                    "error": f"Greenhouse API server 5xx error: HTTP {resp.status_code}",
                    "is_active": True,
                }
            else:
                return {
                    "status": "UNKNOWN",
                    "reason": "AMBIGUOUS",
                    "http_status": resp.status_code,
                    "error": f"Greenhouse API unexpected status: {resp.status_code}",
                    "is_active": True,
                }
        except httpx.TimeoutException:
            return {
                "status": "UNKNOWN",
                "reason": "TIMEOUT",
                "http_status": None,
                "error": "Greenhouse API timeout",
                "is_active": True,
            }
        except httpx.RequestError as exc:
            return {
                "status": "ERROR",
                "reason": "NETWORK_ERROR",
                "http_status": None,
                "error": str(exc),
                "is_active": True,
            }

    async def verify_lever_exact(
        self,
        client: httpx.AsyncClient,
        company_slug: str,
        posting_id: str
    ) -> Dict[str, Any]:
        """
        Verify exact Lever posting existence via public API endpoint:
        https://api.lever.co/v0/postings/{company_site}/{posting_id}
        """
        api_url = f"https://api.lever.co/v0/postings/{company_slug}/{posting_id}"
        try:
            resp = await client.get(api_url)
            if resp.status_code == 200:
                return {
                    "status": "ACTIVE",
                    "reason": "EXACT_JOB_FOUND",
                    "http_status": 200,
                    "error": None,
                    "is_active": True,
                }
            elif resp.status_code in (404, 410):
                return {
                    "status": "INACTIVE",
                    "reason": "EXACT_JOB_NOT_FOUND",
                    "http_status": resp.status_code,
                    "error": f"Lever returned HTTP {resp.status_code} for posting ID {posting_id}",
                    "is_active": False,
                }
            elif 500 <= resp.status_code < 600:
                return {
                    "status": "UNKNOWN",
                    "reason": "TEMPORARY_SERVER_ERROR",
                    "http_status": resp.status_code,
                    "error": f"Lever API server 5xx error: HTTP {resp.status_code}",
                    "is_active": True,
                }
            else:
                return {
                    "status": "UNKNOWN",
                    "reason": "AMBIGUOUS",
                    "http_status": resp.status_code,
                    "error": f"Lever API unexpected status: {resp.status_code}",
                    "is_active": True,
                }
        except httpx.TimeoutException:
            return {
                "status": "UNKNOWN",
                "reason": "TIMEOUT",
                "http_status": None,
                "error": "Lever API timeout",
                "is_active": True,
            }
        except httpx.RequestError as exc:
            return {
                "status": "ERROR",
                "reason": "NETWORK_ERROR",
                "http_status": None,
                "error": str(exc),
                "is_active": True,
            }

    async def verify_general_url(self, client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        """
        Deep URL reachability probe evaluating redirect targets and page content
        to avoid falsely marking generic 200 careers pages as active jobs.
        """
        if not url:
            return {
                "status": "UNKNOWN",
                "reason": "AMBIGUOUS",
                "http_status": None,
                "error": "Missing target URL",
                "is_active": False,
            }

        try:
            response = await client.get(url)
            code = response.status_code
            final_url_str = str(response.url)
            parsed_initial = urlparse(url)
            parsed_final = urlparse(final_url_str)

            # Check for redirect to generic careers or search portal
            initial_path = parsed_initial.path.rstrip("/")
            final_path = parsed_final.path.rstrip("/")
            
            # If initial URL had job identifier but redirected away to error or search portal
            has_error_param = "error=true" in parsed_final.query.lower()
            is_generic_careers_target = (
                final_path in GENERIC_CAREER_PATHS or
                final_path.endswith("/jobs") or
                final_path.endswith("/careers") or
                final_path.endswith("/search") or
                (not final_path and not parsed_final.query)
            )

            if (initial_path != final_path or has_error_param) and (has_error_param or is_generic_careers_target):
                # Check if initial path had job tokens like /jobs/123 that disappeared
                if re.search(r"/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+", initial_path):
                    return {
                        "status": "INACTIVE",
                        "reason": "REDIRECTED_TO_GENERIC_CAREERS",
                        "http_status": code,
                        "error": f"Redirected to generic portal: {final_url_str}",
                        "is_active": False,
                    }

            if 200 <= code < 300:
                # Content scan for expired position markers
                body_text = response.text.lower()
                for phrase in JOB_EXPIRED_PHRASES:
                    if phrase in body_text:
                        return {
                            "status": "INACTIVE",
                            "reason": "JOB_EXPIRED_ON_PAGE",
                            "http_status": code,
                            "error": f"Page content indicates role is closed: '{phrase}'",
                            "is_active": False,
                        }

                return {
                    "status": "ACTIVE",
                    "reason": "EXACT_JOB_FOUND",
                    "http_status": code,
                    "error": None,
                    "is_active": True,
                }
            elif code in (404, 410):
                return {
                    "status": "INACTIVE",
                    "reason": "EXACT_JOB_NOT_FOUND",
                    "http_status": code,
                    "error": f"HTTP {code} Not Found/Gone",
                    "is_active": False,
                }
            elif 500 <= code < 600:
                return {
                    "status": "UNKNOWN",
                    "reason": "TEMPORARY_SERVER_ERROR",
                    "http_status": code,
                    "error": f"Server 5xx error: HTTP {code}",
                    "is_active": True,
                }
            else:
                return {
                    "status": "UNKNOWN",
                    "reason": "AMBIGUOUS",
                    "http_status": code,
                    "error": f"Ambiguous HTTP status: {code}",
                    "is_active": True,
                }

        except httpx.TimeoutException:
            return {
                "status": "UNKNOWN",
                "reason": "TIMEOUT",
                "http_status": None,
                "error": "Connection timed out",
                "is_active": True,
            }
        except httpx.RequestError as exc:
            return {
                "status": "ERROR",
                "reason": "NETWORK_ERROR",
                "http_status": None,
                "error": str(exc),
                "is_active": True,
            }
        except Exception as exc:
            return {
                "status": "ERROR",
                "reason": "AMBIGUOUS",
                "http_status": None,
                "error": f"Unexpected verification error: {exc}",
                "is_active": True,
            }

    async def verify_job_target(
        self,
        client: httpx.AsyncClient,
        url: str,
        source: Optional[str] = None,
        source_job_id: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a job using source-specific API when applicable, falling back to deep URL probe.
        """
        target_url = url or ""
        src_upper = (source or "").upper()

        # 1. Greenhouse Verification
        if src_upper == "GREENHOUSE" or "greenhouse.io" in target_url:
            c_slug, j_id = self.extract_greenhouse_identifiers(target_url, source_job_id, company_name)
            if c_slug and j_id:
                res = await self.verify_greenhouse_exact(client, c_slug, j_id)
                # If API returned definitive active/inactive, return immediately
                if res["reason"] in ("EXACT_JOB_FOUND", "EXACT_JOB_NOT_FOUND"):
                    return res

        # 2. Lever Verification
        if src_upper == "LEVER" or "lever.co" in target_url:
            c_slug, p_id = self.extract_lever_identifiers(target_url, source_job_id, company_name)
            if c_slug and p_id:
                res = await self.verify_lever_exact(client, c_slug, p_id)
                if res["reason"] in ("EXACT_JOB_FOUND", "EXACT_JOB_NOT_FOUND"):
                    return res

        # 3. General Fallback URL Verification
        return await self.verify_general_url(client, target_url)

    async def verify_job(self, db: AsyncSession, job: Job, client: Optional[httpx.AsyncClient] = None) -> Dict[str, Any]:
        """Verify a single job and update all its DB persistence fields."""
        target_url = job.canonical_url or job.source_url

        if client:
            result = await self.verify_job_target(
                client=client,
                url=target_url,
                source=job.source_url if job.source_url in ("GREENHOUSE", "LEVER") else None,
                source_job_id=job.source_job_id,
                company_name=job.company_name,
            )
        else:
            async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=self.timeout_seconds, follow_redirects=True) as c:
                result = await self.verify_job_target(
                    client=c,
                    url=target_url,
                    source=job.source_url if job.source_url in ("GREENHOUSE", "LEVER") else None,
                    source_job_id=job.source_job_id,
                    company_name=job.company_name,
                )

        job.last_verified_at = datetime.now(timezone.utc)
        job.verification_status = result["status"]
        job.verification_reason = result["reason"]
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
