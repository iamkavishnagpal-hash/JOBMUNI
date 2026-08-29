import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverEffect?: boolean;
}

export function Card({ children, hoverEffect = false, className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "bg-surface-50 border border-border-subtle rounded-xl p-5 text-gray-100",
        hoverEffect && "hover:border-border-strong hover:bg-surface-100 transition-all duration-200",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex items-center justify-between pb-3 border-b border-border-subtle mb-4", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn("text-base font-semibold text-white tracking-tight", className)} {...props}>
      {children}
    </h3>
  );
}
