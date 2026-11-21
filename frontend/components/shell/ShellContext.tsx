"use client";

import { createContext, useContext } from "react";
import type { Session } from "@/lib/session";
import type { Inbox, User } from "@/lib/types";

export type PanelView = "inbox" | "activity";

export interface ShellState {
  session: Session | null;
  user: User | null;
  boardId: string | null;
  inbox: Inbox | null;
  refreshInbox: () => Promise<void>;
  /** The one function the sidebar items and the header bell both call. */
  toggleSidePanel: (view: PanelView) => void;
  closeSidePanel: () => void;
  /** Lower or raise the unread count at once, before the server answers. */
  adjustUnread: (delta: number) => void;
}

export const ShellContext = createContext<ShellState | null>(null);

export function useShell(): ShellState {
  const ctx = useContext(ShellContext);
  if (!ctx) throw new Error("useShell must be used inside AppShell");
  return ctx;
}
