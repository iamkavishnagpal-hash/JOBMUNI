from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def check_health(db: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthResponse(
        status="healthy" if "error" not in db_status else "degraded",
        environment=settings.ENVIRONMENT,
        database=db_status,
        db_engine="sqlite" if settings.is_sqlite else "postgresql",
        timestamp=datetime.now(timezone.utc),
        version=settings.VERSION
    )
