import { AlertTriangle, CheckCircle2, Info, X } from "lucide-react";
import type { ReactNode } from "react";

type AlertTone = "success" | "error" | "info";

const toneStyles: Record<AlertTone, string> = {
  success: "border-success-200 bg-success-50 text-success-700",
  error: "border-danger-200 bg-danger-50 text-danger-700",
  info: "border-info-200 bg-info-50 text-info-700",
};

const toneIcons = {
  success: CheckCircle2,
  error: AlertTriangle,
  info: Info,
};

export function AlertBanner({
  tone,
  title,
  children,
  onDismiss,
}: {
  tone: AlertTone;
  title: string;
  children?: ReactNode;
  onDismiss?: () => void;
}) {
  const Icon = toneIcons[tone];
  return (
    <div
      className={`flex items-start gap-3 rounded-xl border p-4 ${toneStyles[tone]}`}
      role={tone === "error" ? "alert" : "status"}
    >
      <Icon aria-hidden="true" className="mt-0.5 size-5 shrink-0" />
      <div className="min-w-0 flex-1">
        <p className="font-semibold">{title}</p>
        {children && (
          <div className="mt-1 text-sm text-ink-700">{children}</div>
        )}
      </div>
      {onDismiss && (
        <button
          aria-label="Dismiss message"
          className="grid min-h-11 min-w-11 place-items-center rounded-md hover:bg-black/5 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-current"
          onClick={onDismiss}
          type="button"
        >
          <X aria-hidden="true" className="size-5" />
        </button>
      )}
    </div>
  );
}
