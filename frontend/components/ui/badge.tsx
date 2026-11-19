import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/** shadcn/ui Badge; tones are the --label-* colour pairs, shapes are pill and tag. */
export const badgeVariants = cva("inline-flex items-center gap-1 text-xs font-semibold", {
  variants: {
    tone: {
      neutral: "bg-surface-hover text-ink-muted",
      green: "bg-label-green text-label-green-fg",
      yellow: "bg-label-yellow text-label-yellow-fg",
      orange: "bg-label-orange text-label-orange-fg",
      red: "bg-label-red text-label-red-fg",
      purple: "bg-label-purple text-label-purple-fg",
      blue: "bg-label-blue text-label-blue-fg",
    },
    shape: {
      pill: "rounded-full px-2 py-1",
      tag: "rounded-sm px-2 py-1 font-medium",
      outline: "rounded-sm border bg-transparent px-2 py-1 font-medium",
    },
  },
  compoundVariants: [
    { shape: "outline", tone: "neutral", className: "border-line text-ink-muted" },
    { shape: "outline", tone: "green", className: "border-label-green-fg" },
    { shape: "outline", tone: "yellow", className: "border-label-yellow-fg" },
    { shape: "outline", tone: "orange", className: "border-label-orange-fg" },
    { shape: "outline", tone: "red", className: "border-label-red-fg" },
    { shape: "outline", tone: "purple", className: "border-label-purple-fg" },
    { shape: "outline", tone: "blue", className: "border-label-blue-fg" },
  ],
  defaultVariants: { tone: "neutral", shape: "pill" },
});

export interface BadgeProps extends ComponentProps<"span">, VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

export function Badge({ className, tone, shape, dot = false, children, ...props }: BadgeProps) {
  return (
    <span data-slot="badge" className={cn(badgeVariants({ tone, shape }), className)} {...props}>
      {dot && <i aria-hidden="true" className="inline-block size-dot shrink-0 rounded-full bg-current" />}
      {children}
    </span>
  );
}
