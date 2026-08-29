# JOBMUNI — Testing & Verification Specification

## 1. Testing Pyramid & Verification Standards

```
                      ┌─────────────────────────┐
                      │    PLAYWRIGHT E2E       │
                      │  (Multi-Viewport Suite) │
                      └────────────┬────────────┘
                                   │
                      ┌────────────┴────────────┐
                      │    API & ROUTE TESTS    │
                      │  (FastAPI TestClient)   │
                      └────────────┬────────────┘
                                   │
                      ┌────────────┴────────────┐
                      │    DATABASE & MODELS    │
                      │  (SQLAlchemy + Alembic) │
                      └────────────┬────────────┘
                                   │
                      ┌────────────┴────────────┐
                      │   CORE SCORING UNIT     │
                      │  (Deterministic Logic)  │
                      └─────────────────────────┘
```

---

## 2. Test Suites Index

### 1. Backend Pytest Suite (`backend/tests/`)
- `test_health.py`: Verifies `/api/v1/health` endpoint returns DB connection state and correct dialect.
- `test_database.py`: Tests CRUD operations on Candidate, Job, and Company entities with async sessions.
- `test_scoring_config.py`: Validates that scoring weights sum to exactly 1.0 (with 400 Bad Request error on violation).
- `test_approvals.py`: Tests the Level 2 human approval state machine (Transitions from `PENDING` $\to$ `APPROVED` or `REJECTED`).

### 2. Frontend Playwright E2E Suite (`frontend/tests/`)
- `phase1.spec.ts`: Executes 12 required scenarios across Desktop Chrome and Mobile Pixel 5:
  1. Application loads and redirects `/` $\to$ `/dashboard`
  2. Dashboard loads with metrics and Career GPS recommendation
  3. Jobs route loads with opportunity radar and modal
  4. Recruiters route loads with CRM cards
  5. Applications route loads with pipeline stages
  6. Interviews route loads with assistant shell
  7. Analytics route loads with conversion telemetry
  8. Approvals route loads with Level 2 guard
  9. Settings route loads with weight sliders and integration health
  10. Mobile viewport navigation works via bottom navigation bar
  11. Zero horizontal overflow across mobile viewports (320px, 375px, 390px)
  12. Production build artifact verification

---

## 3. Strict Testing Invariants

1. **Zero Arbitrary Sleep Delays**: All async tests must use deterministic event listeners, `waitForLoadState('networkidle')`, `waitForURL()`, or polling utilities with timeouts.
2. **Deterministic Test Isolation**: Every test run operates against a fresh or rollbackable database session.
3. **No Flake Toleration**: Tests must execute reliably with identical results across 100 consecutive executions.
