import React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  className,
  disabled,
  ...props
}: ButtonProps) {
  const variantStyles = {
    primary: "bg-accent-indigo hover:bg-indigo-600 text-white shadow-sm border border-indigo-400/20",
    secondary: "bg-surface-200 hover:bg-surface-300 text-gray-200 border border-border-subtle",
    danger: "bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-800/40",
    ghost: "bg-transparent hover:bg-surface-100 text-gray-400 hover:text-gray-200",
    outline: "bg-transparent hover:bg-surface-200 text-gray-300 border border-border-subtle",
  };

  const sizeStyles = {
    sm: "px-2.5 py-1 text-xs rounded-md",
    md: "px-4 py-2 text-sm rounded-lg",
    lg: "px-5 py-2.5 text-base rounded-lg",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-accent-indigo/50 disabled:opacity-50 disabled:pointer-events-none gap-2",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
