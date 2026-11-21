"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseAlert, BaseField, BaseInput, BaseTextarea } from "@/components/shared/BaseField";
import { BaseModal } from "@/components/shared/BaseModal";
import { api } from "@/lib/api";
import { ApiError } from "@/lib/http";

export function NewBoardModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const board = await api.boards.create({ name, ...(description.trim() ? { description: description.trim() } : {}) });
      onClose();
      setName("");
      setDescription("");
      router.push(`/boards/${board.id}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? (err.details?.name?.[0] ?? err.message) : "Could not create the board.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <BaseModal
      open={open}
      title="New board"
      onClose={onClose}
      footer={
        <>
          <BaseButton variant="ghost" onClick={onClose}>
            Cancel
          </BaseButton>
          <BaseButton type="submit" form="new-board-form" className="ml-auto" disabled={busy || !name.trim()}>
            {busy ? "Creating…" : "Create board"}
          </BaseButton>
        </>
      }
    >
      <form id="new-board-form" method="post" className="flex flex-col gap-4" onSubmit={submit}>
        {error && <BaseAlert>{error}</BaseAlert>}
        <BaseField label="Board name" htmlFor="board-name">
          <BaseInput id="board-name" value={name} onChange={(e) => setName(e.target.value)} required />
        </BaseField>
        <BaseField label="Description (optional)" htmlFor="board-description">
          <BaseTextarea id="board-description" maxLength={500} value={description} onChange={(e) => setDescription(e.target.value)} />
        </BaseField>
      </form>
    </BaseModal>
  );
}
