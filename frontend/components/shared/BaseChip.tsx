import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";
import type { Tone } from "@/lib/tones";

/** Each tone fills the chip at once; the active chip adds a border in the same colour. */
const TONE: Record<Tone, string> = {
  green: "bg-label-green text-label-green-fg",
  blue: "bg-label-blue text-label-blue-fg",
  red: "bg-label-red text-label-red-fg",
  purple: "bg-label-purple text-label-purple-fg",
  orange: "bg-label-orange text-label-orange-fg",
};

interface BaseChipProps extends ComponentProps<"button"> {
  tone: Tone;
  active?: boolean;
}

/** Filter chip: a rounded pill filled with its category colour, no dot; the active one gets a border. */
export function BaseChip({ tone, active = false, className, children, type = "button", ...rest }: BaseChipProps) {
  return (
    <button
      type={type}
      aria-pressed={active}
      className={cn(
        "inline-flex cursor-pointer items-center min-h-control-sm shrink-0 rounded-full border px-4 text-meta whitespace-nowrap font-semibold transition-colors duration-fast ease-out focus-ring",
        TONE[tone],
        active ? "border-current" : "border-transparent hover:border-current",
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}
