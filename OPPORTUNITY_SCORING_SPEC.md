# JOBMUNI — Opportunity Scoring & Explainability Specification

## 1. Objective

Provide a transparent, explainable 0-100 opportunity score grounded in factual matching dimensions. Avoid opaque black-box "AI Magic" scores.

---

## 2. Mathematical Scoring Formula

The total composite score $S_{\text{total}} \in [0, 100]$ is computed as:

$$S_{\text{total}} = \sum_{i=1}^{7} (D_i \times W_i)$$

Where $\sum W_i = 1.00$, and the 7 dimensions are:

| Dim ($D_i$) | Dimension Name | Default Weight ($W_i$) | Calculation Basis |
| :--- | :--- | :--- | :--- |
| $D_1$ | **Required Skill Fit** | 0.25 (25%) | $\frac{|S_{\text{req}} \cap E_{\text{cand}}|}{|S_{\text{req}}|} \times 100$ |
| $D_2$ | **Seniority & Title Alignment** | 0.15 (15%) | Target vs. Posting title seniority level match (Lead/Senior = 90-100) |
| $D_3$ | **Domain & Stack Fit** | 0.15 (15%) | Modern Data & BI Stack alignment |
| $D_4$ | **Compensation & Location Fit** | 0.15 (15%) | Salary target comparison (Kubera) + Remote preference match |
| $D_5$ | **Evidence Density & Proof** | 0.10 (10%) | Depth of quantifiable metrics backing the matched skills |
| $D_6$ | **Hiring Signal & Urgency** | 0.10 (10%) | Active ATS posting, direct recruiter presence, hiring urgency |
| $D_7$ | **Freshness & Reachability** | 0.10 (10%) | Days since posted + YAMA live verification status |

---

## 3. Priority Tiering (CHANAKYA Strategy)

- **`ACT_NOW`** ($S_{\text{total}} \ge 85$ and Status = `ACTIVE`): High fit, fresh posting, verified live. Immediate application & recruiter outreach recommended.
- **`HIGH`** ($75 \le S_{\text{total}} < 85$): Strong match with minor skill gaps or moderate age.
- **`MEDIUM`** ($60 \le S_{\text{total}} < 75$): Partial match, secondary target, or below target comp.
- **`NURTURE`** ($40 \le S_{\text{total}} < 60$): Company of interest, but current opening is suboptimal fit.
- **`IGNORE`** ($S_{\text{total}} < 40$ or Status = `INACTIVE`): Low fit, missing mandatory skills, or closed/ghost posting.

---

## 4. Explainability Schema (`ScoreExplainability`)

Every scored opportunity returns a structured explainability block:
- **`headline_why`**: 1-sentence executive summary (e.g. *"95% skill match with verified Snowflake and dbt metrics exceeding comp target by +$15k"*).
- **`key_strengths`**: List of specific positive match factors.
- **`risk_factors_or_gaps`**: List of skill gaps or location compromises.
- **`score_breakdown`**: Exact numeric breakdown for each of the 7 dimensions.
