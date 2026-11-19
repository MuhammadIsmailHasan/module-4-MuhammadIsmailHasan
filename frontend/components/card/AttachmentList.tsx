"use client";

import { useState } from "react";
import { FileArchive, FileText, Link as LinkIcon, Plus, X } from "lucide-react";
import { BaseBadge } from "@/components/shared/BaseBadge";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseCombobox } from "@/components/shared/BaseCombobox";
import { BaseAlert, BaseInput } from "@/components/shared/BaseField";
import { BaseConfirm } from "@/components/shared/BaseConfirm";
import { BasePopover } from "@/components/shared/BasePopover";
import { api } from "@/lib/api";
import { FileDropZone } from "./FileDropZone";
import { absoluteFileUrl, hrefFor, iconFor, isExpired } from "@/lib/attachments";
import type { Attachment } from "@/lib/types";

/** An attachment added in the open modal; it is sent when the user saves. */
export type StagedAttachment = { key: string; kind: "link"; url: string } | { key: string; kind: "file"; file: File };

interface AttachmentListProps {
  attachments: Attachment[];
  /** Ids the user removed in the open modal; hidden here, deleted on save. */
  removedIds: string[];
  staged: StagedAttachment[];
  canEdit: boolean;
  onStage: (item: StagedAttachment) => void;
  onUnstage: (key: string) => void;
  onRemove: (id: string) => void;
}

const KINDS = [
  { value: "link", label: "Link" },
  { value: "file", label: "File" },
];

const tile = "flex min-h-control items-center justify-between gap-2 rounded-sm border border-line bg-surface-raised px-3 text-xs";

function TypeIcon({ kind }: { kind: "document" | "archive" | "link" }) {
  const Icon = kind === "link" ? LinkIcon : kind === "archive" ? FileArchive : FileText;
  return <Icon className="size-icon shrink-0 text-ink-muted" aria-hidden="true" />;
}

/** Links open in a new tab; an expired signed file URL is re-issued first. Changes wait in the draft until Save. */
export function AttachmentList({ attachments, removedIds, staged, canEdit, onStage, onUnstage, onRemove }: AttachmentListProps) {
  const [url, setUrl] = useState("");
  const [kind, setKind] = useState("link");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const shown = attachments.filter((a) => !removedIds.includes(a.id));

  async function open(e: React.MouseEvent, a: Attachment) {
    if (a.url || !a.file_url) return; // plain link: let the anchor do its job
    e.preventDefault();
    let href = absoluteFileUrl(a.file_url);
    try {
      if (isExpired(a.file_url)) {
        const fresh = await api.attachments.freshUrl(a.id);
        if (fresh.file_url) href = absoluteFileUrl(fresh.file_url);
      }
      window.open(href, "_blank", "noopener,noreferrer");
    } catch {
      setError("Could not open the file.");
    }
  }

  const nothing = shown.length === 0 && staged.length === 0;

  return (
    <div className="flex flex-col gap-3">
      <div className={canEdit ? "grid grid-cols-1 items-start gap-3 lg:grid-cols-2" : "flex flex-col"}>
        <div className="flex min-w-0 flex-col gap-3">
          {nothing && <p className="text-sm text-ink-muted">No attachments.</p>}
          <ul className="m-0 flex list-none flex-col gap-3 p-0">
            {shown.map((a) => (
              <li key={a.id} className={tile}>
                <a className="flex min-w-0 items-center gap-2 font-medium no-underline" href={hrefFor(a)} target="_blank" rel="noopener noreferrer" onClick={(e) => open(e, a)}>
                  <TypeIcon kind={iconFor(a)} />
                  <span className="truncate">{a.name}</span>
                </a>
                {canEdit && (
                  <BaseConfirm
                    message={`Remove ${a.name}? It is removed when you save.`}
                    confirmLabel="Remove"
                    onConfirm={() => onRemove(a.id)}
                    trigger={
                      <BaseButton variant="ghost" size="sm" className="size-control-sm shrink-0 px-0" aria-label={`Remove ${a.name}`}>
                        <X aria-hidden="true" />
                      </BaseButton>
                    }
                  />
                )}
              </li>
            ))}
            {staged.map((s) => (
              <li key={s.key} className={tile}>
                <span className="flex min-w-0 items-center gap-2 font-medium">
                  <TypeIcon kind={s.kind === "link" ? "link" : "document"} />
                  <span className="truncate">{s.kind === "link" ? s.url : s.file.name}</span>
                </span>
                <span className="flex shrink-0 items-center gap-2">
                  <BaseBadge>Pending</BaseBadge>
                  <BaseButton variant="ghost" size="sm" className="size-control-sm px-0" aria-label={`Discard ${s.kind === "link" ? s.url : s.file.name}`} onClick={() => onUnstage(s.key)}>
                    <X aria-hidden="true" />
                  </BaseButton>
                </span>
              </li>
            ))}
          </ul>
        </div>
        {canEdit && (
          <BasePopover
            wide
            label="Add an attachment"
            open={adding}
            onOpenChange={setAdding}
            trigger={
              <BaseButton variant="secondary" className="min-h-control w-full justify-start gap-2 px-3 text-xs font-medium">
                <Plus aria-hidden="true" />
                Add attachment
              </BaseButton>
            }
          >
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <span className="text-xs font-medium text-ink-muted">Type</span>
                <BaseCombobox label="Type" options={KINDS} value={kind} onChange={setKind} />
              </div>
              {kind === "link" ? (
                <div className="flex items-center gap-2">
                  <BaseInput type="url" placeholder="https://link" aria-label="Attachment link" value={url} onChange={(e) => setUrl(e.target.value)} />
                  <BaseButton
                    disabled={!url.trim()}
                    onClick={() => {
                      onStage({ key: `link-${Date.now()}`, kind: "link", url: url.trim() });
                      setUrl("");
                      setAdding(false);
                    }}
                  >
                    Add
                  </BaseButton>
                </div>
              ) : (
                <FileDropZone
                  onFile={(file) => {
                    onStage({ key: `file-${Date.now()}`, kind: "file", file });
                    setAdding(false);
                  }}
                />
              )}
            </div>
          </BasePopover>
        )}
      </div>
      {error && <BaseAlert>{error}</BaseAlert>}
    </div>
  );
}
