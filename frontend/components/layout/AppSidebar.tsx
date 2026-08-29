"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Radar,
  Users,
  Briefcase,
  Calendar,
  BarChart3,
  CheckCircle2,
  Settings,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Job Radar", href: "/jobs", icon: Radar },
  { label: "Recruiter CRM", href: "/recruiters", icon: Users },
  { label: "Applications", href: "/applications", icon: Briefcase },
  { label: "Interviews", href: "/interviews", icon: Calendar },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Approval Center", href: "/approvals", icon: CheckCircle2, badge: "Gate" },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-64 border-r border-border-subtle bg-background h-screen sticky top-0 px-4 py-6 justify-between select-none">
      <div>
        {/* Brand Logo & Senior Title */}
        <Link href="/dashboard" className="flex items-center gap-3 px-3 mb-8 group">
          <div className="w-8 h-8 rounded-xl bg-accent-indigo/20 border border-accent-indigo/40 flex items-center justify-center text-accent-indigo font-bold text-sm shadow-inner group-hover:scale-105 transition-transform">
            K
          </div>
          <div>
            <div className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
              Kavish Career OS
            </div>
            <div className="text-[11px] font-mono text-gray-500 uppercase tracking-wider">
              Senior BI & Analytics
            </div>
          </div>
        </Link>

        {/* Navigation items */}
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group",
                  isActive
                    ? "bg-surface-200 text-white border border-border-subtle shadow-sm"
                    : "text-gray-400 hover:text-gray-200 hover:bg-surface-50"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={cn(
                      "w-4 h-4 transition-colors",
                      isActive ? "text-accent-indigo" : "text-gray-400 group-hover:text-gray-300"
                    )}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-accent-amber/20 text-amber-300 border border-amber-500/20">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer System Status Badge */}
      <div className="p-3 rounded-xl bg-surface-50 border border-border-subtle flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-mono text-gray-400">Worker Active</span>
        </div>
        <span className="text-[10px] font-mono text-gray-400">v1.0.0</span>
      </div>
    </aside>
  );
}
