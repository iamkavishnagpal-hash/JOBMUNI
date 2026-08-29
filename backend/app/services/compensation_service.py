import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.services.currency_provider import currency_provider
from app.services.evidence_service import saraswati_service

logger = logging.getLogger("jobmuni.kubera")

class KuberaCompensationService:
    """
    KUBERA Compensation Intelligence Service.
    Deterministically evaluates financial attractiveness against the user's
    candidate opportunity policy.
    Enforces strict data integrity: never fabricates or hallucinates undisclosed salaries.
    """

    def evaluate_compensation(
        self,
        job: Job,
        profile: CandidateProfile
    ) -> Dict[str, Any]:
        """
        Evaluate compensation fit, market percentile, remote value, and explainable tier.
        """
        policy_currency = profile.currency or "USD"
        target_min = profile.target_comp_min or 160000
        target_preferred = profile.target_comp_preferred or 195000
        target_max = profile.target_comp_max or 230000
        remote_pref = (profile.remote_preference or "REMOTE_FIRST").upper()
        intl_pref = (profile.international_preference or "US_ONLY").upper()
        preferred_locs = [loc.lower() for loc in (profile.preferred_locations or [])]

        job_remote = (job.remote_type or "REMOTE").upper()
        job_loc = (job.location or "").lower()

        # 1. Check if Salary is Disclosed
        has_salary = job.salary_min is not None or job.salary_max is not None

        if not has_salary:
            # Undisclosed Salary Handling (Zero Invention)
            remote_val = self._calculate_remote_value(job_remote, remote_pref)
            loc_val = self._calculate_location_value(job_loc, job_remote, preferred_locs, intl_pref)
            total_score = round(0.5 * remote_val + 0.5 * loc_val * 0.5)

            return {
                "job_id": job.id,
                "job_title": job.title,
                "company_name": job.company_name,
                "compensation_tier": "UNKNOWN",
                "salary_source": "UNDISCLOSED_ON_POSTING",
                "salary_fit_score": 0,
                "market_position_score": 0,
                "remote_value_score": round(remote_val, 1),
                "location_value_score": round(loc_val, 1),
                "total_compensation_score": total_score,
                "confidence": 0.35,
                "disclosed_salary": {
                    "raw_min": None,
                    "raw_max": None,
                    "raw_currency": job.salary_currency or "USD",
                    "formatted": "Undisclosed in posting",
                    "normalized_min": None,
                    "normalized_max": None,
                    "normalized_currency": policy_currency,
                    "conversion_status": "EXACT",
                },
                "policy_targets": {
                    "minimum": target_min,
                    "preferred": target_preferred,
                    "maximum": target_max,
                    "currency": policy_currency,
                },
                "reasoning": {
                    "summary": "Compensation range is undisclosed in the job posting. Policy evaluation is restricted to remote and location preferences.",
                    "why_tier_assigned": "Employer did not state base salary on posting.",
                    "policy_comparison": f"Candidate target is {policy_currency} ${target_min:,} - ${target_preferred:,}.",
                    "unknown_factors": [
                        "Base salary range unstated by employer",
                        "Equity / stock grant details unstated",
                        "Annual performance bonus percentage unstated",
                        "401(k) retirement match unstated"
                    ],
                    "confidence_rationale": "Low confidence (0.35) due to undisclosed financial compensation.",
                    "recommended_action": "Inquire regarding compensation bands in initial recruiter screen."
                }
            }

        # 2. Normalize Disclosed Salary via Currency Provider
        raw_min = job.salary_min
        raw_max = job.salary_max
        raw_curr = job.salary_currency or "USD"

        conv_min = currency_provider.convert(float(raw_min) if raw_min else None, raw_curr, policy_currency)
        conv_max = currency_provider.convert(float(raw_max) if raw_max else None, raw_curr, policy_currency)

        norm_min = conv_min.converted_amount if raw_min else None
        norm_max = conv_max.converted_amount if raw_max else None
        conversion_status = conv_max.conversion_status if raw_max else conv_min.conversion_status

        # 3. Calculate Salary Fit Score
        # Effective benchmark uses normalized max if available, otherwise min
        eff_salary = norm_max if norm_max else (norm_min or 0.0)

        if eff_salary >= target_max:
            salary_fit_score = 100.0
            tier = "PREMIUM"
            tier_reason = f"Salary exceeds candidate premium benchmark of {policy_currency} ${target_max:,}."
        elif eff_salary >= target_preferred:
            # 85 to 100
            diff = eff_salary - target_preferred
            span = max(1, target_max - target_preferred)
            salary_fit_score = min(99.0, 85.0 + 15.0 * (diff / span))
            tier = "STRONG"
            tier_reason = f"Salary meets or exceeds preferred target of {policy_currency} ${target_preferred:,}."
        elif eff_salary >= target_min:
            # 60 to 85
            diff = eff_salary - target_min
            span = max(1, target_preferred - target_min)
            salary_fit_score = 60.0 + 25.0 * (diff / span)
            tier = "ACCEPTABLE"
            tier_reason = f"Salary satisfies minimum requirement ({policy_currency} ${target_min:,}) but falls short of preferred target."
        else:
            # Below min: 0 to 50
            diff = target_min - eff_salary
            ratio = min(1.0, diff / max(1, target_min))
            salary_fit_score = max(0.0, 50.0 - 50.0 * ratio)
            tier = "LOW"
            tier_reason = f"Disclosed compensation is below candidate minimum threshold of {policy_currency} ${target_min:,}."

        # 4. Market Position Score (Senior BI baseline $140k - $210k)
        market_baseline_min = 140000.0
        market_baseline_max = 215000.0
        market_pos = min(100.0, max(20.0, ((eff_salary - market_baseline_min) / (market_baseline_max - market_baseline_min)) * 100.0))

        # 5. Remote and Location Value Scores
        remote_val = self._calculate_remote_value(job_remote, remote_pref)
        loc_val = self._calculate_location_value(job_loc, job_remote, preferred_locs, intl_pref)

        # 6. Composite Score
        total_comp_score = round(
            0.55 * salary_fit_score +
            0.20 * market_pos +
            0.15 * remote_val +
            0.10 * loc_val
        )

        # 7. Format strings
        if raw_min and raw_max:
            fmt_raw = f"{raw_curr} ${raw_min:,} - ${raw_max:,}"
        elif raw_min:
            fmt_raw = f"{raw_curr} ${raw_min:,}+"
        else:
            fmt_raw = f"Up to {raw_curr} ${raw_max:,}"

        # Unknown factors / gaps in compensation package
        unknowns = []
        if not job.raw_description or "equity" not in job.raw_description.lower():
            unknowns.append("Equity / RSU compensation details unstated")
        if not job.raw_description or "bonus" not in job.raw_description.lower():
            unknowns.append("Annual performance bonus target unstated")

        confidence = 1.0 if conversion_status == "EXACT" else 0.9

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company_name": job.company_name,
            "compensation_tier": tier,
            "salary_source": "VERIFIED_JOB_SALARY",
            "salary_fit_score": round(salary_fit_score, 1),
            "market_position_score": round(market_pos, 1),
            "remote_value_score": round(remote_val, 1),
            "location_value_score": round(loc_val, 1),
            "total_compensation_score": total_comp_score,
            "confidence": confidence,
            "disclosed_salary": {
                "raw_min": raw_min,
                "raw_max": raw_max,
                "raw_currency": raw_curr,
                "formatted": fmt_raw,
                "normalized_min": norm_min,
                "normalized_max": norm_max,
                "normalized_currency": policy_currency,
                "conversion_status": conversion_status,
            },
            "policy_targets": {
                "minimum": target_min,
                "preferred": target_preferred,
                "maximum": target_max,
                "currency": policy_currency,
            },
            "reasoning": {
                "summary": f"{tier} compensation fit. Disclosed salary {fmt_raw} aligns at {round(salary_fit_score)}% against your {policy_currency} target policy.",
                "why_tier_assigned": tier_reason,
                "policy_comparison": f"Disclosed range ({fmt_raw}) vs Policy ({policy_currency} ${target_min:,} - ${target_preferred:,}).",
                "unknown_factors": unknowns,
                "confidence_rationale": f"High confidence ({confidence}) grounded in verified salary disclosure on job posting.",
                "recommended_action": "Pursue aggressively" if tier in ("PREMIUM", "STRONG") else "Review role scope and total rewards."
            }
        }

    def _calculate_remote_value(self, job_remote: str, remote_pref: str) -> float:
        if job_remote == "REMOTE":
            return 100.0 if remote_pref in ("REMOTE_ONLY", "REMOTE_FIRST") else 95.0
        elif job_remote == "HYBRID":
            return 40.0 if remote_pref == "REMOTE_ONLY" else 80.0
        else: # ONSITE
            return 10.0 if remote_pref == "REMOTE_ONLY" else (40.0 if remote_pref == "REMOTE_FIRST" else 75.0)

    def _calculate_location_value(self, job_loc: str, job_remote: str, preferred_locs: List[str], intl_pref: str) -> float:
        if job_remote == "REMOTE":
            return 100.0

        if any(pref in job_loc for pref in preferred_locs):
            return 100.0

        # Check for international signals
        intl_countries = ["uk", "germany", "india", "singapore", "australia", "canada", "france", "netherlands", "tokyo", "japan"]
        is_intl = any(c in job_loc for c in intl_countries)

        if is_intl and intl_pref == "US_ONLY":
            return 25.0

        return 70.0

    async def evaluate_and_persist_job_compensation(self, db: AsyncSession, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Evaluate compensation intelligence and persist materialized tier and scores to DB.
        """
        stmt = select(Job).where(Job.id == job_id)
        res = await db.execute(stmt)
        job = res.scalars().first()
        if not job:
            return None

        profile = await saraswati_service.get_or_create_default_profile(db)
        eval_result = self.evaluate_compensation(job, profile)

        job.compensation_tier = eval_result["compensation_tier"]
        job.total_compensation_score = eval_result["total_compensation_score"]
        job.compensation_json = eval_result

        await db.commit()
        await db.refresh(job)
        return eval_result

kubera_service = KuberaCompensationService()
