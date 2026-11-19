"use client";

import { Calendar } from "@/components/ui/calendar";
import { fromIso, toIso } from "@/lib/dates";

interface BaseCalendarProps {
  start: string;
  end: string;
  /** Called with the ISO day (YYYY-MM-DD) the user clicked. */
  onPick: (day: string) => void;
  /** ISO days before this one cannot be picked (used while the end date is chosen). */
  notBefore?: string;
}

/** The only calendar in the app: a range calendar over react-day-picker; the range rules live in lib/dates.ts. */
export function BaseCalendar({ start, end, onPick, notBefore }: BaseCalendarProps) {
  const from = start ? fromIso(start) : undefined;
  const to = end ? fromIso(end) : undefined;
  const min = notBefore ? fromIso(notBefore) : undefined;
  return (
    <div className="relative">
      <Calendar
        mode="range"
        selected={from ? { from, to } : undefined}
        defaultMonth={from ?? to}
        disabled={min ? { before: min } : undefined}
        onDayClick={(day) => onPick(toIso(day))}
        onSelect={() => undefined}
      />
    </div>
  );
}
