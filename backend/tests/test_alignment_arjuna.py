import pytest
from httpx import AsyncClient
from app.models.job import Job, JobSkill, Company
from app.models.candidate_profile import CandidateProfile, EvidenceItem
from app.services.alignment_engine import arjuna_engine
from app.services.evidence_service import saraswati_service
from app.services.skill_taxonomy import normalize_skill

@pytest.mark.asyncio
async def test_skill_normalization():
    # Canonical aliases
    norm_pbi, is_pbi = normalize_skill("Microsoft Power BI")
    assert norm_pbi == "Power BI"
    assert is_pbi is True

    norm_sql, is_sql = normalize_skill("PostgreSQL")
    assert norm_sql == "SQL"
    assert is_sql is True

    norm_dbt, is_dbt = normalize_skill("dbt Cloud")
    assert norm_dbt == "dbt"
    assert is_dbt is True

    # Unsupported unknown skill
    norm_cobol, is_cobol = normalize_skill("Cobol Mainframe")
    assert is_cobol is False
    assert norm_cobol == "Cobol Mainframe"

@pytest.mark.asyncio
async def test_100_percent_required_skill_match(db_session):
    await saraswati_service.seed_default_evidence(db_session)
    profile = await saraswati_service.get_or_create_default_profile(db_session)
    evidence_items = await saraswati_service.list_evidence(db_session, active_only=True)

    job = Job(
        company_name="Snowflake Inc",
        title="Senior Analytics Engineer",
        seniority_level="SENIOR",
        skills=[
            JobSkill(skill_name="SQL", is_required=True),
            JobSkill(skill_name="Snowflake", is_required=True),
            JobSkill(skill_name="dbt", is_required=True),
        ]
    )

    result = arjuna_engine.align_job_with_evidence(job, evidence_items, profile)

    assert result["match_verdict"] == "STRONG_MATCH"
    assert result["required_coverage_pct"] == 100.0
    assert len(result["matched_required"]) == 3
    assert len(result["missing_required"]) == 0
    # Confirm exact evidence IDs attached
    sql_match = next(m for m in result["matched_required"] if m["normalized_skill"] == "SQL")
    assert len(sql_match["evidence_ids"]) >= 1
    assert sql_match["verification_state"] == "VERIFIED_GROUND_TRUTH"
    assert sql_match["top_metric"] is not None

@pytest.mark.asyncio
async def test_partial_required_match(db_session):
    await saraswati_service.seed_default_evidence(db_session)
    profile = await saraswati_service.get_or_create_default_profile(db_session)
    evidence_items = await saraswati_service.list_evidence(db_session, active_only=True)

    job = Job(
        company_name="Legacy Tech",
        title="Lead BI Developer",
        seniority_level="LEAD",
        skills=[
            JobSkill(skill_name="SQL", is_required=True),
            JobSkill(skill_name="Cobol Mainframe", is_required=True),
        ]
    )

    result = arjuna_engine.align_job_with_evidence(job, evidence_items, profile)

    assert result["match_verdict"] == "PARTIAL_MATCH"
    assert result["required_coverage_pct"] == 50.0
    assert len(result["matched_required"]) == 1
    assert len(result["missing_required"]) == 1
    assert result["missing_required"][0]["normalized_skill"] == "Cobol Mainframe"
    assert result["missing_required"][0]["verification_state"] == "NO_EVIDENCE"

@pytest.mark.asyncio
async def test_missing_required_skill(db_session):
    await saraswati_service.seed_default_evidence(db_session)
    profile = await saraswati_service.get_or_create_default_profile(db_session)
    evidence_items = await saraswati_service.list_evidence(db_session, active_only=True)

    job = Job(
        company_name="Hardware Corp",
        title="Embedded C++ Engineer",
        seniority_level="SENIOR",
        skills=[
            JobSkill(skill_name="Rust", is_required=True),
            JobSkill(skill_name="Verilog", is_required=True),
        ]
    )

    result = arjuna_engine.align_job_with_evidence(job, evidence_items, profile)

    assert result["match_verdict"] == "INSUFFICIENT_EVIDENCE"
    assert result["required_coverage_pct"] == 0.0
    assert len(result["matched_required"]) == 0
    assert len(result["missing_required"]) == 2

