"use client";

import { Bell, Menu } from "lucide-react";
import Link from "next/link";
import { ShareButton } from "@/components/board/ShareButton";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseVisibility } from "@/components/shared/BaseVisibility";
import type { Board } from "@/lib/types";
import { useShell } from "./ShellContext";
import { UserMenu } from "./UserMenu";

interface AppHeaderProps {
  /** The Board the page shows, if any: the header's page-context slot. */
  board: Board | null;
  drawerOpen: boolean;
  onToggleDrawer: () => void;
}

/** The one header on every protected page: menu (below 960px), brand or Board name, Share, Inbox bell, and the User_Menu. */
export function AppHeader({ board, drawerOpen, onToggleDrawer }: AppHeaderProps) {
  const { session, user, inbox, toggleSidePanel } = useShell();
  const canShare = !!board && !!session && (session.role === "manager" || session.role === "admin" || board.owner_id === session.userId);

  return (
    <header className="z-header flex min-h-touch shrink-0 items-center gap-3 border-b border-line bg-surface-raised px-2 py-1 lg:px-8">
      <BaseButton variant="secondary" size="sm" className="size-control-sm lg:hidden" aria-label="Open menu" aria-expanded={drawerOpen} onClick={onToggleDrawer}>
        <Menu aria-hidden="true" />
      </BaseButton>
      {board ? (
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <BaseVisibility visibility={board.visibility} className="size-icon shrink-0 text-ink-muted" />
          <h1 className="min-w-0 text-page-title font-semibold break-words">{board.name}</h1>
          {canShare && <ShareButton boardId={board.id} />}
        </div>
      ) : (
        <div className="min-w-0 flex-1">
          <Link href="/boards" className="text-page-title font-semibold text-ink no-underline">
            RevoTask
          </Link>
        </div>
      )}
      {session && (
        <div className="flex items-center gap-2">
          <BaseButton variant="ghost" size="sm" className="relative size-control px-0" aria-label="Notifications" onClick={() => toggleSidePanel("inbox")}>
            <Bell aria-hidden="true" />
            {!!inbox?.unread_count && <span aria-hidden="true" className="absolute top-2 right-2 size-alert-dot rounded-full border border-surface-raised bg-danger" />}
          </BaseButton>
          <UserMenu user={user} />
        </div>
      )}
    </header>
  );
}
