"use client";

import { useCallback, useEffect, useState } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseConfirm } from "@/components/shared/BaseConfirm";
import { BaseCard } from "@/components/shared/BaseCard";
import { BaseAlert, BaseInput, BaseTextarea } from "@/components/shared/BaseField";
import { BaseModal } from "@/components/shared/BaseModal";
import { useShell } from "@/components/shell/ShellContext";
import { api, type CardInput } from "@/lib/api";
import { isRangeValid } from "@/lib/dates";
import { ApiError } from "@/lib/http";
import type { Board, Card, Category, Column, Comment, Priority, Member } from "@/lib/types";
import { CardActivity } from "./CardActivity";
import { AttachmentList, type StagedAttachment } from "./AttachmentList";
import { CardAttributes } from "./CardAttributes";
import { CardDescription } from "./CardDescription";
import { CommentComposer } from "./CommentComposer";
import { CommentThread, type CommentSort } from "./CommentThread";
import { SubtaskChecklist } from "./SubtaskChecklist";

interface CardModalProps {
  cardId: string;
  board: Board;
  columns: Column[];
  categories: Category[];
  onClose: () => void;
  onChanged: (card: Card) => void;
  onDeleted: (id: string) => void;
  onCreateCardFromComment?: (comment: Comment) => Promise<void>;
}

interface Form {
  title: string;
  description: string;
  priority: Priority;
  start_date: string;
  end_date: string;
  category_id: string;
  assignee_id: string;
}

const toForm = (c: Card): Form => ({
  title: c.title,
  description: c.description ?? "",
  priority: c.priority,
  start_date: c.start_date ?? "",
  end_date: c.end_date ?? "",
  category_id: c.category_id ?? "",
  assignee_id: c.assignee_id ?? "",
});

