import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.candidate_profile import CandidateProfile
from app.services.alignment_engine import arjuna_engine
from app.services.compensation_service import kubera_service
from app.services.evidence_service import saraswati_service

logger = logging.getLogger("jobmuni.chanakya")

class ChanakyaPrioritizationEngine:
    """
    CHANAKYA Opportunity Prioritization Engine.
    Deterministic decision layer that converts verified and evaluated opportunities
    into ranked, explainable career priorities and next actions.
    Consumes outputs from NARADA, YAMA, SARASWATI, ARJUNA, and KUBERA.
    """

    def evaluate_priority(
        self,
        job: Job,
        alignment_data: Dict[str, Any],
        compensation_data: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates composite priority score, urgency, actionability, effort,
        recommended next action, and transparent explainability.
        """
        # 1. Configurable Weights
        w = weights or {
            "skill_alignment": 0.35,
            "compensation": 0.25,
            "evidence_density": 0.15,
            "hiring_signal": 0.10,
            "freshness": 0.10,
            "remote_location": 0.05,
        }

        # 2. Extract ARJUNA metrics
        req_cov = float(alignment_data.get("required_coverage_pct", 0.0))
        pref_cov = float(alignment_data.get("preferred_coverage_pct", 0.0))
        ev_density = float(alignment_data.get("evidence_coverage_pct", 0.0))
        exp_align = float(alignment_data.get("experience_alignment_pct", 80.0))
        match_verdict = alignment_data.get("match_verdict", "INSUFFICIENT_EVIDENCE")

        skill_align_score = (0.65 * req_cov) + (0.20 * pref_cov) + (0.15 * exp_align)

        # 3. Extract KUBERA metrics
        comp_tier = compensation_data.get("compensation_tier", "UNKNOWN")
        salary_fit = float(compensation_data.get("salary_fit_score", 0.0))
        market_pos = float(compensation_data.get("market_position_score", 0.0))
        remote_val = float(compensation_data.get("remote_value_score", 80.0))
        loc_val = float(compensation_data.get("location_value_score", 80.0))

        if comp_tier == "UNKNOWN":
            # Neutral baseline for undisclosed compensation so high skill fit is not penalized to zero
            comp_align_score = 65.0
        else:
            comp_align_score = (0.70 * salary_fit) + (0.30 * market_pos)

        # 4. Extract YAMA & NARADA metrics
        freshness_conf = float(job.freshness_conf or 1.0)
        hiring_signal = float(job.hiring_signal_score or 75.0)
        is_verified_active = (job.verification_status == "ACTIVE" or job.status == "ACTIVE")
        is_inactive = (job.verification_status == "INACTIVE" or job.status == "INACTIVE" or job.ghost_status in ("LIKELY_INACTIVE", "STALE"))

        # 5. Calculate Raw Composite Priority Score
        remote_loc_score = (remote_val + loc_val) / 2.0

        raw_priority = (
            (w["skill_alignment"] * skill_align_score) +
            (w["compensation"] * comp_align_score) +
            (w["evidence_density"] * ev_density) +
            (w["hiring_signal"] * hiring_signal) +
            (w["freshness"] * (freshness_conf * 100.0)) +
            (w["remote_location"] * remote_loc_score)
        )
        priority_score = min(100, max(0, round(raw_priority)))

        # 6. Calculate Urgency Score (Freshness + Hiring Velocity)
        # Calculate days since first seen or posted
        now = datetime.now(timezone.utc)
        ref_time = job.posted_at or job.first_seen_at or now
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)
        days_old = max(0, (now - ref_time).days)

        if days_old <= 2:
            freshness_factor = 100.0
        elif days_old <= 7:
            freshness_factor = 85.0
        elif days_old <= 14:
            freshness_factor = 65.0
        elif days_old <= 30:
            freshness_factor = 45.0
        else:
            freshness_factor = 25.0

        urgency_score = round((0.65 * freshness_factor) + (0.35 * hiring_signal))

        # 7. Safety Gates & State Penalties
        blocking_factors = []
        if is_inactive:
            priority_score = min(priority_score, 20)
            urgency_score = 10
            priority_tier = "SKIP"
            actionability = "EXPIRED"
            effort_level = "LOW"
            recommended_action = "SKIP"
            lifecycle_status = "EXPIRED"
            blocking_factors.append("Opportunity is inactive or expired on source ATS")
        elif comp_tier == "LOW":
            priority_score = min(priority_score, 42)
            priority_tier = "LOW"
            actionability = "BLOCKED"
            effort_level = "LOW"
            recommended_action = "SKIP"
            lifecycle_status = "EVALUATED"
            blocking_factors.append("Disclosed compensation falls below candidate minimum target")
        else:
            # Determine Actionability & Effort
            if req_cov >= 80.0 and ev_density >= 70.0:
                actionability = "READY_TO_ACT"
                effort_level = "LOW"
                recommended_action = "APPLY"
                lifecycle_status = "READY_TO_ACT"
            elif req_cov >= 80.0:
                actionability = "NEEDS_RESUME"
                effort_level = "MEDIUM"
                recommended_action = "PREPARE_RESUME"
                lifecycle_status = "SHORTLISTED"
            elif 50.0 <= req_cov < 80.0:
                actionability = "NEEDS_EVIDENCE"
                effort_level = "MEDIUM"
                recommended_action = "CONTACT_RECRUITER"
                lifecycle_status = "SHORTLISTED"
            else:
                actionability = "NEEDS_REVIEW"
                effort_level = "HIGH"
                recommended_action = "REVIEW"
                lifecycle_status = "EVALUATED"

            # Determine Priority Tier
            if priority_score >= 85 and urgency_score >= 55:
                priority_tier = "CRITICAL"
            elif priority_score >= 75:
                priority_tier = "HIGH"
            elif priority_score >= 60:
                priority_tier = "MEDIUM"
            elif priority_score >= 40:
                priority_tier = "LOW"
            else:
                priority_tier = "SKIP"
                recommended_action = "SKIP"

        # 8. Compile Explainable Positive & Negative Factors
        positive_factors = []
        negative_factors = []

        # Skill factors
        if req_cov >= 80.0:
            positive_factors.append(f"{req_cov:.0f}% required skill coverage backed by candidate evidence")
        elif req_cov >= 50.0:
            positive_factors.append(f"{req_cov:.0f}% partial skill match")
            negative_factors.append(f"Missing {100 - req_cov:.0f}% of required competencies")
        else:
            negative_factors.append(f"Low required skill fit ({req_cov:.0f}%)")

        # Compensation factors
        if comp_tier in ("PREMIUM", "STRONG"):
            positive_factors.append(f"Compensation aligns strongly with target ({compensation_data.get('disclosed_salary', {}).get('formatted', '')})")
        elif comp_tier == "ACCEPTABLE":
            positive_factors.append("Compensation meets minimum target threshold")
        elif comp_tier == "UNKNOWN":
            negative_factors.append("Base salary unstated on job posting")

        # Remote / Location factors
        if remote_val >= 90.0:
            positive_factors.append("Full remote work alignment")
        elif remote_val <= 40.0:
            negative_factors.append("Onsite/Hybrid requirement does not match remote preference")

        # Freshness factors
        if days_old <= 3:
            positive_factors.append("Fresh posting (verified active within 72h)")
        elif days_old > 21:
            negative_factors.append(f"Posting is {days_old} days old (lower urgency)")

        # Summary text
        summary = (
            f"Ranked as {priority_tier} priority ({priority_score}/100) with urgency {urgency_score}/100. "
            f"Recommended Next Action: {recommended_action.replace('_', ' ')}."
        )

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company_name": job.company_name,
            "priority_score": priority_score,
            "priority_tier": priority_tier,
            "urgency_score": urgency_score,
            "actionability": actionability,
            "effort_level": effort_level,
            "recommended_action": recommended_action,
            "lifecycle_status": lifecycle_status,
            "score_breakdown": {
                "skill_alignment": round(skill_align_score, 1),
                "compensation_alignment": round(comp_align_score, 1),
                "evidence_density": round(ev_density, 1),
                "hiring_signal": round(hiring_signal, 1),
                "freshness": round(freshness_conf * 100.0, 1),
                "remote_location": round(remote_loc_score, 1),
                "composite_score": priority_score,
            },
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "blocking_factors": blocking_factors,
            "reasoning": {
                "summary": summary,
                "why_ranked_here": (
                    f"{priority_tier} tier assigned due to {round(skill_align_score)}% skill alignment and "
                    f"{round(comp_align_score)}% compensation fit."
                ),
                "action_rationale": (
                    f"Action '{recommended_action}' recommended because opportunity is {actionability.replace('_', ' ').lower()} "
                    f"with {effort_level.lower()} effort requirements."
                ),
            },
            "decision_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def evaluate_and_persist_job_priority(self, db: AsyncSession, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Evaluates ARJUNA, KUBERA, and CHANAKYA pipeline and materializes prioritized metrics to DB.
        """
        stmt = select(Job).where(Job.id == job_id)
        res = await db.execute(stmt)
        job = res.scalars().first()
        if not job:
            return None

        # 1. Get or evaluate ARJUNA alignment
        alignment = await arjuna_engine.evaluate_and_persist_job_alignment(db, job_id)
        # 2. Get or evaluate KUBERA compensation
        compensation = await kubera_service.evaluate_and_persist_job_compensation(db, job_id)

        # 3. Evaluate CHANAKYA priority
        eval_result = self.evaluate_priority(job, alignment or {}, compensation or {})

        # 4. Materialize to Job
        job.priority_score = eval_result["priority_score"]
        job.final_score = eval_result["priority_score"]
        job.priority_tier = eval_result["priority_tier"]
        job.urgency_score = eval_result["urgency_score"]
        job.actionability = eval_result["actionability"]
        job.effort_level = eval_result["effort_level"]
        job.recommended_action = eval_result["recommended_action"]
        job.lifecycle_status = eval_result["lifecycle_status"]
        job.chanakya_json = eval_result

        await db.commit()
        await db.refresh(job)
        return eval_result

chanakya_engine = ChanakyaPrioritizationEngine()
