# JOBMUNI — CAREER GPS "Today's Top Actions" Specification

## 1. Objective

**CAREER GPS** synthesizes candidate goals, verified opportunity radar data, and outreach pipelines into a ranked list of high-leverage daily actions, telling the senior candidate exactly where to focus their time for maximum career trajectory impact.

---

## 2. Action Ranking Engine

Career GPS categorizes actions into 4 priority queues:

1. **`IMMEDIATE_APPLY`**:
   - Condition: Unapplied job in `ACT_NOW` priority tier ($\text{Score} \ge 85$), verified active by YAMA within last 24h.
   - Action: Tailor evidence-grounded resume and queue for human review.
2. **`RECRUITER_OUTREACH`**:
   - Condition: Target company has verified recruiter with no active outreach in last 14 days.
   - Action: Draft hyper-targeted introductory message grounded in company tech stack.
3. **`APPLICATION_FOLLOWUP`**:
   - Condition: Submitted application with 0 replies after 5-7 business days.
   - Action: Queue polite check-in / follow-up message with primary recruiter.
4. **`INTERVIEW_PREP`**:
   - Condition: Scheduled upcoming interview in pipeline.
   - Action: Generate company-specific technical & behavioral briefing from Evidence Bank.

---

## 3. Career GPS API Contract

### `GET /api/v1/career-gps/today`
Returns the current ranked daily actions for the user:
```json
{
  "generated_at": "2026-08-30T03:00:00Z",
  "summary_metrics": {
    "total_urgent_actions": 3,
    "top_opportunities_count": 5,
    "pending_approvals_count": 2,
    "target_weekly_applications": 5,
    "current_week_progress": 2
  },
  "top_actions": [
    {
      "id": "act_001",
      "action_type": "IMMEDIATE_APPLY",
      "priority": "P0_URGENT",
      "title": "Apply to Snowflake: Lead Analytics Engineer",
      "reasoning": "Score: 92/100 (ACT_NOW). 100% required skill fit backed by 3 verified Snowflake/dbt evidence items. Posted 2 days ago.",
      "target_id": "9f1c740d-4126-4634-b70b-84fec99535d6",
      "target_type": "JOB",
      "primary_cta": "Review Tailored Application"
    },
    {
      "id": "act_002",
      "action_type": "RECRUITER_OUTREACH",
      "priority": "P1_HIGH",
      "title": "Reach out to Technical Recruiting Lead at Stripe",
      "reasoning": "Direct hiring recruiter for Revenue Intelligence BI team. High alignment with your Stripe-scale data modeling background.",
      "target_id": "rec_stripe_404",
      "target_type": "RECRUITER",
      "primary_cta": "Review Outreach Draft"
    }
  ]
}
```