/** One two-pane modal for viewing and editing; comments live in the right pane, never a second modal. */
export function CardModal({ cardId, board, columns, categories, onClose, onChanged, onDeleted, onCreateCardFromComment }: CardModalProps) {
  const { session } = useShell();
  const [card, setCard] = useState<Card | null>(null);
  const [form, setForm] = useState<Form | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [sort, setSort] = useState<CommentSort>("latest");
  const [comments, setComments] = useState<Comment[] | undefined>(undefined);
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [message, setMessage] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [busy, setBusy] = useState(false);
  const [editingDescription, setEditingDescription] = useState(false);
  const [editingTitle, setEditingTitle] = useState(false);
  const [staged, setStaged] = useState<StagedAttachment[]>([]);
  const [removedIds, setRemovedIds] = useState<string[]>([]);
  const [discarding, setDiscarding] = useState(false);

  const role = session?.role;
  const staff = role === "supervisor" || role === "manager" || role === "admin";
  const canEdit = !!session && (role !== "member" || card?.assignee_id === session.userId);
  const names = Object.fromEntries(members.map((m) => [m.id, m.full_name]));
  const columnNames = Object.fromEntries(columns.map((c) => [c.id, c.name]));

  const load = useCallback(async () => {
    const fresh = await api.cards.get(cardId);
    setCard(fresh);
    setForm(toForm(fresh));
    setComments(fresh.comments);
    return fresh;
  }, [cardId]);

  useEffect(() => {
    load().catch((err) => setMessage(err instanceof ApiError ? err.message : "Could not load the card."));
  }, [load]);

  useEffect(() => {
    // Board staff get each member's Email for the assignee picker; anyone else (or a 403) gets the plain list.
    const plain = () => api.boards.members(board.id).then(setMembers).catch(() => setMembers([]));
    if (staff) api.boards.members(board.id, true).then(setMembers).catch(plain);
    else void plain();
  }, [board.id, staff]);

  const loadComments = useCallback(
    async (next: CommentSort) => {
      setComments(await api.comments.list(cardId, next));
    },
    [cardId],
  );

  /** The Card fields that differ from the loaded card, as one PATCH body. */
  function pendingBody(): CardInput {
    const body: CardInput = {};
    if (!card || !form) return body;
    const original = toForm(card);
    if (form.title !== original.title) body.title = form.title;
    if (form.description !== original.description) body.description = form.description || null;
    if (form.priority !== original.priority) body.priority = form.priority;
    if (form.start_date !== original.start_date) body.start_date = form.start_date || null;
    if (form.end_date !== original.end_date) body.end_date = form.end_date || null;
    if (form.category_id !== original.category_id) body.category_id = form.category_id || null;
    if (form.assignee_id !== original.assignee_id) body.assignee_id = form.assignee_id || null;
    return body;
  }

  const dirty = Object.keys(pendingBody()).length > 0 || staged.length > 0 || removedIds.length > 0;

  /** Closing with unsaved changes asks first. */
  function requestClose() {
    if (dirty) setDiscarding(true);
    else onClose();
  }

  async function save() {
    if (!card || !form) return;
    const body = pendingBody();
    if (!dirty) return setMessage("Nothing to save.");
    setBusy(true);
    setErrors({});
    setMessage(null);
    try {
      if (Object.keys(body).length > 0) await api.cards.update(card.id, body);
      // Attachment changes were staged in the draft; they are applied now, one by one.
      for (const item of [...staged]) {
        if (item.kind === "link") await api.attachments.addLink(card.id, { url: item.url });
        else await api.attachments.upload(card.id, item.file);
        setStaged((cur) => cur.filter((x) => x.key !== item.key));
      }
      for (const id of [...removedIds]) {
        await api.attachments.remove(id);
        setRemovedIds((cur) => cur.filter((x) => x !== id));
      }
      const fresh = await load();
      onChanged(fresh);
      setMessage("Saved.");
    } catch (err) {
      if (err instanceof ApiError && err.details) setErrors(err.details);
      else setMessage(err instanceof ApiError ? err.message : "Could not save.");
    } finally {
      setBusy(false);
    }
  }

  async function archive() {
    if (!card) return;
    try {
      onChanged(await api.cards.archive(card.id));
      onClose();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Could not archive.");
    }
  }

  async function remove() {
    if (!card) return;
    try {
      await api.cards.remove(card.id);
      onDeleted(card.id);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Could not delete.");
    }
  }

  const fieldErrors = (key: string) => errors[key];
  const set = <K extends keyof Form>(key: K, value: Form[K]) => setForm((f) => (f ? { ...f, [key]: value } : f));
  const canComment = !!session && role !== "admin";
  const datesValid = !form || isRangeValid(form.start_date, form.end_date);
  const doneId = columns.find((c) => c.name === "Done")?.id;
  const today = new Date().toISOString().slice(0, 10);
  const overdue = !!form?.end_date && form.end_date < today && card?.column_id !== doneId;
  const columnName = columns.find((c) => c.id === card?.column_id)?.name;
  const messages = Object.values(errors).flat();
  const showRight = !!card && (comments !== undefined || !!card.activity);

  const footer = card && form && (
    <div className="ml-auto flex flex-wrap items-center gap-2">
      {canEdit && staff && (
        <BaseButton variant="secondary" onClick={archive}>
          Archive
        </BaseButton>
      )}
      {canEdit && staff && (
        <BaseConfirm message="Delete this card? This cannot be undone from the board." onConfirm={remove} trigger={<BaseButton variant="danger">Delete</BaseButton>} />
      )}
      {canEdit && (
        <BaseButton onClick={save} disabled={busy || !datesValid}>
          Save changes
        </BaseButton>
      )}
    </div>
  );

  return (
    <>
    <BaseModal
      open
      size="full"
      title={`${form ? form.title.trim() || "Untitled card" : "Card"} | ${board.name}`}
      scrollBody={false}
      onClose={requestClose}
      footer={footer}
    >
      {!card || !form ? (
        <p className="text-ink-muted">{message ?? "Loading…"}</p>
      ) : (
        <div className="min-h-0 flex-1 overflow-y-auto lg:overflow-hidden">
          <div className="grid grid-cols-1 gap-6 lg:h-full lg:grid-cols-5 lg:grid-rows-1">
            <div className="flex min-w-0 flex-col gap-6 lg:col-span-3 lg:min-h-0 lg:overflow-y-auto">
              <BaseCard title="Details">
                <div className="flex items-center justify-between gap-3">
                  {editingTitle && canEdit ? (
                    <BaseInput
                      autoFocus
                      aria-label="Title"
                      value={form.title}
                      aria-invalid={errors.title ? true : undefined}
                      onChange={(e) => set("title", e.target.value)}
                    />
                  ) : (
                    <h4 className="min-w-0 flex-1 text-page-title font-semibold break-words">{form.title.trim() || "Untitled card"}</h4>
                  )}
                  {canEdit && (
                    <BaseButton variant="secondary" size="sm" aria-label={editingTitle ? "Done editing title" : "Edit title"} onClick={() => setEditingTitle((v) => !v)}>
                      {editingTitle ? "Done" : "Edit"}
                    </BaseButton>
                  )}
                </div>
                <CardAttributes
                  value={form}
                  onChange={(patch) => setForm((f) => (f ? { ...f, ...patch } : f))}
                  categories={categories}
                  members={members}
                  assigneeFallback={card?.assignee_name ? { name: card.assignee_name, avatar_url: card.assignee_avatar_url ?? null } : null}
                  columnName={columnName}
                  canEdit={canEdit}
                  canAssign={staff}
                  overdue={overdue}
                />
                {!datesValid && <BaseAlert>The end date cannot be before the start date.</BaseAlert>}
                {messages.length > 0 && <BaseAlert>{messages.join(" ")}</BaseAlert>}
                {message && <BaseAlert tone="info">{message}</BaseAlert>}
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold">Description</h4>
                    {canEdit && (
                      <BaseButton variant="secondary" size="sm" onClick={() => setEditingDescription((v) => !v)}>
                        {editingDescription ? "Done" : "Edit"}
                      </BaseButton>
                    )}
                  </div>
                  {canEdit && editingDescription ? (
                    <BaseTextarea aria-label="Description" autoFocus value={form.description} onChange={(e) => set("description", e.target.value)} />
                  ) : (
                    <CardDescription text={form.description || null} />
                  )}
                </div>
              </BaseCard>

              <BaseCard title="Attachments">
                <AttachmentList
                  attachments={card.attachments}
                  removedIds={removedIds}
                  staged={staged}
                  canEdit={canEdit}
                  onStage={(item) => setStaged((cur) => [...cur, item])}
                  onUnstage={(key) => setStaged((cur) => cur.filter((x) => x.key !== key))}
                  onRemove={(id) => setRemovedIds((cur) => [...cur, id])}
                />
              </BaseCard>

              <BaseCard title="Subtasks">
                <SubtaskChecklist cardId={card.id} subtasks={card.subtasks} canEdit={canEdit} onChange={(subtasks) => { setCard({ ...card, subtasks }); onChanged({ ...card, subtasks }); }} />
              </BaseCard>
            </div>

            {showRight && (
              <div className="flex min-w-0 flex-col gap-6 lg:col-span-2 lg:min-h-0 lg:overflow-y-auto">
                {comments !== undefined && (
                  <BaseCard title="Comments">
                    {canComment && (
                      <CommentComposer
                        onSubmit={async (content) => {
                          await api.comments.create(card.id, content);
                          await loadComments(sort);
                        }}
                      />
                    )}
                    <CommentThread
                      comments={comments}
                      sort={sort}
                      names={names}
                      canReply={canComment}
                      canPrioritize={role === "manager"}
                      onSortChange={(next) => { setSort(next); void loadComments(next); }}
                      onReply={async (id, content) => { await api.comments.reply(id, content); await loadComments(sort); }}
                      onTogglePriority={async (id) => { await api.comments.togglePriority(id); await loadComments(sort); }}
                      onCreateCard={onCreateCardFromComment}
                    />
                  </BaseCard>
                )}
                {card.activity && (
                  <BaseCard title="Activity">
                    <CardActivity cardId={card.id} initial={card.activity} names={names} columns={columnNames} />
                  </BaseCard>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </BaseModal>
    <BaseModal
      open={discarding}
      title="Discard changes?"
      onClose={() => setDiscarding(false)}
      footer={
        <div className="ml-auto flex items-center gap-2">
          <BaseButton variant="secondary" onClick={() => setDiscarding(false)}>
            Keep editing
          </BaseButton>
          <BaseButton variant="danger" onClick={onClose}>
            Discard
          </BaseButton>
        </div>
      }
    >
      <p className="text-sm">You have changes that are not saved. They are lost if you close the card.</p>
    </BaseModal>
    </>
  );
}
