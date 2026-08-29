from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.scoring_config import ScoringConfig
from app.schemas.scoring_config import ScoringConfigResponse, ScoringConfigCreate, ScoringConfigUpdate

router = APIRouter()

@router.get("", response_model=ScoringConfigResponse)
async def get_active_scoring_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScoringConfig).where(ScoringConfig.is_active == True))
    config = result.scalars().first()
    if not config:
        # Create default if not exists
        config = ScoringConfig()
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config

@router.put("", response_model=ScoringConfigResponse)
async def update_scoring_config(config_in: ScoringConfigUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScoringConfig).where(ScoringConfig.is_active == True))
    config = result.scalars().first()
    if not config:
        config = ScoringConfig()
        db.add(config)
    
    update_data = config_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(config, field, val)

    # Validate weight sum
    total = (
        config.weight_skill_fit +
        config.weight_seniority +
        config.weight_domain +
        config.weight_compensation +
        config.weight_freshness +
        config.weight_hiring_signal +
        config.weight_recruiter
    )
    if abs(total - 1.0) > 0.01:
        raise HTTPException(status_code=400, detail=f"Weights must sum to 1.0. Current sum: {total:.2f}")

    await db.commit()
    await db.refresh(config)
    return config
