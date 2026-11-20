"use client";

import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export interface MenuEntry {
  label: string;
  icon?: LucideIcon;
  /** A link item; otherwise `onSelect` runs. */
  href?: string;
  onSelect?: () => void;
}

interface BaseMenuProps {
  /** The element that opens the menu; a single focusable element. */
  trigger: ReactNode;
  /** Accessible name of the menu itself. */
  label: string;
  items: MenuEntry[];
  /** A heading row, for example who is signed in. */
  heading?: string;
}

/** The only action menu in the app: a thin wrapper over the shadcn/ui DropdownMenu (Radix). */
export function BaseMenu({ trigger, label, items, heading }: BaseMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>{trigger}</DropdownMenuTrigger>
      <DropdownMenuContent aria-label={label}>
        {heading && (
          <>
            <DropdownMenuLabel>{heading}</DropdownMenuLabel>
            <DropdownMenuSeparator />
          </>
        )}
        {items.map(({ label: text, icon: Icon, href, onSelect }) =>
          href ? (
            <DropdownMenuItem key={text} asChild>
              <Link href={href}>
                {Icon && <Icon aria-hidden="true" />}
                {text}
              </Link>
            </DropdownMenuItem>
          ) : (
            <DropdownMenuItem key={text} onSelect={onSelect}>
              {Icon && <Icon aria-hidden="true" />}
              {text}
            </DropdownMenuItem>
          ),
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
