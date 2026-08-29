export interface DashboardSummary {
  urgent_opportunities_count: number;
  recruiter_replies_count: number;
  followups_due_count: number;
  approvals_pending_count: number;
  interviews_this_week_count: number;
  active_applications_count: number;
  funnel_bottleneck: string;
  career_gps_top_action?: {
    title: string;
    reason: string;
    cta_label: string;
    cta_route: string;
  };
}

export interface JobSkill {
  id: string;
  skill_name: string;
  category: string;
  is_required: boolean;
  weight: number;
}

export interface Job {
  id: string;
  company_name: string;
  title: string;
  location: string;
  remote_type: string;
  source_url?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  seniority_level: string;
  domain_category: string;
  raw_description?: string;
  posted_at?: string;
  first_seen_at: string;
  last_verified_at: string;
  last_http_status: number;
  status: "ACTIVE" | "STALE" | "CLOSED" | "UNKNOWN";
  freshness_conf: number;
  hiring_signal_score: number;
  hiring_signal_tier: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  final_score: number;
  priority_tier: "ACT_NOW" | "HIGH" | "MEDIUM" | "NURTURE" | "IGNORE";
  score_breakdown: Record<string, any>;
  created_at: string;
  skills: JobSkill[];
}

export interface Recruiter {
  id: string;
  company_name: string;
  name: string;
  role: string;
  email?: string;
  linkedin_url?: string;
  relationship_status: string;
  engagement_score: number;
  first_contact?: string;
  last_contact?: string;
  followup_due_date?: string;
  notes?: string;
  created_at: string;
}

export interface Application {
  id: string;
  job_id: string;
  recruiter_id?: string;
  status: string;
  jd_alignment_score: number;
  applied_date?: string;
  referral_source?: string;
  notes?: string;
  created_at: string;
}

export interface ApprovalRequest {
  id: string;
  action_type: string;
  autonomy_level: number;
  title: string;
  reason: string;
  generated_content: {
    subject?: string;
    body?: string;
    recipient?: string;
    [key: string]: any;
  };
  supporting_evidence: any[];
  status: "PENDING" | "APPROVED" | "REJECTED" | "EDITED_AND_APPROVED";
  decision_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface ScoringConfig {
  id: string;
  config_name: string;
  weight_skill_fit: number;
  weight_seniority: number;
  weight_domain: number;
  weight_compensation: number;
  weight_freshness: number;
  weight_hiring_signal: number;
  weight_recruiter: number;
  is_active: boolean;
}

export interface IntegrationsStatus {
  database: {
    engine: string;
    url_configured: boolean;
    status: string;
  };
  google_sheets: {
    configured: boolean;
    spreadsheet_id: string;
    status: string;
  };
  ai_provider: {
    provider: string;
    configured: boolean;
    status: string;
  };
  email_smtp: {
    configured: boolean;
    host: string;
    status: string;
  };
}
