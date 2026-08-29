# Kavish Career OS — Evidence Bank (Truth Engine) Specification

## 1. Objective & Philosophy
The **Evidence Bank** is the immutable repository of verified facts, career achievements, project metrics, and technical expertise for the candidate.

### The Factual Integrity Mandate
- **Zero Hallucination Rule**: When generating tailored resumes, cover letters, outreach emails, or interview talking points, the AI provider is strictly constrained via prompt engineering and RAG retrieval to use **only** facts present in the Evidence Bank.
- If a JD asks for a tool (e.g. `Kubernetes`) that is not present in the candidate's Evidence Bank, the system **explicitly flags the gap in JD Alignment Score** rather than inventing fake experience.

---

## 2. Evidence Taxonomy

```
[Candidate Master Profile]
       ├── METRICS (e.g. "$2.4M cloud spend reduction", "45ms p99 query latency")
       ├── PROJECTS (e.g. "Enterprise Snowflake Migration", "dbt Semantic Layer Rollout")
       ├── LEADERSHIP (e.g. "Mentored 6 BI Engineers", "Led cross-functional stakeholder syncs")
       ├── TECH_STACK (e.g. "SQL Expert", "dbt Core/Cloud", "Tableau", "Looker", "BigQuery")
       └── DOMAINS (e.g. "FinTech Risk Analytics", "E-Commerce Funnel Optimization", "SaaS B2B")
```

---

## 3. Storage & Retrieval Pattern
Each evidence record contains:
```json
{
  "id": "evid-001",
  "category": "METRIC",
  "skill_or_tool": "Snowflake",
  "title": "Optimized multi-cluster warehouse cost",
  "evidence_text": "Architected auto-suspend and query-clustering policies across 14 BI pipelines, reducing monthly compute spend by 38% ($14,000/mo) while sustaining sub-second dashboard latencies.",
  "quant_metric": "38% compute cost reduction ($168k/yr)",
  "source_company": "Acme Analytics Corp",
  "confidence": 1.0
}
```

When evaluating a job description, the system extracts the JD's required skills, queries the Evidence Bank via semantic and exact keyword match, and computes the **Evidence Coverage Ratio**.
