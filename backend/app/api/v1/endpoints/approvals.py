from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.application import ApprovalRequest
from app.schemas.approval import ApprovalRequestResponse, ApprovalDecisionRequest

router = APIRouter()

@router.get("", response_model=List[ApprovalRequestResponse])
async def list_approvals(status_filter: Optional[str] = "PENDING", db: AsyncSession = Depends(get_db)):
    query = select(ApprovalRequest).order_by(desc(ApprovalRequest.created_at))
    if status_filter:
        query = query.where(ApprovalRequest.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{approval_id}/decision", response_model=ApprovalRequestResponse)
async def decide_approval(
    approval_id: str,
    decision_in: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))
    approval = result.scalars().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    if decision_in.decision == "APPROVE":
        approval.status = "APPROVED"
        approval.decision_at = datetime.now(timezone.utc)
    elif decision_in.decision == "EDIT_AND_APPROVE":
        approval.status = "EDITED_AND_APPROVED"
        if decision_in.modified_content:
            approval.generated_content = decision_in.modified_content
        approval.decision_at = datetime.now(timezone.utc)
    elif decision_in.decision == "REJECT":
        approval.status = "REJECTED"
        approval.rejection_reason = decision_in.rejection_reason
        approval.decision_at = datetime.now(timezone.utc)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid decision: {decision_in.decision}")

    await db.commit()
    await db.refresh(approval)
    return approval
