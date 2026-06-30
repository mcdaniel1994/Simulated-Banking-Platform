import { AlertTriangle, X } from "lucide-react";
import { useEffect, useRef } from "react";

import { Button } from "./Button";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  pending?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

// This focused dialog makes reversible but high-impact admin actions explicit.
export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel,
  pending = false,
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  const returnFocusRef = useRef<HTMLElement | null>(null);

  // Capture the invoking control once per opening, then restore keyboard context on close.
  useEffect(() => {
    if (!open) return;
    returnFocusRef.current =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    cancelRef.current?.focus();
    return () => {
      returnFocusRef.current?.focus();
      returnFocusRef.current = null;
    };
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape" && !pending) onCancel();
    }
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [open, pending, onCancel]);

  if (!open) return null;

  return (
    <div
      aria-labelledby="confirm-title"
      aria-describedby="confirm-description"
      aria-modal="true"
      className="fixed inset-0 z-50 grid place-items-center bg-ink-950/45 p-4"
      role="alertdialog"
    >
      <section className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-start gap-4">
          <span className="grid size-12 shrink-0 place-items-center rounded-full bg-danger-50 text-danger-700">
            <AlertTriangle aria-hidden="true" className="size-6" />
          </span>
          <div className="min-w-0 flex-1">
            <h2 className="text-xl font-bold text-ink-950" id="confirm-title">
              {title}
            </h2>
            <p className="mt-2 leading-6 text-ink-700" id="confirm-description">
              {description}
            </p>
          </div>
          <button
            aria-label="Close confirmation"
            className="grid min-h-11 min-w-11 place-items-center rounded-lg text-ink-700 hover:bg-ivory-100 focus-visible:outline-3 focus-visible:outline-forest-700"
            disabled={pending}
            onClick={onCancel}
            type="button"
          >
            <X aria-hidden="true" className="size-5" />
          </button>
        </div>
        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <Button
            ref={cancelRef}
            disabled={pending}
            onClick={onCancel}
            type="button"
            variant="secondary"
          >
            Cancel
          </Button>
          <Button
            disabled={pending}
            onClick={onConfirm}
            type="button"
            variant="danger"
          >
            {pending ? "Working…" : confirmLabel}
          </Button>
        </div>
      </section>
    </div>
  );
}
