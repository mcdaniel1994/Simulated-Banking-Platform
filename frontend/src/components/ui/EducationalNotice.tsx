import { GraduationCap } from "lucide-react";

import { NorthstarMark } from "./NorthstarMark";

// The persistent notice prevents the polished interface from being mistaken for a real bank.
export function EducationalNotice() {
  return (
    <aside
      aria-label="Educational simulation notice"
      className="relative mb-10 overflow-hidden rounded-xl border border-success-200 bg-success-50/60 px-4 py-4 sm:px-7 sm:py-5"
    >
      <div className="relative z-10 flex items-start gap-3 sm:gap-4">
        <span className="grid size-12 shrink-0 place-items-center rounded-full bg-success-200 text-forest-950 sm:size-14">
          <GraduationCap aria-hidden="true" className="size-6 sm:size-7" />
        </span>
        <div>
          <p className="font-bold text-success-700 sm:text-lg">
            Educational simulation — no real money
          </p>
          <p className="mt-1 max-w-4xl text-sm leading-6 text-ink-700 sm:text-base sm:leading-7">
            Northstar Learning Bank is a learning environment. All accounts,
            balances, and transactions are simulated for educational purposes
            only.
          </p>
        </div>
      </div>
      <NorthstarMark className="absolute -right-3 top-1/2 size-28 -translate-y-1/2 text-success-200 opacity-45" />
    </aside>
  );
}
