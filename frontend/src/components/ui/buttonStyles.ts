export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

const baseClasses =
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold transition focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-gold-300 disabled:cursor-not-allowed disabled:opacity-55";

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-forest-900 text-white shadow-sm hover:bg-forest-800 active:bg-forest-950",
  secondary:
    "border border-stone-300 bg-white text-forest-950 hover:border-forest-700 hover:bg-ivory-100",
  ghost: "text-forest-900 hover:bg-white/10",
  danger:
    "border border-danger-700 bg-white text-danger-700 hover:bg-danger-50",
};

// Links and real buttons share one visual contract without hiding their native semantics.
export function buttonClassName(
  variant: ButtonVariant = "primary",
  className = "",
) {
  return `${baseClasses} ${variantClasses[variant]} ${className}`.trim();
}
