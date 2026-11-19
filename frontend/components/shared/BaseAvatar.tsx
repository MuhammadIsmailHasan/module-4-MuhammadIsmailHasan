import { BaseTooltip } from "@/components/shared/BaseTooltip";
import { cn } from "@/lib/utils";
import { initials } from "@/lib/format";

interface BaseAvatarProps {
  name: string;
  size?: "sm" | "md";
  className?: string;
  /** The "+7" overflow chip. */
  label?: string;
}

/** Brand-coloured initials circle (24px in cards, 32px in the sidebar and header); hovering or focusing it shows the full name. */
export function BaseAvatar({ name, size = "sm", className, label }: BaseAvatarProps) {
  return (
    <BaseTooltip label={name}>
      <span
        role="img"
        aria-label={name}
        className={cn(
          "inline-flex shrink-0 items-center justify-center rounded-full bg-brand font-semibold text-on-brand focus-ring",
          size === "sm" ? "size-avatar-sm text-2xs" : "size-avatar-md text-2xs",
          className,
        )}
      >
        {label ?? initials(name)}
      </span>
    </BaseTooltip>
  );
}
