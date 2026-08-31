# JOBMUNI🧘‍♂️

A personal career discovery and execution engine built on data engineering principles.

---

## Why I Built This

I treated my job search as a data pipeline problem.

If you are a senior engineer or data professional looking for your next role, you quickly run into a few systemic issues with modern hiring:

1. **Timing is everything**: High-quality roles receive hundreds of applicants within 48 to 72 hours. Reaching a recruiter or hiring manager early is often the difference between getting an interview and having your resume sit unread in an ATS queue.
2. **Job boards are polluted**: A large percentage of listings are stale, already filled, duplicates, or evergreen postings kept open for talent pipelining without active headcount.
3. **Volume without signal fails**: Spraying hundreds of generic applications rarely works. What works is matching exact verified competencies against specific role requirements with quantifiable project evidence.
4. **Disconnected decision data**: Role requirements, candidate experience, compensation boundaries, location constraints, and posting timing live in separate places. Evaluating each role manually takes hours of repetitive work every day.

I didn't want to spend 2 hours every morning manually checking Greenhouse and Lever boards, reading repetitive descriptions, checking salary bands, and maintaining spreadsheets. 

I wanted a system that continuously ingests opportunities, verifies that the posting actually exists, evaluates skill and compensation alignment against verified facts, computes an objective priority score, and tells me: **"Here is the one opportunity worth acting on today, and here is what you should do next."**

---

## How It Works

The system models career execution as a deterministic state pipeline:

$$\text{DISCOVER} \longrightarrow \text{VERIFY} \longrightarrow \text{MATCH} \longrightarrow \text{VALUE} \longrightarrow \text{PRIORITIZE} \longrightarrow \text{ACT} \longrightarrow \text{TRACK} \longrightarrow \text{LEARN}$$

```
[ATS Feeds / Job Postings]
          │
          ▼
┌─────────────────────────┐
│ 1. NARADA (Discovery)   │  Ingests raw postings, normalizes schema, extracts skills & comp
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│ 2. YAMA (Verification)  │  Validates live HTTP status on exact job endpoint, detects ghost jobs
└─────────┬───────────────┘
          │ (Active postings only)
          ▼
┌─────────────────────────┐     ┌───────────────────────────────┐
│ 3. ARJUNA (JD Matching) │ ◄── │ SARASWATI (Evidence Bank)     │
└─────────┬───────────────┘     │ Verified STAR facts & metrics │
          │                     └───────────────────────────────┘
          ▼
┌─────────────────────────┐     ┌───────────────────────────────┐
│ 4. KUBERA (Comp Intel)  │ ◄── │ Candidate Opportunity Policy  │
└─────────┬───────────────┘     │ Min/Target comp, Currency FX  │
          │                     └───────────────────────────────┘
          ▼
┌─────────────────────────┐
│ 5. CHANAKYA (Priority)  │  Composite 0-100 score + Urgency + Next Best Action
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│ 6. Command Center UI    │  Next.js interface for review & decision making
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│ 7. Level 2 Human Gate   │  Explicit human approval before any external action
└─────────────────────────┘
```

---

## Architecture & Module Responsibilities

The module names represent functional responsibilities within the pipeline:

### 1. Ingestion & Verification
* **`NARADA` (Information Discovery)**: Polls configured company ATS feeds (Greenhouse, Lever) and accepts manual JD text. Normalizes raw HTML into structured schemas: required skills, preferred skills, location, remote status, and compensation ranges.
* **`YAMA` (Verification & Freshness)**: Validates that the exact posting is still live. It inspects HTTP status codes and redirect chains (catching cases where a 301/302 redirects to a generic careers landing page or returns 404). It applies a freshness decay score to flag likely inactive roles.

