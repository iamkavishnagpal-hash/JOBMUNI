import pytest
from app.models.application import ApprovalRequest

@pytest.mark.asyncio
async def test_approval_decision_flow(test_db, client):
    # 1. Create a pending approval request
    approval = ApprovalRequest(
        action_type="OUTREACH_EMAIL",
        title="Send outreach to Sarah Jenkins (Staff Recruiter)",
        reason="Senior BI position at Snowflake; high skill match.",
        generated_content={"subject": "Inquiry regarding Senior BI Lead Role", "body": "Hi Sarah..."},
        status="PENDING"
    )
    test_db.add(approval)
    await test_db.commit()
    await test_db.refresh(approval)

    # 2. Query pending approvals
    list_resp = await client.get("/api/v1/approvals")
    assert list_resp.status_code == 200
    approvals = list_resp.json()
    assert len(approvals) >= 1
    assert approvals[0]["status"] == "PENDING"

    # 3. Approve the request
    decision_resp = await client.post(
        f"/api/v1/approvals/{approval.id}/decision",
        json={"decision": "APPROVE"}
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["status"] == "APPROVED"
    assert decision_resp.json()["decision_at"] is not None
