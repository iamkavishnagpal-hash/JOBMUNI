import pytest
from sqlalchemy import select
from app.services.ats_connectors.base import NormalizedJob
from app.services.discovery_service import NaradaDiscoveryService, normalize_canonical_url
from app.models.job import Job, Company

def test_normalize_canonical_url():
    raw1 = "https://boards.greenhouse.io/stripe/jobs/123?gh_src=linkedin&utm_campaign=data"
    assert normalize_canonical_url(raw1) == "https://boards.greenhouse.io/stripe/jobs/123"

    raw2 = "https://jobs.lever.co/netflix/456/?lever-source=indeed&utm_medium=cpc"
    assert normalize_canonical_url(raw2) == "https://jobs.lever.co/netflix/456"

@pytest.mark.asyncio
async def test_idempotent_ingestion_and_deduplication(db_session):
    service = NaradaDiscoveryService()

    jobs_batch_1 = [
        NormalizedJob(
            company_name="Snowflake",
            title="Lead Analytics Engineer",
            source="GREENHOUSE",
            source_job_id="snow_dedup_001",
            url="https://boards.greenhouse.io/snowflake/jobs/snow_dedup_001?gh_src=email",
            location="Remote",
            remote_status="REMOTE",
            salary_min=175000,
            salary_max=225000,
            raw_description="Lead role with SQL, Snowflake, and dbt.",
            required_skills=["SQL", "Snowflake", "dbt"],
        ),
        NormalizedJob(
            company_name="Databricks",
            title="Senior BI Architect",
            source="LEVER",
            source_job_id="db_dedup_002",
            url="https://jobs.lever.co/databricks/db_dedup_002",
            location="Remote",
            remote_status="REMOTE",
            salary_min=165000,
            salary_max=210000,
            raw_description="Senior BI with Databricks, SQL, and Power BI.",
            required_skills=["Databricks", "SQL", "Power BI"],
        ),
    ]

    # First ingestion run
    res1 = await service.ingest_normalized_jobs(db_session, jobs_batch_1, task_name="TEST_RUN_1")
    assert res1["records_created"] == 2
    assert res1["records_updated"] == 0
    assert res1["records_failed"] == 0

    # Verify DB has 2 jobs
    q = await db_session.execute(select(Job))
    all_jobs = q.scalars().all()
    assert len(all_jobs) == 2

    # Second ingestion run with SAME items (plus tracking query param change)
    jobs_batch_2 = [
        NormalizedJob(
            company_name="Snowflake",
            title="Lead Analytics Engineer",
            source="GREENHOUSE",
            source_job_id="snow_dedup_001",
            url="https://boards.greenhouse.io/snowflake/jobs/snow_dedup_001?gh_src=twitter&utm_source=feed",
            location="Remote",
            remote_status="REMOTE",
            salary_min=180000,  # updated salary
            salary_max=230000,
            raw_description="Updated description with SQL, Snowflake, dbt.",
            required_skills=["SQL", "Snowflake", "dbt"],
        ),
    ]

    res2 = await service.ingest_normalized_jobs(db_session, jobs_batch_2, task_name="TEST_RUN_2")
    assert res2["records_created"] == 0
    assert res2["records_updated"] == 1
    assert res2["records_failed"] == 0

    # Verify DB STILL has 2 jobs total (no duplicate created)
    q2 = await db_session.execute(select(Job))
    all_jobs_after = q2.scalars().all()
    assert len(all_jobs_after) == 2

    # Verify the updated job has the updated fields
    snow_job = next(j for j in all_jobs_after if j.source_job_id == "snow_dedup_001")
    assert snow_job.verification_status == "ACTIVE"
    assert snow_job.company_name == "Snowflake"
