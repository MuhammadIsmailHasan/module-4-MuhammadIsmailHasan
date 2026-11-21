import type { Card, Subtask } from "./types";

/** Card progress as the Backend derives it: `(20 * done + total) // (2 * total)` (0 to 10), null without Subtasks (Requirement 27). */
export function deriveProgress(done: number, total: number): number | null {
  return total > 0 ? Math.floor((20 * done + total) / (2 * total)) : null;
}

/** A Card with its derived progress fields recomputed from these Subtasks, so the meter follows a toggle without a reload. */
export function withSubtasks(card: Card, subtasks: Subtask[]): Card {
  const done = subtasks.filter((s) => s.is_done).length;
  return { ...card, subtasks, progress: deriveProgress(done, subtasks.length), subtask_done_count: done, subtask_total_count: subtasks.length };
}
