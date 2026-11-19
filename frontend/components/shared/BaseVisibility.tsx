import { Lock, LockOpen } from "lucide-react";
import { cn } from "@/lib/utils";

/** Lock for a private board, open lock for a public one; a labelled icon with a tooltip. */
export function BaseVisibility({ visibility, className }: { visibility: "public" | "private"; className?: string }) {
  const label = visibility === "private" ? "Private board" : "Public board";
  const Icon = visibility === "private" ? Lock : LockOpen;
  return <Icon role="img" aria-label={label} className={cn("size-icon-sm shrink-0", className)}><title>{label}</title></Icon>;
}
