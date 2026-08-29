# JOBMUNI — GSD Master Implementation Plan

## 1. GSD Execution Methodology
Following the `/GSD` autonomous engineering methodology, development is partitioned into strictly bounded, atomic phases. Each phase establishes explicit deliverables, dependency chains, and automated verification criteria before advancing.

---

## 2. Phase-by-Phase Roadmap

### ✅ PHASE 1: Architectural Foundation & Foundational Shell (COMPLETED)
- **Scope**:
  - FastAPI backend with SQLAlchemy 2.0 async ORM and Pydantic v2.
  - Multi-dialect support (PostgreSQL production config + SQLite WAL local dev).
  - 16 core database entities and Alembic migrations.
  - Next.js 14 App Router frontend with Obsidian Executive theme.
  - 9 foundational pages (`/`, `/dashboard`, `/jobs`, `/recruiters`, `/applications`, `/interviews`, `/analytics`, `/approvals`, `/settings`).
  - Configurable opportunity scoring engine (7 weight dimensions).
  - Level 2 Human Approval Center initial scaffold.
- **Verification Gate**:
  - Backend Pytest suite passes 100% (4/4).
  - Frontend production build compiles with 0 errors.
  - Playwright E2E suite passes 100% (24/24 tests across Desktop & Mobile).

---

### 🚀 PHASE 2: Live Ingestion & Brahmastra Discovery Engine (NARADA & YAMA)
- **Scope**:
  - Implement the standalone background worker process (`worker/main.py`).
  - Implement `NARADA` discovery connectors for official ATS boards (Greenhouse JSON API, Lever JSON API).
  - Implement `YAMA` live URL validator and ghost job detector.
  - Automated JD parser service extracting required skills (SQL, Snowflake, dbt, Looker, Python, BigQuery) and seniority.
  - Background cron scheduler executing 24/7 independently of frontend.
- **Deliverables**:
  - `backend/app/services/discovery_service.py`
  - `backend/app/services/ats_connectors/`
  - `worker/main.py`
  - Unit and integration tests for ATS ingestion and ghost detection.
- **Verification Gate**:
  - Live mock/sandbox ATS feeds ingested and deduplicated.
  - Stale job URLs flagged inactive accurately.
  - Automation runs logged to `automation_runs`.

---

### 🚀 PHASE 3: Strategy, Intelligence & Evidence Bank Grounding (CHANAKYA & SARASWATI)
- **Scope**:
  - Candidate Evidence Bank CRUD and semantic skill indexing (`SARASWATI`).
  - Multi-factor opportunity scoring calculation against candidate Evidence Bank (`CHANAKYA`).
  - Real-time Career GPS algorithm computing the top high-leverage daily action.
  - Compensation benchmarking and market intelligence normalization (`KUBERA`).
- **Deliverables**:
  - `backend/app/services/evidence_service.py`
  - `backend/app/services/career_gps_service.py`
  - `backend/app/services/compensation_service.py`
  - Frontend Evidence Bank management view and Career GPS action execution card.
- **Verification Gate**:
  - Dynamic score breakdown correctly reflects Evidence Bank alignment.
  - Career GPS dynamically selects top priority job/outreach based on score & freshness.

---

### 🚀 PHASE 4: Positioning, Asset Generation & Approval Center (KRISHNA & VISHWAKARMA)
- **Scope**:
  - Provider-agnostic AI Gateway integration with strict Evidence Bank grounding guardrails.
  - Resume tailoring service generating ATS-friendly markdown and PDF versions (`VISHWAKARMA`).
  - Personalized recruiter pitch generator based on hiring manager profile and mutual tech stack (`KRISHNA`).
  - Full-featured Level 2 Approval Center with rich diff inspector, email preview, and approve/reject triggers.
- **Deliverables**:
  - `backend/app/services/ai_gateway.py`
  - `backend/app/services/resume_tailor_service.py`
  - `backend/app/services/outreach_generator.py`
  - Frontend interactive Approval Center with live review modal.
- **Verification Gate**:
  - Zero hallucination test: Generated resume contains only verified Evidence Bank facts.
  - Outbound dispatch is physically impossible without human approval state transition.

---

### 🚀 PHASE 5: Google Workspace Integration & Execution (GARUDA & HANUMAN)
- **Scope**:
  - Bidirectional Google Sheets operational adapter (mirroring Jobs, CRM, Applications).
  - Authorized Gmail OAuth / SMTP dispatch engine for approved outreaches (`HANUMAN`).
  - Mobile PWA offline caching and service worker registration.
  - Recruiter CRM follow-up cadence automation (3-day / 7-day nudge triggers).
- **Deliverables**:
  - `backend/app/services/google_sheets_service.py`
  - `backend/app/services/email_dispatch_service.py`
  - `worker/tasks/sheets_sync_task.py`
- **Verification Gate**:
  - Edits made in Google Sheets sync back to PostgreSQL with conflict resolution.
  - Approved emails dispatch cleanly via authorized provider.

---

### 🚀 PHASE 6: Learning, A/B Analytics & Enterprise Hardening (SANJAYA)
- **Scope**:
  - Funnel conversion analytics engine tracking response rates by company tier, seniority, and skill.
  - A/B testing matrix for outreach messages.
  - Production containerization (Docker, Docker Compose, Kubernetes manifests).
  - PostgreSQL cloud migration guides and automated daily DB backups.
- **Deliverables**:
  - `backend/app/services/analytics_engine.py`
  - `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`, `Dockerfile.worker`
  - Full end-to-end regression test suite.
- **Verification Gate**:
  - Complete end-to-end pipeline run from ATS feed ingestion to approved dispatch and analytics logging.
