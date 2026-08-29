"use client";
import React from "react";
import { Header } from "@/components/layout/Header";
import { EmptyState } from "@/components/ui/EmptyState";
import { Calendar, Sparkles, BookOpen } from "lucide-react";

export default function InterviewsPage() {
  return (
    <div>
      <Header
        title="Interview Assistant & Memory"
        subtitle="Contextual SQL & BI technical case prep, behavioral STAR frameworks, and post-round notes"
      />

      <EmptyState
        icon={Calendar}
        title="No Scheduled Interviews"
        description="Interview prep modules and memory logs activate when an application advances to the interview stage."
      />
    </div>
  );
}
