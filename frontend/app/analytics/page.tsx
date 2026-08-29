"use client";
import React from "react";
import { Header } from "@/components/layout/Header";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { BarChart3, TrendingUp, Layers, Target } from "lucide-react";

export default function AnalyticsPage() {
  return (
    <div>
      <Header
        title="Career Funnel & Conversion Intelligence"
        subtitle="End-to-end telemetry across discovery, recruiter reply rates, interview transitions, and A/B tests"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-accent-indigo" />
              Full Funnel Progression
            </CardTitle>
          </CardHeader>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between p-2 rounded bg-surface-100 border border-border-subtle">
              <span className="text-gray-400">1. Jobs Discovered</span>
              <span className="text-white font-bold">0</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-100 border border-border-subtle">
              <span className="text-gray-400">2. Qualified (&gt;75 Score)</span>
              <span className="text-white font-bold">0</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-100 border border-border-subtle">
              <span className="text-gray-400">3. Recruiter Outreach Sent</span>
              <span className="text-white font-bold">0</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-100 border border-border-subtle">
              <span className="text-gray-400">4. Recruiter Replies Received</span>
              <span className="text-white font-bold">0</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-surface-100 border border-border-subtle">
              <span className="text-gray-400">5. Interviews Conducted</span>
              <span className="text-white font-bold">0</span>
            </div>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-4 h-4 text-emerald-400" />
              A/B Experiment Matrix
            </CardTitle>
          </CardHeader>
          <div className="p-6 text-center text-sm text-gray-400">
            No active experiments running yet. Experiment tracking measures outreach subject lines and tailored resume format conversion rates.
          </div>
        </Card>
      </div>
    </div>
  );
}
