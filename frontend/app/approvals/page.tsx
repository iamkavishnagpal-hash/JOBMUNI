"use client";
import React, { useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { api } from "@/lib/api";
import { ApprovalRequest } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { ShieldCheck, Check, X, ShieldAlert, FileText, Send } from "lucide-react";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.getApprovals("PENDING");
      setApprovals(data);
    } catch (err) {
      console.error("Failed to load approvals", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleDecision = async (id: string, decision: "APPROVE" | "REJECT") => {
    try {
      setActionLoading(id);
      await api.decideApproval(id, decision);
      await loadApprovals();
    } catch (err) {
      console.error("Decision failed", err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div>
      <Header
        title="Approval Center (Human-in-the-Loop Gate)"
        subtitle="Level 2 Autonomy: All outgoing emails, applications, and external messages strictly require user review"
      />

      {/* Autonomy Level Warning */}
      <div className="mb-6 p-4 rounded-xl bg-surface-50 border border-border-subtle flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-2 text-amber-400">
          <ShieldAlert className="w-4 h-4" />
          <span>AUTONOMY POLICY LEVEL 2 ENFORCED: Zero blind external dispatch</span>
        </div>
        <Badge variant="warning">STRICT HUMAN GATE</Badge>
      </div>

      {loading ? (
        <div className="p-12 text-center text-gray-400 font-mono">Loading approval queue...</div>
      ) : approvals.length === 0 ? (
        <EmptyState
          icon={ShieldCheck}
          title="Approval Queue is Clear"
          description="No outbound communications or applications pending your authorization. As background workers generate drafts, they will appear here for review."
        />
      ) : (
        <div className="space-y-4">
          {approvals.map((req) => (
            <Card key={req.id} className="border-amber-500/30 bg-surface-50">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border-subtle">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="warning">{req.action_type}</Badge>
                    <span className="text-xs font-mono text-gray-400">Queued {formatDate(req.created_at)}</span>
                  </div>
                  <h3 className="text-base font-semibold text-white">{req.title}</h3>
                  <p className="text-xs text-gray-400 mt-1">{req.reason}</p>
                </div>

                <div className="flex items-center gap-2 self-end md:self-center">
                  <Button
                    variant="danger"
                    size="sm"
                    disabled={actionLoading === req.id}
                    onClick={() => handleDecision(req.id, "REJECT")}
                  >
                    <X className="w-3.5 h-3.5 mr-1" />
                    Reject
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    disabled={actionLoading === req.id}
                    onClick={() => handleDecision(req.id, "APPROVE")}
                  >
                    <Check className="w-3.5 h-3.5 mr-1" />
                    Approve & Dispatch
                  </Button>
                </div>
              </div>

              {/* Draft payload preview */}
              <div className="mt-4 p-3 rounded-lg bg-surface-100 border border-border-subtle font-mono text-xs text-gray-300">
                <div className="font-semibold text-white mb-2">Generated Draft Payload:</div>
                <div className="text-gray-400 mb-1">Subject: {req.generated_content?.subject || "N/A"}</div>
                <div className="whitespace-pre-wrap text-gray-300 bg-background/50 p-2.5 rounded border border-border-subtle mt-2">
                  {req.generated_content?.body || JSON.stringify(req.generated_content, null, 2)}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
