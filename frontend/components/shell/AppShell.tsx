"use client";

import { Bell, Menu } from "lucide-react";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { api } from "@/lib/api";
import { getSession, getStoredUser, type Session } from "@/lib/session";
import type { Board, Inbox, User } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ShellContext, type PanelView } from "./ShellContext";
import { SidePanel } from "./SidePanel";
import { Sidebar } from "./Sidebar";

/** Client shell: sidebar drawer + persistent header + side panel host around the page content. */
export function AppShell({ boards, children }: { boards: Board[]; children: ReactNode }) {
  const pathname = usePathname();
  const boardId = /^\/boards\/([^/]+)/.exec(pathname)?.[1] ?? null;
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [inbox, setInbox] = useState<Inbox | null>(null);
  const [drawer, setDrawer] = useState(false);
  const [panel, setPanel] = useState<PanelView | null>(null);

  useEffect(() => {
    setSession(getSession());
    setUser(getStoredUser());
  }, [pathname]);

  const refreshInbox = useCallback(async () => {
    if (!getSession()) return;
    try {
      setInbox(await api.notifications.inbox());
    } catch {
      setInbox(null);
    }
  }, []);

  useEffect(() => {
    if (session) void refreshInbox();
  }, [session, refreshInbox]);

  const toggleSidePanel = useCallback((view: PanelView) => setPanel((cur) => (cur === view ? null : view)), []);
  const state = useMemo(
    () => ({ session, user, boardId, inbox, refreshInbox, toggleSidePanel }),
    [session, user, boardId, inbox, refreshInbox, toggleSidePanel],
  );
  const current = boards.find((b) => b.id === boardId);

  return (
    <ShellContext.Provider value={state}>
      <div className="relative flex h-screen overflow-hidden">
        <div
          aria-hidden="true"
          onClick={() => setDrawer(false)}
          className={cn("fixed inset-0 z-scrim bg-scrim transition-opacity duration-base lg:hidden", drawer ? "opacity-100" : "pointer-events-none opacity-0")}
        />
        <Sidebar boards={boards} open={drawer} onNavigate={() => setDrawer(false)} />
        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          {/* Persistent mobile header: menu, title, inbox. From lg the board header and sidebar carry these. */}
          <header className="z-header flex min-h-touch shrink-0 items-center gap-2 border-b border-line bg-surface-raised px-2 py-1 lg:hidden">
            <BaseButton variant="secondary" size="sm" className="size-control-sm" aria-label="Open menu" aria-expanded={drawer} onClick={() => setDrawer((d) => !d)}>
              <Menu aria-hidden="true" />
            </BaseButton>
            <h1 className="min-w-0 flex-1 py-1 text-heading font-semibold break-words">{current?.name ?? "Boards"}</h1>
            {session && (
              <BaseButton variant="secondary" size="sm" className="relative size-control-sm" aria-label="Open inbox" onClick={() => toggleSidePanel("inbox")}>
                <Bell aria-hidden="true" />
                {!!inbox?.unread_count && <span className="absolute -top-1 -right-1 size-alert-dot rounded-full border border-surface-raised bg-danger" />}
              </BaseButton>
            )}
          </header>
          <main className="min-h-0 min-w-0 flex-1 overflow-y-auto">{children}</main>
        </div>
        <SidePanel view={panel} onClose={() => setPanel(null)} />
      </div>
    </ShellContext.Provider>
  );
}
