# JOBMUNI — Product Specification

## 1. Product Category & Vision
**JOBMUNI** is an Autonomous Career Intelligence & Execution Operating System built specifically for senior data, BI, and analytics professionals. It operates as an executive copilot that transforms job searching from reactive manual searching into a high-precision, data-driven, and disciplined career campaign.

---

## 2. The 11-Stage Core Product Loop

```
  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │ 1. DISCOVER  │ ───► │  2. VERIFY   │ ───► │3. UNDERSTAND │
  │ (Feeds & ATS)│      │(Active Status│      │ (JD Decomp)  │
  └──────────────┘      └──────────────┘      └──────┬───────┘
                                                     │
  ┌──────────────┐      ┌──────────────┐      ┌──────▼───────┐
  │ 6. POSITION  │ ◄─── │5. STRATEGIZE │ ◄─── │   4. SCORE   │
  │(Evidence Fit)│      │(Timing/Route)│      │(7-Dim Weight)│
  └──────┬───────┘      └──────────────┘      └──────────────┘
         │
  ┌──────▼───────┐      ┌──────────────┐      ┌──────────────┐
  │  7. PREPARE  │ ───► │  8. APPROVE  │ ───► │  9. EXECUTE  │
  │(Resume/Draft)│      │ (Human Gate) │      │(Dispatch App)│
  └──────────────┘      └──────────────┘      └──────┬───────┘
                                                     │
                        ┌──────────────┐      ┌──────▼───────┐
                        │  11. LEARN   │ ◄─── │  10. TRACK   │
                        │(Model Tune)  │      │(Status/Stage)│
                        └──────────────┘      └──────────────┘
```

1. **DISCOVER**: Ingest opportunities from official ATS endpoints (Greenhouse, Lever, Workday), company job boards, RSS feeds, and manual user submissions.
2. **VERIFY**: Check listing live status, HTTP response codes, posting freshness (<48h priority), and detect "ghost jobs" (stale listings without hiring activity).
3. **UNDERSTAND**: Deconstruct raw job descriptions into structured requirements, tech stacks (SQL, Snowflake, dbt, Looker, Python), seniority level, reporting hierarchy, and domain focus.
4. **SCORE**: Compute transparent multi-factor opportunity scores (0–100) using configurable algorithm weights.
5. **STRATEGIZE**: Determine optimal engagement paths (direct ATS submission vs. warm internal recruiter outreach vs. peer connection).
6. **POSITION**: Map job requirements directly against candidate Evidence Bank stories, extracting high-impact metrics (e.g. `$1.2M ARR saved`, `10x query speedup`).
7. **PREPARE**: Tailor resumes, craft personalized recruiter outreach pitches, and generate company-specific interview prep briefs.
8. **APPROVE (Human Gate)**: Stage all outgoing communications in the Approval Center. Require deliberate user authorization before any external dispatch.
9. **EXECUTE**: Dispatch approved emails via authorized SMTP / Gmail API and submit verified applications.
10. **TRACK**: Maintain real-time pipeline status (Applied, Recruiter Screen, Technical Interview, Hiring Manager, Offer, Rejected) across the web app and Google Sheets.
11. **LEARN**: Analyze conversion rates by skill, company tier, and outreach channel, feeding insights back into scoring weights and future strategy.

---

## 3. Product Modules & Screen Index

### 1. Executive Command Center (`/dashboard`)
- **Key Metrics Cockpit**: Urgent Act-Now Opportunities (<48h fresh, $\ge 80$ score), Recruiter Replies Pending, Follow-Ups Due, Approvals Queue, Active Interviews.
- **Career GPS Daily Recommended Action**: Top high-leverage task for today calculated by the Chanakya engine.
- **Conversion Funnel Bottleneck Diagnostic**: Real-time identification of pipeline friction points.

### 2. Job Radar (`/jobs`)
- **Opportunity Stream**: Filterable list by Priority (`ACT_NOW`, `HIGH`, `MEDIUM`, `NURTURE`, `IGNORE`), Location, Remote status, and Score.
- **Score Breakdown Inspector**: Detailed breakdown of the 7 scoring dimensions for every job.
- **Manual JD Ingest Modal**: Fast pasting and automatic parsing of any unlisted JD text or URL.

### 3. Recruiter CRM (`/recruiters`)
- **Recruiter Directory**: Verified talent partners, executive headhunters, and hiring managers.
- **Company & Tech Alignment**: Company affiliation, primary hiring domains, response history, and scheduled cadence.

### 4. Application Pipeline (`/applications`)
- **Kanban & List Pipeline**: Stages: `Identified` $\to$ `Drafting` $\to$ `Approved` $\to$ `Submitted` $\to$ `Screening` $\to$ `Interviewing` $\to$ `Offer` $\to$ `Archived`.
- **Artifact Inspector**: Tailored resume version, submitted cover letter, and notes linked to each application.

### 5. Interview Assistant & Memory (`/interviews`)
- **Interview Stages**: Upcoming round tracker, interviewer profile context, and question prediction based on company ATS profile.
- **Debrief Vault**: Post-interview question logging, candidate performance notes, and follow-up thank-you email generator.

### 6. Career Funnel Analytics (`/analytics`)
- **Conversion Funnel Progression**: Application $\to$ Screen $\to$ Interview $\to$ Offer conversion rates.
- **A/B Strategy Performance**: Metric comparison of direct ATS submissions vs. personalized recruiter outreach.

### 7. Human Approval Center (`/approvals`)
- **Autonomy Guard Level 2**: Central holding zone for all outbound application materials, connection notes, and follow-up emails.
- **Diff & Preview View**: Full rendered preview of email text, recipient address, and attached resume before granting execution.

### 8. System Configuration & Settings (`/settings`)
- **Interactive Scoring Tuner**: Configurable weight sliders for the 7 scoring criteria (enforces 100% total sum).
- **Service Status & Health**: Live connectivity indicators for PostgreSQL, Google Sheets Adapter, AI Gateway, and Outbound SMTP.
