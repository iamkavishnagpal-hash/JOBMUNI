from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
import logging
from app.services.ats_connectors.base import BaseATSConnector, NormalizedJob, logger
from app.services.jd_parser import JDParser

def parse_epoch_millis(ms_val: Optional[int]) -> Optional[datetime]:
    if not ms_val:
        return None
    try:
        return datetime.fromtimestamp(ms_val / 1000.0, tz=timezone.utc)
    except Exception:
        return None

class LeverConnector(BaseATSConnector):
    """
    Official public API connector for Lever job postings.
    Endpoint: https://api.lever.co/v0/postings/{company_site}?mode=json
    """

    BASE_URL = "https://api.lever.co/v0/postings/{company_site}?mode=json"

    async def fetch_jobs(self, company_identifier: str) -> List[NormalizedJob]:
        """
        Fetch all active public postings from a Lever company slug.
        Example company_identifier: 'netflix', 'atlassian', 'spotify'
        """
        url = self.BASE_URL.format(company_site=company_identifier)
        jobs: List[NormalizedJob] = []

        try:
            async with self.get_client() as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[Lever] Failed to fetch {company_identifier}: HTTP {response.status_code}")
                    return []

                payload = response.json()
                if not isinstance(payload, list):
                    return []

                for item in payload:
                    parsed = self.parse_job_payload(company_identifier, item)
                    if parsed:
                        jobs.append(parsed)

        except httpx.RequestError as exc:
            logger.error(f"[Lever] Network error fetching {company_identifier}: {exc}")
        except Exception as exc:
            logger.error(f"[Lever] Unexpected error parsing {company_identifier}: {exc}")

        return jobs

    def parse_job_payload(self, company_name: str, item: Dict[str, Any]) -> Optional[NormalizedJob]:
        """Normalize a single Lever posting entry."""
        if not item or not item.get("id"):
            return None

        source_job_id = str(item.get("id"))
        title = item.get("text", "").strip()
        if not title:
            return None

        # Build clean plain text description from descriptionPlain and lists
        desc_parts = []
        if item.get("descriptionPlain"):
            desc_parts.append(item.get("descriptionPlain"))
        
        # Lever lists (e.g. "What you'll do", "What we're looking for")
        for list_obj in item.get("lists", []):
            if isinstance(list_obj, dict):
                list_title = list_obj.get("text", "")
                list_content = list_obj.get("content", "")
                if list_title:
                    desc_parts.append(f"\n{list_title}:\n{list_content}")

        if item.get("additionalPlain"):
            desc_parts.append(f"\nAdditional Information:\n{item.get('additionalPlain')}")

        full_desc = "\n".join(desc_parts).strip()

        # Categories
        categories = item.get("categories") or {}
        location_name = categories.get("location")
        commitment = categories.get("commitment")  # Full-time, etc.
        team = categories.get("team")
        workplace_type = item.get("workplaceType", "").upper()  # remote, hybrid, onsite

        url = item.get("hostedUrl") or f"https://jobs.lever.co/{company_name}/{source_job_id}"
        posted_at = parse_epoch_millis(item.get("createdAt"))

        # Run JD parser
        parsed_jd = JDParser.parse(title=title, raw_description=full_desc, location_hint=location_name)

        if "HYBRID" in workplace_type:
            remote_status = "HYBRID"
        elif "REMOTE" in workplace_type:
            remote_status = "REMOTE"
        elif "ONSITE" in workplace_type or "ON-SITE" in workplace_type or "ON_SITE" in workplace_type:
            remote_status = "ON_SITE"
        else:
            remote_status = parsed_jd.remote_status

        # Salary extraction check on Lever salaryRange if present
        salary_range = item.get("salaryRange") or {}
        sal_min = salary_range.get("min") or parsed_jd.salary_min
        sal_max = salary_range.get("max") or parsed_jd.salary_max
        currency = salary_range.get("currency") or parsed_jd.salary_currency

        return NormalizedJob(
            company_name=company_name.capitalize(),
            title=title,
            source="LEVER",
            source_job_id=source_job_id,
            url=url,
            canonical_url=url,
            location=location_name or parsed_jd.location,
            remote_status=remote_status,
            salary_min=int(sal_min) if sal_min else None,
            salary_max=int(sal_max) if sal_max else None,
            salary_currency=currency,
            posted_at=posted_at,
            raw_description=full_desc,
            required_skills=parsed_jd.required_skills,
            preferred_skills=parsed_jd.preferred_skills,
            seniority_level=parsed_jd.seniority_level,
            domain_category=parsed_jd.domain_category,
            extra_metadata={
                "workplaceType": workplace_type,
                "commitment": commitment,
                "team": team,
                "department": categories.get("department"),
            }
        )
