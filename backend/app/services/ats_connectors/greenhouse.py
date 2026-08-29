import re
import html
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
import logging
from app.services.ats_connectors.base import BaseATSConnector, NormalizedJob, logger
from app.services.jd_parser import JDParser

def clean_html(raw_html: str) -> str:
    """Strip HTML tags and unescape entities to return clean text."""
    if not raw_html:
        return ""
    # Replace line breaks and paragraph tags with newlines
    text = re.sub(r"<(?:p|br|div|li)[^>]*>", "\n", raw_html, flags=re.IGNORECASE)
    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Unescape HTML entities
    text = html.unescape(text)
    # Normalize multiple whitespace and newlines
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()

def parse_iso_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        # Handle '2026-08-20T12:00:00Z' or '2026-08-20T12:00:00-04:00'
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None

class GreenhouseConnector(BaseATSConnector):
    """
    Official public API connector for Greenhouse job boards.
    Endpoint: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
    """

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"

    async def fetch_jobs(self, company_identifier: str) -> List[NormalizedJob]:
        """
        Fetch all active public postings from a Greenhouse board token.
        Example company_identifier: 'snowflake', 'stripe', 'figma'
        """
        url = self.BASE_URL.format(board_token=company_identifier)
        jobs: List[NormalizedJob] = []

        try:
            async with self.get_client() as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[Greenhouse] Failed to fetch {company_identifier}: HTTP {response.status_code}")
                    return []

                payload = response.json()
                raw_jobs = payload.get("jobs", [])
                
                for item in raw_jobs:
                    parsed = self.parse_job_payload(company_identifier, item)
                    if parsed:
                        jobs.append(parsed)
                        
        except httpx.RequestError as exc:
            logger.error(f"[Greenhouse] Network error fetching {company_identifier}: {exc}")
        except Exception as exc:
            logger.error(f"[Greenhouse] Unexpected error parsing {company_identifier}: {exc}")

        return jobs

    def parse_job_payload(self, company_name: str, item: Dict[str, Any]) -> Optional[NormalizedJob]:
        """Normalize a single Greenhouse job entry."""
        if not item or not item.get("id"):
            return None

        source_job_id = str(item.get("id"))
        title = item.get("title", "").strip()
        if not title:
            return None

        # Clean HTML content
        raw_content = item.get("content", "")
        clean_desc = clean_html(raw_content)

        # Location extraction
        loc_obj = item.get("location") or {}
        location_name = loc_obj.get("name") if isinstance(loc_obj, dict) else str(loc_obj)
        
        # Absolute posting URL
        url = item.get("absolute_url") or f"https://boards.greenhouse.io/{company_name}/jobs/{source_job_id}"
        
        # Date posted / updated
        posted_at = parse_iso_date(item.get("updated_at"))

        # Run JD Parser for deterministic skill extraction and seniority
        parsed_jd = JDParser.parse(title=title, raw_description=clean_desc, location_hint=location_name)

        return NormalizedJob(
            company_name=company_name.capitalize(),
            title=title,
            source="GREENHOUSE",
            source_job_id=source_job_id,
            url=url,
            canonical_url=url,
            location=location_name or parsed_jd.location,
            remote_status=parsed_jd.remote_status,
            salary_min=parsed_jd.salary_min,
            salary_max=parsed_jd.salary_max,
            salary_currency=parsed_jd.salary_currency,
            posted_at=posted_at,
            raw_description=clean_desc,
            required_skills=parsed_jd.required_skills,
            preferred_skills=parsed_jd.preferred_skills,
            seniority_level=parsed_jd.seniority_level,
            domain_category=parsed_jd.domain_category,
            extra_metadata={
                "internal_job_id": item.get("internal_job_id"),
                "requisition_id": item.get("requisition_id"),
                "departments": [d.get("name") for d in item.get("departments", []) if isinstance(d, dict)],
                "offices": [o.get("name") for o in item.get("offices", []) if isinstance(o, dict)],
            }
        )