@pytest.mark.asyncio
async def test_preferred_skill_matching(db_session):
    await saraswati_service.seed_default_evidence(db_session)
    profile = await saraswati_service.get_or_create_default_profile(db_session)
    evidence_items = await saraswati_service.list_evidence(db_session, active_only=True)

    job = Job(
        company_name="Modern BI Labs",
        title="Senior BI Engineer",
        seniority_level="SENIOR",
        skills=[
            JobSkill(skill_name="SQL", is_required=True),
            JobSkill(skill_name="Looker", is_required=False),
            JobSkill(skill_name="UnicornTechTool", is_required=False),
        ]
    )

    result = arjuna_engine.align_job_with_evidence(job, evidence_items, profile)

    assert result["required_coverage_pct"] == 100.0
    assert result["preferred_coverage_pct"] == 50.0
    assert len(result["matched_preferred"]) == 1
    assert result["matched_preferred"][0]["normalized_skill"] == "Looker"
    assert len(result["missing_preferred"]) == 1
    assert result["missing_preferred"][0]["requirement"] == "UnicornTechTool"

@pytest.mark.asyncio
async def test_no_evidence_bank_empty(db_session):
    # Pass empty evidence list
    job = Job(
        company_name="Stripe",
        title="Staff Data Engineer",
        seniority_level="STAFF",
        skills=[JobSkill(skill_name="SQL", is_required=True)]
    )
    result = arjuna_engine.align_job_with_evidence(job, [], None)

    assert result["match_verdict"] == "INSUFFICIENT_EVIDENCE"
    assert result["required_coverage_pct"] == 0.0
    assert result["evidence_coverage_pct"] == 0.0

@pytest.mark.asyncio
async def test_multiple_evidence_records(db_session):
    profile = await saraswati_service.get_or_create_default_profile(db_session)
    # Add 2 separate SQL evidence items
    ev1 = EvidenceItem(
        profile_id=profile.id,
        category="TECH_SKILL",
        skill_or_tool="SQL",
        title="ETL Optimization",
        evidence_text="Optimized SQL ETL pipelines reducing time by 50%.",
        quant_metric="50% faster",
        confidence=0.9,
    )
    ev2 = EvidenceItem(
        profile_id=profile.id,
        category="BUSINESS_IMPACT",
        skill_or_tool="SQL",
        title="Query Tuning",
        evidence_text="Rewrote query joins for business intelligence dashboards.",
        quant_metric="10x faster joins",
        confidence=1.0,
    )
    db_session.add_all([ev1, ev2])
    await db_session.commit()

    job = Job(company_name="DataCo", title="BI Engineer", seniority_level="SENIOR", skills=[JobSkill(skill_name="SQL", is_required=True)])
    result = arjuna_engine.align_job_with_evidence(job, [ev1, ev2], profile)

    match = result["matched_required"][0]
    assert match["evidence_count"] == 2
    assert len(match["evidence_ids"]) == 2
    assert match["confidence"] == 1.0

@pytest.mark.asyncio
async def test_alignment_api_endpoints(client: AsyncClient, db_session):
    await saraswati_service.seed_default_evidence(db_session)
    
    # Create test job
    job = Job(
        company_name="Snowflake Inc",
        title="Lead Analytics Engineer",
        seniority_level="LEAD",
        location="Remote, US",
        status="ACTIVE",
    )
    db_session.add(job)
    await db_session.flush()

    db_session.add(JobSkill(job_id=job.id, skill_name="Snowflake", is_required=True))
    db_session.add(JobSkill(job_id=job.id, skill_name="dbt", is_required=True))
    db_session.add(JobSkill(job_id=job.id, skill_name="Tableau", is_required=False))
    await db_session.commit()

    # Test GET /api/v1/jobs/{job_id}/alignment
    get_res = await client.get(f"/api/v1/jobs/{job.id}/alignment")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["job_id"] == job.id
    assert data["match_verdict"] == "STRONG_MATCH"
    assert data["required_coverage_pct"] == 100.0
    assert len(data["matched_required"]) == 2
    assert "reasoning" in data
    assert len(data["reasoning"]["positive_factors"]) >= 2

    # Test POST /api/v1/jobs/{job_id}/alignment (re-evaluation)
    post_res = await client.post(f"/api/v1/jobs/{job.id}/alignment")
    assert post_res.status_code == 200
    assert post_res.json()["match_verdict"] == "STRONG_MATCH"
