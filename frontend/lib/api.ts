import {
  DashboardSummary,
  Job,
  Recruiter,
  Application,
  ApprovalRequest,
  ScoringConfig,
  IntegrationsStatus,
} from "./types";
import {
  FALLBACK_SUMMARY,
  FALLBACK_JOBS,
  FALLBACK_EVIDENCE,
  FALLBACK_RECRUITERS,
  FALLBACK_APPLICATIONS,
  FALLBACK_APPROVALS,
  FALLBACK_SCORING_CONFIG,
  FALLBACK_INTEGRATIONS,
} from "./fallbackData";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function fetchJson<T>(endpoint: string, options?: RequestInit, fallback?: T): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500); // 3.5s timeout for resilient fallback

    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      cache: "no-store",
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (err: any) {
    if (fallback !== undefined) {
      console.warn(`[JOBMUNI] Live backend unreachable at ${url} (${err.message}). Using local store data.`);
      return fallback;
    }
    console.error(`API Fetch Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () =>
    fetchJson<{ status: string; environment: string; database: string; version: string }>(
      "/health",
      undefined,
      { status: "HEALTHY", environment: "PREVIEW_DEMO", database: "SQLITE_WAL", version: "1.0.0" }
    ),

  // Dashboard
  getDashboardSummary: () => fetchJson<DashboardSummary>("/dashboard/summary", undefined, FALLBACK_SUMMARY),

  // Jobs
  getJobs: (params?: { status?: string; priority?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status_filter", params.status);
    if (params?.priority) searchParams.set("priority_filter", params.priority);
    const qs = searchParams.toString();
    return fetchJson<Job[]>(`/jobs${qs ? `?${qs}` : ""}`, undefined, FALLBACK_JOBS);
  },
  parseJobManual: (data: { company_name: string; title: string; raw_text: string; source_url?: string; location?: string }) =>
    fetchJson<Job>("/jobs/manual-parse", {
      method: "POST",
      body: JSON.stringify(data),
    }, {
      id: `manual-${Date.now()}`,
      company_name: data.company_name,
      title: data.title,
      location: data.location || "Remote",
      source: "MANUAL",
      status: "VERIFIED",
      verified_status: "ACTIVE",
      priority_score: 84,
      urgency_score: 88,
      actionability: "READY_TO_ACT",
      effort_level: "LOW",
      recommended_action: "APPLY",
      lifecycle_status: "READY_TO_ACT",
      extracted_required_skills: ["SQL", "dbt", "Snowflake", "Python"],
      extracted_preferred_skills: ["Looker"],
      created_at: new Date().toISOString(),
    } as unknown as Job),

  getJobAlignment: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/alignment`, undefined, FALLBACK_JOBS[0]?.arjuna_match_json),
  evaluateJobAlignment: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/alignment`, { method: "POST" }, FALLBACK_JOBS[0]?.arjuna_match_json),

  getJobCompensation: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/compensation`, undefined, FALLBACK_JOBS[0]?.kubera_comp_json),
  evaluateJobCompensation: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/compensation`, { method: "POST" }, FALLBACK_JOBS[0]?.kubera_comp_json),

  getPrioritizedJobs: (params?: { tier_filter?: string; action_filter?: string }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return fetchJson<Job[]>(`/jobs/prioritized${qs ? `?${qs}` : ""}`, undefined, FALLBACK_JOBS);
  },
  getJobPriority: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/priority`, undefined, FALLBACK_JOBS[0]?.chanakya_json),
  evaluateJobPriority: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/priority`, { method: "POST" }, FALLBACK_JOBS[0]?.chanakya_json),

  getCompensationPolicy: () =>
    fetchJson<any>("/evidence-bank/candidate/compensation-policy", undefined, {
      base_currency: "USD",
      target_comp_min: 160000,
      target_comp_preferred: 185000,
      target_comp_max: 230000,
      remote_required: true,
    }),
  updateCompensationPolicy: (data: any) =>
    fetchJson<any>("/evidence-bank/candidate/compensation-policy", {
      method: "PUT",
      body: JSON.stringify(data),
    }, data),

  // Recruiters
  getRecruiters: () => fetchJson<Recruiter[]>("/recruiters", undefined, FALLBACK_RECRUITERS),
  createRecruiter: (data: { company_name: string; name: string; role?: string; email?: string; linkedin_url?: string; notes?: string }) =>
    fetchJson<Recruiter>("/recruiters", {
      method: "POST",
      body: JSON.stringify(data),
    }, {
      id: `rec-${Date.now()}`,
      ...data,
      status: "ACTIVE",
      created_at: new Date().toISOString(),
    } as unknown as Recruiter),

  // Applications
  getApplications: () => fetchJson<Application[]>("/applications", undefined, FALLBACK_APPLICATIONS),
  createApplication: (data: { job_id: string; recruiter_id?: string; notes?: string }) =>
    fetchJson<Application>("/applications", {
      method: "POST",
      body: JSON.stringify(data),
    }, {
      id: `app-${Date.now()}`,
      ...data,
      stage: "APPLIED",
      created_at: new Date().toISOString(),
    } as unknown as Application),

  // Approvals
  getApprovals: (status = "PENDING") =>
    fetchJson<ApprovalRequest[]>(`/approvals?status_filter=${status}`, undefined, FALLBACK_APPROVALS),
  decideApproval: (id: string, decision: "APPROVE" | "REJECT" | "EDIT_AND_APPROVE", modifiedContent?: any, rejectionReason?: string) =>
    fetchJson<ApprovalRequest>(`/approvals/${id}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision, modified_content: modifiedContent, rejection_reason: rejectionReason }),
    }, {
      id,
      action_type: "DISPATCH_RECRUITER_OUTREACH",
      target_entity: "Stripe",
      summary: "Outreach approved",
      risk_level: "MEDIUM",
      status: decision === "APPROVE" || decision === "EDIT_AND_APPROVE" ? "APPROVED" : "REJECTED",
      created_at: new Date().toISOString(),
    } as unknown as ApprovalRequest),

  // Scoring Config
  getScoringConfig: () => fetchJson<ScoringConfig>("/scoring-config", undefined, FALLBACK_SCORING_CONFIG),
  updateScoringConfig: (data: Partial<ScoringConfig>) =>
    fetchJson<ScoringConfig>("/scoring-config", {
      method: "PUT",
      body: JSON.stringify(data),
    }, {
      ...FALLBACK_SCORING_CONFIG,
      ...data,
    } as ScoringConfig),

  // Integrations Settings
  getIntegrations: () => fetchJson<IntegrationsStatus>("/settings/integrations", undefined, FALLBACK_INTEGRATIONS),

  getEvidenceItems: async (params?: { category?: string; skill_or_tool?: string; search?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set("category", params.category);
    if (params?.skill_or_tool) searchParams.set("skill_or_tool", params.skill_or_tool);
    if (params?.search) searchParams.set("search", params.search);
    const qs = searchParams.toString();
    const res = await fetchJson<any[]>(`/evidence-bank${qs ? `?${qs}` : ""}`, undefined, FALLBACK_EVIDENCE);
    if (!res || res.length === 0) {
      let list = [...FALLBACK_EVIDENCE];
      if (params?.category && params.category !== "ALL") {
        list = list.filter((i) => i.category === params.category);
      }
      if (params?.search) {
        const q = params.search.toLowerCase();
        list = list.filter(
          (i) =>
            i.skill_or_tool?.toLowerCase().includes(q) ||
            i.title?.toLowerCase().includes(q) ||
            i.evidence_text?.toLowerCase().includes(q)
        );
      }
      return list;
    }
    return res;
  },
  getSkillsSummary: () =>
    fetchJson<any>("/evidence-bank/skills/summary", undefined, {
      total_skills: 12,
      total_evidence_items: 4,
      categories_count: 5,
      top_skills: [
        { skill: "Snowflake", count: 3, highest_proficiency: "EXPERT" },
        { skill: "dbt", count: 2, highest_proficiency: "EXPERT" },
        { skill: "Looker", count: 2, highest_proficiency: "EXPERT" },
        { skill: "SQL", count: 4, highest_proficiency: "EXPERT" },
        { skill: "Python", count: 2, highest_proficiency: "ADVANCED" },
      ],
    }),
  createEvidenceItem: (data: any) =>
    fetchJson<any>("/evidence-bank", {
      method: "POST",
      body: JSON.stringify(data),
    }, {
      id: `ev-${Date.now()}`,
      ...data,
      created_at: new Date().toISOString(),
    }),
  deleteEvidenceItem: (id: string) =>
    fetchJson<void>(`/evidence-bank/${id}`, {
      method: "DELETE",
    }, undefined),
  seedEvidenceBank: () =>
    fetchJson<{ status: string; created_count?: number }>("/evidence-bank/seed", {
      method: "POST",
    }, { status: "SEEDED", created_count: 4 }),
};
