import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobSkill
from app.models.candidate_profile import CandidateProfile, EvidenceItem
from app.services.skill_taxonomy import normalize_skill, CANONICAL_SKILLS
from app.services.evidence_service import saraswati_service

logger = logging.getLogger("jobmuni.arjuna")

class ArjunaAlignmentEngine:
    """
    ARJUNA Precision JD Alignment Engine.
    Deterministically evaluates Job requirements against the SARASWATI Evidence Bank.
    Guarantees zero inference and zero hallucination: if evidence does not exist in
    SARASWATI, the requirement is explicitly reported as UNKNOWN / NO_EVIDENCE.
    """

    def align_job_with_evidence(
        self,
        job: Job,
        evidence_items: List[EvidenceItem],
        candidate_profile: Optional[CandidateProfile] = None
    ) -> Dict[str, Any]:
        """
        Execute deterministic alignment between a Job and Candidate Evidence.
        """
        # If candidate has 0 active evidence records
        if not evidence_items:
            return self._build_empty_evidence_result(job)

        # 1. Index candidate evidence by normalized skill
        evidence_by_skill: Dict[str, List[EvidenceItem]] = {}
        for ev in evidence_items:
            if not ev.is_active:
                continue
            norm_skill, _ = normalize_skill(ev.skill_or_tool)
            if norm_skill not in evidence_by_skill:
                evidence_by_skill[norm_skill] = []
            evidence_by_skill[norm_skill].append(ev)
            
            # Also index any matching tags
            for tag in (ev.tags or []):
                norm_tag, _ = normalize_skill(tag)
                if norm_tag not in evidence_by_skill:
                    evidence_by_skill[norm_tag] = []
                if ev not in evidence_by_skill[norm_tag]:
                    evidence_by_skill[norm_tag].append(ev)

        # 2. Categorize Job Requirements
        req_skills: List[str] = []
        pref_skills: List[str] = []
        
        for js in (job.skills or []):
            if js.is_required:
                req_skills.append(js.skill_name)
            else:
                pref_skills.append(js.skill_name)

        # If job has no skills extracted yet, fallback to canonical mentions in title/raw_description
        if not req_skills and not pref_skills and job.raw_description:
            for canonical in CANONICAL_SKILLS:
                norm_c, _ = normalize_skill(canonical)
                if norm_c.lower() in job.raw_description.lower():
                    req_skills.append(norm_c)

        # 3. Match Required Skills
        matched_required = []
        missing_required = []
        unknown_requirements = []

        for r_raw in req_skills:
            r_norm, is_known = normalize_skill(r_raw)
            if not is_known:
                unknown_requirements.append(r_raw)

            if r_norm in evidence_by_skill:
                ev_list = evidence_by_skill[r_norm]
                matched_required.append({
                    "requirement": r_raw,
                    "normalized_skill": r_norm,
                    "matched": True,
                    "evidence_ids": [e.id for e in ev_list],
                    "evidence_count": len(ev_list),
                    "confidence": max((e.confidence for e in ev_list), default=1.0),
                    "top_metric": next((e.quant_metric for e in ev_list if e.quant_metric), None),
                    "source_companies": list(set(e.source_company for e in ev_list if e.source_company)),
                    "verification_state": "VERIFIED_GROUND_TRUTH"
                })
            else:
                missing_required.append({
                    "requirement": r_raw,
                    "normalized_skill": r_norm,
                    "matched": False,
                    "evidence_ids": [],
                    "verification_state": "NO_EVIDENCE"
                })

        # 4. Match Preferred Skills
        matched_preferred = []
        missing_preferred = []

        for p_raw in pref_skills:
            p_norm, is_known = normalize_skill(p_raw)
            if not is_known and p_raw not in unknown_requirements:
                unknown_requirements.append(p_raw)

            if p_norm in evidence_by_skill:
                ev_list = evidence_by_skill[p_norm]
                matched_preferred.append({
                    "requirement": p_raw,
                    "normalized_skill": p_norm,
                    "matched": True,
                    "evidence_ids": [e.id for e in ev_list],
                    "evidence_count": len(ev_list),
                    "confidence": max((e.confidence for e in ev_list), default=1.0),
                    "top_metric": next((e.quant_metric for e in ev_list if e.quant_metric), None),
                    "source_companies": list(set(e.source_company for e in ev_list if e.source_company)),
                    "verification_state": "VERIFIED_GROUND_TRUTH"
                })
            else:
                missing_preferred.append({
                    "requirement": p_raw,
                    "normalized_skill": p_norm,
                    "matched": False,
                    "evidence_ids": [],
                    "verification_state": "NO_EVIDENCE"
                })

        # 5. Coverage Math Calculations
        total_req_count = len(req_skills)
        if total_req_count > 0:
            required_coverage_pct = round((len(matched_required) / total_req_count) * 100.0, 1)
        else:
            required_coverage_pct = 100.0

        total_pref_count = len(pref_skills)
        if total_pref_count > 0:
            preferred_coverage_pct = round((len(matched_preferred) / total_pref_count) * 100.0, 1)
        else:
            preferred_coverage_pct = 100.0

        all_matched = matched_required + matched_preferred
        if all_matched:
            with_metrics_count = sum(1 for m in all_matched if m.get("top_metric"))
            evidence_coverage_pct = round((with_metrics_count / len(all_matched)) * 100.0, 1)
        else:
            evidence_coverage_pct = 0.0

        # 6. Seniority / Experience Alignment
        cand_seniority = candidate_profile.target_seniority.upper() if candidate_profile else "SENIOR"
        job_seniority = (job.seniority_level or "SENIOR").upper()
        experience_alignment_pct = self._calculate_seniority_alignment(cand_seniority, job_seniority)

        # 7. Match Verdict Determination
        if not all_matched:
            match_verdict = "INSUFFICIENT_EVIDENCE"
        elif required_coverage_pct >= 80.0 and experience_alignment_pct >= 75.0:
            match_verdict = "STRONG_MATCH"
        elif required_coverage_pct >= 50.0:
            match_verdict = "PARTIAL_MATCH"
        else:
            match_verdict = "WEAK_MATCH"

        # 8. Explainability Synthesis
        positive_factors = []
        for m in matched_required:
            factor = f"Verified evidence for required skill '{m['normalized_skill']}' with {m['evidence_count']} item(s)"
            if m.get("top_metric"):
                factor += f" (Metric: {m['top_metric']})"
            positive_factors.append(factor)

        negative_factors = []
        for miss in missing_required:
            negative_factors.append(f"Missing candidate evidence for required skill '{miss['normalized_skill']}'")
        for miss_p in missing_preferred:
            negative_factors.append(f"No evidence for preferred skill '{miss_p['normalized_skill']}'")

        if match_verdict == "STRONG_MATCH":
            summary = f"Strong alignment with {required_coverage_pct}% required skill fit backed by {len(all_matched)} verified candidate evidence items."
            recommended_action = "Prioritize application and highlight verified quantifiable metrics in customized resume."
        elif match_verdict == "PARTIAL_MATCH":
            summary = f"Partial fit with {required_coverage_pct}% required skill coverage. {len(missing_required)} required requirement(s) lack backing evidence."
            recommended_action = "Review missing requirements before outreach to determine if transferable experience applies."
        elif match_verdict == "WEAK_MATCH":
            summary = f"Weak alignment ({required_coverage_pct}% required coverage). Key mandatory tools are absent from Evidence Bank."
            recommended_action = "Deprioritize unless acquiring target competencies."
        else:
            summary = "Insufficient candidate evidence found to establish a verifiable match."
            recommended_action = "Add verified project STAR items to SARASWATI Evidence Bank."

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company_name": job.company_name,
            "match_verdict": match_verdict,
            "required_coverage_pct": required_coverage_pct,
            "preferred_coverage_pct": preferred_coverage_pct,
            "evidence_coverage_pct": evidence_coverage_pct,
            "experience_alignment_pct": experience_alignment_pct,
            "matched_required": matched_required,
            "missing_required": missing_required,
            "matched_preferred": matched_preferred,
            "missing_preferred": missing_preferred,
            "unknown_requirements": unknown_requirements,
            "reasoning": {
                "summary": summary,
                "positive_factors": positive_factors,
                "negative_factors": negative_factors,
                "unknowns": [f"Unmapped requirement '{u}'" for u in unknown_requirements],
                "recommended_action": recommended_action,
            }
        }

    def _calculate_seniority_alignment(self, cand_seniority: str, job_seniority: str) -> float:
        """Evaluate seniority alignment percentage."""
        seniority_weights = {
            "ENTRY": 1,
            "JUNIOR": 2,
            "MID": 3,
            "SENIOR": 4,
            "LEAD": 5,
            "STAFF": 6,
            "PRINCIPAL": 7,
            "DIRECTOR": 8,
        }
        cand_level = seniority_weights.get(cand_seniority, 4)
        job_level = seniority_weights.get(job_seniority, 4)
        
        diff = abs(cand_level - job_level)
        if diff == 0:
            return 100.0
        elif cand_level > job_level and diff == 1:
            # Overqualified by 1 level (e.g. Lead applying to Senior role) -> excellent fit
            return 95.0
        elif diff == 1:
            return 85.0
        elif diff == 2:
            return 60.0
        else:
            return 40.0

    def _build_empty_evidence_result(self, job: Job) -> Dict[str, Any]:
        """Construct fallback result when no candidate evidence is available."""
        return {
            "job_id": job.id,
            "job_title": job.title,
            "company_name": job.company_name,
            "match_verdict": "INSUFFICIENT_EVIDENCE",
            "required_coverage_pct": 0.0,
            "preferred_coverage_pct": 0.0,
            "evidence_coverage_pct": 0.0,
            "experience_alignment_pct": 50.0,
            "matched_required": [],
            "missing_required": [{"requirement": s.skill_name, "normalized_skill": s.skill_name, "matched": False, "evidence_ids": [], "verification_state": "NO_EVIDENCE"} for s in (job.skills or []) if s.is_required],
            "matched_preferred": [],
            "missing_preferred": [{"requirement": s.skill_name, "normalized_skill": s.skill_name, "matched": False, "evidence_ids": [], "verification_state": "NO_EVIDENCE"} for s in (job.skills or []) if not s.is_required],
            "unknown_requirements": [],
            "reasoning": {
                "summary": "No active candidate evidence found in SARASWATI Evidence Bank.",
                "positive_factors": [],
                "negative_factors": ["Evidence Bank is empty. Add verified competencies and project metrics to enable precision matching."],
                "unknowns": [],
                "recommended_action": "Seed or populate SARASWATI Candidate Evidence Bank."
            }
        }

    async def evaluate_and_persist_job_alignment(self, db: AsyncSession, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Evaluate alignment for a given job and persist materialized alignment metrics to DB.
        """
        stmt = select(Job).where(Job.id == job_id)
        res = await db.execute(stmt)
        job = res.scalars().first()
        if not job:
            return None

        # Fetch candidate profile and evidence items
        profile = await saraswati_service.get_or_create_default_profile(db)
        evidence_items = await saraswati_service.list_evidence(db, active_only=True, limit=500)

        alignment_result = self.align_job_with_evidence(job, evidence_items, profile)

        # Update materialized columns on Job
        job.match_verdict = alignment_result["match_verdict"]
        job.required_coverage_pct = alignment_result["required_coverage_pct"]
        job.preferred_coverage_pct = alignment_result["preferred_coverage_pct"]
        job.evidence_coverage_pct = alignment_result["evidence_coverage_pct"]
        job.experience_alignment_pct = alignment_result["experience_alignment_pct"]
        job.alignment_json = alignment_result

        await db.commit()
        await db.refresh(job)
        return alignment_result

arjuna_engine = ArjunaAlignmentEngine()
