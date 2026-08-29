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
  canonical_url?: string;
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
  status: "ACTIVE" | "STALE" | "CLOSED" | "INACTIVE" | "UNKNOWN";
  verification_status: "ACTIVE" | "INACTIVE" | "UNKNOWN" | "ERROR";
  verification_reason?: string;
  verification_error?: string;
  verification_http_status?: number;
  ghost_signal_score: number;
  ghost_signal_reasons: string[];
  ghost_status: "ACTIVE" | "STALE" | "LIKELY_INACTIVE" | "UNKNOWN";
  freshness_conf: number;
  hiring_signal_score: number;
  hiring_signal_tier: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  final_score: number;
  priority_tier: "ACT_NOW" | "HIGH" | "MEDIUM" | "NURTURE" | "IGNORE";
  score_breakdown: Record<string, any>;
  match_verdict?: "STRONG_MATCH" | "PARTIAL_MATCH" | "WEAK_MATCH" | "INSUFFICIENT_EVIDENCE" | string;
  required_coverage_pct?: number;
  preferred_coverage_pct?: number;
  evidence_coverage_pct?: number;
  experience_alignment_pct?: number;
  alignment_json?: any;
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
  hiring_authority_tier: string;
  engagement_score?: number;
  last_contacted_at?: string;
  notes?: string;
  created_at: string;
}

export interface Application {
  id: string;
  job_id: string;
  job_title?: string;
  company_name?: string;
  stage: string;
  status?: string;
  jd_alignment_score?: number;
  applied_date?: string;
  target_salary_offered?: number;
  notes?: string;
  created_at: string;
}

export interface ApprovalRequest {
  id: string;
  request_type?: "OUTREACH_EMAIL" | "LINKEDIN_MESSAGE" | "RESUME_CUSTOMIZATION" | "AUTONOMOUS_ACTION";
  action_type?: string;
  title: string;
  summary: string;
  reason?: string;
  proposed_content?: {
    subject?: string;
    body?: string;
    recipient?: string;
    [key: string]: any;
  };
  generated_content?: {
    subject?: string;
    body?: string;
    recipient?: string;
    [key: string]: any;
  };
  supporting_evidence?: any[];
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

export interface EvidenceItem {
  id: string;
  profile_id: string;
  category: "TECH_SKILL" | "BUSINESS_IMPACT" | "ARCHITECTURE_PROJECT" | "LEADERSHIP_MANAGEMENT" | "CERTIFICATION";
  skill_or_tool: string;
  title: string;
  evidence_text: string;
  situation?: string;
  task?: string;
  action?: string;
  result?: string;
  quant_metric?: string;
  source_company?: string;
  timeframe_start?: string;
  timeframe_end?: string;
  tags: string[];
  confidence: number;
  verified_by_user: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SkillSummaryItem {
  skill_name: string;
  evidence_count: number;
  categories: string[];
  top_metrics: string[];
  evidence_ids: string[];
}

export interface SkillsSummary {
  total_skills: number;
  total_evidence_items: number;
  skills: SkillSummaryItem[];
}
