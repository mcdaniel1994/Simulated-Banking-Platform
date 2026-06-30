import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";

import { Button } from "./Button";

interface PageStateProps {
  kind: "loading" | "empty" | "error";
  title: string;
  message?: string;
  onRetry?: () => void;
}

// Full-page states retain layout and provide a recovery path instead of replacing it with raw text.
export function PageState({ kind, title, message, onRetry }: PageStateProps) {
  const Icon =
    kind === "loading" ? LoaderCircle : kind === "empty" ? Inbox : AlertCircle;
  return (
    <section
      aria-live="polite"
      className="mx-auto grid max-w-xl justify-items-center gap-3 rounded-xl border border-stone-200 bg-white p-8 text-center shadow-card"
      role={kind === "error" ? "alert" : "status"}
    >
      <Icon
        aria-hidden="true"
        className={`size-8 text-forest-800 ${kind === "loading" ? "animate-spin" : ""}`}
      />
      <h1 className="text-xl font-bold text-ink-950">{title}</h1>
      {message && <p className="text-ink-700">{message}</p>}
      {kind === "error" && onRetry && (
        <Button onClick={onRetry} type="button">
          Try again
        </Button>
      )}
    </section>
  );
}
