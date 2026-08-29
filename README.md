# Kavish Career OS — Executive Career Operating System

Kavish Career OS is a production-grade, personal Career Operating System engineered specifically for a **Senior Data, BI & Analytics Professional**.

Built around the core workflow principle:
$$\text{FIND} \longrightarrow \text{QUALIFY} \longrightarrow \text{PRIORITIZE} \longrightarrow \text{PREPARE} \longrightarrow \text{CONNECT} \longrightarrow \text{TRACK} \longrightarrow \text{LEARN}$$

---

## Key Architecture Foundations

1. **Dual-Persistence Engine**:
   - **Production Source of Truth**: PostgreSQL via SQLAlchemy 2.0 async ORM.
   - **Local Development / Offline Sandbox**: SQLite with WAL mode (`career_os.db`).
   - **Operational & Control Surface**: Google Sheets bidirectional sync adapter (not the single DB).
2. **Autonomy Guardrails (Level 2 Human Gate)**:
   - Level 0 (Autonomous): Job discovery, freshness verification, scoring, analytics.
   - Level 1 (Auto-Prepare): Tailoring resumes, drafting emails, preparing interview STAR answers.
   - **Level 2 (Strict Human Approval Required)**: Dispatching cold emails, follow-ups, and submitting applications.
   - Level 3 (Prohibited): Financial or destructive actions.
3. **Factual Integrity & Evidence Bank**:
   - Candidate claims are strictly grounded in verified facts, quantified metrics, and enterprise project records. Zero hallucinations.
4. **Independent Background Worker**:
   - Background tasks execute 24/7 independently of Antigravity IDE, user laptops, or browser sessions.

---

## Phase 1 Deliverables & Pages

- **`/dashboard`**: Executive Command Center with actionable counts, funnel bottleneck diagnostic, and Career GPS daily top action.
- **`/jobs`**: Job Radar with live opportunity manual JD parsing and transparent multi-factor scoring (0-100).
- **`/recruiters`**: Recruiter CRM tracking talent sourcers, tech stack alignment, and relationship stages.
- **`/applications`**: Application Pipeline tracking stages without blind auto-apply.
- **`/interviews`**: Interview Assistant & Memory module for SQL/BI technical case prep.
- **`/analytics`**: Career Funnel progression metrics and A/B experiment matrix.
- **`/approvals`**: Approval Center (Human-in-the-loop gate) with state machine (`APPROVE` / `REJECT` / `EDIT`).
- **`/settings`**: Dynamic Opportunity Scoring weight tuner (Skill fit, Seniority, Domain, Comp, Freshness, Signal, Recruiter) and service integrations health monitor.

---

## Development Setup & Running Locally

### 1. Backend Setup (FastAPI & Python 3.14+)

```bash
# From repository root
cd backend

# Create & activate virtual environment (if not already created)
python -m venv ../venv
..\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run automated test suite
pytest

# Start backend development server (Port 8000)
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (Next.js & TypeScript)

```bash
# From repository root
cd frontend

# Install dependencies
npm install

# Build for production verification
npm run build

# Start frontend development server (Port 3000)
npm run dev
```

---

## API Endpoints Reference

- `GET /api/v1/health` — Health check & DB connection status
- `GET /api/v1/dashboard/summary` — Command Center metrics & Career GPS recommendation
- `GET /api/v1/jobs` — Filtered opportunities with score breakdowns
- `POST /api/v1/jobs/manual-parse` — Ingest & score raw JD text
- `GET /api/v1/recruiters` — Recruiter CRM contacts
- `GET /api/v1/applications` — Application pipeline
- `GET /api/v1/approvals` — Pending Level 2 human approval queue
- `POST /api/v1/approvals/{id}/decision` — Approve/Reject/Edit action
- `GET /api/v1/scoring-config` — Active scoring weights
- `PUT /api/v1/scoring-config` — Update scoring weights (must sum to 100%)
- `GET /api/v1/settings/integrations` — Database, Sheets, AI, SMTP health
