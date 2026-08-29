# JOBMUNI — REST API Specification

## 1. Gateway Overview
- **Base URL**: `/api/v1`
- **Protocol**: HTTP/1.1 and HTTP/2 over TLS
- **Format**: JSON (Pydantic v2 schemas)
- **Authentication**: Bearer Token / API Key Header (`X-API-KEY`)
- **Error Format**:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested job ID was not found.",
    "details": {}
  }
}
```

---

## 2. Core Endpoint Index

### 1. System Health & Observability
- `GET /api/v1/health`
  - **Description**: Returns DB connection status, dialect, and background worker heartbeat.
  - **Response 200**:
    ```json
    {
      "status": "healthy",
      "database": "connected",
      "db_engine": "postgresql",
      "worker_status": "active",
      "version": "1.0.0"
    }
    ```

- `GET /api/v1/telemetry/runs`
  - **Description**: Query recent automation runs logged by the Brahmastra orchestration engine.
  - **Query Params**: `limit=50`, `agent_name=NARADA`, `status=FAILURE`
  - **Response 200**: `List[AutomationRunSchema]`

---

### 2. Executive Dashboard & Career GPS
- `GET /api/v1/dashboard/summary`
  - **Description**: Aggregates urgent job counts, pending approvals, recruiter replies, follow-ups due, and today's top Career GPS action.
  - **Response 200**:
    ```json
    {
      "urgent_opportunities_count": 4,
      "approvals_pending_count": 2,
      "recruiter_replies_count": 1,
      "followups_due_count": 3,
      "interviews_this_week_count": 2,
      "active_applications_count": 12,
      "career_gps_top_action": {
        "title": "Review 2 Approved Outreaches for Snowflake & Stripe",
        "reason": "High-urgency roles posted <24h ago with verified recruiter contacts.",
        "cta_label": "Go to Approvals",
        "cta_route": "/approvals"
      }
    }
    ```

---

### 3. Job Radar & Ingestion
- `GET /api/v1/jobs`
  - **Query Params**: `priority=ACT_NOW`, `remote_status=REMOTE`, `min_score=75`, `limit=50`, `offset=0`
  - **Response 200**: `List[JobResponseSchema]`

- `POST /api/v1/jobs/manual-parse`
  - **Description**: Ingest raw JD text or URL. Automatically runs decompression, skill extraction, and scoring.
  - **Request Body**:
    ```json
    {
      "company_name": "Databricks",
      "job_title": "Lead Solutions Architect - Analytics",
      "posting_url": "https://databricks.com/careers/123",
      "raw_description": "We are seeking a Lead BI/Analytics Architect with Snowflake, dbt..."
    }
    ```
  - **Response 201**: `JobDetailSchema`

- `GET /api/v1/jobs/{id}`
  - **Response 200**: Full job schema with 7-dimensional score breakdown.

---

### 4. Recruiter CRM
- `GET /api/v1/recruiters`
  - **Query Params**: `company_id=...`, `outreach_status=...`
  - **Response 200**: `List[RecruiterSchema]`

- `POST /api/v1/recruiters`
  - **Request Body**: `RecruiterCreateSchema`
  - **Response 201**: `RecruiterSchema`

---

### 5. Application Pipeline
- `GET /api/v1/applications`
  - **Query Params**: `status=...`
  - **Response 200**: `List[ApplicationSchema]`

- `PATCH /api/v1/applications/{id}/stage`
  - **Request Body**: `{"new_status": "INTERVIEWING", "notes": "Passed technical screen"}`
  - **Response 200**: `ApplicationSchema`

---

### 6. Human Approval Center (Level 2 Autonomy Gate)
- `GET /api/v1/approvals`
  - **Query Params**: `status=PENDING`
  - **Response 200**: `List[ApprovalRequestSchema]`

- `POST /api/v1/approvals/{id}/decision`
  - **Description**: Human approves or rejects a staged outreach or application dispatch.
  - **Request Body**:
    ```json
    {
      "decision": "APPROVED",
      "notes": "Looks great, dispatch via Gmail"
    }
    ```
  - **Response 200**:
    ```json
    {
      "id": "appr_123",
      "status": "APPROVED",
      "dispatch_status": "QUEUED_FOR_DISPATCH"
    }
    ```

---

### 7. Evidence Bank
- `GET /api/v1/evidence-bank`
  - **Response 200**: `List[EvidenceItemSchema]`

- `POST /api/v1/evidence-bank`
  - **Request Body**: `EvidenceItemCreateSchema`
  - **Response 201**: `EvidenceItemSchema`

---

### 8. System Configuration & Weights
- `GET /api/v1/scoring-config`
  - **Response 200**: `ScoringConfigSchema` (Returns the 7 weights summing to 1.0)

- `PUT /api/v1/scoring-config`
  - **Request Body**: `ScoringConfigUpdateSchema` (Validates that weights sum to exactly 1.0)
  - **Response 200**: `ScoringConfigSchema`
