"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import { Job } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Radar, Plus, Sparkles, Building2, MapPin, CheckCircle, Flame } from "lucide-react";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

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

  return (
    <div>
      <Header
        title="Job Radar & Opportunity Engine"
        subtitle="Ingested Senior Data & Analytics opportunities evaluated by configurable fit weights"
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
            <Card key={job.id} hoverEffect className="flex flex-col justify-between">
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

                <div className="flex flex-wrap gap-2 text-xs text-gray-400 mb-4 font-mono">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {job.location} ({job.remote_type})
                  </span>
                  <span>•</span>
                  <span>Signal: {job.hiring_signal_score}% ({job.hiring_signal_tier})</span>
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
                <span className="text-emerald-400">{job.status}</span>
              </div>
            </Card>
          ))}
        </div>
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
            <label className="block text-xs font-medium text-gray-300 mb-1">Posting Source URL (Optional)</label>
            <input
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://..."
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Raw Job Description Text *</label>
            <textarea
              required
              rows={8}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste the full job description here (responsibilities, required skills, data stack, etc.)..."
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm font-mono focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? "Analyzing & Scoring..." : "Score & Ingest Opportunity"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
