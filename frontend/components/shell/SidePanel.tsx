"use client";

import { X } from "lucide-react";
import { BaseButton } from "@/components/shared/BaseButton";
import { cn } from "@/lib/utils";
import { ActivityView } from "./ActivityView";
import { InboxView } from "./InboxView";
import type { PanelView } from "./ShellContext";

interface SidePanelProps {
  view: PanelView | null;
  onClose: () => void;
}

/** Slides in from the right; one panel hosts both Inbox and Activity. */
export function SidePanel({ view, onClose }: SidePanelProps) {
  return (
    <>
      <div
        aria-hidden="true"
        onClick={onClose}
        className={cn("fixed inset-0 z-panel-scrim bg-scrim transition-opacity duration-base", view ? "opacity-100" : "pointer-events-none opacity-0")}
      />
      <aside
        aria-label={view === "activity" ? "Activity" : "Inbox"}
        aria-hidden={!view}
        className={cn(
          "fixed inset-y-0 right-0 z-panel flex w-full max-w-panel-sm flex-col border-l border-line bg-surface-raised shadow-panel transition-transform duration-slow ease-out",
          view ? "translate-x-0" : "invisible translate-x-full",
        )}
      >
        <div className="flex items-center justify-between border-b border-line p-4">
          <h2 className="text-heading font-semibold">{view === "activity" ? "Activity" : "Inbox"}</h2>
          <BaseButton variant="ghost" size="sm" className="size-control-sm px-0" onClick={onClose} aria-label="Close panel">
            <X aria-hidden="true" />
          </BaseButton>
        </div>
        <div className="flex flex-1 flex-col gap-2 overflow-y-auto p-4">
          {view === "inbox" && <InboxView />}
          {view === "activity" && <ActivityView />}
        </div>
      </aside>
    </>
  );
}
