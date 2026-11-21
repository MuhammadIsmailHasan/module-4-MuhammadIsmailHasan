import { Calendar, Flag, ListChecks, Paperclip } from "lucide-react";
import { BaseAvatar } from "@/components/shared/BaseAvatar";
import { BaseBadge, type BadgeTone } from "@/components/shared/BaseBadge";
import { shortDate } from "@/lib/format";
import { categoryTone } from "@/lib/tones";
import type { Card, Category, Priority, Member } from "@/lib/types";
import { cn } from "@/lib/utils";

const PRIORITY_TONE: Record<Priority, BadgeTone> = { high: "red", medium: "orange", low: "green" };

interface CardTileProps {
  card: Card;
  category?: Category;
  assignee?: Pick<Member, "full_name" | "avatar_url">;
  overdue: boolean;
  draggable: boolean;
  onOpen: () => void;
  onDragStart: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragEnd: () => void;
}

/** The card face, Trello style: label chips, title, a row of small badges, and the assignee avatar. */
export function CardTile({ card, category, assignee, overdue, draggable, onOpen, onDragStart, onDragEnd }: CardTileProps) {
  const total = card.subtasks.length;
  const done = card.subtasks.filter((s) => s.is_done).length;
  const complete = total > 0 && done === total;
  return (
    <div
      data-flip-id={card.id}
      data-card-id={card.id}
      role="button"
      tabIndex={0}
      draggable={draggable}
      aria-label={`Open card ${card.title}`}
      onClick={onOpen}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), onOpen())}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      className={cn(
        "flex flex-col gap-3 rounded-card border border-line bg-surface-raised p-4 shadow-card transition-all duration-base ease-out focus-ring",
        "hover:border-brand",
        draggable ? "cursor-grab active:cursor-grabbing" : "cursor-pointer",
      )}
    >
      <div className="flex flex-wrap gap-1">
        {category && (
          <BaseBadge shape="tag" dot tone={categoryTone(category)} className="text-card-tag lowercase">
            {category.name}
          </BaseBadge>
        )}
        <BaseBadge shape="outline" tone={PRIORITY_TONE[card.priority]} className="text-card-tag lowercase">
          <Flag className="size-icon-sm" aria-hidden="true" />
          {card.priority}
        </BaseBadge>
      </div>
      <div className="text-card-title font-semibold break-words">{card.title}</div>
      {card.description && <p className="line-clamp-2 text-card-meta text-ink-muted">{card.description}</p>}
      <div className="flex flex-wrap items-center gap-3 text-card-meta text-ink-muted">
        {card.end_date && (
          <span className={cn("inline-flex items-center gap-1", overdue && "rounded-sm bg-label-red px-1 font-semibold text-label-red-fg")}>
            <Calendar className="size-icon-sm" aria-hidden="true" />
            {overdue ? `Overdue · ${shortDate(card.end_date)}` : shortDate(card.end_date)}
          </span>
        )}
        {total > 0 && (
          <span className={cn("inline-flex items-center gap-1", complete && "rounded-sm bg-label-green px-1 font-semibold text-label-green-fg")}>
            <ListChecks className="size-icon-sm" aria-hidden="true" />
            {done}/{total}
            <span className="sr-only"> subtasks done</span>
          </span>
        )}
        {card.attachments.length > 0 && (
          <span className="inline-flex items-center gap-1">
            <Paperclip className="size-icon-sm" aria-hidden="true" />
            {card.attachments.length}
          </span>
        )}
        {assignee && <BaseAvatar name={assignee.full_name} src={assignee.avatar_url} className="ml-auto" />}
      </div>
    </div>
  );
}
