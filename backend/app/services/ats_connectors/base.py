import abc
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import httpx
import logging

logger = logging.getLogger("jobmuni.ats_connectors")

USER_AGENT = "JOBMUNI-CareerBot/1.0 (+https://jobmuni.ai/bot-info)"

@dataclass
class NormalizedJob:
    """Standardized representation of an ingested job before DB persistence."""
    company_name: str
    title: str
    source: str  # GREENHOUSE, LEVER, ASHBY, WORKDAY, MANUAL
    source_job_id: str
    url: str
    canonical_url: Optional[str] = None
    location: Optional[str] = None
    remote_status: str = "UNKNOWN"  # REMOTE, HYBRID, ON_SITE, UNKNOWN
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    posted_at: Optional[datetime] = None
    raw_description: str = ""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    seniority_level: str = "SENIOR"
    domain_category: str = "BI_ANALYTICS"
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

class BaseATSConnector(abc.ABC):
    """
    Abstract base class for all ATS job connectors.
    Provides standard async HTTP client session, rate limiting, and interface contracts.
    """
    
    def __init__(self, timeout_seconds: float = 12.0):
        self.timeout_seconds = timeout_seconds

    def get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
            timeout=self.timeout_seconds,
            follow_redirects=True,
        )

    @abc.abstractmethod
    async def fetch_jobs(self, company_identifier: str) -> List[NormalizedJob]:
        """Fetch and normalize all active jobs for a company identifier/board token."""
        pass

    @abc.abstractmethod
    def parse_job_payload(self, company_name: str, item: Dict[str, Any]) -> Optional[NormalizedJob]:
        """Convert a single raw JSON entry into a NormalizedJob object."""
        pass
