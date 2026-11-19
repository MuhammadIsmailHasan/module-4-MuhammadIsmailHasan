import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/** shadcn/ui Button, themed from the design tokens. Import only from components/shared/. */
export const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-sm border border-transparent text-sm font-semibold whitespace-nowrap cursor-pointer select-none transition-all duration-fast ease-out focus-ring disabled:pointer-events-none disabled:opacity-disabled active:translate-y-px [&_svg]:size-icon [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-brand text-on-brand shadow-card hover:bg-brand-strong",
        secondary: "border-line bg-surface-raised text-ink hover:bg-surface-hover",
        ghost: "bg-transparent text-ink-muted hover:bg-surface-hover hover:text-ink",
        destructive: "bg-danger text-on-brand shadow-card hover:opacity-faint",
      },
      size: {
        default: "min-h-control px-4",
        sm: "min-h-control-sm px-3 text-xs",
        icon: "size-touch",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export interface ButtonProps extends ComponentProps<"button">, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return <Comp data-slot="button" className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}
