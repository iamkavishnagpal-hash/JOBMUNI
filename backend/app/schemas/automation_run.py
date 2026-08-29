from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AutomationRunBase(BaseModel):
    task_name: str = "GENERIC_TASK"
    task_type: str
    agent_name: str = "BRAHMASTRA"
    status: str = "SUCCESS"
    duration_ms: int = 0
    items_processed: int = 0
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    retry_count: int = 0
    error_message: Optional[str] = None
    metadata_json: Dict[str, Any] = {}

class AutomationRunResponse(AutomationRunBase):
    id: str
    started_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AutomationRunPaginationResponse(BaseModel):
    items: List[AutomationRunResponse]
    total: int
    page: int
    limit: int
    pages: int
