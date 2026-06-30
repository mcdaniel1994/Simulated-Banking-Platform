interface NorthstarMarkProps {
  className?: string;
}

// The local brand mark stays dependency-free while functional icons come from Lucide.
export function NorthstarMark({ className }: NorthstarMarkProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      viewBox="0 0 48 48"
    >
      <path
        d="M24 2 28.5 19.5 46 24l-17.5 4.5L24 46l-4.5-17.5L2 24l17.5-4.5L24 2Z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="2"
      />
      <path
        d="m24 11 2.2 10.8L37 24l-10.8 2.2L24 37l-2.2-10.8L11 24l10.8-2.2L24 11Z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.5"
      />
      <circle cx="24" cy="24" fill="currentColor" r="2" />
    </svg>
  );
}
