import type { HTMLAttributes } from "react";

export type BadgeTone = "neutral" | "green" | "yellow" | "orange" | "red" | "purple" | "blue";

interface BaseBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

/** The only badge in the app; tones map to the prototype's --label-* colour pairs. */
export function BaseBadge({ tone = "neutral", className = "", ...rest }: BaseBadgeProps) {
  return <span className={["badge", `badge-${tone}`, className].filter(Boolean).join(" ")} {...rest} />;
}
