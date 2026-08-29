# JOBMUNI — SARASWATI Candidate Evidence Bank Specification

## 1. Objective

The **Candidate Evidence Bank (SARASWATI)** serves as the authoritative source of truth for the candidate's professional career history, technical skills, quantifiable business metrics, and project accomplishments.

**Zero Invention Policy**: All downstream matching, scoring, resume customization, and recruiter communications must link strictly to valid, verified evidence records in this bank.

---

## 2. Evidence Model & Taxonomy

### Categories
1. `TECH_SKILL`: Specific proficiency in tools/languages (e.g. `SQL`, `Snowflake`, `dbt`, `Looker`, `Python`, `Power BI`, `Databricks`, `Azure`, `AWS`, `GCP`).
2. `BUSINESS_IMPACT`: Measured quantitative results (e.g. `$1.2M annual cloud compute cost reduction`, `45% faster dashboard query SLA`).
3. `ARCHITECTURE_PROJECT`: End-to-end data platform delivery (e.g. `Modern Data Stack migration from on-prem SQL Server to Snowflake`).
4. `LEADERSHIP_MANAGEMENT`: Mentorship, stakeholder management, cross-functional collaboration.
5. `CERTIFICATION`: Verified credentials (e.g. `Snowflake SnowPro Core`, `dbt Certified Developer`).

### Schema Definition (`evidence_items`)
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(36)` (UUID) | Unique Evidence ID |
| `profile_id` | `VARCHAR(36)` | Candidate Profile Reference |
| `category` | `VARCHAR(50)` | Category enum |
| `skill_or_tool` | `VARCHAR(100)` | Primary associated skill (normalized taxonomy) |
| `title` | `VARCHAR(255)` | Short descriptive headline |
| `evidence_text` | `TEXT` | Full STAR description (Situation, Task, Action, Result) |
| `quant_metric` | `VARCHAR(255)` | Explicit quantified metric string |
| `source_company` | `VARCHAR(255)` | Company where achievement occurred |
| `timeframe_start` | `DATE` / `VARCHAR(50)` | Period of execution |
| `timeframe_end` | `DATE` / `VARCHAR(50)` | Period of execution |
| `confidence` | `FLOAT` | Reliability rating (default 1.0) |
| `verified_by_user` | `BOOLEAN` | User has audited and confirmed accuracy |

---

## 3. Evidence API Contract

- `GET /api/v1/evidence-bank`: List all candidate evidence items (supports filtering by `category`, `skill_or_tool`, `search`).
- `POST /api/v1/evidence-bank`: Create new evidence item with mandatory metrics and text validation.
- `GET /api/v1/evidence-bank/{id}`: Retrieve single evidence item with linked job matches.
- `PUT /api/v1/evidence-bank/{id}`: Update evidence item.
- `DELETE /api/v1/evidence-bank/{id}`: Soft delete / remove evidence item.
- `GET /api/v1/evidence-bank/skills-summary`: Returns matrix of verified skills with evidence counts and top metrics.
