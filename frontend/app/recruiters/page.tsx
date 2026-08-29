"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { api } from "@/lib/api";
import { Recruiter } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Users, Plus, Mail, Linkedin, Building2, Send } from "lucide-react";

export default function RecruitersPage() {
  const [recruiters, setRecruiters] = useState<Recruiter[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [companyName, setCompanyName] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("Technical Recruiter");
  const [email, setEmail] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [notes, setNotes] = useState("");

  const loadRecruiters = async () => {
    try {
      setLoading(true);
      const data = await api.getRecruiters();
      setRecruiters(data);
    } catch (err) {
      console.error("Failed to load recruiters", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecruiters();
  }, []);

  const handleCreateRecruiter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName || !name) return;
    try {
      setSubmitting(true);
      await api.createRecruiter({
        company_name: companyName,
        name,
        role,
        email: email || undefined,
        linkedin_url: linkedinUrl || undefined,
        notes: notes || undefined,
      });
      setIsModalOpen(false);
      setCompanyName("");
      setName("");
      setEmail("");
      setLinkedinUrl("");
      setNotes("");
      await loadRecruiters();
    } catch (err) {
      console.error("Failed to create recruiter", err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <Header
        title="Recruiter CRM & Outreach Paths"
        subtitle="Manage verified talent partners, engineering hiring managers, and active relationships"
        actionButton={{
          label: "Add Recruiter Contact",
          onClick: () => setIsModalOpen(true),
          icon: <Plus className="w-4 h-4" />,
        }}
      />

      {loading ? (
        <div className="p-12 text-center text-gray-400 font-mono">Loading recruiter relationships...</div>
      ) : recruiters.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No Recruiter Contacts Added"
          description="Track technical sourcers and engineering hiring managers for your target Senior BI & Analytics companies."
          actionLabel="Add Recruiter"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recruiters.map((recruiter) => (
            <Card key={recruiter.id} hoverEffect className="flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <h3 className="text-base font-semibold text-white">{recruiter.name}</h3>
                    <span className="text-xs font-mono text-gray-400 flex items-center gap-1 mt-0.5">
                      <Building2 className="w-3.5 h-3.5" />
                      {recruiter.company_name}
                    </span>
                  </div>
                  <Badge variant="indigo">{recruiter.relationship_status}</Badge>
                </div>

                <p className="text-xs text-gray-300 mb-4">{recruiter.role}</p>

                <div className="space-y-2 text-xs text-gray-400 font-mono">
                  {recruiter.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="w-3.5 h-3.5 text-gray-500" />
                      <span className="truncate">{recruiter.email}</span>
                    </div>
                  )}
                  {recruiter.linkedin_url && (
                    <div className="flex items-center gap-2">
                      <Linkedin className="w-3.5 h-3.5 text-gray-500" />
                      <a
                        href={recruiter.linkedin_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-accent-indigo hover:underline truncate"
                      >
                        LinkedIn Profile
                      </a>
                    </div>
                  )}
                </div>

                {recruiter.notes && (
                  <p className="text-xs text-gray-400 mt-3 p-2 rounded bg-surface-100 border border-border-subtle italic">
                    &ldquo;{recruiter.notes}&rdquo;
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-border-subtle flex items-center justify-between text-xs text-gray-500 font-mono mt-4">
                <span>Engagement: {recruiter.engagement_score}%</span>
                <span>Added {formatDate(recruiter.created_at)}</span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Add Recruiter Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Recruiter Contact">
        <form onSubmit={handleCreateRecruiter} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Company Name *</label>
            <input
              type="text"
              required
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Databricks"
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Recruiter Name *</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Sarah Jenkins"
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Role / Title</label>
            <input
              type="text"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Senior Tech Recruiter"
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="sarah.jenkins@example.com"
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">LinkedIn Profile URL</label>
            <input
              type="url"
              value={linkedinUrl}
              onChange={(e) => setLinkedinUrl(e.target.value)}
              placeholder="https://linkedin.com/in/..."
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1">Notes</label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Sourcing specifically for the Core Analytics & dbt team..."
              className="w-full px-3 py-2 rounded-lg bg-surface-100 border border-border-subtle text-white text-sm focus:outline-none focus:border-accent-indigo"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-border-subtle">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? "Saving..." : "Save Contact"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
