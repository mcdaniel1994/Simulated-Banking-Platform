import type { ReactNode } from "react";

interface FormFieldProps {
  id: string;
  label: string;
  children: ReactNode;
  error?: string;
  hint?: string;
  required?: boolean;
}

// The wrapper gives every form the same visible label, help text, and error relationship.
export function FormField({
  id,
  label,
  children,
  error,
  hint,
  required,
}: FormFieldProps) {
  return (
    <div className="grid gap-2">
      <div className="flex items-center gap-1">
        <label className="text-sm font-semibold text-ink-950" htmlFor={id}>
          {label}
        </label>
        {required && (
          <span aria-hidden="true" className="text-danger-700">
            *
          </span>
        )}
      </div>
      {children}
      {error && (
        <p className="text-sm font-medium text-danger-700" id={`${id}-error`}>
          {error}
        </p>
      )}
      {hint && (
        <p className="text-sm text-ink-500" id={`${id}-hint`}>
          {hint}
        </p>
      )}
    </div>
  );
}
