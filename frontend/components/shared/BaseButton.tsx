import type { ButtonHTMLAttributes } from "react";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
export type ButtonSize = "sm" | "md";

interface BaseButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  block?: boolean;
}

/** The only button in the app: styled from tokens.css, with focus and disabled states built in. */
export function BaseButton({
  variant = "primary",
  size = "md",
  block = false,
  className = "",
  type = "button",
  ...rest
}: BaseButtonProps) {
  const classes = ["btn", `btn-${variant}`, `btn-${size}`, block ? "btn-block" : "", className].filter(Boolean).join(" ");
  return <button type={type} className={classes} {...rest} />;
}