### 2. Evidence Grounding & Matching
* **`SARASWATI` (Candidate Evidence Bank)**: A structured fact store containing real project accomplishments, STAR breakdowns (Situation, Task, Action, Result), quantifiable metrics (e.g. *"$140k/yr compute cost reduction"*, *"58% reduction in ETL runtime"*), and employer provenance.
  * **Zero Hallucination Rule**: The matching engine cannot invent, assume, or infer skills. If a skill does not exist in the Evidence Bank, it is categorized as `NO_EVIDENCE`.
* **`ARJUNA` (Precision Alignment Engine)**: Matches parsed JD requirements against the candidate's Evidence Bank using an auditable taxonomy with alias normalization. Outputs 4 concrete metrics:
  * `Required Coverage %`: Percentage of required JD skills backed by candidate evidence.
  * `Preferred Coverage %`: Percentage of nice-to-have skills matched.
  * `Evidence Density %`: Ratio of matched skills supported by quantifiable metrics.
  * `Seniority Fit %`: Title and experience level delta.

### 3. Financial & Strategic Evaluation
* **`KUBERA` (Compensation Intelligence)**: Evaluates financial attractiveness against the candidate's configured policy (`target_comp_min`, `target_comp_preferred`, `target_comp_max`).
  * **Currency Normalization Boundary**: Converts foreign currencies (USD, EUR, GBP, CAD, AUD, INR) to policy base currency via explicit exchange rates with transparent audit flags (`EXACT`, `CONVERTED`, `UNKNOWN_RATE`).
  * **Undisclosed Salary Handling**: If compensation is missing from the posting, it is explicitly marked `UNKNOWN` rather than guessed.
* **`CHANAKYA` (Opportunity Prioritization)**: Computes a composite priority score ($0-100$) by combining skill match, compensation fit, evidence density, hiring signal, freshness, and remote alignment.
  * Computes a separate **Urgency** score based on posting age (velocity).
  * Assigns **Actionability** (`READY_TO_ACT`, `NEEDS_RESUME`, `NEEDS_EVIDENCE`, `NEEDS_RECRUITER_OUTREACH`, `BLOCKED`, `EXPIRED`).
  * Suggests **Next Best Action** (`APPLY`, `CONTACT_RECRUITER`, `PREPARE_RESUME`, `REVIEW`, `SKIP`).

### 4. Control & Safety
* **Level 2 Human Approval Gate**: All external-facing actions (sending an outreach email, submitting an application) require explicit review and manual approval in the web interface. The system never executes external side effects autonomously.

---

## Implementation Status

| Component | Status | Implementation Details |
| :--- | :--- | :--- |
| **Independent Background Worker** | **Implemented** | `worker/main.py` runs scheduled polling, ingestion, verification, and scoring independently of the web frontend or IDE. |
| **ATS Feed Connectors** | **Implemented** | Automated ingestion for Greenhouse and Lever API/board feeds, plus manual JD parser. |
| **ATS Job-Level Verifier (`YAMA`)** | **Implemented** | Inspects redirect chains, detects expired markers, and updates verification status in DB. |
| **Candidate Evidence Bank (`SARASWATI`)** | **Implemented** | Full CRUD, STAR breakdown, metrics storage, and profile policy management. |
| **Skill Taxonomy & Alignment (`ARJUNA`)** | **Implemented** | Canonical dictionary for Senior BI / Data competencies, 4-gauge coverage calculations, and evidence IDs linking. |
| **Compensation Engine (`KUBERA`)** | **Implemented** | Currency boundary, policy comparison, market percentile evaluation, and gap reporting. |
| **Opportunity Prioritization (`CHANAKYA`)** | **Implemented** | Multi-factor weighted composite scoring, velocity urgency, effort estimation, and next-action recommendation. |
| **Web Command Center** | **Implemented** | Next.js 14 interface with Job Radar, multi-agent intelligence modals, priority filtering, and responsive design. |
| **Execution Agent (`HANUMAN`)** | **Planned** | Tailored resume bullet generation and outreach drafting for the Level 2 approval queue. |
| **Google Sheets Sync Adapter** | **Planned** | Auxiliary operational control surface syncing bidirectional status with the PostgreSQL source of truth. |

