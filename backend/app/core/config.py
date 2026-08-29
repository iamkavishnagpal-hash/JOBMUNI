import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_SQLITE_DB = os.path.join(BACKEND_DIR, "career_os.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "JOBMUNI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="development | staging | production")
    API_V1_PREFIX: str = "/api/v1"
    
    # Database Configuration (PostgreSQL production default with SQLite fallback for local dev)
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{DEFAULT_SQLITE_DB}",
        description="PostgreSQL (postgresql+asyncpg://user:pass@host:5432/db) or SQLite"
    )
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    
    # Optional External Service Credentials (Must only come from environment)
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON_PATH: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    @computed_field
    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL
        
    model_config = SettingsConfigDict(
        env_file=os.path.join(BACKEND_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
