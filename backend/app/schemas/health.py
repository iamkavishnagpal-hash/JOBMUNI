from datetime import datetime
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Overall system health status")
    environment: str
    database: str = Field(description="connected | disconnected | error")
    db_engine: str = Field(description="postgresql | sqlite")
    timestamp: datetime
    version: str
