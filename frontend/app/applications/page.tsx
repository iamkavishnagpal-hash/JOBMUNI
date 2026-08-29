"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { api } from "@/lib/api";
import { Application } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Briefcase, CheckCircle2, Clock, Send } from "lucide-react";

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  const loadApplications = async () => {
    try {
      setLoading(true);
      const data = await api.getApplications();
      setApplications(data);
    } catch (err) {
      console.error("Failed to load applications", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApplications();
  }, []);

  const STAGES = [
    { key: "DISCOVERED", label: "Discovered" },
    { key: "SHORTLISTED", label: "Shortlisted" },
    { key: "READY_FOR_REVIEW", label: "Approval Gate" },
    { key: "APPLIED", label: "Applied" },
    { key: "INTERVIEWING", label: "Interviewing" },
    { key: "OFFER", label: "Offer" },
  ];

  return (
    <div>
      <Header
        title="Application Pipeline"
        subtitle="Track end-to-end lifecycle from qualification to offer without blind auto-apply"
      />

      {loading ? (
        <div className="p-12 text-center text-gray-400 font-mono">Loading application pipeline...</div>
      ) : applications.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No Active Applications"
          description="Applications move here when shortlisted from Job Radar or when tailored application packages are prepared."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3 overflow-x-auto">
          {STAGES.map((stage) => {
            const items = applications.filter((a) => a.status === stage.key);
            return (
              <div key={stage.key} className="bg-surface-50/60 border border-border-subtle rounded-xl p-3 flex flex-col min-w-[200px]">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-border-subtle">
                  <span className="text-xs font-semibold text-gray-300">{stage.label}</span>
                  <Badge variant="outline">{items.length}</Badge>
                </div>

                <div className="space-y-2 flex-1">
                  {items.map((app) => (
                    <Card key={app.id} className="p-3 bg-surface-100 border-border-subtle">
                      <div className="text-xs font-semibold text-white truncate">Job #{app.job_id.slice(0, 8)}</div>
                      <div className="text-[11px] font-mono text-emerald-400 mt-1">
                        Fit: {app.jd_alignment_score}%
                      </div>
                      <div className="text-[10px] text-gray-500 font-mono mt-2">
                        {formatDate(app.created_at)}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
