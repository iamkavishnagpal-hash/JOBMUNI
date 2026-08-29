from typing import Dict, Any, Tuple
from app.models.scoring_config import ScoringConfig
from app.models.job import Job

class OpportunityScoringService:
    @staticmethod
    def calculate_score(job_data: Dict[str, Any], config: ScoringConfig) -> Tuple[int, str, Dict[str, Any]]:
        """
        Calculates a transparent 0-100 opportunity score and priority tier
        using dynamic configurable weights.
        """
        # 1. Skill Fit Score (0-100)
        skills = job_data.get("skills", [])
        skill_score = 75
        if skills:
            matched = sum(1 for s in skills if s.get("skill_name", "").lower() in ["sql", "snowflake", "dbt", "looker", "bigquery", "tableau", "python", "data modeling", "power bi"])
            skill_score = int(min(100, (matched / max(1, len(skills))) * 100 + 30))
        
        # 2. Seniority Score (0-100)
        title = job_data.get("title", "").lower()
        if any(w in title for w in ["lead", "staff", "manager", "head", "principal", "director"]):
            seniority_score = 95
        elif "senior" in title or "sr" in title:
            seniority_score = 90
        elif "mid" in title or "specialist" in title:
            seniority_score = 70
        else:
            seniority_score = 60

        # 3. Domain / BI Focus Score (0-100)
        domain_score = 85 if any(k in title for k in ["bi", "analytics", "business intelligence", "data"]) else 60

        # 4. Salary / Compensation & Location Fit (0-100)
        remote_type = str(job_data.get("remote_type", "REMOTE")).upper()
        location_score = 95 if "REMOTE" in remote_type else (80 if "HYBRID" in remote_type else 50)
        salary_max = job_data.get("salary_max") or 0
        if salary_max >= 180000:
            salary_score = 95
        elif salary_max >= 150000:
            salary_score = 85
        else:
            salary_score = 75
        comp_loc_score = int((location_score + salary_score) / 2)

        # 5. Freshness Score (0-100)
        status = job_data.get("status", "ACTIVE")
        freshness_score = 95 if status == "ACTIVE" else (40 if status == "STALE" else 10)

        # 6. Hiring Signal Score (0-100)
        hiring_signal_score = job_data.get("hiring_signal_score", 75)

        # 7. Recruiter Score (0-100)
        recruiter_score = 70  # baseline reachability

        # Weighted final composite calculation
        final_score = int(
            (skill_score * config.weight_skill_fit) +
            (seniority_score * config.weight_seniority) +
            (domain_score * config.weight_domain) +
            (comp_loc_score * config.weight_compensation) +
            (freshness_score * config.weight_freshness) +
            (hiring_signal_score * config.weight_hiring_signal) +
            (recruiter_score * config.weight_recruiter)
        )
        final_score = max(0, min(100, final_score))

        # Priority tier assignment
        if final_score >= 85 and status == "ACTIVE":
            priority_tier = "ACT_NOW"
        elif final_score >= 75:
            priority_tier = "HIGH"
        elif final_score >= 60:
            priority_tier = "MEDIUM"
        elif final_score >= 40:
            priority_tier = "NURTURE"
        else:
            priority_tier = "IGNORE"

        breakdown = {
            "skill_score": skill_score,
            "seniority_score": seniority_score,
            "domain_score": domain_score,
            "comp_location_score": comp_loc_score,
            "freshness_score": freshness_score,
            "hiring_signal_score": hiring_signal_score,
            "recruiter_score": recruiter_score,
            "weights_used": {
                "skill": config.weight_skill_fit,
                "seniority": config.weight_seniority,
                "domain": config.weight_domain,
                "compensation": config.weight_compensation,
                "freshness": config.weight_freshness,
                "hiring_signal": config.weight_hiring_signal,
                "recruiter": config.weight_recruiter,
            }
        }

        return final_score, priority_tier, breakdown

scoring_service = OpportunityScoringService()