---

## Engineering Design & Technical Decisions

1. **PostgreSQL as Source of Truth**: The relational database stores all normalized entities (`jobs`, `companies`, `candidate_profiles`, `evidence_items`, `scoring_configs`, `approvals`). SQLite with WAL mode is used for fast local development.
2. **Deterministic Logic Over Prompt Engineering**: Matching, scoring, currency conversions, and verification use deterministic algorithms rather than unpredictable LLM prompts. AI classification is restricted to structured extraction where evidence is strictly grounded.
3. **Decoupled Worker Architecture**: Discovery and verification tasks run in a standalone background process (`worker/main.py`) with structured logging, run IDs, and retry policies. The frontend is purely a control surface.
4. **Test-Driven Rigor**:
   - **Backend**: **66 unit and integration tests** in pytest covering edge cases (salary below min, foreign currencies, redirect chains, stale posting decay, skill gap detection, empty evidence banks).
   - **Frontend**: **60 Playwright end-to-end tests** covering route navigation, modal interactions, tab switching, and responsive viewport validation across mobile (320px, 375px, 390px) and desktop screens.

---

## Repository Structure

```
JOBMUNI/
├── backend/
│   ├── alembic/              # Database schema migrations (001 through 007)
│   ├── app/
│   │   ├── api/v1/           # REST endpoints (jobs, evidence, approvals, settings)
│   │   ├── core/             # Database connection, config, logging
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   └── services/         # Core business logic:
│   │       ├── alignment_engine.py      # ARJUNA skill matching
│   │       ├── compensation_service.py  # KUBERA compensation intel
│   │       ├── chanakya_engine.py       # CHANAKYA prioritization
│   │       ├── currency_provider.py     # FX normalization boundary
│   │       ├── discovery_service.py     # NARADA ATS ingestion
│   │       ├── evidence_service.py      # SARASWATI evidence bank
│   │       ├── jd_parser.py             # Deterministic text parser
│   │       ├── skill_taxonomy.py        # Canonical skill mapping
│   │       └── verification_service.py  # YAMA ATS verification
│   └── tests/                # 66 backend pytest tests
├── frontend/
│   ├── app/                  # Next.js 14 App Router pages
│   │   ├── dashboard/        # Executive overview & Career GPS
│   │   ├── jobs/             # Job Radar & multi-agent intelligence drawer
│   │   ├── evidence-bank/    # SARASWATI competency management
│   │   ├── recruiters/       # Recruiter CRM
│   │   ├── approvals/        # Level 2 Human-in-the-loop review
│   │   └── settings/         # Scoring weights & opportunity policy
│   ├── components/ui/        # Reusable UI components (Modals, Badges, Cards)
│   └── tests/                # 60 Playwright E2E tests & visual capture scripts
└── worker/
    └── main.py               # Standalone 24/7 background worker
```

---

## Local Development & Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv ../venv
source ../venv/bin/activate   # Windows: ..\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run unit & integration test suite
pytest -v

# Start FastAPI server (Port 8000)
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run Playwright E2E test suite
npx playwright test

# Build production bundle
npm run build

# Start frontend application (Port 3000)
npm run start
```

### 4. Background Worker Setup

```bash
cd worker
python main.py
```

---

## Data & Safety Principles

* **No Automated Spam**: The engine never blindly applies or spams recruiters. It identifies high-signal matches and prepares context for human decision-making.
* **Ground-Truth Accountability**: Every score, recommendation, and skill verdict cites the exact Evidence IDs and data points used in the calculation.
* **Fail-Safe Defaults**: Missing data is marked as `UNKNOWN` rather than estimated. Stale or ambiguous postings are downgraded automatically.

---

## Author

Built by **Kavish Nagpal** — Senior BI & Analytics Engineer.
