# Kavish Career OS — Career GPS Specification

## 1. Objective & Purpose
The **Career GPS Engine** converts real-time application funnel data, new opportunities, and outreach states into a prioritized, ranked daily agenda: **"Today's Top Actions"**.

Rather than forcing the user to manually hunt through dozens of jobs and CRM rows, the Career GPS computes urgency, conversion odds, and response momentum to recommend the highest-leverage next moves.

---

## 2. Priority Ranking Algorithm & Factors

```
Priority Score = W1*(Urgency Factor) + W2*(Opportunity Score) + W3*(Response Momentum) + W4*(Deadline Penalty)
```

### Action Categories & Logic Rules:
1. **Fresh High-Fit Outreach**:
   - Condition: Job score $\ge 80$, posted $<48\text{ hours}$ ago, verified hiring signal = `HIGH`.
   - Action: *"Contact Recruiter [Name] at [Company] for [Title] — posted [X] hours ago"*.
2. **Follow-Up Cadences Due**:
   - Condition: Outreach sent 3, 7, or 14 days ago with status `SENT` and no reply.
   - Action: *"Send Day-3 Follow-Up to [Recruiter] — High historical reply rate"*.
3. **Application Ready for Submission**:
   - Condition: Tailored resume generated with JD Alignment Score $\ge 85$, pending approval.
   - Action: *"Review and approve application for [Company]"*.
4. **Upcoming Interview Prep**:
   - Condition: Interview scheduled within next 48 hours.
   - Action: *"Practice Technical SQL & BI System Design for [Company] interview"*.
5. **Pruning Low-Signal Stale Jobs**:
   - Condition: Jobs older than 45 days with closed ATS status.
   - Action: *"Archive 4 stale opportunities to declutter funnel"*.

---

## 3. API Output Schema
```json
{
  "generated_at": "2026-08-30T08:00:00Z",
  "bottleneck_diagnostic": "Recruiter response rate on Variant B is 8% lower than Variant A.",
  "top_actions": [
    {
      "id": "gps-act-001",
      "priority": 1,
      "urgency_tier": "CRITICAL",
      "action_type": "OUTREACH",
      "title": "Reach out to Alex Rivera (Senior Tech Recruiter) at FinTech Corp",
      "reason": "Job posted 42 minutes ago; 94% BI skill match; active hiring signal.",
      "target_entity_type": "job",
      "target_entity_id": "job-uuid-123",
      "cta_label": "Generate Outreach",
      "cta_route": "/approvals"
    }
  ]
}
```
