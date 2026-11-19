"use client";

import { useEffect, useState } from "react";
import { getSession, type Session } from "@/lib/session";

/** The Token claims for UI affordances only; the server still enforces every permission. */
export function useSession(): Session | null {
  const [session, setSession] = useState<Session | null>(null);
  useEffect(() => setSession(getSession()), []);
  return session;
}
