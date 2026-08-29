import os
import sys
import json
import time
import uuid
import signal
import asyncio
import logging
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import AsyncSessionLocal
from app.services.discovery_service import NaradaDiscoveryService
from app.services.verification_service import YamaVerificationService
from app.services.ghost_detector import GhostDetectorService
from app.services.ats_connectors.base import NormalizedJob
from app.models.automation_run import AutomationRun

# Configure Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [JOBMUNI-WORKER] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("worker")

# Target companies to poll during regular discovery runs
DEFAULT_TARGET_BOARDS = [
    ("GREENHOUSE", "snowflake"),
    ("GREENHOUSE", "stripe"),
    ("LEVER", "netflix"),
]

class JobmuniWorker:
    """
    Independent 24/7 Background Automation Worker (Brahmastra Engine).
    Runs decoupled from Next.js, FastAPI, and local developer devices.
    """

    def __init__(self, loop_interval: int = 300, session_factory: Optional[Any] = None):
        self.loop_interval = loop_interval
        self.session_factory = session_factory or AsyncSessionLocal
        self.is_running = True
        self.discovery_service = NaradaDiscoveryService()
        self.verification_service = YamaVerificationService()
        self.ghost_detector = GhostDetectorService()

    def handle_shutdown(self, signum, frame):
        logger.info(f"Received signal {signum}. Initiating graceful worker shutdown...")
        self.is_running = False

    async def execute_discovery(self, target_boards: Optional[List[tuple]] = None, fixture_path: Optional[str] = None) -> Dict[str, Any]:
        """Execute NARADA job discovery pipeline."""
        run_id = str(uuid.uuid4())
        logger.info(f"[{run_id}] Starting NARADA discovery task...")
        
        async with self.session_factory() as db:
            if fixture_path and os.path.exists(fixture_path):
                logger.info(f"[{run_id}] Ingesting offline fixture: {fixture_path}")
                with open(fixture_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                
                normalized_jobs = []
                for item in raw_data:
                    # Convert dict to NormalizedJob
                    posted_at = None
                    if item.get("posted_at"):
                        try:
                            posted_at = datetime.fromisoformat(item["posted_at"].replace("Z", "+00:00"))
                        except Exception:
                            pass
                    
                    nj = NormalizedJob(
                        company_name=item.get("company_name", "Target Company"),
                        title=item.get("title", "Lead BI Engineer"),
                        source=item.get("source", "GREENHOUSE"),
                        source_job_id=str(item.get("source_job_id", uuid.uuid4())),
                        url=item.get("url", "https://example.com/job/1"),
                        canonical_url=item.get("canonical_url", item.get("url")),
                        location=item.get("location", "Remote, US"),
                        remote_status=item.get("remote_status", "REMOTE"),
                        salary_min=item.get("salary_min"),
                        salary_max=item.get("salary_max"),
                        salary_currency=item.get("salary_currency", "USD"),
                        posted_at=posted_at,
                        raw_description=item.get("raw_description", ""),
                        required_skills=item.get("required_skills", ["SQL", "Snowflake", "dbt"]),
                        preferred_skills=item.get("preferred_skills", ["Looker", "Python"]),
                        seniority_level=item.get("seniority_level", "SENIOR"),
                        domain_category=item.get("domain_category", "BI_ANALYTICS"),
                    )
                    normalized_jobs.append(nj)

                res = await self.discovery_service.ingest_normalized_jobs(db, normalized_jobs, task_name=f"NARADA_FIXTURE_{run_id[:8]}")
                logger.info(f"[{run_id}] Fixture Ingestion complete: {res}")
                return res
            
            # Live Board Ingestion
            boards = target_boards or DEFAULT_TARGET_BOARDS
            total_stats = {"records_processed": 0, "records_created": 0, "records_updated": 0, "records_failed": 0}
            
            for source_type, company_slug in boards:
                try:
                    logger.info(f"[{run_id}] Fetching {source_type} board for '{company_slug}'...")
                    res = await self.discovery_service.ingest_board(db, source_type, company_slug)
                    total_stats["records_processed"] += res["records_processed"]
                    total_stats["records_created"] += res["records_created"]
                    total_stats["records_updated"] += res["records_updated"]
                    total_stats["records_failed"] += res["records_failed"]
                    logger.info(f"[{run_id}] {company_slug} result: created={res['records_created']}, updated={res['records_updated']}")
                except Exception as exc:
                    logger.warning(f"[{run_id}] Board ingestion failed for {company_slug}: {exc}")
                    total_stats["records_failed"] += 1

            return total_stats

    async def execute_verification(self, limit: int = 50) -> Dict[str, Any]:
        """Execute YAMA live reachability verification."""
        run_id = str(uuid.uuid4())
        logger.info(f"[{run_id}] Starting YAMA URL verification task (limit={limit})...")
        async with self.session_factory() as db:
            res = await self.verification_service.verify_active_jobs(db, limit=limit, task_name=f"YAMA_VERIFY_{run_id[:8]}")
            logger.info(f"[{run_id}] YAMA Verification complete: verified={res['records_updated']}, failed={res['records_failed']}")
            return res

    async def execute_ghost_detection(self, limit: int = 100) -> Dict[str, Any]:
        """Execute Ghost Job signal detection."""
        run_id = str(uuid.uuid4())
        logger.info(f"[{run_id}] Starting Ghost Job scan (limit={limit})...")
        async with self.session_factory() as db:
            res = await self.ghost_detector.scan_and_tag_jobs(db, limit=limit, task_name=f"GHOST_SCAN_{run_id[:8]}")
            logger.info(f"[{run_id}] Ghost Job scan complete: scanned={res['records_updated']}")
            return res

    async def record_heartbeat(self):
        """Record system heartbeat."""
        async with self.session_factory() as db:
            run = AutomationRun(
                task_name="WORKER_HEARTBEAT",
                task_type="HEARTBEAT",
                agent_name="BRAHMASTRA",
                status="SUCCESS",
                started_at=datetime.now(timezone.utc),
                finished_at=datetime.now(timezone.utc),
                duration_ms=5,
                items_processed=1,
                records_processed=1,
                metadata_json={"worker_status": "ONLINE", "uptime_sec": int(time.time())},
            )
            db.add(run)
            await db.commit()

    async def run_loop(self):
        """Continuous background execution loop."""
        logger.info(f"JOBMUNI 24/7 Automation Worker initialized. Interval: {self.loop_interval}s.")
        iteration = 0

        while self.is_running:
            iteration += 1
            logger.info(f"=== Worker Iteration #{iteration} ===")
            
            try:
                # 1. Heartbeat
                await self.record_heartbeat()
                
                # 2. Ingest public feeds
                await self.execute_discovery()
                
                # 3. Verify reachability
                await self.execute_verification()
                
                # 4. Scan ghost jobs
                await self.execute_ghost_detection()
                
            except Exception as exc:
                logger.error(f"[Worker Error in Iteration #{iteration}]: {exc}", exc_info=True)

            logger.info(f"Iteration #{iteration} complete. Sleeping for {self.loop_interval}s...")
            
            # Non-blocking sleep with shutdown interruption
            for _ in range(self.loop_interval):
                if not self.is_running:
                    break
                await asyncio.sleep(1)

        logger.info("JOBMUNI Worker shut down cleanly.")

def main():
    parser = argparse.ArgumentParser(description="JOBMUNI 24/7 Autonomous Background Worker")
    parser.add_argument("--run-once", action="store_true", help="Run scheduled tasks once and exit")
    parser.add_argument("--task", choices=["discovery", "verify", "ghost", "all"], default="all", help="Specific task to run")
    parser.add_argument("--interval", type=int, default=300, help="Loop interval in seconds (default 300)")
    parser.add_argument("--fixture", type=str, default=None, help="Path to offline JSON fixture to ingest")
    args = parser.parse_args()

    worker = JobmuniWorker(loop_interval=args.interval)

    # Set up signal handlers for graceful shutdown on POSIX / Windows
    signal.signal(signal.SIGINT, worker.handle_shutdown)
    signal.signal(signal.SIGTERM, worker.handle_shutdown)

    async def runner():
        if args.run_once:
            logger.info(f"Running single execution for task '{args.task}'...")
            if args.task in ("discovery", "all"):
                await worker.execute_discovery(fixture_path=args.fixture)
            if args.task in ("verify", "all"):
                await worker.execute_verification()
            if args.task in ("ghost", "all"):
                await worker.execute_ghost_detection()
            await worker.record_heartbeat()
            logger.info("Single execution completed.")
        else:
            await worker.run_loop()

    asyncio.run(runner())

if __name__ == "__main__":
    main()
