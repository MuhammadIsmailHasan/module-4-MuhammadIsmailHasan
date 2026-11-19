import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

export const fieldClasses =
  "w-full rounded-sm border border-line bg-surface-raised px-3 text-sm text-ink placeholder:text-ink-muted transition-all duration-fast focus-visible:border-brand focus-ring disabled:cursor-not-allowed disabled:bg-surface-hover disabled:opacity-disabled aria-invalid:border-danger";

export function Input({ className, ...props }: ComponentProps<"input">) {
  return <input data-slot="input" className={cn(fieldClasses, "min-h-control", className)} {...props} />;
}

export function Textarea({ className, ...props }: ComponentProps<"textarea">) {
  return <textarea data-slot="textarea" className={cn(fieldClasses, "min-h-12 resize-y py-3", className)} {...props} />;
}

