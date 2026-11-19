import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";
import type { Tone } from "@/lib/tones";

const DOT: Record<Tone, string> = {
  green: "bg-tone-green",
  blue: "bg-tone-blue",
  red: "bg-tone-red",
  purple: "bg-tone-purple",
  orange: "bg-tone-orange",
};

interface BaseChipProps extends ComponentProps<"button"> {
  tone: Tone;
  active?: boolean;
}

/** Filter chip: a quiet text pill; the active one takes the brand tint. A dot carries the category tone. */
export function BaseChip({ tone, active = false, className, children, type = "button", ...rest }: BaseChipProps) {
  return (
    <button
      type={type}
      aria-pressed={active}
      className={cn(
        "inline-flex cursor-pointer items-center gap-2 min-h-control-sm shrink-0 rounded-sm border px-3 text-meta whitespace-nowrap font-semibold transition-colors duration-fast ease-out focus-ring",
        active ? "border-brand bg-brand-tint text-brand" : "border-line bg-transparent text-ink-muted hover:bg-surface hover:text-ink",
        className,
      )}
      {...rest}
    >
      <i aria-hidden="true" className={cn("inline-block size-dot-md shrink-0 rounded-full", DOT[tone])} />
      {children}
    </button>
  );
}
