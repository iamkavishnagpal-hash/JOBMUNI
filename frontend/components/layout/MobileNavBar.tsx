"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Radar,
  Users,
  CheckCircle2,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const MOBILE_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Radar", href: "/jobs", icon: Radar },
  { label: "CRM", href: "/recruiters", icon: Users },
  { label: "Approvals", href: "/approvals", icon: CheckCircle2 },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function MobileNavBar() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-surface-50/95 backdrop-blur-md border-t border-border-subtle px-2 py-2 flex items-center justify-around">
      {MOBILE_ITEMS.map((item) => {
        const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-col items-center gap-1 py-1 px-3 rounded-lg text-[10px] font-medium transition-colors",
              isActive ? "text-accent-indigo" : "text-gray-400 hover:text-gray-200"
            )}
          >
            <Icon className="w-5 h-5" />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
