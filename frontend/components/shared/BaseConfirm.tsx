"use client";

import { cloneElement, useState, type MouseEvent, type ReactElement, type ReactNode } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { BaseModal } from "@/components/shared/BaseModal";
import { BasePopover } from "@/components/shared/BasePopover";

interface BaseConfirmProps {
  /** The element that asks; it opens the confirmation instead of acting. */
  trigger: ReactElement<{ onClick?: (e: MouseEvent) => void }>;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void | Promise<void>;
  /** A small panel anchored to the trigger (default), or a centred dialog for removals others rely on (Decision AC). */
  variant?: "popover" | "modal";
  /** The dialog title of the modal form. */
  title?: string;
  /** Extra lines under the message in the modal form. */
  detail?: ReactNode;
}

/** A confirmation: a message, a secondary Cancel, and a danger confirm button, as a popover or as a modal. */
export function BaseConfirm({ trigger, message, confirmLabel = "Delete", onConfirm, variant = "popover", title = "Are you sure?", detail }: BaseConfirmProps) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  async function confirm() {
    setBusy(true);
    try {
      await onConfirm();
      setOpen(false);
    } finally {
      setBusy(false);
    }
  }

  const buttons = (
    <>
      <BaseButton variant="secondary" size="sm" onClick={() => setOpen(false)}>
        Cancel
      </BaseButton>
      <BaseButton variant="danger" size="sm" disabled={busy} onClick={() => void confirm()}>
        {confirmLabel}
      </BaseButton>
    </>
  );

  if (variant === "modal") {
    return (
      <>
        {cloneElement(trigger, { onClick: () => setOpen(true) })}
        <BaseModal open={open} title={title} onClose={() => setOpen(false)} footer={<div className="ml-auto flex items-center gap-2">{buttons}</div>}>
          <p className="text-sm">{message}</p>
          {detail && <div className="mt-2 text-sm text-ink-muted">{detail}</div>}
        </BaseModal>
      </>
    );
  }

  return (
    <BasePopover label="Confirm" open={open} onOpenChange={setOpen} trigger={trigger}>
      <div className="flex flex-col gap-3">
        <p className="text-sm">{message}</p>
        <div className="flex items-center justify-end gap-2">{buttons}</div>
      </div>
    </BasePopover>
  );
}
