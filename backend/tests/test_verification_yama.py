import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from app.services.verification_service import YamaVerificationService
from app.models.job import Job

@pytest.mark.asyncio
async def test_exact_active_greenhouse_job():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": 12345, "title": "Staff Data Engineer"}
    mock_client.get.return_value = mock_resp

    result = await service.verify_job_target(
        client=mock_client,
        url="https://boards.greenhouse.io/snowflake/jobs/12345",
        source="GREENHOUSE",
        source_job_id="12345",
        company_name="Snowflake"
    )
    assert result["status"] == "ACTIVE"
    assert result["reason"] == "EXACT_JOB_FOUND"
    assert result["http_status"] == 200
    assert result["is_active"] is True
    # Verify API URL was called directly
    mock_client.get.assert_called_with("https://boards-api.greenhouse.io/v1/boards/snowflake/jobs/12345")

@pytest.mark.asyncio
async def test_exact_missing_greenhouse_job():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_client.get.return_value = mock_resp

    result = await service.verify_job_target(
        client=mock_client,
        url="https://boards.greenhouse.io/stripe/jobs/old_999",
        source="GREENHOUSE",
        source_job_id="old_999",
        company_name="Stripe"
    )
    assert result["status"] == "INACTIVE"
    assert result["reason"] == "EXACT_JOB_NOT_FOUND"
    assert result["http_status"] == 404
    assert result["is_active"] is False

@pytest.mark.asyncio
async def test_greenhouse_redirect_to_generic_careers_page():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    # Final URL after following redirects landed on generic search page with error param
    mock_resp.url = httpx.URL("https://stripe.com/careers/search?error=true")
    mock_resp.text = "<html><body>Search all open roles at Stripe</body></html>"
    mock_client.get.return_value = mock_resp

    result = await service.verify_general_url(
        client=mock_client,
        url="https://boards.greenhouse.io/stripe/jobs/gh_stripe_202"
    )
    assert result["status"] == "INACTIVE"
    assert result["reason"] == "REDIRECTED_TO_GENERIC_CAREERS"
    assert result["is_active"] is False

@pytest.mark.asyncio
async def test_exact_active_lever_job():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "lever_abc_1", "text": "Senior BI Engineer"}
    mock_client.get.return_value = mock_resp

    result = await service.verify_job_target(
        client=mock_client,
        url="https://jobs.lever.co/netflix/lever_abc_1",
        source="LEVER",
        source_job_id="lever_abc_1",
        company_name="Netflix"
    )
    assert result["status"] == "ACTIVE"
    assert result["reason"] == "EXACT_JOB_FOUND"
    assert result["http_status"] == 200
    assert result["is_active"] is True
    mock_client.get.assert_called_with("https://api.lever.co/v0/postings/netflix/lever_abc_1")

@pytest.mark.asyncio
async def test_exact_missing_lever_job():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_client.get.return_value = mock_resp

    result = await service.verify_job_target(
        client=mock_client,
        url="https://jobs.lever.co/netflix/gone_post_2",
        source="LEVER",
        source_job_id="gone_post_2",
        company_name="Netflix"
    )
    assert result["status"] == "INACTIVE"
    assert result["reason"] == "EXACT_JOB_NOT_FOUND"
    assert result["http_status"] == 404
    assert result["is_active"] is False

@pytest.mark.asyncio
async def test_temporary_5xx_server_error():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_client.get.return_value = mock_resp

    result = await service.verify_job_target(
        client=mock_client,
        url="https://example.com/jobs/data-eng",
        source=None
    )
    assert result["status"] == "UNKNOWN"
    assert result["reason"] == "TEMPORARY_SERVER_ERROR"
    assert result["http_status"] == 503
    assert result["is_active"] is True

@pytest.mark.asyncio
async def test_timeout_handling():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Read timed out")

    result = await service.verify_job_target(
        client=mock_client,
        url="https://example.com/jobs/slow-job"
    )
    assert result["status"] == "UNKNOWN"
    assert result["reason"] == "TIMEOUT"
    assert result["is_active"] is True

@pytest.mark.asyncio
async def test_generic_200_careers_page_with_expired_marker():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.url = httpx.URL("https://example.com/jobs/123")
    mock_resp.text = "<html><body><h1>Lead Analytics Engineer</h1><p>Notice: This position has been closed and is no longer accepting applications.</p></body></html>"
    mock_client.get.return_value = mock_resp

    result = await service.verify_general_url(
        client=mock_client,
        url="https://example.com/jobs/123"
    )
    assert result["status"] == "INACTIVE"
    assert result["reason"] == "JOB_EXPIRED_ON_PAGE"
    assert result["is_active"] is False

@pytest.mark.asyncio
async def test_ambiguous_response_403():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.url = httpx.URL("https://example.com/jobs/restricted")
    mock_client.get.return_value = mock_resp

    result = await service.verify_general_url(
        client=mock_client,
        url="https://example.com/jobs/restricted"
    )
    assert result["status"] == "UNKNOWN"
    assert result["reason"] == "AMBIGUOUS"
    assert result["http_status"] == 403
    assert result["is_active"] is True

@pytest.mark.asyncio
async def test_job_db_update_preserves_verification_reason(db_session):
    service = YamaVerificationService()
    job = Job(
        company_name="Snowflake",
        title="Lead BI Engineer",
        source_url="https://boards.greenhouse.io/snowflake/jobs/snow_101",
        source_job_id="snow_101",
        status="ACTIVE",
        verification_status="UNKNOWN",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_client.get.return_value = mock_resp

    res = await service.verify_job(db_session, job, client=mock_client)
    assert res["reason"] == "EXACT_JOB_NOT_FOUND"
    assert job.verification_status == "INACTIVE"
    assert job.verification_reason == "EXACT_JOB_NOT_FOUND"
    assert job.status == "INACTIVE"
    assert job.verification_http_status == 404
