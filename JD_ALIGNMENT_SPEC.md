# JOBMUNI — ARJUNA Precision JD Alignment Engine Specification

## 1. Objective

The **ARJUNA Alignment Engine** deterministically cross-references parsed Job Descriptions against the **SARASWATI Candidate Evidence Bank** to calculate exact required/preferred skill coverage, identifying true matches and gaps without black-box guessing.

---

## 2. Alignment Logic & Mathematics

### A. Skill Matching Vectors
Let $S_{\text{req}}$ be the set of required skills extracted from the job description.
Let $S_{\text{pref}}$ be the set of preferred skills extracted from the job description.
Let $E_{\text{cand}}$ be the set of skills backed by active candidate evidence in the Evidence Bank.

$$\text{Required Coverage} = \frac{|S_{\text{req}} \cap E_{\text{cand}}|}{|S_{\text{req}}|} \times 100 \quad (\text{if } |S_{\text{req}}| = 0, \text{defaults to } 100\%)$$

$$\text{Preferred Coverage} = \frac{|S_{\text{pref}} \cap E_{\text{cand}}|}{|S_{\text{pref}}|} \times 100 \quad (\text{if } |S_{\text{pref}}| = 0, \text{defaults to } 100\%)$$

### B. Evidence Density Score
Calculates the depth of proof supporting the matched skills:
$$\text{Evidence Density} = \min\left(100, \sum_{s \in (S_{\text{req}} \cap E_{\text{cand}})} \text{EvidenceCount}(s) \times 15 + \sum \text{HasMetric}(s) \times 10\right)$$

### C. Skill Match Categorization
For every skill requirement in the JD:
- **Direct Match (Strong)**: Skill exists in Evidence Bank with quantifiable metrics and STAR text.
- **Related / Partial Match**: Skill belongs to the same domain category (e.g. AWS vs. Azure; Power BI vs. Tableau).
- **Gap (Missing)**: Skill is explicitly required in the JD but candidate has 0 backing evidence records.

---

## 3. Alignment Output Schema (`JobAlignmentResult`)

```json
{
  "job_id": "9f1c740d-4126-4634-b70b-84fec99535d6",
  "required_coverage_pct": 100.0,
  "preferred_coverage_pct": 75.0,
  "evidence_density_score": 90,
  "matched_required_skills": [
    {
      "skill": "SQL",
      "evidence_count": 4,
      "top_metric": "Optimized multi-terabyte ETL pipeline reducing runtimes by 60%"
    },
    {
      "skill": "Snowflake",
      "evidence_count": 3,
      "top_metric": "$140k/yr compute cost reduction via warehouse right-sizing"
    },
    {
      "skill": "dbt",
      "evidence_count": 2,
      "top_metric": "Created 80+ validated models with CI/dbt test coverage"
    }
  ],
  "matched_preferred_skills": [
    {
      "skill": "Looker",
      "evidence_count": 2,
      "top_metric": "Built self-serve semantic models used by 450+ daily active stakeholders"
    }
  ],
  "missing_skills": ["Databricks"],
  "alignment_verdict": "STRONG_FIT"
}
```
