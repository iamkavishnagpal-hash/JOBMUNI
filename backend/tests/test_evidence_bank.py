import pytest
from httpx import AsyncClient
from app.services.evidence_service import saraswati_service
from app.schemas.evidence import EvidenceItemCreate, EvidenceItemUpdate

@pytest.mark.asyncio
async def test_seed_default_evidence(db_session):
    # 1. First seeding run
    res1 = await saraswati_service.seed_default_evidence(db_session)
    assert res1["status"] == "SUCCESS"
    assert res1["created_count"] >= 12

    # 2. Idempotent check
    res2 = await saraswati_service.seed_default_evidence(db_session)
    assert res2["status"] == "ALREADY_SEEDED"

    # 3. Verify items in DB
    items = await saraswati_service.list_evidence(db_session)
    assert len(items) >= 12
    skills = [it.skill_or_tool for it in items]
    assert "SQL" in skills
    assert "Snowflake" in skills
    assert "dbt" in skills
    assert "Looker" in skills

@pytest.mark.asyncio
async def test_list_evidence_filtering(db_session):
    await saraswati_service.seed_default_evidence(db_session)

    # Filter by category
    tech_items = await saraswati_service.list_evidence(db_session, category="TECH_SKILL")
    assert len(tech_items) > 0
    assert all(it.category == "TECH_SKILL" for it in tech_items)

    # Filter by skill
    snow_items = await saraswati_service.list_evidence(db_session, skill_or_tool="Snowflake")
    assert len(snow_items) >= 1
    assert any("Snowflake" in it.skill_or_tool for it in snow_items)

    # Search by keyword
    cost_items = await saraswati_service.list_evidence(db_session, search="savings")
    assert len(cost_items) >= 1

@pytest.mark.asyncio
async def test_create_evidence_item_valid(db_session):
    payload = EvidenceItemCreate(
        category="TECH_SKILL",
        skill_or_tool="dbt",
        title="Automated Data Quality Testing Suite",
        evidence_text="Implemented dbt test assertions across 50 staging and dimensional models, catching 14 critical pipeline anomalies before executive review.",
        situation="Production data warehouse suffered from silent null values in foreign key joins.",
        task="Enforce strict relational data constraints at build time.",
        action="Created singular and generic dbt schema tests embedded in automated pull request CI pipelines.",
        result="Zero schema breakages reached downstream reporting tables over a 12-month period.",
        quant_metric="100% prevention of relational schema breakages over 12 months",
        source_company="Data Scale Inc",
        tags=["dbt", "Data Quality", "Testing", "CI/CD"],
        confidence=1.0,
    )
    item = await saraswati_service.create_evidence_item(db_session, payload)
    assert item.id is not None
    assert item.skill_or_tool == "dbt"
    assert item.quant_metric == "100% prevention of relational schema breakages over 12 months"
    assert item.situation is not None

@pytest.mark.asyncio
async def test_create_evidence_item_short_claim(db_session):
    with pytest.raises(Exception) as exc:
        EvidenceItemCreate(
            category="TECH_SKILL",
            skill_or_tool="SQL",
            title="Good at SQL",
            evidence_text="Too short",  # 9 chars (< 10 chars) -> should fail integrity validation
        )
    assert "at least 10 characters" in str(exc.value)

@pytest.mark.asyncio
async def test_update_and_delete_evidence_item(db_session):
    payload = EvidenceItemCreate(
        category="TECH_SKILL",
        skill_or_tool="Python",
        title="Initial Title",
        evidence_text="Initial descriptive text of sufficient length.",
        quant_metric="10x speedup",
    )
    item = await saraswati_service.create_evidence_item(db_session, payload)

    # Update
    updated = await saraswati_service.update_evidence_item(
        db_session,
        item.id,
        EvidenceItemUpdate(title="Updated High Impact Python Title", quant_metric="25x speedup")
    )
    assert updated.title == "Updated High Impact Python Title"
    assert updated.quant_metric == "25x speedup"

    # Soft Delete
    deleted = await saraswati_service.delete_evidence_item(db_session, item.id)
    assert deleted is True

    # Confirm not in active list
    active_items = await saraswati_service.list_evidence(db_session, active_only=True)
    assert item.id not in [it.id for it in active_items]

@pytest.mark.asyncio
async def test_skills_summary_aggregation(db_session):
    await saraswati_service.seed_default_evidence(db_session)
    summary = await saraswati_service.get_skills_summary(db_session)

    assert summary.total_skills >= 10
    assert summary.total_evidence_items >= 12
    sql_skill = next((s for s in summary.skills if s.skill_name == "SQL"), None)
    assert sql_skill is not None
    assert sql_skill.evidence_count >= 1
    assert len(sql_skill.top_metrics) >= 1
    assert len(sql_skill.evidence_ids) >= 1

@pytest.mark.asyncio
async def test_get_evidence_for_skills(db_session):
    await saraswati_service.seed_default_evidence(db_session)
    mapping = await saraswati_service.get_evidence_for_skills(db_session, ["SQL", "Snowflake", "NonExistentSkill"])
    
    assert len(mapping["SQL"]) >= 1
    assert len(mapping["Snowflake"]) >= 1
    assert len(mapping["NonExistentSkill"]) == 0

@pytest.mark.asyncio
async def test_evidence_api_endpoints(client: AsyncClient, db_session):
    # Test POST /api/v1/evidence-bank/seed
    seed_res = await client.post("/api/v1/evidence-bank/seed")
    assert seed_res.status_code == 200

    # Test GET /api/v1/evidence-bank
    list_res = await client.get("/api/v1/evidence-bank")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 12

    # Test GET /api/v1/evidence-bank/{id}
    item_id = items[0]["id"]
    get_res = await client.get(f"/api/v1/evidence-bank/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == item_id

    # Test GET /api/v1/evidence-bank/skills/summary
    sum_res = await client.get("/api/v1/evidence-bank/skills/summary")
    assert sum_res.status_code == 200
    assert sum_res.json()["total_skills"] >= 10

    # Test POST /api/v1/evidence-bank (create)
    create_payload = {
        "category": "BUSINESS_IMPACT",
        "skill_or_tool": "BigQuery",
        "title": "Query Scan Cost Reduction via Partitioning",
        "evidence_text": "Enforced date partitioning on 50TB dataset reducing query compute fees by $4,000 monthly.",
        "quant_metric": "$4,000/mo query cost reduction",
        "tags": ["BigQuery", "GCP", "FinOps"]
    }
    create_res = await client.post("/api/v1/evidence-bank", json=create_payload)
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # Test DELETE /api/v1/evidence-bank/{id}
    del_res = await client.delete(f"/api/v1/evidence-bank/{created_id}")
    assert del_res.status_code == 204
