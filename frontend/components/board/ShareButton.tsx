"use client";

import { Check, Copy, Share2 } from "lucide-react";
import { useState } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseConfirm } from "@/components/shared/BaseConfirm";
import { BaseAlert, BaseInput } from "@/components/shared/BaseField";
import { BasePopover } from "@/components/shared/BasePopover";
import { api, type ShareState } from "@/lib/api";
import { ApiError } from "@/lib/http";

/** Share popover for the board owner, a Manager, or an Admin: enable, copy the link, regenerate, disable (Req 18.22). */
export function ShareButton({ boardId }: { boardId: string }) {
  const [state, setState] = useState<ShareState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const link = state?.path ? `${window.location.origin}${state.path}` : "";

  async function run(action: () => Promise<ShareState>) {
    setError(null);
    try {
      setState(await action());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not update the share link.");
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Copy failed. Select the link and copy it by hand.");
    }
  }

  return (
    <BasePopover
      label="Share this board"
      wide
      onOpenChange={(open) => {
        if (open) void run(() => api.boards.share(boardId));
      }}
      trigger={
        <BaseButton variant="secondary" size="sm">
          <Share2 aria-hidden="true" />
          Share
        </BaseButton>
      }
    >
      <div className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold">Share a read-only view</h2>
        <p className="text-xs text-ink-muted">Anyone with the link sees cards, subtasks and attachments. Comments and activity stay private.</p>
        {error && <BaseAlert>{error}</BaseAlert>}
        <label className="flex min-h-control items-center gap-3 text-sm">
          <input
            type="checkbox"
            className="size-checkbox accent-brand"
            checked={!!state?.enabled}
            disabled={!state}
            onChange={(e) => void run(() => (e.target.checked ? api.boards.enableShare(boardId) : api.boards.disableShare(boardId)))}
          />
          Link sharing {state?.enabled ? "on" : "off"}
        </label>
        {state?.enabled && (
          <>
            <div className="flex items-center gap-2">
              <BaseInput readOnly aria-label="Share link" value={link} onFocus={(e) => e.currentTarget.select()} />
              <BaseButton variant="secondary" size="sm" aria-label="Copy link" onClick={() => void copy()}>
                {copied ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}
                {copied ? "Copied" : "Copy"}
              </BaseButton>
            </div>
            <div className="flex items-center justify-end gap-2">
              <BaseConfirm
                message="Make a new link? The old link stops working."
                confirmLabel="Regenerate"
                onConfirm={() => run(() => api.boards.regenerateShare(boardId))}
                trigger={
                  <BaseButton variant="secondary" size="sm">
                    Regenerate
                  </BaseButton>
                }
              />
              <BaseConfirm
                message="Turn off sharing? The link stops working."
                confirmLabel="Disable"
                onConfirm={() => run(() => api.boards.disableShare(boardId))}
                trigger={
                  <BaseButton variant="secondary" size="sm">
                    Disable
                  </BaseButton>
                }
              />
            </div>
          </>
        )}
      </div>
    </BasePopover>
  );
}
