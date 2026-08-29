import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "indigo" | "outline";
}

export function Badge({ children, variant = "default", className, ...props }: BadgeProps) {
  const variantStyles = {
    default: "bg-surface-200 text-gray-300 border-border-subtle",
    success: "bg-emerald-950/60 text-emerald-400 border-emerald-800/40",
    warning: "bg-amber-950/60 text-amber-400 border-amber-800/40",
    danger: "bg-rose-950/60 text-rose-400 border-rose-800/40",
    indigo: "bg-indigo-950/60 text-indigo-400 border-indigo-800/40",
    outline: "bg-transparent text-gray-400 border-border-subtle",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border font-mono",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
