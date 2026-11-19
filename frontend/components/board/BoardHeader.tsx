"use client";

import { Bell, Search } from "lucide-react";
import { useState } from "react";
import { BaseAvatar } from "@/components/shared/BaseAvatar";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseInput } from "@/components/shared/BaseField";
import { BaseModal } from "@/components/shared/BaseModal";
import { BaseVisibility } from "@/components/shared/BaseVisibility";
import { useShell } from "@/components/shell/ShellContext";
import type { Board, Card, Category, User } from "@/lib/types";
import { FilterRow } from "./FilterRow";

interface BoardHeaderProps {
  board: Board;
  cards: Card[];
  members: User[];
  categories: Category[];
  categoryId: string | null;
  search: string;
  onSearch: (value: string) => void;
  onCategory: (id: string | null) => void;
}

/** One row: board name and progress, the category filter, then search, the Inbox bell, and the signed-in user. */
export function BoardHeader({ board, cards, categories, categoryId, search, onSearch, onCategory }: BoardHeaderProps) {
  const { session, user, inbox, toggleSidePanel } = useShell();
  const [searching, setSearching] = useState(false);
  const doneId = board.columns?.find((c) => c.name === "Done")?.id;
  const done = doneId ? cards.filter((c) => c.column_id === doneId).length : 0;
  const percent = cards.length ? Math.round((done / cards.length) * 100) : 0;

  const field = (
    <div className="relative">
      <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-3 size-icon -translate-y-1/2 text-ink-muted" />
      <BaseInput type="search" className="border-transparent bg-surface pl-12" placeholder="Search" aria-label="Search cards" value={search} onChange={(e) => onSearch(e.target.value)} />
    </div>
  );

  const section = "flex items-center rounded-sm border border-line px-3 py-2";

  return (
    <header className="relative z-header flex shrink-0 flex-col gap-3 border-b border-line bg-surface-raised px-4 py-3 lg:px-8">
      <div className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <BaseVisibility visibility={board.visibility} className="size-icon text-ink-muted" />
          <h1 className="min-w-0 text-page-title font-semibold break-words">{board.name}</h1>
        </div>
        {session && (
          <div className="hidden items-center gap-2 lg:flex">
            <BaseButton variant="ghost" size="sm" className="relative size-control px-0" aria-label="Notifications" onClick={() => toggleSidePanel("inbox")}>
              <Bell aria-hidden="true" />
              {!!inbox?.unread_count && <span aria-hidden="true" className="absolute top-2 right-2 size-alert-dot rounded-full border border-surface-raised bg-danger" />}
            </BaseButton>
            <BaseAvatar name={user?.full_name ?? "Signed in"} size="md" />
            <span className="text-sm font-medium whitespace-nowrap">{user?.full_name ?? "Signed in"}</span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-stretch gap-3 lg:flex-nowrap">
        <section aria-label="Progress" className={`${section} shrink-0 gap-3`}>
          <span className="text-xs whitespace-nowrap text-ink-muted">
            {done} of {cards.length} done · {percent}%
          </span>
          <div role="progressbar" aria-label="Board progress" aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent} className="h-progress w-progress-track max-w-full overflow-hidden rounded-full bg-surface">
            <div className="h-full rounded-full bg-brand transition-all duration-base" style={{ width: `${percent}%` }} />
          </div>
        </section>
        <section aria-label="Categories" className={`${section} order-last w-full min-w-0 lg:order-none lg:w-auto lg:flex-1`}>
          <div className="min-w-0 flex-1">
            <FilterRow categories={categories} categoryId={categoryId} onCategory={onCategory} />
          </div>
        </section>
        <section aria-label="Search" className={`${section} ml-auto lg:ml-0`}>
          <div className="hidden w-search lg:block">{field}</div>
          <BaseButton variant="ghost" size="sm" className="size-control-sm px-0 lg:hidden" aria-label="Search cards" onClick={() => setSearching(true)}>
            <Search aria-hidden="true" />
          </BaseButton>
        </section>
      </div>
      <BaseModal open={searching} title="Search cards" onClose={() => setSearching(false)}>
        {field}
      </BaseModal>
    </header>
  );
}
