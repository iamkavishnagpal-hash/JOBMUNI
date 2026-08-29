from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from app.models.scoring_config import ScoringConfig

class OpportunityScoringService:
    @staticmethod
    def calculate_score_from_dict(job_data: Dict[str, Any], config: Optional[ScoringConfig] = None) -> Tuple[int, str, Dict[str, Any]]:
        """Calculates a transparent 0-100 opportunity score and priority tier."""
        w_skill = (getattr(config, "weight_skill_fit", None) if config else None) or 0.25
        w_sen = (getattr(config, "weight_seniority", None) if config else None) or 0.15
        w_dom = (getattr(config, "weight_domain", None) if config else None) or 0.15
        w_comp = (getattr(config, "weight_compensation", None) if config else None) or 0.15
        w_fresh = (getattr(config, "weight_freshness", None) if config else None) or 0.10
        w_sig = (getattr(config, "weight_hiring_signal", None) if config else None) or 0.10
        w_rec = (getattr(config, "weight_recruiter", None) if config else None) or 0.10

        skills = job_data.get("skills", [])
        skill_score = 75
        if skills:
            if isinstance(skills[0], str):
                skill_names = [s.lower() for s in skills]
            else:
                skill_names = [s.get("skill_name", "").lower() for s in skills if isinstance(s, dict)]
            matched = sum(1 for s in skill_names if s in ["sql", "snowflake", "dbt", "looker", "bigquery", "tableau", "python", "data modeling", "power bi", "databricks", "aws", "gcp", "azure"])
            skill_score = int(min(100, (matched / max(1, len(skills))) * 100 + 35))

        title = str(job_data.get("title", "")).lower()
        if any(w in title for w in ["lead", "staff", "manager", "head", "principal", "director", "vp"]):
            seniority_score = 95
        elif "senior" in title or "sr" in title:
            seniority_score = 90
        elif "mid" in title or "specialist" in title:
            seniority_score = 70
        else:
            seniority_score = 65

        domain_score = 90 if any(k in title for k in ["bi", "analytics", "business intelligence", "data", "solution"]) else 65

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

        status = job_data.get("status", "ACTIVE")
        freshness_score = 95 if status == "ACTIVE" else (40 if status == "STALE" else 10)

        hiring_signal_score = job_data.get("hiring_signal_score", 75)
        recruiter_score = 70

        final_score = int(
            (skill_score * w_skill) +
            (seniority_score * w_sen) +
            (domain_score * w_dom) +
            (comp_loc_score * w_comp) +
            (freshness_score * w_fresh) +
            (hiring_signal_score * w_sig) +
            (recruiter_score * w_rec)
        )
        final_score = max(0, min(100, final_score))

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
                "skill": w_skill,
                "seniority": w_sen,
                "domain": w_dom,
                "compensation": w_comp,
                "freshness": w_fresh,
                "hiring_signal": w_sig,
                "recruiter": w_rec,
            }
        }

        return final_score, priority_tier, breakdown

    @classmethod
    def calculate_score(cls, *args, **kwargs) -> Any:
        if args and isinstance(args[0], dict):
            config = args[1] if len(args) > 1 else kwargs.get("config")
            return cls.calculate_score_from_dict(args[0], config=config)
        
        # Keyword based
        title = kwargs.get("title", "")
        raw_description = kwargs.get("raw_description", "")
        location = kwargs.get("location", "")
        remote_status = kwargs.get("remote_status", "REMOTE")
        salary_min = kwargs.get("salary_min")
        salary_max = kwargs.get("salary_max")
        posted_at = kwargs.get("posted_at")
        is_active = kwargs.get("is_active", True)
        config = kwargs.get("config")

        data = {
            "title": title,
            "raw_description": raw_description,
            "location": location,
            "remote_type": remote_status,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "status": "ACTIVE" if is_active else "INACTIVE",
            "skills": [{"skill_name": w} for w in ["SQL", "Snowflake", "dbt", "Python"] if w.lower() in (raw_description or "").lower()],
            "hiring_signal_score": 80,
        }
        final_score, priority_tier, breakdown = cls.calculate_score_from_dict(data, config=config)
        return {
            "total_score": final_score,
            "priority_tier": priority_tier,
            "hiring_signal_score": 80,
            "breakdown": breakdown,
        }

OpportunityScorer = OpportunityScoringService
scoring_service = OpportunityScoringService()
