# JOBMUNI — Automation & Background Worker Specification

## 1. Background Worker Topology
The JOBMUNI Automation Engine runs as a dedicated, standalone Python process (`worker/main.py`) running continuously in the cloud environment.

- **Process Isolation**: Completely decoupled from Next.js frontend, FastAPI web servers, and local user machines.
- **Heartbeat Mechanism**: Every 60 seconds, the worker writes a heartbeat timestamp to `automation_runs` table.
- **Concurrency Model**: AsyncIO task loop with concurrency bounds (max 5 parallel HTTP workers to prevent external rate limiting).

---

## 2. Automation Cadence & Cron Schedules

| Cadence | Scheduled Tasks | Assigned Agents | Error Policy |
| :--- | :--- | :--- | :--- |
| **Every 15 min** | Poll official ATS job boards (Greenhouse, Lever) for target companies | `NARADA` | Exponential backoff (1m, 5m, 15m) on 429 rate limits |
| **Every 1 hour** | Verify HTTP live status of all active jobs older than 24h; flag stale ghost jobs | `YAMA` | Retry 2x before marking inactive |
| **Every 2 hours** | Check for overdue recruiter follow-up milestones (e.g. 5 days post-outreach) | `CHANAKYA`, `ARJUNA` | Stage follow-up draft in Approval Center |
| **Every 4 hours** | Bidirectional Google Sheets operational sync (push new jobs, pull user edits) | `GARUDA` | Optimistic locking with conflict resolution (Postgres wins) |
| **Daily (08:00)** | Generate daily Career GPS recommendation & aggregate funnel telemetry | `CHANAKYA`, `SANJAYA` | Non-blocking retry |

---

## 3. Rate Limiting & Ethical Discovery Policy

JOBMUNI adheres strictly to the highest standards of automated internet citizenship:
- **Maximum Request Rates**:
  - Official ATS APIs (Greenhouse/Lever): $\le 1$ request per 2 seconds per domain.
  - General Company Career Sites: $\le 1$ request per 5 seconds per domain.
- **Robots.txt & Access Invariants**:
  - Strictly observe `Disallow` directives and `Crawl-delay` headers.
  - Zero CAPTCHA solving, zero login-wall bypassing, zero proxy rotating to circumvent anti-bot protections.
  - Always identify with a standard, polite User-Agent string: `JOBMUNI-CareerBot/1.0 (+https://jobmuni.ai/bot-info)`.

---

## 4. Google Sheets Operational Sync Architecture

Google Sheets serves as an operational control surface and remote mirror:
- **Sync Direction**: Bidirectional with PostgreSQL as the authoritative source of truth.
- **Sheets Layout**:
  - Sheet 1: `Jobs & Radar` (Job title, company, score, priority, status, URL)
  - Sheet 2: `Recruiter CRM` (Name, company, email, status, last contact)
  - Sheet 3: `Application Pipeline` (Stage, date applied, resume version, notes)
- **Conflict Resolution Rule**: In the event of a simultaneous update conflict, PostgreSQL state is authoritative. User manual notes edited in Sheets are merged into Postgres via row-level hashing.

---

## 5. Structured Error Handling & Zero Silent Failures

Every automated execution records a structured record in `automation_runs`:
```json
{
  "run_id": "run_98234ab8",
  "timestamp": "2026-08-30T02:00:00Z",
  "agent": "NARADA",
  "action": "POLL_GREENHOUSE_FEED",
  "source": "https://boards-api.greenhouse.io/v1/boards/snowflake/jobs",
  "status": "SUCCESS",
  "items_ingested": 3,
  "duration_ms": 412,
  "retry_count": 0
}
```

If an unrecoverable exception occurs:
1. The error message and full stack trace are written to `automation_runs.error_message`.
2. A high-priority dashboard alert is flagged for the user.
3. The worker remains alive and advances to the next scheduled pipeline step.
