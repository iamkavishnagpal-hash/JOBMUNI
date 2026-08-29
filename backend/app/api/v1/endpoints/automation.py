from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.automation_run import AutomationRun
from app.schemas.automation_run import AutomationRunResponse

router = APIRouter()

@router.get("", response_model=List[AutomationRunResponse])
async def list_automation_runs(
    task_type: Optional[str] = None,
    agent_name: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(AutomationRun).order_by(desc(AutomationRun.started_at))
    
    if task_type:
        query = query.where(AutomationRun.task_type == task_type)
    if agent_name:
        query = query.where(AutomationRun.agent_name == agent_name)
    if status_filter:
        query = query.where(AutomationRun.status == status_filter)
        
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
