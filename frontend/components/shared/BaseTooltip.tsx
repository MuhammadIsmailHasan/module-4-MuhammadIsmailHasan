"use client";

import type { ReactElement } from "react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface BaseTooltipProps {
  label: string;
  /** The single element that carries the tooltip. */
  children: ReactElement;
  side?: "top" | "right" | "bottom" | "left";
}

/** The only tooltip in the app: a thin wrapper over the shadcn/ui Tooltip (hover and keyboard focus; hides on leave and on click). */
export function BaseTooltip({ label, children, side = "top" }: BaseTooltipProps) {
  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>{children}</TooltipTrigger>
        <TooltipContent side={side}>{label}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
