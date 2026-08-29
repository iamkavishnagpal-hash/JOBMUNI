import React from "react";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: number | string;
  subtext?: string;
  icon: LucideIcon;
  variant?: "default" | "emerald" | "amber" | "indigo" | "rose";
  onClick?: () => void;
}

export function StatCard({
  label,
  value,
  subtext,
  icon: Icon,
  variant = "default",
  onClick,
}: StatCardProps) {
  const iconColor = {
    default: "text-gray-400 bg-surface-200",
    emerald: "text-emerald-400 bg-emerald-950/60 border border-emerald-800/40",
    amber: "text-amber-400 bg-amber-950/60 border border-amber-800/40",
    indigo: "text-indigo-400 bg-indigo-950/60 border border-indigo-800/40",
    rose: "text-rose-400 bg-rose-950/60 border border-rose-800/40",
  };

  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-surface-50 border border-border-subtle rounded-xl p-5 flex flex-col justify-between relative overflow-hidden transition-all duration-150",
        onClick && "cursor-pointer hover:border-border-strong hover:bg-surface-100"
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">{label}</span>
        <div className={cn("p-2 rounded-lg", iconColor[variant])}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-3">
        <span className="text-2xl font-bold text-white font-mono">{value}</span>
        {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
      </div>
    </div>
  );
}
