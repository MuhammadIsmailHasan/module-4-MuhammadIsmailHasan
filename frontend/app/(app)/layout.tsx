import type { ReactNode } from "react";
import { AppShell } from "@/components/shell/AppShell";
import { serverGet } from "@/lib/server";
import type { Board } from "@/lib/types";

// The shell's board list is the board switcher. Guests get the public boards.
export default async function AppLayout({ children }: { children: ReactNode }) {
  const boards = await serverGet<Board[]>("/boards");
  return <AppShell boards={boards}>{children}</AppShell>;
}
