"use client";

import type { ReactNode } from "react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface BasePopoverProps {
  /** The element that opens the popover; it must be a single focusable element. */
  trigger: ReactNode;
  children: ReactNode;
  /** Accessible name of the popover panel. */
  label: string;
  wide?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

/** The only popover in the app: a thin wrapper over the shadcn/ui Popover (Radix). */
export function BasePopover({ trigger, children, label, wide = false, open, onOpenChange }: BasePopoverProps) {
  return (
    <Popover open={open} onOpenChange={onOpenChange}>
      <PopoverTrigger asChild>{trigger}</PopoverTrigger>
      <PopoverContent aria-label={label} className={cn("w-popover", wide && "w-popover-wide")}>
        {children}
      </PopoverContent>
    </Popover>
  );
}
