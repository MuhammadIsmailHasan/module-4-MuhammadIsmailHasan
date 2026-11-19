import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface BaseCardProps {
  title: string;
  children: ReactNode;
  /** Controls beside the title (a toggle, an Edit button). */
  action?: ReactNode;
  className?: string;
}

/** A titled section with a border, like a Bootstrap card: heading bar on top, content below. */
export function BaseCard({ title, children, action, className }: BaseCardProps) {
  const id = `card-${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
  return (
    <section aria-labelledby={id} className={cn("flex min-w-0 shrink-0 flex-col overflow-hidden rounded-md border border-line bg-surface-raised shadow-card", className)}>
      <header className="flex items-center justify-between gap-2 border-b border-line bg-surface px-4 py-3">
        <h3 id={id} className="text-sm font-bold">
          {title}
        </h3>
        {action}
      </header>
      <div className="flex min-w-0 flex-col gap-3 p-4">{children}</div>
    </section>
  );
}
