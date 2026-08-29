import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.job import Job
from app.models.automation_run import AutomationRun

@pytest.mark.asyncio
async def test_list_jobs_and_filtering(client: AsyncClient, db_session):
    # Insert test jobs
    j1 = Job(company_name="Snowflake", title="Lead Analytics Engineer", status="ACTIVE", priority_tier="ACT_NOW", final_score=92)
    j2 = Job(company_name="Stripe", title="Senior BI Developer", status="ACTIVE", priority_tier="HIGH", final_score=84)
    j3 = Job(company_name="Acme", title="Junior Analyst", status="INACTIVE", priority_tier="IGNORE", final_score=35)
    db_session.add_all([j1, j2, j3])
    await db_session.commit()

    # Test list all
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

    # Test priority filter
    res_priority = await client.get("/api/v1/jobs?priority_filter=ACT_NOW")
    assert res_priority.status_code == 200
    act_now_items = res_priority.json()
    assert len(act_now_items) == 1
    assert act_now_items[0]["company_name"] == "Snowflake"

    # Test status filter
    res_status = await client.get("/api/v1/jobs?status_filter=INACTIVE")
    assert res_status.status_code == 200
    inactive_items = res_status.json()
    assert len(inactive_items) == 1
    assert inactive_items[0]["company_name"] == "Acme"

@pytest.mark.asyncio
async def test_get_single_job_and_404(client: AsyncClient, db_session):
    j = Job(company_name="Figma", title="Data Engineering Lead", status="ACTIVE")
    db_session.add(j)
    await db_session.commit()
    await db_session.refresh(j)

    # Test found
    res = await client.get(f"/api/v1/jobs/{j.id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Data Engineering Lead"

    # Test 404
    res_404 = await client.get("/api/v1/jobs/non_existent_id_999")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()

@pytest.mark.asyncio
async def test_automation_runs_api(client: AsyncClient, db_session):
    r1 = AutomationRun(task_name="TEST_TASK_1", task_type="JOB_DISCOVERY", agent_name="NARADA", status="SUCCESS")
    r2 = AutomationRun(task_name="TEST_TASK_2", task_type="FRESHNESS_VERIFY", agent_name="YAMA", status="SUCCESS")
    db_session.add_all([r1, r2])
    await db_session.commit()

    response = await client.get("/api/v1/automation-runs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Filter by agent
    res_narada = await client.get("/api/v1/automation-runs?agent_name=NARADA")
    assert res_narada.status_code == 200
    narada_runs = res_narada.json()
    assert all(r["agent_name"] == "NARADA" for r in narada_runs)

@pytest.mark.asyncio
async def test_manual_parse_endpoint(client: AsyncClient):
    payload = {
        "company_name": "Databricks",
        "title": "Lead Solutions Architect",
        "raw_text": "Seeking a Lead Architect with SQL, Databricks, Python, and Snowflake experience. Compensation: $180k - $240k. 100% remote.",
        "location": "Remote, US"
    }
    response = await client.post("/api/v1/jobs/manual-parse", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "Databricks"
    assert data["seniority_level"] == "LEAD"
    assert data["remote_type"] == "REMOTE"
    assert data["salary_min"] == 180000
    assert data["salary_max"] == 240000
    assert data["final_score"] > 0
