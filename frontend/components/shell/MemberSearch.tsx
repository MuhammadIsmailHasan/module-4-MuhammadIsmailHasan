"use client";

import { useEffect, useState } from "react";
import { BaseAvatar } from "@/components/shared/BaseAvatar";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseAlert, BaseInput } from "@/components/shared/BaseField";
import { api, type Candidate } from "@/lib/api";
import { ApiError } from "@/lib/http";

const DEBOUNCE_MS = 250;
const MIN_CHARS = 2;

interface MemberSearchProps {
  boardId: string;
  onAdded: () => void;
}

/** Search users who are not on the board yet (GET /boards/{id}/candidates) and add the chosen one. */
export function MemberSearch({ boardId, onAdded }: MemberSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Candidate[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const short = query.trim().length < MIN_CHARS;

  useEffect(() => {
    if (short) {
      setResults(null);
      return;
    }
    let live = true;
    setError(null);
    const t = setTimeout(() => {
      api.boards
        .candidates(boardId, query.trim())
        .then((r) => live && setResults(r))
        .catch(() => live && setError("Could not search users."));
    }, DEBOUNCE_MS);
    return () => {
      live = false;
      clearTimeout(t);
    };
  }, [boardId, query, short]);

  async function add(user: Candidate) {
    setError(null);
    try {
      await api.boards.addMember(boardId, user.id);
      onAdded();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add the member.");
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <BaseInput autoFocus type="search" placeholder="Search people" aria-label="Search people" value={query} onChange={(e) => setQuery(e.target.value)} />
      {error && <BaseAlert>{error}</BaseAlert>}
      <ul className="m-0 flex max-h-popover-list list-none flex-col gap-1 overflow-y-auto p-0" aria-label="People">
        {results?.map((u) => (
          <li key={u.id}>
            <BaseButton variant="ghost" className="h-auto min-h-control w-full justify-start gap-2 px-2 font-normal text-ink" onClick={() => void add(u)}>
              <BaseAvatar name={u.full_name} size="md" />
              <span className="min-w-0 text-left">
                <span className="block truncate text-sm">{u.full_name}</span>
                <span className="block truncate text-xs text-ink-muted">
                  @{u.username} · {u.email}
                </span>
              </span>
            </BaseButton>
          </li>
        ))}
        {short && <li className="px-2 text-meta text-ink-muted">Type at least {MIN_CHARS} characters.</li>}
        {!short && results && results.length === 0 && <li className="px-2 text-meta text-ink-muted">No people to add.</li>}
        {!short && !results && <li className="px-2 text-meta text-ink-muted">Loading…</li>}
      </ul>
    </div>
  );
}
