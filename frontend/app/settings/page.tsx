"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { ScoringConfig, IntegrationsStatus } from "@/lib/types";
import { Sliders, Database, FileSpreadsheet, Bot, Mail, CheckCircle2, AlertCircle } from "lucide-react";

export default function SettingsPage() {
  const [config, setConfig] = useState<ScoringConfig | null>(null);
  const [integrations, setIntegrations] = useState<IntegrationsStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [skillWeight, setSkillWeight] = useState(25);
  const [seniorityWeight, setSeniorityWeight] = useState(15);
  const [domainWeight, setDomainWeight] = useState(15);
  const [compWeight, setCompWeight] = useState(15);
  const [freshnessWeight, setFreshnessWeight] = useState(10);
  const [signalWeight, setSignalWeight] = useState(10);
  const [recruiterWeight, setRecruiterWeight] = useState(10);

  const loadData = async () => {
    try {
      setLoading(true);
      const [cfg, integ] = await Promise.all([
        api.getScoringConfig(),
        api.getIntegrations(),
      ]);
      setConfig(cfg);
      setIntegrations(integ);

      setSkillWeight(Math.round(cfg.weight_skill_fit * 100));
      setSeniorityWeight(Math.round(cfg.weight_seniority * 100));
      setDomainWeight(Math.round(cfg.weight_domain * 100));
      setCompWeight(Math.round(cfg.weight_compensation * 100));
      setFreshnessWeight(Math.round(cfg.weight_freshness * 100));
      setSignalWeight(Math.round(cfg.weight_hiring_signal * 100));
      setRecruiterWeight(Math.round(cfg.weight_recruiter * 100));
    } catch (err) {
      console.error("Failed to load settings", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalWeight =
    skillWeight +
    seniorityWeight +
    domainWeight +
    compWeight +
    freshnessWeight +
    signalWeight +
    recruiterWeight;

  const handleSaveWeights = async (e: React.FormEvent) => {
    e.preventDefault();
    if (totalWeight !== 100) {
      setError(`Weights must sum exactly to 100%. Current sum: ${totalWeight}%`);
      return;
    }
    try {
      setSaving(true);
      setError(null);
      await api.updateScoringConfig({
        weight_skill_fit: skillWeight / 100,
        weight_seniority: seniorityWeight / 100,
        weight_domain: domainWeight / 100,
        weight_compensation: compWeight / 100,
        weight_freshness: freshnessWeight / 100,
        weight_hiring_signal: signalWeight / 100,
        weight_recruiter: recruiterWeight / 100,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to update scoring weights");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <Header
        title="Settings & System Configuration"
        subtitle="Manage configurable opportunity scoring algorithms, database credentials, and service integrations"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Opportunity Scoring Weights Tuning */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-accent-indigo" />
                Configurable Opportunity Scoring Weights
              </CardTitle>
            </CardHeader>

            <form onSubmit={handleSaveWeights} className="space-y-4">
              <p className="text-xs text-gray-400">
                Adjust how the Opportunity Engine evaluates incoming jobs for Senior Data & Analytics roles. Weights must sum to exactly 100%.
              </p>

              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                    <span>1. Skill Fit (SQL, Snowflake, dbt, Looker)</span>
                    <span className="text-white font-bold">{skillWeight}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    value={skillWeight}
                    onChange={(e) => setSkillWeight(Number(e.target.value))}
                    className="w-full accent-accent-indigo"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                    <span>2. Seniority & Title Alignment</span>
                    <span className="text-white font-bold">{seniorityWeight}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="40"
                    value={seniorityWeight}
                    onChange={(e) => setSeniorityWeight(Number(e.target.value))}
                    className="w-full accent-accent-indigo"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                    <span>3. BI & Analytics Domain Focus</span>
                    <span className="text-white font-bold">{domainWeight}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="40"
                    value={domainWeight}
                    onChange={(e) => setDomainWeight(Number(e.target.value))}
                    className="w-full accent-accent-indigo"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                    <span>4. Compensation & Remote/Location Fit</span>
                    <span className="text-white font-bold">{compWeight}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="40"
                    value={compWeight}
                    onChange={(e) => setCompWeight(Number(e.target.value))}
                    className="w-full accent-accent-indigo"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                    <span>5. Job Freshness & Verification Status</span>
                    <span className="text-white font-bold">{freshnessWeight}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="30"
                    value={freshnessWeight}
                    onChange={(e) => setFreshnessWeight(Number(e.target.value))}
                    className="w-full accent-accent-indigo"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                    <span>6. Hiring Signal Urgency (Active vs Ghost)</span>
                    <span className="text-white font-bold">{signalWeight}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="30"
                    value={signalWeight}
                    onChange={(e) => setSignalWeight(Number(e.target.value))}
                    className="w-full accent-accent-indigo"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                    <span>7. Recruiter Reachability / Presence</span>
                    <span className="text-white font-bold">{recruiterWeight}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="30"
                    value={recruiterWeight}
                    onChange={(e) => setRecruiterWeight(Number(e.target.value))}
                    className="w-full accent-accent-indigo"
                  />
                </div>
              </div>

              {/* Total Summary */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-100 border border-border-subtle font-mono text-xs">
                <span>Total Weight Allocation:</span>
                <span className={totalWeight === 100 ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                  {totalWeight}% {totalWeight === 100 ? "✓ (Valid)" : "✗ (Must be 100%)"}
                </span>
              </div>

              {error && (
                <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800/40 text-rose-300 text-xs">
                  {error}
                </div>
              )}

              {saveSuccess && (
                <div className="p-3 rounded-lg bg-emerald-950/60 border border-emerald-800/40 text-emerald-300 text-xs flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" /> Scoring configuration saved successfully.
                </div>
              )}

              <Button type="submit" variant="primary" size="md" disabled={saving || totalWeight !== 100}>
                {saving ? "Saving..." : "Save Configured Weights"}
              </Button>
            </form>
          </Card>
        </div>

        {/* Integration Status Pane */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Service Status & Boundary</CardTitle>
            </CardHeader>
            <div className="space-y-3 font-mono text-xs">
              {/* Database */}
              <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-300 flex items-center gap-1.5 font-sans font-medium">
                    <Database className="w-3.5 h-3.5 text-accent-indigo" />
                    Database
                  </span>
                  <Badge variant="success">CONNECTED</Badge>
                </div>
                <div className="text-gray-400 text-[11px]">
                  Engine: {integrations?.database?.engine || "sqlite (local cache)"}
                </div>
              </div>

              {/* Google Sheets */}
              <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-300 flex items-center gap-1.5 font-sans font-medium">
                    <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                    Google Sheets Adapter
                  </span>
                  <Badge variant={integrations?.google_sheets?.configured ? "success" : "outline"}>
                    {integrations?.google_sheets?.status || "NOT_CONFIGURED"}
                  </Badge>
                </div>
                <div className="text-gray-400 text-[11px]">
                  Sheet: {integrations?.google_sheets?.spreadsheet_id || "Not configured yet"}
                </div>
              </div>

              {/* AI Engine */}
              <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-300 flex items-center gap-1.5 font-sans font-medium">
                    <Bot className="w-3.5 h-3.5 text-accent-indigo" />
                    AI Gateway
                  </span>
                  <Badge variant="indigo">{integrations?.ai_provider?.status || "READY"}</Badge>
                </div>
                <div className="text-gray-400 text-[11px]">
                  Provider: {integrations?.ai_provider?.provider || "Offline Heuristic Fallback"}
                </div>
              </div>

              {/* Email / SMTP */}
              <div className="p-3 rounded-lg bg-surface-100 border border-border-subtle">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-gray-300 flex items-center gap-1.5 font-sans font-medium">
                    <Mail className="w-3.5 h-3.5 text-amber-400" />
                    Outbound SMTP
                  </span>
                  <Badge variant={integrations?.email_smtp?.configured ? "success" : "outline"}>
                    {integrations?.email_smtp?.status || "NOT_CONFIGURED"}
                  </Badge>
                </div>
                <div className="text-gray-400 text-[11px]">
                  Host: {integrations?.email_smtp?.host || "Not configured yet"}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
