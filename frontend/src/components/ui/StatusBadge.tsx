import type { AccountStatus } from "../../types/api";

type Status = AccountStatus | "ACTIVE_USER" | "INACTIVE_USER";

const statusStyles: Record<Status, string> = {
  ACTIVE: "bg-success-200 text-success-700",
  ACTIVE_USER: "bg-success-200 text-success-700",
  FROZEN: "bg-warning-200 text-warning-700",
  CLOSED: "bg-stone-200 text-ink-700",
  INACTIVE_USER: "bg-danger-200 text-danger-700",
};

// A dot plus text ensures status is never communicated by color alone.
export function StatusBadge({
  status,
  label,
}: {
  status: Status;
  label?: string;
}) {
  const displayLabel =
    label ??
    (status === "ACTIVE_USER"
      ? "Active"
      : status === "INACTIVE_USER"
        ? "Inactive"
        : status);

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-md px-3 py-1 text-xs font-bold tracking-wide ${statusStyles[status]}`}
    >
      <span aria-hidden="true" className="size-2 rounded-full bg-current" />
      {displayLabel}
    </span>
  );
}
