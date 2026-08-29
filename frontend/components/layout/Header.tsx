"use client";
import React from "react";
import { Sparkles, Terminal, Bell } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface HeaderProps {
  title: string;
  subtitle?: string;
  actionButton?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
}

export function Header({ title, subtitle, actionButton }: HeaderProps) {
  return (
    <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border-subtle mb-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">{title}</h1>
        {subtitle && <p className="text-xs sm:text-sm text-gray-400 mt-1">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {actionButton && (
          <Button onClick={actionButton.onClick} variant="primary" size="sm">
            {actionButton.icon}
            {actionButton.label}
          </Button>
        )}
      </div>
    </header>
  );
}
