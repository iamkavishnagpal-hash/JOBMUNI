# JOBMUNI — Security Architecture & Autonomy Policy

## 1. Secrets Management & Environment Isolation

### Strict Rules:
1. **Zero Hardcoded Secrets**: No API keys, database connection strings, SMTP passwords, or OAuth tokens in source code or git history.
2. **Environment Variable Injection**: All credentials loaded strictly via environment variables (e.g. `DATABASE_URL`, `OPENAI_API_KEY`, `GOOGLE_SHEETS_CREDENTIALS_JSON`).
3. **Frontend Isolation**: No backend secrets or private database credentials exposed to the Next.js client bundle. Only `NEXT_PUBLIC_` prefixed variables are accessible client-side.
4. **Git Hygiene**: `.env`, `.env.local`, and credential files are strictly ignored in `.gitignore`.

---

## 2. Autonomy Policy & Level 2 Guardrails

JOBMUNI enforces **Autonomy Policy Level 2 (Human Gatekeeper)**:

```
┌───────────────────────────────────────────────────────────┐
│ AUTONOMOUS (Level 1): Permitted Without Human Approval    │
│ - Job discovery and ingestion from official public feeds  │
│ - Live URL verification and stale job pruning             │
│ - Match scoring and multi-factor fit evaluation           │
│ - Evidence Bank skill extraction and alignment analysis   │
│ - Drafting resume markdown and cover letter variations    │
│ - Syncing database state to Google Sheets operational view│
└───────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│ HUMAN APPROVAL MANDATORY (Level 2 Gate): Blocked by Guard  │
│ - Sending any email or message to a recruiter or employer │
│ - Submitting an official application to an ATS / company  │
│ - Modifying or archiving candidate Evidence Bank items    │
│ - Overwriting production scoring algorithm weights        │
└───────────────────────────────────────────────────────────┘
```

---

## 3. Evidence Bank Integrity & Anti-Hallucination Policy

The **Evidence Bank** (`evidence_items`) is the single cryptographic source of truth for the candidate's professional achievements.
- **Rule of Grounding**: Generative AI tools may rephrase, emphasize, or tailor bullet points, but **every factual metric, role, company name, tool, and outcome must map directly to an Evidence Bank record**.
- **Violation Flagging**: Any AI-generated asset containing ungrounded claims (e.g., claiming 8 years of AWS experience when the Evidence Bank shows 3) is automatically rejected by the pre-approval validator.

---

## 4. API Security & Access Controls

- **CORS Configuration**: Restricted strictly to authorized origins (e.g. `http://localhost:3000` in dev, production domain in prod).
- **SQL Injection Prevention**: 100% parameterized queries via SQLAlchemy 2.0 async ORM and Pydantic v2 type coercion.
- **Rate Limiting**: Ingress API rate limiting on public endpoints to prevent abuse.
- **Audit Trails**: All human approval decisions logged with timestamps and operator IP in `approval_requests`.
