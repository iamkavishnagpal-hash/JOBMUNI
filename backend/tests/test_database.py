import pytest
from sqlalchemy import select
from app.models.candidate_profile import CandidateProfile, EvidenceItem
from app.models.job import Job, JobSkill
from app.models.scoring_config import ScoringConfig

@pytest.mark.asyncio
async def test_database_crud_and_models(test_db):
    # 1. Create Profile and Evidence
    profile = CandidateProfile(
        full_name="Kavish",
        email="kavish@example.com",
        target_title="Lead BI & Analytics Engineer",
        target_seniority="LEAD"
    )
    test_db.add(profile)
    await test_db.flush()

    evidence = EvidenceItem(
        profile_id=profile.id,
        category="METRIC",
        skill_or_tool="Snowflake",
        title="Warehouse Cost Optimization",
        evidence_text="Reduced Snowflake monthly compute by 38% through warehouse auto-suspend and clustering policies.",
        quant_metric="$168k/yr savings"
    )
    test_db.add(evidence)
    await test_db.commit()

    # 2. Query back
    result = await test_db.execute(select(CandidateProfile).where(CandidateProfile.id == profile.id))
    fetched_profile = result.scalars().first()
    assert fetched_profile is not None
    assert fetched_profile.full_name == "Kavish"
    assert len(fetched_profile.evidence_items) == 1
    assert fetched_profile.evidence_items[0].skill_or_tool == "Snowflake"
