/** Date rules for the card modal. Dates are ISO "YYYY-MM-DD" strings: no time of day and no time zone. */

export interface Range {
  start: string;
  end: string;
}

const pad = (n: number) => String(n).padStart(2, "0");

export function toIso(d: Date): string {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function fromIso(iso: string): Date {
  return new Date(`${iso}T00:00:00`);
}

export const isIso = (value: string) => /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(fromIso(value).getTime());

/** True when either date is empty, or the end is the same day as the start or later (ISO strings sort as dates). */
export function isRangeValid(start: string, end: string): boolean {
  return !start || !end || end >= start;
}

/**
 * A day clicked in the calendar:
 * - no start yet: it becomes the start;
 * - a start and no end: a later or equal day becomes the end, an earlier day restarts the range there;
 * - both set: a later or equal day becomes the new end, an earlier day restarts the range there.
 */
export function normalizeRange(start: string, end: string, picked: string): Range {
  if (!start) return { start: picked, end: "" };
  if (picked < start) return { start: picked, end: "" };
  return { start, end: picked };
}

/** A new start typed or picked: moving it past the end clears the end (reported through `cleared`). */
export function withStart(range: Range, start: string): Range & { cleared: boolean } {
  if (range.end && start && start > range.end) return { start, end: "", cleared: true };
  return { start, end: range.end, cleared: false };
}

/** Days before this one are not selectable while the end date is being picked. */
export function minSelectable(range: Range): string | undefined {
  return range.start && !range.end ? range.start : undefined;
}
