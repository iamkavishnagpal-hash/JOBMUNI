import pytest

@pytest.mark.asyncio
async def test_scoring_config_api(client):
    # 1. Fetch active config
    response = await client.get("/api/v1/scoring-config")
    assert response.status_code == 200
    data = response.json()
    assert data["weight_skill_fit"] == 0.25
    assert data["weight_seniority"] == 0.15

    # 2. Update config with valid weights
    update_payload = {
        "weight_skill_fit": 0.30,
        "weight_seniority": 0.15,
        "weight_domain": 0.15,
        "weight_compensation": 0.10,
        "weight_freshness": 0.10,
        "weight_hiring_signal": 0.10,
        "weight_recruiter": 0.10
    }
    update_resp = await client.put("/api/v1/scoring-config", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["weight_skill_fit"] == 0.30

    # 3. Update with invalid weights (sum != 1.0)
    invalid_payload = {
        "weight_skill_fit": 0.50,
        "weight_seniority": 0.50,
        "weight_domain": 0.50
    }
    invalid_resp = await client.put("/api/v1/scoring-config", json=invalid_payload)
    assert invalid_resp.status_code == 422 or invalid_resp.status_code == 400
