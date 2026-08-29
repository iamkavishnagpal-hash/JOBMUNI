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
  AlertCircle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  TrendingUp,
  Award,
} from "lucide-react";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Selected job for Alignment Modal
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [alignmentData, setAlignmentData] = useState<any | null>(null);
  const [alignmentLoading, setAlignmentLoading] = useState(false);

  // Form state
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");

  const loadJobs = async () => {
    try {
      setLoading(true);
      const data = await api.getJobs();
      setJobs(data);
    } catch (err) {
      console.error("Failed to load jobs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const openAlignmentDrawer = async (job: Job) => {
    setSelectedJob(job);
    try {
      setAlignmentLoading(true);
      const data = await api.getJobAlignment(job.id);
      setAlignmentData(data);
    } catch (err) {
      console.error("Failed to fetch alignment:", err);
    } finally {
      setAlignmentLoading(false);
    }
  };

  const handleReevaluateAlignment = async () => {
    if (!selectedJob) return;
    try {
      setAlignmentLoading(true);
      const data = await api.evaluateJobAlignment(selectedJob.id);
      setAlignmentData(data);
      await loadJobs();
    } catch (err) {
      console.error("Failed to reevaluate alignment:", err);
    } finally {
      setAlignmentLoading(false);
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
      case "ACT_NOW":
        return <Badge variant="danger"><Flame className="w-3 h-3 mr-1 inline" />ACT NOW</Badge>;
      case "HIGH":
        return <Badge variant="success">HIGH FIT</Badge>;
      case "MEDIUM":
        return <Badge variant="indigo">MEDIUM</Badge>;
      default:
        return <Badge variant="outline">{tier}</Badge>;
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

  return (
    <div className="space-y-6">
      <Header
        title="Job Radar & Opportunity Engine"
        subtitle="Live Senior BI & Analytics opportunities aligned deterministically against SARASWATI Evidence Bank"
        actionButton={{
          label: "Ingest Opportunity (Paste JD)",
          onClick: () => setIsModalOpen(true),
          icon: <Plus className="w-4 h-4" />,
        }}
      />

      {loading ? (
        <div className="p-12 text-center text-gray-400 font-mono">Loading opportunities from database...</div>
      ) : jobs.length === 0 ? (
        <EmptyState
          icon={Radar}
          title="No Opportunities Ingested Yet"
          description="Job Radar continuously monitors configured sources. Ingest your first Senior BI / Analytics opportunity by pasting a job description."
          actionLabel="Ingest Job Description"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <Card
              key={job.id}
              hoverEffect
              onClick={() => openAlignmentDrawer(job)}
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
                      {job.final_score}
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
                </div>

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
                  <Target className="w-3 h-3" /> View ARJUNA Fit
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* ARJUNA JD Alignment Details Modal */}
      {selectedJob && (
        <Modal
          isOpen={!!selectedJob}
          onClose={() => {
            setSelectedJob(null);
            setAlignmentData(null);
          }}
          title={`ARJUNA Precision Alignment — ${selectedJob.company_name}`}
          maxWidth="xl"
        >
          {alignmentLoading || !alignmentData ? (
            <div className="p-8 text-center text-gray-400 font-mono text-xs">
              Calculating evidence-grounded alignment against SARASWATI...
            </div>
          ) : (
            <div className="space-y-5 text-xs">
              {/* Header Summary */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3.5 rounded-lg bg-surface-100 border border-border-subtle">
                <div>
                  <div className="text-sm font-bold text-white">{alignmentData.job_title}</div>
                  <div className="text-gray-400 font-mono text-[11px]">{alignmentData.company_name}</div>
                </div>
                <div className="flex items-center gap-2">
                  {getVerdictBadge(alignmentData.match_verdict)}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleReevaluateAlignment}
                    disabled={alignmentLoading}
                    className="flex items-center gap-1"
                  >
                    <RefreshCw className={`w-3 h-3 ${alignmentLoading ? "animate-spin" : ""}`} />
                    <span>Re-evaluate</span>
                  </Button>
                </div>
              </div>

              {/* 4 Multi-Dimension Coverage Gauges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
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

              {/* Explainable Reasoning Block */}
              {alignmentData.reasoning && (
                <div className="p-3.5 rounded-lg bg-surface-100 border border-border-subtle space-y-2">
                  <div className="font-semibold text-white text-xs flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-accent-indigo" />
                    Explainable Rationale & Recommended Action
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
                        {m.source_companies?.length > 0 && ` • Provenance: ${m.source_companies.join(", ")}`}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Missing Skills / Gaps */}
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
