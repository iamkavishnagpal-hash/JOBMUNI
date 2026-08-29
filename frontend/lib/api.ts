import {
  DashboardSummary,
  Job,
  Recruiter,
  Application,
  ApprovalRequest,
  ScoringConfig,
  IntegrationsStatus,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      cache: "no-store",
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (err: any) {
    console.error(`API Fetch Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => fetchJson<{ status: string; environment: string; database: string; version: string }>("/health"),

  // Dashboard
  getDashboardSummary: () => fetchJson<DashboardSummary>("/dashboard/summary"),

  // Jobs
  getJobs: (params?: { status?: string; priority?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status_filter", params.status);
    if (params?.priority) searchParams.set("priority_filter", params.priority);
    const qs = searchParams.toString();
    return fetchJson<Job[]>(`/jobs${qs ? `?${qs}` : ""}`);
  },
  parseJobManual: (data: { company_name: string; title: string; raw_text: string; source_url?: string; location?: string }) =>
    fetchJson<Job>("/jobs/manual-parse", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getJobAlignment: (jobId: string) => fetchJson<any>(`/jobs/${jobId}/alignment`),
  evaluateJobAlignment: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/alignment`, {
      method: "POST",
    }),
  getJobCompensation: (jobId: string) => fetchJson<any>(`/jobs/${jobId}/compensation`),
  evaluateJobCompensation: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/compensation`, {
      method: "POST",
    }),
  getPrioritizedJobs: (params?: { tier_filter?: string; action_filter?: string }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return fetchJson<Job[]>(`/jobs/prioritized${qs ? `?${qs}` : ""}`);
  },
  getJobPriority: (jobId: string) => fetchJson<any>(`/jobs/${jobId}/priority`),
  evaluateJobPriority: (jobId: string) =>
    fetchJson<any>(`/jobs/${jobId}/priority`, {
      method: "POST",
    }),
  getCompensationPolicy: () => fetchJson<any>("/evidence-bank/candidate/compensation-policy"),
  updateCompensationPolicy: (data: any) =>
    fetchJson<any>("/evidence-bank/candidate/compensation-policy", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Recruiters
  getRecruiters: () => fetchJson<Recruiter[]>("/recruiters"),
  createRecruiter: (data: { company_name: string; name: string; role?: string; email?: string; linkedin_url?: string; notes?: string }) =>
    fetchJson<Recruiter>("/recruiters", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Applications
  getApplications: () => fetchJson<Application[]>("/applications"),
  createApplication: (data: { job_id: string; recruiter_id?: string; notes?: string }) =>
    fetchJson<Application>("/applications", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Approvals
  getApprovals: (status = "PENDING") => fetchJson<ApprovalRequest[]>(`/approvals?status_filter=${status}`),
  decideApproval: (id: string, decision: "APPROVE" | "REJECT" | "EDIT_AND_APPROVE", modifiedContent?: any, rejectionReason?: string) =>
    fetchJson<ApprovalRequest>(`/approvals/${id}/decision`, {
      method: "POST",
      body: JSON.stringify({ decision, modified_content: modifiedContent, rejection_reason: rejectionReason }),
    }),

  // Scoring Config
  getScoringConfig: () => fetchJson<ScoringConfig>("/scoring-config"),
  updateScoringConfig: (data: Partial<ScoringConfig>) =>
    fetchJson<ScoringConfig>("/scoring-config", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Integrations Settings
  getIntegrations: () => fetchJson<IntegrationsStatus>("/settings/integrations"),

  // Evidence Bank (SARASWATI)
  getEvidenceItems: (params?: { category?: string; skill_or_tool?: string; search?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set("category", params.category);
    if (params?.skill_or_tool) searchParams.set("skill_or_tool", params.skill_or_tool);
    if (params?.search) searchParams.set("search", params.search);
    const qs = searchParams.toString();
    return fetchJson<any[]>(`/evidence-bank${qs ? `?${qs}` : ""}`);
  },
  getSkillsSummary: () => fetchJson<any>("/evidence-bank/skills/summary"),
  createEvidenceItem: (data: any) =>
    fetchJson<any>("/evidence-bank", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteEvidenceItem: (id: string) =>
    fetchJson<void>(`/evidence-bank/${id}`, {
      method: "DELETE",
    }),
  seedEvidenceBank: () =>
    fetchJson<{ status: string; created_count?: number }>("/evidence-bank/seed", {
      method: "POST",
    }),
};
