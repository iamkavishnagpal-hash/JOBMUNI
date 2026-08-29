import os
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from worker.main import JobmuniWorker
from app.models.automation_run import AutomationRun
from app.models.job import Job

@pytest.mark.asyncio
async def test_worker_fixture_execution(test_engine, db_session):
    fixture_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "sample_jobs.json"))
    assert os.path.exists(fixture_path)

    session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    worker = JobmuniWorker(loop_interval=60, session_factory=session_factory)
    
    # 1. Test discovery execution with fixture
    res = await worker.execute_discovery(fixture_path=fixture_path)
    assert res["status"] == "SUCCESS"
    assert res["records_created"] == 3
    assert res["records_failed"] == 0

    # Verify jobs exist in DB
    q = await db_session.execute(select(Job))
    jobs = q.scalars().all()
    assert len(jobs) == 3

    # 2. Test YAMA verification execution
    v_res = await worker.execute_verification(limit=10)
    assert v_res["records_processed"] >= 3

    # 3. Test Ghost detection execution
    g_res = await worker.execute_ghost_detection(limit=10)
    assert g_res["records_processed"] >= 3

    # 4. Test heartbeat
    await worker.record_heartbeat()

    # Verify automation runs logged in DB
    runs_q = await db_session.execute(select(AutomationRun))
    runs = runs_q.scalars().all()
    assert len(runs) >= 4
    task_types = [r.task_type for r in runs]
    assert "JOB_DISCOVERY" in task_types
    assert "FRESHNESS_VERIFY" in task_types
    assert "GHOST_DETECTION" in task_types
    assert "HEARTBEAT" in task_types
