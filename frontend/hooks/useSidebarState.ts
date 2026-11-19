"use client";

import { useCallback, useEffect, useState } from "react";

const KEY = "kanban.sidebar.collapsed";

/** Collapsed or expanded Sidebar, remembered in the browser (storage may be blocked, so every access is guarded). */
export function useSidebarState(): [boolean, () => void] {
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    try {
      setCollapsed(window.localStorage.getItem(KEY) === "1");
    } catch {
      /* storage unavailable: stay expanded */
    }
  }, []);

  const toggle = useCallback(() => {
    setCollapsed((cur) => {
      const next = !cur;
      try {
        window.localStorage.setItem(KEY, next ? "1" : "0");
      } catch {
        /* ignore */
      }
      return next;
    });
  }, []);

  return [collapsed, toggle];
}
