from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict

class ScoringConfigBase(BaseModel):
    config_name: str = "Default Senior BI & Analytics"
    weight_skill_fit: float = Field(default=0.25, ge=0.0, le=1.0)
    weight_seniority: float = Field(default=0.15, ge=0.0, le=1.0)
    weight_domain: float = Field(default=0.15, ge=0.0, le=1.0)
    weight_compensation: float = Field(default=0.15, ge=0.0, le=1.0)
    weight_freshness: float = Field(default=0.10, ge=0.0, le=1.0)
    weight_hiring_signal: float = Field(default=0.10, ge=0.0, le=1.0)
    weight_recruiter: float = Field(default=0.10, ge=0.0, le=1.0)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_total_weight(self):
        total = (
            self.weight_skill_fit +
            self.weight_seniority +
            self.weight_domain +
            self.weight_compensation +
            self.weight_freshness +
            self.weight_hiring_signal +
            self.weight_recruiter
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Total weights must sum to 1.0 (100%). Current sum: {total:.2f}")
        return self

class ScoringConfigCreate(ScoringConfigBase):
    pass

class ScoringConfigUpdate(BaseModel):
    config_name: Optional[str] = None
    weight_skill_fit: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    weight_seniority: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    weight_domain: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    weight_compensation: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    weight_freshness: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    weight_hiring_signal: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    weight_recruiter: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None

class ScoringConfigResponse(ScoringConfigBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
