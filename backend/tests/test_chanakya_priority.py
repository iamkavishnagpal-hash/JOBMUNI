import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient

from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.services.chanakya_engine import chanakya_engine
from app.services.evidence_service import saraswati_service

@pytest.fixture
def test_job():
    return Job(
        company_name="Snowflake",
        title="Senior Analytics Engineer",
        salary_min=190000,
        salary_max=240000,
        salary_currency="USD",
        remote_type="REMOTE",
        location="Remote, US",
        status="ACTIVE",
        verification_status="ACTIVE",
        freshness_conf=1.0,
        hiring_signal_score=85,
        posted_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

def test_high_skill_high_compensation(test_job):
    alignment_data = {
        "required_coverage_pct": 100.0,
        "preferred_coverage_pct": 100.0,
        "evidence_coverage_pct": 100.0,
        "experience_alignment_pct": 95.0,
        "match_verdict": "STRONG_MATCH",
    }
    compensation_data = {
        "compensation_tier": "PREMIUM",
        "salary_fit_score": 100.0,
        "market_position_score": 95.0,
        "remote_value_score": 100.0,
        "location_value_score": 100.0,
        "disclosed_salary": {"formatted": "USD $190,000 - $240,000"},
    }

    res = chanakya_engine.evaluate_priority(test_job, alignment_data, compensation_data)

    assert res["priority_score"] >= 88
    assert res["priority_tier"] in ("CRITICAL", "HIGH")
    assert res["urgency_score"] >= 75
    assert res["actionability"] == "READY_TO_ACT"
    assert res["effort_level"] == "LOW"
    assert res["recommended_action"] == "APPLY"
    assert len(res["positive_factors"]) >= 3

def test_high_skill_low_compensation(test_job):
    alignment_data = {
        "required_coverage_pct": 100.0,
        "preferred_coverage_pct": 80.0,
        "evidence_coverage_pct": 90.0,
        "experience_alignment_pct": 90.0,
        "match_verdict": "STRONG_MATCH",
    }
    compensation_data = {
        "compensation_tier": "LOW",
        "salary_fit_score": 25.0,
        "market_position_score": 20.0,
        "remote_value_score": 100.0,
        "location_value_score": 100.0,
        "disclosed_salary": {"formatted": "USD $100,000 - $120,000"},
    }

    res = chanakya_engine.evaluate_priority(test_job, alignment_data, compensation_data)

    # Low comp is a safety gate
    assert res["priority_tier"] == "LOW"
    assert res["priority_score"] <= 45
    assert res["actionability"] == "BLOCKED"
    assert res["recommended_action"] == "SKIP"
    assert "Disclosed compensation falls below" in res["blocking_factors"][0]

def test_low_skill_high_compensation(test_job):
    alignment_data = {
        "required_coverage_pct": 20.0,
        "preferred_coverage_pct": 0.0,
        "evidence_coverage_pct": 20.0,
        "experience_alignment_pct": 50.0,
        "match_verdict": "WEAK_MATCH",
    }
    compensation_data = {
        "compensation_tier": "PREMIUM",
        "salary_fit_score": 100.0,
        "market_position_score": 95.0,
        "remote_value_score": 100.0,
        "location_value_score": 100.0,
    }

    res = chanakya_engine.evaluate_priority(test_job, alignment_data, compensation_data)

    assert res["priority_score"] < 60
    assert res["priority_tier"] in ("LOW", "SKIP")
    assert res["actionability"] == "NEEDS_REVIEW"

def test_fresh_job_vs_stale_job_urgency(test_job):
    test_job.posted_at = datetime.now(timezone.utc) - timedelta(days=1)
    alignment = {"required_coverage_pct": 80.0, "preferred_coverage_pct": 70.0, "evidence_coverage_pct": 80.0}
    compensation = {"compensation_tier": "STRONG", "salary_fit_score": 85.0, "market_position_score": 80.0}

    res_fresh = chanakya_engine.evaluate_priority(test_job, alignment, compensation)

    test_job.posted_at = datetime.now(timezone.utc) - timedelta(days=40)
    res_stale = chanakya_engine.evaluate_priority(test_job, alignment, compensation)

    assert res_fresh["urgency_score"] > res_stale["urgency_score"]
    assert res_fresh["urgency_score"] >= 80
    assert res_stale["urgency_score"] <= 50

def test_expired_inactive_job_penalty(test_job):
    test_job.status = "INACTIVE"
    test_job.verification_status = "INACTIVE"

    alignment = {"required_coverage_pct": 100.0, "preferred_coverage_pct": 100.0, "evidence_coverage_pct": 100.0}
    compensation = {"compensation_tier": "PREMIUM", "salary_fit_score": 100.0, "market_position_score": 95.0}

    res = chanakya_engine.evaluate_priority(test_job, alignment, compensation)

    assert res["priority_score"] <= 20
    assert res["priority_tier"] == "SKIP"
    assert res["actionability"] == "EXPIRED"
    assert res["recommended_action"] == "SKIP"

def test_unknown_salary_neutral_handling(test_job):
    alignment = {
        "required_coverage_pct": 95.0,
        "preferred_coverage_pct": 80.0,
        "evidence_coverage_pct": 90.0,
        "experience_alignment_pct": 90.0,
        "match_verdict": "STRONG_MATCH"
    }
    compensation = {
        "compensation_tier": "UNKNOWN",
        "salary_fit_score": 0.0,
        "market_position_score": 0.0,
        "remote_value_score": 100.0,
        "location_value_score": 100.0,
    }

    res = chanakya_engine.evaluate_priority(test_job, alignment, compensation)

    # Undisclosed compensation does not drag high skill match to 0
    assert res["priority_score"] >= 75
    assert res["priority_tier"] in ("CRITICAL", "HIGH")
    assert "Base salary unstated on job posting" in res["negative_factors"]

def test_configurable_weights(test_job):
    alignment = {"required_coverage_pct": 100.0, "preferred_coverage_pct": 100.0, "evidence_coverage_pct": 100.0}
    compensation = {"compensation_tier": "STRONG", "salary_fit_score": 85.0, "market_position_score": 80.0}

    # Skill heavy
    weights_skill = {"skill_alignment": 0.70, "compensation": 0.10, "evidence_density": 0.10, "hiring_signal": 0.05, "freshness": 0.05, "remote_location": 0.0}
    res_skill = chanakya_engine.evaluate_priority(test_job, alignment, compensation, weights=weights_skill)

    # Comp heavy
    weights_comp = {"skill_alignment": 0.10, "compensation": 0.70, "evidence_density": 0.05, "hiring_signal": 0.05, "freshness": 0.05, "remote_location": 0.05}
    res_comp = chanakya_engine.evaluate_priority(test_job, alignment, compensation, weights=weights_comp)

    assert res_skill["priority_score"] != res_comp["priority_score"]

@pytest.mark.asyncio
async def test_chanakya_api_endpoints(client: AsyncClient, db_session):
    profile = await saraswati_service.get_or_create_default_profile(db_session)

    job1 = Job(
        company_name="Databricks",
        title="Principal BI Architect",
        salary_min=210000,
        salary_max=260000,
        salary_currency="USD",
        remote_type="REMOTE",
        location="Remote, US",
        status="ACTIVE",
    )
    job2 = Job(
        company_name="Legacy Corp",
        title="Junior Analyst",
        salary_min=80000,
        salary_max=95000,
        salary_currency="USD",
        remote_type="ONSITE",
        location="Austin, TX",
        status="ACTIVE",
    )
    db_session.add_all([job1, job2])
    await db_session.commit()
    await db_session.refresh(job1)
    await db_session.refresh(job2)

    # Test GET /api/v1/jobs/{job_id}/priority
    get_res = await client.get(f"/api/v1/jobs/{job1.id}/priority")
    assert get_res.status_code == 200
    prio1 = get_res.json()
    assert prio1["job_id"] == job1.id
    assert "priority_score" in prio1
    assert "recommended_action" in prio1
    assert "score_breakdown" in prio1

    # Test GET /api/v1/jobs/prioritized
    list_res = await client.get("/api/v1/jobs/prioritized")
    assert list_res.status_code == 200
    prioritized_list = list_res.json()
    assert len(prioritized_list) >= 2
    # Ensure ordered by priority score descending
    scores = [j["priority_score"] for j in prioritized_list]
    assert scores == sorted(scores, reverse=True)
