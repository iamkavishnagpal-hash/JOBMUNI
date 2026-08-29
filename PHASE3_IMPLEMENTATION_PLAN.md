# JOBMUNI — Phase 3 Master Implementation Plan: Evidence-Grounded Career Intelligence

## 1. Executive Summary & Scope

Phase 3 builds the evidence-grounded intelligence and prioritization layer of JOBMUNI. It connects candidate ground truth from the **SARASWATI Evidence Bank** to verified opportunities from Phase 2/2.1, executing deterministic skill alignment, compensation intelligence, transparent 0-100 scoring, and daily action ranking via **CAREER GPS**.

---

## 2. Pre-Build Architecture Audit & Conflict Assessment

### Audit against Phase 1, Phase 2, & Phase 2.1:
1. **Multi-Dialect Database Compatibility**:
   - `candidate_profiles` and `evidence_items` tables are already present in base schema.
   - We will introduce a clean migration `004_phase3_intelligence_schema.py` adding `match_verdict`, `required_coverage`, `preferred_coverage`, `evidence_coverage`, and `explainability_json` columns to `jobs` or linked `job_matches` table.
   - All migrations will use `batch_alter_table` for SQLite & PostgreSQL parity.
2. **Deterministic Verification Compatibility**:
   - Phase 3 engines consume jobs verified by YAMA (`verification_status == 'ACTIVE'`). Inactive jobs (`INACTIVE`) are automatically assigned to `IGNORE` tier.
3. **Autonomy Guardrails**:
   - Strictly respects Autonomy Level 2 (Human in the loop). No auto-apply or unapproved outbound communication.

**Audit Result**: **0 architectural conflicts detected.** The Phase 3 design cleanly layers on top of Phase 1, 2, and 2.1 without breaking existing APIs or data flows.

---

## 3. Work Breakdown & Implementation Phases

### Phase 3.1: Saraswati Evidence Bank Service
- **Service**: `app/services/evidence_service.py`
  - Seed default Senior BI & Analytics competencies (`SQL`, `Snowflake`, `dbt`, `Looker`, `Python`, `Power BI`, `Databricks`, `Azure`, `AWS`, `BigQuery`, `Tableau`, `Data Modeling`) with verified quantified impact metrics and STAR stories.
  - CRUD operations with metric format validation.
- **Endpoints**: `backend/app/api/v1/endpoints/evidence_bank.py`

### Phase 3.2: Arjuna JD Alignment Engine
- **Service**: `app/services/alignment_engine.py`
  - Cross-references job required skills and preferred skills with candidate evidence items.
  - Calculates exact % required coverage, % preferred coverage, and evidence density.
  - Identifies concrete match strengths and gaps.

### Phase 3.3: Kubera Compensation Intelligence
- **Service**: `app/services/compensation_service.py`
  - Compares disclosed salary ranges against candidate min and target compensation.
  - Assigns compensation alignment scores and tier classifications (`PREMIUM_ABOVE_TARGET`, `TARGET_ALIGNED`, `ACCEPTABLE_MINIMUM`, `BELOW_THRESHOLD`, `UNDISCLOSED`).

### Phase 3.4: Chanakya Opportunity Prioritizer & Explainability Engine
- **Service**: `app/services/scoring_service.py` & `app/services/explainability_service.py`
  - Integrates all 7 scoring dimensions into a transparent 0-100 composite score.
  - Generates structured explainability blocks (`headline_why`, `key_strengths`, `risk_factors_or_gaps`, `score_breakdown`).
  - Assigns priority tiers: `ACT_NOW`, `HIGH`, `MEDIUM`, `NURTURE`, `IGNORE`.

### Phase 3.5: Career GPS "Today's Top Actions" Engine
- **Service**: `app/services/career_gps_service.py`
  - Aggregates high-priority opportunities, outreach triggers, and pipeline tasks into a ranked daily action queue.
- **Endpoints**: `GET /api/v1/career-gps/today` and `GET /api/v1/career-gps/summary`

### Phase 3.6: Standalone Worker Phase 3 Integration
- Update `worker/main.py` to run the Phase 3 alignment, scoring, and Career GPS evaluation pipeline in its scheduled automation cycle.

### Phase 3.7: Comprehensive Test Suite & Verification
- Authored unit tests in `backend/tests/`:
  - `test_evidence_bank.py`: Evidence CRUD, validation, skill summary
  - `test_alignment_arjuna.py`: Required/preferred skill coverage math, zero-hallucination verification
  - `test_compensation_kubera.py`: Salary tier evaluation and comp scores
  - `test_opportunity_scoring_phase3.py`: 7-dimension mathematical composite & breakdown
  - `test_career_gps.py`: Action queue generation and prioritization
  - `test_explainability.py`: Rationale and gap analysis generation
- E2E Playwright tests in `frontend/tests/phase3.spec.ts`.

---

## 4. Verification Plan

1. Run `alembic upgrade head`
2. Run full backend test suite: `pytest -v`
3. Run background worker against test fixture
4. Verify Career GPS and Evidence Bank API responses
5. Run full Playwright test suite: `npx playwright test`
6. Verify 0 horizontal overflow across mobile viewports
7. Create clean Git commit for Phase 3
