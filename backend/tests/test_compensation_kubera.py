import pytest
from httpx import AsyncClient
from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.services.compensation_service import kubera_service
from app.services.currency_provider import currency_provider
from app.services.evidence_service import saraswati_service

@pytest.fixture
def test_profile():
    return CandidateProfile(
        full_name="Kavish",
        email="kavish@test.local",
        target_comp_min=160000,
        target_comp_preferred=195000,
        target_comp_max=230000,
        currency="USD",
        remote_preference="REMOTE_FIRST",
        international_preference="US_ONLY",
        preferred_locations=["Remote US", "San Francisco, CA", "Seattle, WA", "New York, NY"]
    )

def test_currency_conversion():
    # USD to USD
    res_usd = currency_provider.convert(100000, "USD", "USD")
    assert res_usd.conversion_status == "EXACT"
    assert res_usd.converted_amount == 100000.0

    # EUR to USD (1.08)
    res_eur = currency_provider.convert(100000, "EUR", "USD")
    assert res_eur.conversion_status == "CONVERTED"
    assert res_eur.converted_amount == 108000.0

    # GBP to USD (1.28)
    res_gbp = currency_provider.convert(100000, "GBP", "USD")
    assert res_gbp.conversion_status == "CONVERTED"
    assert res_gbp.converted_amount == 128000.0

    # Unknown currency
    res_unk = currency_provider.convert(100000, "XYZ", "USD")
    assert res_unk.conversion_status == "UNKNOWN_RATE"
    assert res_unk.converted_amount == 100000.0

def test_salary_below_minimum(test_profile):
    job = Job(
        company_name="LowPay Corp",
        title="BI Analyst",
        salary_min=120000,
        salary_max=135000,
        salary_currency="USD",
        remote_type="REMOTE",
    )
    res = kubera_service.evaluate_compensation(job, test_profile)

    assert res["compensation_tier"] == "LOW"
    assert res["salary_fit_score"] < 50.0
    assert "below candidate minimum" in res["reasoning"]["why_tier_assigned"]

def test_salary_inside_minimum_preferred_range(test_profile):
    job = Job(
        company_name="MidRange Tech",
        title="Senior BI Engineer",
        salary_min=165000,
        salary_max=175000,
        salary_currency="USD",
        remote_type="REMOTE",
    )
    res = kubera_service.evaluate_compensation(job, test_profile)

    assert res["compensation_tier"] == "ACCEPTABLE"
    assert 60.0 <= res["salary_fit_score"] <= 85.0

def test_salary_above_preferred_range(test_profile):
    job = Job(
        company_name="HighGrowth Inc",
        title="Lead Analytics Engineer",
        salary_min=190000,
        salary_max=210000,
        salary_currency="USD",
        remote_type="REMOTE",
    )
    res = kubera_service.evaluate_compensation(job, test_profile)

    assert res["compensation_tier"] == "STRONG"
    assert 85.0 <= res["salary_fit_score"] <= 99.0

def test_salary_above_maximum_premium(test_profile):
    job = Job(
        company_name="Tier1 Tech",
        title="Staff Data Architect",
        salary_min=220000,
        salary_max=245000,
        salary_currency="USD",
        remote_type="REMOTE",
    )
    res = kubera_service.evaluate_compensation(job, test_profile)

    assert res["compensation_tier"] == "PREMIUM"
    assert res["salary_fit_score"] == 100.0
    assert res["total_compensation_score"] >= 90

def test_missing_salary_undisclosed(test_profile):
    job = Job(
        company_name="Stealth AI",
        title="Lead BI Engineer",
        salary_min=None,
        salary_max=None,
        remote_type="REMOTE",
    )
    res = kubera_service.evaluate_compensation(job, test_profile)

    assert res["compensation_tier"] == "UNKNOWN"
    assert res["salary_source"] == "UNDISCLOSED_ON_POSTING"
    assert res["salary_fit_score"] == 0
    assert len(res["reasoning"]["unknown_factors"]) >= 2

def test_remote_preference_alignment(test_profile):
    job_remote = Job(company_name="A", title="Role A", salary_min=180000, salary_max=200000, remote_type="REMOTE")
    job_onsite = Job(company_name="B", title="Role B", salary_min=180000, salary_max=200000, remote_type="ONSITE")

    res_rem = kubera_service.evaluate_compensation(job_remote, test_profile)
    res_ons = kubera_service.evaluate_compensation(job_onsite, test_profile)

    assert res_rem["remote_value_score"] == 100.0
    assert res_ons["remote_value_score"] == 40.0
    assert res_rem["total_compensation_score"] > res_ons["total_compensation_score"]

def test_international_location_penalty(test_profile):
    job_us = Job(company_name="US Corp", title="Role", salary_min=180000, salary_max=200000, location="San Francisco, CA", remote_type="ONSITE")
    job_intl = Job(company_name="UK Corp", title="Role", salary_min=180000, salary_max=200000, location="London, UK", remote_type="ONSITE")

    res_us = kubera_service.evaluate_compensation(job_us, test_profile)
    res_intl = kubera_service.evaluate_compensation(job_intl, test_profile)

    assert res_us["location_value_score"] == 100.0
    assert res_intl["location_value_score"] == 25.0

@pytest.mark.asyncio
async def test_compensation_api_endpoints(client: AsyncClient, db_session):
    profile = await saraswati_service.get_or_create_default_profile(db_session)

    job = Job(
        company_name="Databricks",
        title="Staff Solutions Architect",
        salary_min=200000,
        salary_max=240000,
        salary_currency="USD",
        remote_type="REMOTE",
        location="Remote, US",
        status="ACTIVE",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Test GET /api/v1/jobs/{job_id}/compensation
    get_res = await client.get(f"/api/v1/jobs/{job.id}/compensation")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["job_id"] == job.id
    assert data["compensation_tier"] == "PREMIUM"
    assert data["salary_fit_score"] == 100.0
    assert data["disclosed_salary"]["formatted"] == "USD $200,000 - $240,000"

    # Test candidate compensation policy GET and PUT
    pol_get = await client.get("/api/v1/evidence-bank/candidate/compensation-policy")
    assert pol_get.status_code == 200
    assert pol_get.json()["target_comp_min"] == profile.target_comp_min

    # Update policy (raise min to 250k)
    pol_put = await client.put(
        "/api/v1/evidence-bank/candidate/compensation-policy",
        json={"target_comp_min": 250000, "target_comp_preferred": 280000, "target_comp_max": 320000}
    )
    assert pol_put.status_code == 200
    assert pol_put.json()["target_comp_min"] == 250000

    # Re-evaluate compensation with POST
    post_res = await client.post(f"/api/v1/jobs/{job.id}/compensation")
    assert post_res.status_code == 200
    # Now $240k is below $250k min -> tier changes to LOW
    assert post_res.json()["compensation_tier"] == "LOW"
