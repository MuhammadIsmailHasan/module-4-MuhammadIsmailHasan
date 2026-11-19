"use client";

import { useState, type ReactElement } from "react";
import { BaseButton } from "@/components/shared/BaseButton";
import { BasePopover } from "@/components/shared/BasePopover";

interface BaseConfirmProps {
  /** The element that asks; it opens the confirmation instead of acting. */
  trigger: ReactElement;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void | Promise<void>;
}

/** A small confirmation popover: a message, a secondary Cancel, and a danger confirm button. */
export function BaseConfirm({ trigger, message, confirmLabel = "Delete", onConfirm }: BaseConfirmProps) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  return (
    <BasePopover label="Confirm" open={open} onOpenChange={setOpen} trigger={trigger}>
      <div className="flex flex-col gap-3">
        <p className="text-sm">{message}</p>
        <div className="flex items-center justify-end gap-2">
          <BaseButton variant="secondary" size="sm" onClick={() => setOpen(false)}>
            Cancel
          </BaseButton>
          <BaseButton
            variant="danger"
            size="sm"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await onConfirm();
                setOpen(false);
              } finally {
                setBusy(false);
              }
            }}
          >
            {confirmLabel}
          </BaseButton>
        </div>
      </div>
    </BasePopover>
  );
}
