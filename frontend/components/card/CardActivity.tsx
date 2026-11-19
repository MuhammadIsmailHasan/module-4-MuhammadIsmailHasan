"use client";

import { useState } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { api } from "@/lib/api";
import type { ActivityEntry } from "@/lib/types";
import { ActivityList } from "./ActivityList";

interface CardActivityProps {
  cardId: string;
  /** The first page the card response embedded. */
  initial: ActivityEntry[];
  names: Record<string, string>;
  columns: Record<string, string>;
}

/** The card's own log: the embedded first page, then Load more asks for older rows with `before`. */
export function CardActivity({ cardId, initial, names, columns }: CardActivityProps) {
  const [extra, setExtra] = useState<ActivityEntry[]>([]);
  const [hasMore, setHasMore] = useState(initial.length >= EMBEDDED_PAGE);
  const [busy, setBusy] = useState(false);
  const rows = [...initial, ...extra];

  async function loadMore() {
    const last = rows[rows.length - 1];
    if (!last) return;
    setBusy(true);
    try {
      const page = await api.cards.activity(cardId, { limit: EMBEDDED_PAGE, before: last.id });
      setExtra((cur) => [...cur, ...page]);
      setHasMore(page.length === EMBEDDED_PAGE);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <ActivityList entries={rows} names={names} columns={columns} />
      {hasMore && (
        <BaseButton variant="secondary" disabled={busy} onClick={() => void loadMore()}>
          {busy ? "Loading…" : "Load more"}
        </BaseButton>
      )}
    </div>
  );
}

/** The card response embeds this many activity rows (the API default page). */
const EMBEDDED_PAGE = 20;
