# JOBMUNI — KUBERA Compensation Intelligence Specification

## 1. Objective

The **KUBERA Compensation Engine** evaluates job salary ranges against candidate compensation targets and market percentiles for Senior/Lead Data & BI roles, ensuring candidate time is spent only on economically viable opportunities.

---

## 2. Compensation Alignment Logic

### Input Variables
- `candidate_comp_min`: Minimum acceptable base (e.g. `$160,000`)
- `candidate_comp_target`: Target base (e.g. `$195,000`)
- `job_salary_min`: Disclosed posting min (e.g. `$170,000`)
- `job_salary_max`: Disclosed posting max (e.g. `$220,000`)

### Compensation Scoring Formula ($C_{\text{score}} \in [0, 100]$)

1. **Both Min & Max Disclosed**:
   - If `job_salary_max >= candidate_comp_target`: $C_{\text{score}} = 95 - 100$
   - If `job_salary_max >= candidate_comp_min` and `< candidate_comp_target`: $C_{\text{score}} = 75 - 85$
   - If `job_salary_max < candidate_comp_min`: $C_{\text{score}} = \max(20, 50 - \frac{\text{diff}}{1000})$
2. **Only Minimum Disclosed**:
   - Evaluates `job_salary_min` against `candidate_comp_min`.
3. **No Salary Disclosed (Undisclosed Range)**:
   - Uses seniority and company tier baseline estimates (e.g. Senior BI at Tier 1 Tech: default estimated midpoint `$175,000`).
   - Assigns baseline confidence of 70.

### Tier Classification
- `PREMIUM_ABOVE_TARGET`: `job_salary_max` exceeds target by $\ge \$15,000$.
- `TARGET_ALIGNED`: `job_salary_max` falls within $[ \text{target} - \$10\text{k}, \text{target} + \$15\text{k} ]$.
- `ACCEPTABLE_MINIMUM`: `job_salary_max` meets minimum threshold.
- `BELOW_THRESHOLD`: `job_salary_max` is below minimum.
- `UNDISCLOSED`: Salary range not published by employer.
