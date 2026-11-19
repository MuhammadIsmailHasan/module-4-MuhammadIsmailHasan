"use client";

import { useState } from "react";
import { BaseBadge } from "@/components/shared/BaseBadge";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseAlert } from "@/components/shared/BaseField";
import { usePagedList } from "@/hooks/usePagedList";
import { api } from "@/lib/api";
import { formatWhen } from "@/lib/activity";
import { cn } from "@/lib/utils";
import { useShell } from "./ShellContext";

/** Lists notifications as the server returned them, one page at a time; nothing is computed client-side. */
export function InboxView() {
  const { inbox, refreshInbox } = useShell();
  const [version, setVersion] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const list = usePagedList(async (page) => (await api.notifications.inbox(page)).items, [version]);

  async function run(action: () => Promise<unknown>) {
    setError(null);
    try {
      await action();
      await refreshInbox();
      setVersion((v) => v + 1);
    } catch {
      setError("Could not update notifications.");
    }
  }

  if (list.error && !list.rows) return <p className="text-meta text-ink-muted">{list.error}</p>;
  if (!list.rows || !inbox) return <p className="text-ink-muted">Loading…</p>;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between gap-2">
        <BaseBadge tone={inbox.unread_count ? "red" : "neutral"}>{inbox.unread_count} unread</BaseBadge>
        <BaseButton size="sm" variant="secondary" disabled={!inbox.unread_count} onClick={() => run(() => api.notifications.readAll())}>
          Mark all read
        </BaseButton>
      </div>
      {error && <BaseAlert>{error}</BaseAlert>}
      {list.rows.length === 0 && <p className="text-meta text-ink-muted">No notifications.</p>}
      <ul className="m-0 flex list-none flex-col gap-2 p-0">
        {list.rows.map((n) => (
          <li key={n.id} className={cn("flex items-start gap-3 rounded-sm p-3", !n.is_read && "bg-label-blue")}>
            <span aria-hidden="true" className={cn("mt-1 size-dot shrink-0 rounded-full", n.is_read ? "bg-line" : "bg-ring")} />
            <div className="flex-1 text-sm">
              <div>{n.type === "assigned" ? "A card was assigned to you" : "A card is due today"}</div>
              <div className="mt-1 text-xs text-ink-muted">{formatWhen(n.created_at) || n.notify_date}</div>
            </div>
            {!n.is_read && (
              <BaseButton size="sm" variant="secondary" onClick={() => run(() => api.notifications.markRead(n.id))}>
                Mark read
              </BaseButton>
            )}
          </li>
        ))}
      </ul>
      {list.hasMore && (
        <BaseButton variant="secondary" disabled={list.loadingMore} onClick={() => void list.loadMore()}>
          {list.loadingMore ? "Loading…" : "Load more"}
        </BaseButton>
      )}
    </div>
  );
}
