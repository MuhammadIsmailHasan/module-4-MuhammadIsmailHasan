"use client";

import { Calendar, Columns3, Flag, Tag, User as UserIcon, type LucideIcon } from "lucide-react";
import { useState, type ReactNode } from "react";
import { BaseAvatar } from "@/components/shared/BaseAvatar";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseCombobox, type ComboOption } from "@/components/shared/BaseCombobox";
import { BasePopover } from "@/components/shared/BasePopover";
import { shortDate } from "@/lib/format";
import type { Category, Priority, User } from "@/lib/types";
import { cn } from "@/lib/utils";
import { DateRangePicker } from "./DateRangePicker";

export interface AttributeValues {
  priority: Priority;
  category_id: string;
  start_date: string;
  end_date: string;
  assignee_id: string;
}

interface CardAttributesProps {
  value: AttributeValues;
  onChange: (patch: Partial<AttributeValues>) => void;
  categories: Category[];
  members: User[];
  columnName?: string;
  /** May change category, priority, and dates. */
  canEdit: boolean;
  /** May change the assignee (Supervisor, Manager, Admin). */
  canAssign: boolean;
  overdue: boolean;
}

const PRIORITY_COLOR: Record<Priority, string> = { high: "text-label-red-fg", medium: "text-label-orange-fg", low: "text-label-green-fg" };
const PRIORITIES: Priority[] = ["high", "medium", "low"];

const row = "h-auto min-h-control w-full justify-start gap-3 px-3 text-sm font-normal text-ink";

/** The icon and the text of one attribute row; every row has the same height, font, and icon size. */
function RowContent({ icon: Icon, iconClass, children }: { icon: LucideIcon; iconClass?: string; children: ReactNode }) {
  return (
    <>
      <Icon className={cn("size-icon shrink-0 text-ink-muted", iconClass)} aria-hidden="true" />
      <span className="min-w-0 flex-1 truncate text-left">{children}</span>
    </>
  );
}

function StaticRow({ icon, iconClass, label, children, danger }: { icon: LucideIcon; iconClass?: string; label: string; children: ReactNode; danger?: boolean }) {
  return (
    <div role="group" aria-label={label} className={cn("flex min-h-control w-full items-center gap-3 rounded-sm border border-line px-3 text-sm", danger && "text-danger")}>
      <RowContent icon={icon} iconClass={iconClass}>
        {children}
      </RowContent>
    </div>
  );
}

/** Column, category, priority, dates, and assignee as plain icon rows; each editable row opens a searchable select or a popover on the draft. */
export function CardAttributes({ value, onChange, categories, members, columnName, canEdit, canAssign, overdue }: CardAttributesProps) {
  const [datesOpen, setDatesOpen] = useState(false);
  const category = categories.find((c) => c.id === value.category_id);
  const assignee = members.find((m) => m.id === value.assignee_id);
  const dateLabel =
    value.start_date && value.end_date
      ? `${shortDate(value.start_date)} – ${shortDate(value.end_date)}`
      : value.end_date
        ? `Due ${shortDate(value.end_date)}`
        : value.start_date
          ? `Starts ${shortDate(value.start_date)}`
          : "No dates";

  const categoryOptions: ComboOption[] = [{ value: "", label: "No label" }, ...categories.map((c) => ({ value: c.id, label: c.name, render: <span className="lowercase">{c.name}</span> }))];
  const priorityOptions: ComboOption[] = PRIORITIES.map((p) => ({
    value: p,
    label: p[0].toUpperCase() + p.slice(1),
    render: (
      <span className="flex items-center gap-2">
        <Flag className={cn("size-icon-sm", PRIORITY_COLOR[p])} aria-hidden="true" />
        <span className="capitalize">{p}</span>
      </span>
    ),
  }));
  const memberOptions: ComboOption[] = [
    { value: "", label: "Unassigned" },
    ...members.map((m) => ({
      value: m.id,
      label: m.full_name,
      keywords: [m.login_identifier],
      render: (
        <span className="flex items-center gap-2">
          <BaseAvatar name={m.full_name} />
          <span className="truncate">{m.full_name}</span>
        </span>
      ),
    })),
  ];

  const priorityName = value.priority[0].toUpperCase() + value.priority.slice(1);
  const categoryText = category?.name ?? "No label";
  const assigneeText = assignee?.full_name ?? "Unassigned";

  return (
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
      <StaticRow icon={Columns3} label={`Column: ${columnName ?? ""}`}>
        {columnName ?? "No column"}
      </StaticRow>

      {canEdit ? (
        <BaseCombobox
          label="Label"
          options={categoryOptions}
          value={value.category_id}
          onChange={(v) => onChange({ category_id: v })}
          trigger={
            <BaseButton variant="secondary" className={row} aria-label={`Label: ${categoryText}`}>
              <RowContent icon={Tag}><span className="lowercase">{categoryText}</span></RowContent>
            </BaseButton>
          }
        />
      ) : (
        <StaticRow icon={Tag} label={`Label: ${categoryText}`}>
          <span className="lowercase">{categoryText}</span>
        </StaticRow>
      )}

      {canEdit ? (
        <BaseCombobox
          label="Priority"
          options={priorityOptions}
          value={value.priority}
          onChange={(v) => onChange({ priority: v as Priority })}
          trigger={
            <BaseButton variant="secondary" className={row} aria-label={`Priority: ${priorityName}`}>
              <RowContent icon={Flag} iconClass={PRIORITY_COLOR[value.priority]}>
                {priorityName}
              </RowContent>
            </BaseButton>
          }
        />
      ) : (
        <StaticRow icon={Flag} iconClass={PRIORITY_COLOR[value.priority]} label={`Priority: ${priorityName}`}>
          {priorityName}
        </StaticRow>
      )}

      {canEdit ? (
        <BasePopover
          wide
          label="Choose dates"
          open={datesOpen}
          onOpenChange={setDatesOpen}
          trigger={
            <BaseButton variant="secondary" className={cn(row, overdue && "border-danger text-danger")} aria-label={`Dates: ${dateLabel}${overdue ? ", overdue" : ""}`}>
              <RowContent icon={Calendar} iconClass={overdue ? "text-danger" : undefined}>
                {dateLabel}
              </RowContent>
            </BaseButton>
          }
        >
          <DateRangePicker value={{ start: value.start_date, end: value.end_date }} onChange={(r) => onChange({ start_date: r.start, end_date: r.end })} />
        </BasePopover>
      ) : (
        <StaticRow icon={Calendar} label={`Dates: ${dateLabel}`} danger={overdue}>
          {dateLabel}
        </StaticRow>
      )}

      {canAssign ? (
        <BaseCombobox
          label="Assignee"
          options={memberOptions}
          value={value.assignee_id}
          searchable
          onChange={(v) => onChange({ assignee_id: v })}
          trigger={
            <BaseButton variant="secondary" className={row} aria-label={`Assignee: ${assigneeText}`}>
              <RowContent icon={UserIcon}>{assigneeText}</RowContent>
            </BaseButton>
          }
        />
      ) : (
        <StaticRow icon={UserIcon} label={`Assignee: ${assigneeText}`}>
          {assigneeText}
        </StaticRow>
      )}
    </div>
  );
}
