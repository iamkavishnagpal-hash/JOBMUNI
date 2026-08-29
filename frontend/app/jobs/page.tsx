"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import { Job } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import {
  Radar,
  Plus,
  Building2,
  MapPin,
  Flame,
  ShieldCheck,
  Target,
  DollarSign,
  TrendingUp,
  Award,
  CheckCircle2,
  XCircle,
  RefreshCw,
  HelpCircle,
  Zap,
  ArrowRight,
  Clock,
  Sparkles,
  AlertTriangle,
} from "lucide-react";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [tierFilter, setTierFilter] = useState<string>("ALL");

  // Selected job for Intelligence Modal
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [activeTab, setActiveTab] = useState<"PRIORITY" | "ALIGNMENT" | "COMPENSATION">("PRIORITY");
  const [priorityData, setPriorityData] = useState<any | null>(null);
  const [alignmentData, setAlignmentData] = useState<any | null>(null);
  const [compensationData, setCompensationData] = useState<any | null>(null);
  const [intelLoading, setIntelLoading] = useState(false);

  // Form state
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");

  const loadJobs = async () => {
    try {
      setLoading(true);
      const data = await api.getPrioritizedJobs(tierFilter !== "ALL" ? { tier_filter: tierFilter } : undefined);
      setJobs(data);
    } catch (err) {
      console.error("Failed to load jobs", err);
      // Fallback
      const fb = await api.getJobs();
      setJobs(fb);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, [tierFilter]);

  const openIntelModal = async (job: Job) => {
    setSelectedJob(job);
    setActiveTab("PRIORITY");
    try {
      setIntelLoading(true);
      const [prio, align, comp] = await Promise.all([
        api.getJobPriority(job.id),
        api.getJobAlignment(job.id),
        api.getJobCompensation(job.id),
      ]);
      setPriorityData(prio);
      setAlignmentData(align);
      setCompensationData(comp);
    } catch (err) {
      console.error("Failed to fetch intelligence:", err);
    } finally {
      setIntelLoading(false);
    }
  };

  const handleReevaluateIntel = async () => {
    if (!selectedJob) return;
    try {
      setIntelLoading(true);
      const [prio, align, comp] = await Promise.all([
        api.evaluateJobPriority(selectedJob.id),
        api.evaluateJobAlignment(selectedJob.id),
        api.evaluateJobCompensation(selectedJob.id),
      ]);
      setPriorityData(prio);
      setAlignmentData(align);
      setCompensationData(comp);
      await loadJobs();
    } catch (err) {
      console.error("Failed to reevaluate intelligence:", err);
    } finally {
      setIntelLoading(false);
    }
  };

  const handleParseJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName || !jobTitle || !rawText) return;
    try {
      setSubmitting(true);
      await api.parseJobManual({
        company_name: companyName,
        title: jobTitle,
        raw_text: rawText,
        source_url: sourceUrl || undefined,
      });
      setIsModalOpen(false);
      setCompanyName("");
      setJobTitle("");
      setRawText("");
      setSourceUrl("");
      await loadJobs();
    } catch (err) {
      console.error("Failed to parse job", err);
    } finally {
      setSubmitting(false);
    }
  };

  const getPriorityBadge = (tier: string) => {
    switch (tier) {
      case "CRITICAL":
      case "ACT_NOW":
        return <Badge variant="danger" className="font-bold"><Flame className="w-3 h-3 mr-1 inline" />CRITICAL PRIORITY</Badge>;
      case "HIGH":
        return <Badge variant="success" className="font-bold">HIGH PRIORITY</Badge>;
      case "MEDIUM":
        return <Badge variant="indigo">MEDIUM</Badge>;
      case "LOW":
        return <Badge variant="outline" className="text-gray-400">LOW</Badge>;
      default:
        return <Badge variant="outline" className="text-gray-500">{tier}</Badge>;
    }
  };

  const getVerdictBadge = (verdict: string) => {
    switch (verdict) {
      case "STRONG_MATCH":
        return <Badge variant="success">STRONG MATCH</Badge>;
      case "PARTIAL_MATCH":
        return <Badge variant="warning">PARTIAL MATCH</Badge>;
      case "WEAK_MATCH":
        return <Badge variant="danger">WEAK MATCH</Badge>;
      default:
        return <Badge variant="outline">INSUFFICIENT EVIDENCE</Badge>;
    }
  };

  const getCompTierBadge = (tier: string) => {
    switch (tier) {
      case "PREMIUM":
        return <Badge variant="success" className="bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold">PREMIUM COMP</Badge>;
      case "STRONG":
        return <Badge variant="indigo" className="font-bold">STRONG COMP</Badge>;
      case "ACCEPTABLE":
        return <Badge variant="outline" className="text-gray-300">ACCEPTABLE COMP</Badge>;
      case "LOW":
        return <Badge variant="danger">BELOW TARGET</Badge>;
      default:
        return <Badge variant="outline" className="text-gray-500">SALARY UNDISCLOSED</Badge>;
    }
  };

  const getActionBadge = (action: string) => {
    switch (action) {
      case "APPLY":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold">⚡ Apply Direct</span>;
      case "CONTACT_RECRUITER":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-mono font-bold">🎯 Outreach Recruiter</span>;
      case "PREPARE_RESUME":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-mono font-bold">📄 Tailor Resume</span>;
      case "REVIEW":
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-gray-500/20 text-gray-300 text-[10px] font-mono font-bold">🔍 Review Details</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-mono font-bold">🚫 Skip Role</span>;
    }
  };

  return (
    <div className="space-y-6">
      <Header
        title="Job Radar & Prioritization Engine"
        subtitle="Ranked Senior BI & Analytics opportunities evaluated deterministically by CHANAKYA, ARJUNA, and KUBERA"
        actionButton={{
          label: "Ingest Opportunity (Paste JD)",
          onClick: () => setIsModalOpen(true),
          icon: <Plus className="w-4 h-4" />,
        }}
      />

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-border-subtle pb-3">
        {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((tier) => (
          <button
            key={tier}
            onClick={() => setTierFilter(tier)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
              tierFilter === tier
                ? "bg-accent-indigo text-white font-bold shadow-sm"
                : "bg-surface-100 text-gray-400 hover:text-white"
            }`}
          >
            {tier === "ALL" ? "All Ranked" : `${tier} Priority`}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="p-12 text-center text-gray-400 font-mono text-xs">Loading prioritized opportunities from database...</div>
      ) : jobs.length === 0 ? (
        <EmptyState
          icon={Radar}
          title="No Opportunities Found"
          description="No opportunities match the selected priority filter. Ingest new opportunities or clear the filter."
          actionLabel="Ingest Job Description"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <Card
              key={job.id}
              hoverEffect
              onClick={() => openIntelModal(job)}
              className="flex flex-col justify-between cursor-pointer transition-all hover:border-accent-indigo/60"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <span className="text-xs font-mono text-gray-400 flex items-center gap-1">
                      <Building2 className="w-3.5 h-3.5" />
                      {job.company_name}
                    </span>
                    <h3 className="text-base font-semibold text-white mt-1 leading-snug">{job.title}</h3>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-xl font-bold font-mono text-emerald-400">
                      {job.priority_score || job.final_score}
                      <span className="text-xs text-gray-500 font-normal">/100</span>
                    </span>
                    {getPriorityBadge(job.priority_tier)}
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400 mb-3 font-mono">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {job.location} ({job.remote_type})
                  </span>
                  <span>•</span>
                  {job.match_verdict && (
                    <span>{getVerdictBadge(job.match_verdict)}</span>
                  )}
                  {job.compensation_tier && job.compensation_tier !== "UNKNOWN" && (
                    <span>{getCompTierBadge(job.compensation_tier)}</span>
                  )}
                </div>

                {job.recommended_action && (
                  <div className="mb-3 p-2 rounded bg-surface-200 border border-border-subtle flex items-center justify-between">
                    <span className="text-[11px] text-gray-400 font-mono">Next Best Action:</span>
                    {getActionBadge(job.recommended_action)}
                  </div>
                )}

                {job.skills && job.skills.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {job.skills.slice(0, 5).map((skill) => (
                      <Badge key={skill.id || skill.skill_name} variant="outline">
                        {skill.skill_name}
                      </Badge>
                    ))}
                    {job.skills.length > 5 && (
                      <span className="text-[10px] text-gray-500 font-mono self-center">
                        +{job.skills.length - 5} more
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-border-subtle flex items-center justify-between text-xs text-gray-500 font-mono">
                <span>First seen: {formatDate(job.first_seen_at)}</span>
                <span className="text-accent-indigo hover:underline flex items-center gap-1">
                  <Target className="w-3 h-3" /> View Intelligence
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Intelligence Modal (CHANAKYA, ARJUNA, KUBERA) */}
      {selectedJob && (
        <Modal
          isOpen={!!selectedJob}
          onClose={() => {
            setSelectedJob(null);
            setPriorityData(null);
            setAlignmentData(null);
            setCompensationData(null);
          }}
          title={`${selectedJob.title} — ${selectedJob.company_name}`}
          maxWidth="xl"
        >
          {intelLoading || !priorityData || !alignmentData || !compensationData ? (
            <div className="p-8 text-center text-gray-400 font-mono text-xs">
              Calculating evidence-grounded career intelligence...
            </div>
          ) : (
            <div className="space-y-5 text-xs">
              {/* Top Navigation Switcher */}
              <div className="flex flex-wrap items-center justify-between border-b border-border-subtle pb-3 gap-2">
                <div className="flex flex-wrap items-center gap-1.5">
                  <button
                    onClick={() => setActiveTab("PRIORITY")}
                    className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition-all ${
                      activeTab === "PRIORITY"
                        ? "bg-accent-indigo text-white shadow-sm font-semibold"
                        : "bg-surface-100 text-gray-400 hover:text-white"
                    }`}
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>CHANAKYA Priority</span>
                  </button>
                  <button
                    onClick={() => setActiveTab("ALIGNMENT")}
                    className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition-all ${
                      activeTab === "ALIGNMENT"
                        ? "bg-accent-indigo text-white shadow-sm font-semibold"
                        : "bg-surface-100 text-gray-400 hover:text-white"
                    }`}
                  >
                    <Target className="w-3.5 h-3.5" />
                    <span>ARJUNA Skill Fit</span>
                  </button>
                  <button
                    onClick={() => setActiveTab("COMPENSATION")}
                    className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition-all ${
                      activeTab === "COMPENSATION"
                        ? "bg-accent-indigo text-white shadow-sm font-semibold"
                        : "bg-surface-100 text-gray-400 hover:text-white"
                    }`}
                  >
                    <DollarSign className="w-3.5 h-3.5" />
                    <span>KUBERA Compensation</span>
                  </button>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleReevaluateIntel}
                  disabled={intelLoading}
                  className="flex items-center gap-1 text-[11px]"
                >
                  <RefreshCw className={`w-3 h-3 ${intelLoading ? "animate-spin" : ""}`} />
                  <span>Re-evaluate</span>
                </Button>
              </div>

              {/* TAB 1: CHANAKYA PRIORITY */}
              {activeTab === "PRIORITY" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3.5 rounded-lg bg-surface-100 border border-border-subtle">
                    <div>
                      <div className="font-bold text-white text-sm">CHANAKYA Decision & Prioritization</div>
                      <div className="text-gray-400 text-[11px]">{priorityData.company_name}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getPriorityBadge(priorityData.priority_tier)}
                    </div>
                  </div>

                  {/* 4 Prioritization Gauges */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-xl font-bold font-mono text-emerald-400">{priorityData.priority_score}</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Priority Score</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-xl font-bold font-mono text-amber-400">{priorityData.urgency_score}</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Urgency (Velocity)</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-xs font-bold font-mono text-cyan-400 truncate">{priorityData.actionability?.replace(/_/g, " ")}</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Actionability</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-xs font-bold font-mono text-accent-indigo">{priorityData.effort_level} EFFORT</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Execution Effort</div>
                    </div>
                  </div>

                  {/* Next Best Action Banner */}
                  <div className="p-3.5 rounded-lg bg-accent-indigo/10 border border-accent-indigo/30 space-y-1.5">
                    <div className="font-semibold text-accent-indigo flex items-center justify-between">
                      <span className="flex items-center gap-1.5">
                        <Zap className="w-4 h-4" /> Recommended Next Action
                      </span>
                      {getActionBadge(priorityData.recommended_action)}
                    </div>
                    <p className="text-gray-300 text-[11px] leading-relaxed">
                      {priorityData.reasoning?.action_rationale}
                    </p>
                  </div>

                  {/* Why this job is ranked here */}
                  <div className="p-3.5 rounded-lg bg-surface-100 border border-border-subtle space-y-2">
                    <div className="font-semibold text-white text-xs flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      Why Ranked Here
                    </div>
                    <p className="text-gray-300 leading-relaxed">{priorityData.reasoning?.why_ranked_here}</p>

                    {/* Positive Factors */}
                    {priorityData.positive_factors?.length > 0 && (
                      <div className="space-y-1 pt-1">
                        <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-bold">Positive Factors:</span>
                        <ul className="space-y-1 text-gray-300 text-[11px]">
                          {priorityData.positive_factors.map((f: string, idx: number) => (
                            <li key={idx} className="flex items-center gap-1.5">
                              <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                              <span>{f}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Negative Factors */}
                    {priorityData.negative_factors?.length > 0 && (
                      <div className="space-y-1 pt-1">
                        <span className="text-[10px] font-mono uppercase tracking-wider text-amber-400 font-bold">Negative / Gap Factors:</span>
                        <ul className="space-y-1 text-gray-400 text-[11px]">
                          {priorityData.negative_factors.map((f: string, idx: number) => (
                            <li key={idx} className="flex items-center gap-1.5">
                              <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                              <span>{f}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 2: ARJUNA ALIGNMENT */}
              {activeTab === "ALIGNMENT" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-surface-100 border border-border-subtle">
                    <div>
                      <div className="font-bold text-white text-xs">Skill & Evidence Alignment</div>
                      <div className="text-gray-400 text-[11px]">{selectedJob.company_name}</div>
                    </div>
                    <div>{getVerdictBadge(alignmentData.match_verdict)}</div>
                  </div>

                  {/* 4 Coverage Gauges */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-emerald-400">{alignmentData.required_coverage_pct}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Required Coverage</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-accent-indigo">{alignmentData.preferred_coverage_pct}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Preferred Coverage</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-amber-400">{alignmentData.evidence_coverage_pct}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Evidence Density</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-cyan-400">{alignmentData.experience_alignment_pct}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Seniority Fit</div>
                    </div>
                  </div>

                  {/* Explainable Rationale */}
                  {alignmentData.reasoning && (
                    <div className="p-3.5 rounded-lg bg-surface-100 border border-border-subtle space-y-2">
                      <div className="font-semibold text-white text-xs flex items-center gap-1.5">
                        <ShieldCheck className="w-4 h-4 text-accent-indigo" />
                        Explainable Rationale & Action
                      </div>
                      <p className="text-gray-300 leading-relaxed">{alignmentData.reasoning.summary}</p>
                      {alignmentData.reasoning.recommended_action && (
                        <div className="p-2 rounded bg-surface-200 text-[11px] text-emerald-300 font-mono">
                          Action: {alignmentData.reasoning.recommended_action}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Matched Required Skills */}
                  <div className="space-y-2">
                    <div className="font-semibold text-gray-300 flex items-center gap-1 text-[11px] uppercase tracking-wider">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      Matched Required Skills ({alignmentData.matched_required?.length || 0})
                    </div>
                    <div className="space-y-2">
                      {alignmentData.matched_required?.map((m: any, idx: number) => (
                        <div key={idx} className="p-2.5 rounded bg-surface-100 border border-border-subtle space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-white text-xs font-mono">{m.normalized_skill}</span>
                            <Badge variant="success" className="text-[10px]">
                              {m.evidence_count} Verified Record(s)
                            </Badge>
                          </div>
                          {m.top_metric && (
                            <div className="text-emerald-400 font-mono text-[11px] flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              <span>{m.top_metric}</span>
                            </div>
                          )}
                          <div className="text-[10px] text-gray-500 font-mono">
                            Evidence IDs: {m.evidence_ids?.slice(0, 2).join(", ")}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Missing Skills */}
                  {alignmentData.missing_required?.length > 0 && (
                    <div className="space-y-2">
                      <div className="font-semibold text-gray-300 flex items-center gap-1 text-[11px] uppercase tracking-wider">
                        <XCircle className="w-3.5 h-3.5 text-rose-400" />
                        Missing Required Skills ({alignmentData.missing_required.length})
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {alignmentData.missing_required.map((miss: any, idx: number) => (
                          <Badge key={idx} variant="danger">
                            {miss.normalized_skill || miss.requirement} (No Evidence)
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 3: KUBERA COMPENSATION */}
              {activeTab === "COMPENSATION" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-surface-100 border border-border-subtle">
                    <div>
                      <div className="font-bold text-white text-xs">Financial Compensation Evaluation</div>
                      <div className="text-gray-400 text-[11px]">
                        Disclosed: <span className="font-mono text-emerald-400">{compensationData.disclosed_salary?.formatted}</span>
                      </div>
                    </div>
                    <div>{getCompTierBadge(compensationData.compensation_tier)}</div>
                  </div>

                  {/* 4 Financial / Policy Gauges */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-emerald-400">{compensationData.salary_fit_score}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Salary Fit</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-accent-indigo">{compensationData.market_position_score}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Market Position</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-cyan-400">{compensationData.remote_value_score}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Remote Alignment</div>
                    </div>
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle text-center">
                      <div className="text-lg font-bold font-mono text-amber-400">{compensationData.location_value_score}%</div>
                      <div className="text-[10px] text-gray-400 mt-0.5">Location Value</div>
                    </div>
                  </div>

                  {/* Policy Comparison & Rationale */}
                  {compensationData.reasoning && (
                    <div className="p-3.5 rounded-lg bg-surface-100 border border-border-subtle space-y-2">
                      <div className="font-semibold text-white text-xs flex items-center gap-1.5">
                        <DollarSign className="w-4 h-4 text-emerald-400" />
                        Compensation Analysis & Policy Comparison
                      </div>
                      <p className="text-gray-300 leading-relaxed">{compensationData.reasoning.summary}</p>
                      <div className="p-2 rounded bg-surface-200 text-[11px] text-gray-300 font-mono">
                        Policy Target: {compensationData.reasoning.policy_comparison}
                      </div>
                      {compensationData.reasoning.recommended_action && (
                        <div className="p-2 rounded bg-surface-200 text-[11px] text-emerald-300 font-mono">
                          Action: {compensationData.reasoning.recommended_action}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Unknown Factors */}
                  {compensationData.reasoning?.unknown_factors?.length > 0 && (
                    <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle space-y-1.5">
                      <div className="font-semibold text-gray-400 flex items-center gap-1 text-[11px] uppercase tracking-wider">
                        <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                        Unknown Financial Factors ({compensationData.reasoning.unknown_factors.length})
                      </div>
                      <ul className="list-disc list-inside space-y-1 text-gray-400 text-[11px]">
                        {compensationData.reasoning.unknown_factors.map((unk: string, idx: number) => (
                          <li key={idx}>{unk}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </Modal>
      )}

      {/* Ingest Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Ingest Job Description" maxWidth="lg">
        <form onSubmit={handleParseJob} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1">Company Name *</label>
              <input
                type="text"
                required
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g. Snowflake"
                className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1">Job Title *</label>
              <input
                type="text"
                required
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Lead BI Engineer"
                className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Job Description Raw Text *</label>
            <textarea
              rows={6}
              required
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste full job description text here..."
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Source URL (Optional)</label>
            <input
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://..."
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={submitting}>
              {submitting ? "Ingesting..." : "Ingest & Parse Opportunity"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
