import pytest
from datetime import datetime, timezone, timedelta
from app.services.ghost_detector import GhostDetectorService
from app.models.job import Job

def test_ghost_detector_active_fresh_job():
    fresh_job = Job(
        company_name="Snowflake",
        title="Lead BI Engineer",
        posted_at=datetime.now(timezone.utc) - timedelta(days=5),
        first_seen_at=datetime.now(timezone.utc) - timedelta(days=5),
        raw_description="A complete job description with SQL, Snowflake, dbt, and modern data stack requirements. Over 100 characters long.",
        location="Remote, US",
        remote_type="REMOTE",
        verification_status="ACTIVE",
        last_http_status=200,
    )
    score, reasons, status = GhostDetectorService.evaluate_job(fresh_job)
    assert score < 40
    assert status == "ACTIVE"
    assert len(reasons) == 0

def test_ghost_detector_stale_60_days():
    stale_job = Job(
        company_name="Legacy Tech",
        title="Senior BI Analyst",
        posted_at=datetime.now(timezone.utc) - timedelta(days=65),
        first_seen_at=datetime.now(timezone.utc) - timedelta(days=65),
        raw_description="Short text",  # < 100 chars (+20)
        location="Austin, TX",
        remote_type="HYBRID",
        verification_status="ACTIVE",
        last_http_status=200,
    )
    score, reasons, status = GhostDetectorService.evaluate_job(stale_job)
    # Age > 60d (+25) + short desc (+20) = 45 -> STALE
    assert 40 <= score < 70
    assert status == "STALE"
    assert any("exceeds 60 days" in r for r in reasons)
    assert any("description" in r for r in reasons)

def test_ghost_detector_inactive_removed():
    inactive_job = Job(
        company_name="Fast Corp",
        title="Staff Data Architect",
        posted_at=datetime.now(timezone.utc) - timedelta(days=40),
        first_seen_at=datetime.now(timezone.utc) - timedelta(days=40),
        raw_description="Standard full description text exceeding 100 characters in length for realistic testing.",
        location="San Francisco, CA",
        remote_type="REMOTE",
        verification_status="INACTIVE",
        last_http_status=404,
    )
    score, reasons, status = GhostDetectorService.evaluate_job(inactive_job)
    # Inactive (+60) + age > 30d (+10) = 70 -> LIKELY_INACTIVE
    assert score >= 70
    assert status == "LIKELY_INACTIVE"
    assert any("404/410" in r for r in reasons)

@pytest.mark.asyncio
async def test_ghost_detector_scan_and_tag(db_session):
    service = GhostDetectorService()
    job = Job(
        company_name="Old Co",
        title="Data Modeler",
        posted_at=datetime.now(timezone.utc) - timedelta(days=100),
        first_seen_at=datetime.now(timezone.utc) - timedelta(days=100),
        raw_description="Tiny",
        status="ACTIVE",
        verification_status="INACTIVE",
        last_http_status=404,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    res = await service.scan_and_tag_jobs(db_session, limit=10)
    assert res["records_updated"] == 1
    assert job.ghost_status == "LIKELY_INACTIVE"
    assert job.status == "INACTIVE"
