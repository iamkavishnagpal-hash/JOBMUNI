"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import { EvidenceItem, SkillsSummary } from "@/lib/types";
import {
  ShieldCheck,
  Plus,
  Search,
  Sparkles,
  Award,
  Layers,
  ChevronDown,
  ChevronUp,
  Building,
  TrendingUp,
  Cpu,
  Trash2,
} from "lucide-react";

const CATEGORIES = [
  { id: "ALL", label: "All Items" },
  { id: "TECH_SKILL", label: "Tech Skills" },
  { id: "ARCHITECTURE_PROJECT", label: "Architecture" },
  { id: "BUSINESS_IMPACT", label: "Business Impact" },
  { id: "LEADERSHIP_MANAGEMENT", label: "Leadership" },
  { id: "CERTIFICATION", label: "Certifications" },
];

export default function EvidenceBankPage() {
  const [items, setItems] = useState<EvidenceItem[]>([]);
  const [summary, setSummary] = useState<SkillsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // New evidence form
  const [newCategory, setNewCategory] = useState("TECH_SKILL");
  const [newSkill, setNewSkill] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [newText, setNewText] = useState("");
  const [newMetric, setNewMetric] = useState("");
  const [newCompany, setNewCompany] = useState("");
  const [newSituation, setNewSituation] = useState("");
  const [newAction, setNewAction] = useState("");
  const [newResult, setNewResult] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const loadEvidence = async () => {
    try {
      setLoading(true);
      const [evidenceList, sum] = await Promise.all([
        api.getEvidenceItems({
          category: selectedCategory === "ALL" ? undefined : selectedCategory,
          search: searchQuery || undefined,
        }),
        api.getSkillsSummary(),
      ]);
      setItems(evidenceList);
      setSummary(sum);
    } catch (err) {
      console.error("Failed to load evidence bank:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvidence();
  }, [selectedCategory, searchQuery]);

  const handleSeed = async () => {
    try {
      setSeeding(true);
      await api.seedEvidenceBank();
      await loadEvidence();
    } catch (err) {
      console.error("Seeding error:", err);
    } finally {
      setSeeding(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!newSkill || !newTitle || !newText) {
      setFormError("Skill, title, and descriptive evidence text are required.");
      return;
    }
    if (newText.length < 10) {
      setFormError("Evidence description must be at least 10 characters.");
      return;
    }

    try {
      await api.createEvidenceItem({
        category: newCategory,
        skill_or_tool: newSkill,
        title: newTitle,
        evidence_text: newText,
        quant_metric: newMetric || undefined,
        source_company: newCompany || undefined,
        situation: newSituation || undefined,
        action: newAction || undefined,
        result: newResult || undefined,
        tags: [newSkill],
      });
      setIsAddModalOpen(false);
      // Reset form
      setNewTitle("");
      setNewSkill("");
      setNewText("");
      setNewMetric("");
      setNewCompany("");
      setNewSituation("");
      setNewAction("");
      setNewResult("");
      await loadEvidence();
    } catch (err: any) {
      setFormError(err.message || "Failed to create evidence item");
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to remove this evidence record?")) {
      await api.deleteEvidenceItem(id);
      await loadEvidence();
    }
  };

  return (
    <div className="space-y-6">
      <Header
        title="Candidate Evidence Bank (SARASWATI)"
        subtitle="Ground truth repository for verified skills, quantifiable metrics, and STAR project achievements (Zero AI Hallucinations)"
      />

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-accent-indigo/10 text-accent-indigo">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xl font-bold text-white">{summary?.total_skills || 0}</div>
            <div className="text-xs text-gray-400">Verified Competencies</div>
          </div>
        </Card>

        <Card className="p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xl font-bold text-white">{summary?.total_evidence_items || 0}</div>
            <div className="text-xs text-gray-400">Backed Evidence Records</div>
          </div>
        </Card>

        <Card className="p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xl font-bold text-white">100%</div>
            <div className="text-xs text-gray-400">Ground Truth Confidence</div>
          </div>
        </Card>
      </div>

      {/* Control Bar: Search, Category Tabs, Add Button */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedCategory === cat.id
                  ? "bg-accent-indigo text-white font-semibold shadow-sm"
                  : "bg-surface-100 text-gray-400 hover:text-gray-200 border border-border-subtle"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <div className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-500" />
            <input
              type="text"
              placeholder="Search skills or metrics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-surface-100 border border-border-subtle rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <Button variant="primary" size="sm" onClick={() => setIsAddModalOpen(true)} className="flex items-center gap-1.5">
            <Plus className="w-3.5 h-3.5" />
            <span>Add Evidence</span>
          </Button>

          {items.length === 0 && (
            <Button variant="outline" size="sm" onClick={handleSeed} disabled={seeding} className="flex items-center gap-1.5 text-xs">
              <Sparkles className="w-3.5 h-3.5 text-accent-indigo" />
              <span>{seeding ? "Seeding..." : "Seed Default Bank"}</span>
            </Button>
          )}
        </div>
      </div>

      {/* Evidence Items List */}
      {loading ? (
        <div className="p-12 text-center text-gray-500 text-sm">Loading Candidate Evidence Bank...</div>
      ) : items.length === 0 ? (
        <Card className="p-8 text-center space-y-3 border-dashed">
          <Layers className="w-8 h-8 text-gray-500 mx-auto" />
          <h3 className="text-sm font-semibold text-white">No Evidence Items Found</h3>
          <p className="text-xs text-gray-400 max-w-md mx-auto">
            Populate your Evidence Bank with verified STAR bullet points and quantifiable metrics to ground all future JD match scoring.
          </p>
          <Button variant="primary" size="sm" onClick={handleSeed} disabled={seeding}>
            Seed Default Senior BI Competencies
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {items.map((item) => {
            const isExpanded = expandedId === item.id;
            return (
              <Card key={item.id} className="p-5 space-y-3 transition-all hover:border-border-strong">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="indigo" className="font-mono font-bold">
                        {item.skill_or_tool}
                      </Badge>
                      <Badge variant="outline" className="text-[10px]">
                        {item.category.replace("_", " ")}
                      </Badge>
                      {item.source_company && (
                        <span className="text-xs text-gray-400 flex items-center gap-1">
                          <Building className="w-3 h-3 text-gray-500" />
                          {item.source_company}
                        </span>
                      )}
                    </div>
                    <h3 className="text-sm font-semibold text-white mt-1">{item.title}</h3>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-auto">
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : item.id)}
                      className="p-1.5 text-xs text-gray-400 hover:text-white flex items-center gap-1 rounded bg-surface-200"
                    >
                      <span>{isExpanded ? "Hide STAR" : "View STAR"}</span>
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-1.5 text-gray-500 hover:text-rose-400 rounded bg-surface-200"
                      title="Delete Evidence"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Metric Callout */}
                {item.quant_metric && (
                  <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-medium">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>{item.quant_metric}</span>
                  </div>
                )}

                {/* Evidence Text Body */}
                <p className="text-xs text-gray-300 leading-relaxed">{item.evidence_text}</p>

                {/* Collapsible STAR Breakdown */}
                {isExpanded && (item.situation || item.action || item.result) && (
                  <div className="mt-3 p-3.5 rounded-lg bg-surface-100 border border-border-subtle space-y-2.5 text-xs">
                    <div className="font-semibold text-accent-indigo text-[11px] uppercase tracking-wider">
                      Structured STAR Context
                    </div>
                    {item.situation && (
                      <div>
                        <span className="font-bold text-gray-300">Situation: </span>
                        <span className="text-gray-400">{item.situation}</span>
                      </div>
                    )}
                    {item.task && (
                      <div>
                        <span className="font-bold text-gray-300">Task: </span>
                        <span className="text-gray-400">{item.task}</span>
                      </div>
                    )}
                    {item.action && (
                      <div>
                        <span className="font-bold text-gray-300">Action: </span>
                        <span className="text-gray-400">{item.action}</span>
                      </div>
                    )}
                    {item.result && (
                      <div>
                        <span className="font-bold text-emerald-400">Result: </span>
                        <span className="text-gray-300 font-medium">{item.result}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Tags List */}
                {item.tags && item.tags.length > 0 && (
                  <div className="flex items-center gap-1.5 flex-wrap pt-1">
                    {item.tags.map((tag, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded bg-surface-200 text-[10px] font-mono text-gray-400">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* Add Evidence Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-lg p-6 rounded-xl bg-surface-50 border border-border-strong space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-border-subtle pb-3">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-accent-indigo" />
                Add Ground Truth Evidence Record
              </h2>
              <button onClick={() => setIsAddModalOpen(false)} className="text-gray-400 hover:text-white text-xs">
                ✕
              </button>
            </div>

            {formError && (
              <div className="p-2.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-400 mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full p-2 rounded bg-surface-100 border border-border-subtle text-white focus:outline-none focus:border-accent-indigo"
                  >
                    <option value="TECH_SKILL">Tech Skill</option>
                    <option value="ARCHITECTURE_PROJECT">Architecture Project</option>
                    <option value="BUSINESS_IMPACT">Business Impact</option>
                    <option value="LEADERSHIP_MANAGEMENT">Leadership</option>
                    <option value="CERTIFICATION">Certification</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-1">Primary Skill / Tool *</label>
                  <input
                    type="text"
                    placeholder="e.g. Snowflake, dbt, SQL"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    required
                    className="w-full p-2 rounded bg-surface-100 border border-border-subtle text-white focus:outline-none focus:border-accent-indigo"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Headline Title *</label>
                <input
                  type="text"
                  placeholder="e.g. Enterprise Snowflake Multi-Cluster Cost Optimization"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  className="w-full p-2 rounded bg-surface-100 border border-border-subtle text-white focus:outline-none focus:border-accent-indigo"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-400 mb-1">Quantified Metric</label>
                  <input
                    type="text"
                    placeholder="e.g. $140k/yr cloud cost savings"
                    value={newMetric}
                    onChange={(e) => setNewMetric(e.target.value)}
                    className="w-full p-2 rounded bg-surface-100 border border-border-subtle text-white focus:outline-none focus:border-accent-indigo"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-1">Source Company</label>
                  <input
                    type="text"
                    placeholder="e.g. Enterprise Analytics Corp"
                    value={newCompany}
                    onChange={(e) => setNewCompany(e.target.value)}
                    className="w-full p-2 rounded bg-surface-100 border border-border-subtle text-white focus:outline-none focus:border-accent-indigo"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Full Evidence Claim / Description *</label>
                <textarea
                  rows={3}
                  placeholder="Detail your exact technical contribution and measurable outcome..."
                  value={newText}
                  onChange={(e) => setNewText(e.target.value)}
                  required
                  className="w-full p-2 rounded bg-surface-100 border border-border-subtle text-white focus:outline-none focus:border-accent-indigo"
                />
              </div>

              {/* STAR Inputs */}
              <div className="p-3 rounded bg-surface-100 border border-border-subtle space-y-2">
                <span className="font-semibold text-gray-300 text-[11px]">STAR Breakdown (Optional)</span>
                <input
                  type="text"
                  placeholder="Situation: Context or challenge..."
                  value={newSituation}
                  onChange={(e) => setNewSituation(e.target.value)}
                  className="w-full p-1.5 rounded bg-surface-200 border border-border-subtle text-white text-[11px]"
                />
                <input
                  type="text"
                  placeholder="Action: Exact technical decisions taken..."
                  value={newAction}
                  onChange={(e) => setNewAction(e.target.value)}
                  className="w-full p-1.5 rounded bg-surface-200 border border-border-subtle text-white text-[11px]"
                />
                <input
                  type="text"
                  placeholder="Result: Business value delivered..."
                  value={newResult}
                  onChange={(e) => setNewResult(e.target.value)}
                  className="w-full p-1.5 rounded bg-surface-200 border border-border-subtle text-white text-[11px]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-border-subtle">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsAddModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm">
                  Save Ground Truth Record
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
