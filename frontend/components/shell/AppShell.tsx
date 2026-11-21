"use client";

import { usePathname } from "next/navigation";
import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { api } from "@/lib/api";
import { getSession, getStoredUser, storeUser, type Session } from "@/lib/session";
import { panelTitle } from "@/lib/titles";
import type { Board, Inbox, User } from "@/lib/types";
import { cn } from "@/lib/utils";
import { AppHeader } from "./AppHeader";
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

  // The stored user can be stale (a signed avatar URL lives 15 minutes), so load it fresh once per session.
  useEffect(() => {
    if (!session) return;
    let live = true;
    api.auth
      .me()
      .then((fresh) => {
        if (!live) return;
        storeUser(fresh);
        setUser(fresh);
      })
      .catch(() => undefined);
    return () => {
      live = false;
    };
  }, [session]);

  // An open Inbox or Activity panel names the tab; closing it restores the page title (Requirement 32, criterion 4).
  useEffect(() => {
    if (!panel) return;
    const previous = document.title;
    document.title = panelTitle(panel, inbox?.unread_count ?? 0);
    return () => {
      document.title = previous;
    };
  }, [panel, inbox?.unread_count]);

  const toggleSidePanel = useCallback((view: PanelView) => setPanel((cur) => (cur === view ? null : view)), []);
  const closeSidePanel = useCallback(() => setPanel(null), []);
  const adjustUnread = useCallback(
    (delta: number) => setInbox((cur) => (cur ? { ...cur, unread_count: Math.max(0, cur.unread_count + delta) } : cur)),
    [],
  );
  const state = useMemo(
    () => ({ session, user, boardId, inbox, refreshInbox, toggleSidePanel, closeSidePanel, adjustUnread }),
    [session, user, boardId, inbox, refreshInbox, toggleSidePanel, closeSidePanel, adjustUnread],
  );
  const current = boards.find((b) => b.id === boardId);

  return (
    <ShellContext.Provider value={state}>
      <div className="relative flex h-screen flex-col overflow-hidden">
        <AppHeader board={current ?? null} drawerOpen={drawer} onToggleDrawer={() => setDrawer((d) => !d)} />
        <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <div
          aria-hidden="true"
          onClick={() => setDrawer(false)}
          className={cn("fixed inset-0 z-scrim bg-scrim transition-opacity duration-base lg:hidden", drawer ? "opacity-100" : "pointer-events-none opacity-0")}
        />
        <Sidebar boards={boards} open={drawer} onNavigate={() => setDrawer(false)} />
        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <main className="min-h-0 min-w-0 flex-1 overflow-y-auto">{children}</main>
        </div>
        <SidePanel view={panel} onClose={() => setPanel(null)} />
        </div>
      </div>
    </ShellContext.Provider>
  );
}
