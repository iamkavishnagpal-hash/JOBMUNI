import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.verification_service import YamaVerificationService
from app.models.job import Job

@pytest.mark.asyncio
async def test_yama_verify_url_200_active():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_client.head.return_value = mock_resp

    result = await service.verify_url(mock_client, "https://boards.greenhouse.io/stripe/jobs/123")
    assert result["status"] == "ACTIVE"
    assert result["http_status"] == 200
    assert result["is_active"] is True
    assert result["error"] is None

@pytest.mark.asyncio
async def test_yama_verify_url_404_inactive():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_client.head.return_value = mock_resp

    result = await service.verify_url(mock_client, "https://boards.greenhouse.io/stripe/jobs/old_123")
    assert result["status"] == "INACTIVE"
    assert result["http_status"] == 404
    assert result["is_active"] is False

@pytest.mark.asyncio
async def test_yama_verify_url_410_inactive():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 410
    mock_client.head.return_value = mock_resp

    result = await service.verify_url(mock_client, "https://jobs.lever.co/netflix/gone_456")
    assert result["status"] == "INACTIVE"
    assert result["http_status"] == 410
    assert result["is_active"] is False

@pytest.mark.asyncio
async def test_yama_verify_url_500_conservative():
    # 5xx should NOT mark job inactive (conservative resilience rule)
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_client.head.return_value = mock_resp

    result = await service.verify_url(mock_client, "https://example.com/job/500")
    assert result["status"] == "UNKNOWN"
    assert result["http_status"] == 500
    assert result["is_active"] is True

@pytest.mark.asyncio
async def test_yama_verify_url_timeout_conservative():
    service = YamaVerificationService()
    mock_client = AsyncMock()
    mock_client.head.side_effect = httpx.TimeoutException("Connection timed out")

    result = await service.verify_url(mock_client, "https://example.com/job/timeout")
    assert result["status"] == "UNKNOWN"
    assert result["http_status"] is None
    assert result["is_active"] is True
    assert "timeout" in result["error"].lower()

@pytest.mark.asyncio
async def test_yama_verify_job_db_update(db_session):
    service = YamaVerificationService()
    job = Job(
        company_name="Acme Corp",
        title="BI Developer",
        source_url="https://example.com/jobs/acme_1",
        status="ACTIVE",
        verification_status="UNKNOWN",
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    mock_client = AsyncMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_client.head.return_value = mock_resp

    await service.verify_job(db_session, job, client=mock_client)
    assert job.verification_status == "INACTIVE"
    assert job.status == "INACTIVE"
    assert job.verification_http_status == 404
