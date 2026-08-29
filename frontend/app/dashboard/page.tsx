"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { StatCard } from "@/components/ui/StatCard";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { DashboardSummary } from "@/lib/types";
import {
  Flame,
  MessageSquareReply,
  Clock,
  ShieldAlert,
  Calendar,
  Compass,
  ArrowRight,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardSummary();
      setSummary(data);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  return (
    <div>
      <Header
        title="Executive Command Center"
        subtitle="Operational cockpit for Senior Data, BI & Analytics opportunities"
        actionButton={{
          label: "Refresh Metrics",
          onClick: loadSummary,
          icon: <RefreshCw className="w-3.5 h-3.5" />,
        }}
      />

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-950/60 border border-rose-800/40 text-rose-300 text-sm flex items-center justify-between">
          <span>Backend connection notice: {error}. Backend is starting or offline.</span>
          <Button variant="danger" size="sm" onClick={loadSummary}>
            Retry
          </Button>
        </div>
      )}

      {/* Top Actionable Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <StatCard
          label="Urgent Act-Now"
          value={summary?.urgent_opportunities_count ?? 0}
          subtext="High fit (<48h fresh)"
          icon={Flame}
          variant="emerald"
        />
        <StatCard
          label="Recruiter Replies"
          value={summary?.recruiter_replies_count ?? 0}
          subtext="Pending review"
          icon={MessageSquareReply}
          variant="indigo"
        />
        <StatCard
          label="Follow-Ups Due"
          value={summary?.followups_due_count ?? 0}
          subtext="Cadence alerts"
          icon={Clock}
          variant="amber"
        />
        <StatCard
          label="Approvals Queue"
          value={summary?.approvals_pending_count ?? 0}
          subtext="Human gate required"
          icon={ShieldAlert}
          variant="amber"
        />
        <StatCard
          label="Interviews"
          value={summary?.interviews_this_week_count ?? 0}
          subtext="Active pipeline"
          icon={Calendar}
          variant="default"
        />
      </div>

      {/* Career GPS Recommendation Banner */}
      <Card className="mb-8 bg-gradient-to-r from-surface-50 to-surface-100 border-accent-indigo/30">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-accent-indigo/20 text-accent-indigo border border-accent-indigo/30 mt-0.5">
              <Compass className="w-6 h-6 animate-spin-slow" />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <Badge variant="indigo">CAREER GPS</Badge>
                <span className="text-xs font-mono text-gray-400">Today&apos;s Recommended Action</span>
              </div>
              <h3 className="text-sm sm:text-base font-semibold text-white break-words">
                {summary?.career_gps_top_action?.title || "Ingest and evaluate active Senior BI opportunities"}
              </h3>
              <p className="text-xs sm:text-sm text-gray-400 mt-1 max-w-2xl">
                {summary?.career_gps_top_action?.reason ||
                  "Configure ingestion sources or paste target job descriptions to compute alignment."}
              </p>
            </div>
          </div>
          <Link href={summary?.career_gps_top_action?.cta_route || "/jobs"}>
            <Button variant="primary" size="md">
              {summary?.career_gps_top_action?.cta_label || "Go to Job Radar"}
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
      </Card>

      {/* Funnel Bottleneck Diagnostic & Live Modules Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              Funnel Conversion Diagnostic
            </CardTitle>
          </CardHeader>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-surface-100 border border-border-subtle">
              <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                <span>System Diagnostic</span>
                <Badge variant="success">HEALTHY</Badge>
              </div>
              <p className="text-sm text-gray-200 mt-1">
                {summary?.funnel_bottleneck || "No bottlenecks detected. Keep applying to high-signal opportunities."}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle">
                <span className="text-gray-400 block mb-1">Active Applications</span>
                <span className="text-lg font-mono font-bold text-white">
                  {summary?.active_applications_count ?? 0}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle">
                <span className="text-gray-400 block mb-1">Autonomy Guard</span>
                <span className="text-xs font-mono font-bold text-amber-400">LEVEL 2 ACTIVE</span>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Execution Shortcuts</CardTitle>
          </CardHeader>
          <div className="grid grid-cols-2 gap-3">
            <Link href="/jobs" className="p-3.5 rounded-xl bg-surface-100 hover:bg-surface-200 border border-border-subtle transition-colors flex flex-col justify-between">
              <span className="text-xs font-medium text-gray-400">Ingest Opportunity</span>
              <span className="text-sm font-semibold text-white mt-2">Paste New JD &rarr;</span>
            </Link>
            <Link href="/approvals" className="p-3.5 rounded-xl bg-surface-100 hover:bg-surface-200 border border-border-subtle transition-colors flex flex-col justify-between">
              <span className="text-xs font-medium text-gray-400">Human Approval Gate</span>
              <span className="text-sm font-semibold text-white mt-2">Review Outgoing &rarr;</span>
            </Link>
            <Link href="/recruiters" className="p-3.5 rounded-xl bg-surface-100 hover:bg-surface-200 border border-border-subtle transition-colors flex flex-col justify-between">
              <span className="text-xs font-medium text-gray-400">Recruiter CRM</span>
              <span className="text-sm font-semibold text-white mt-2">Manage Contacts &rarr;</span>
            </Link>
            <Link href="/settings" className="p-3.5 rounded-xl bg-surface-100 hover:bg-surface-200 border border-border-subtle transition-colors flex flex-col justify-between">
              <span className="text-xs font-medium text-gray-400">Scoring Weights</span>
              <span className="text-sm font-semibold text-white mt-2">Tune Algorithms &rarr;</span>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
