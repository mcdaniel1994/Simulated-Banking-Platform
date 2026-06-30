import { PiggyBank, WalletCards } from "lucide-react";

import type { AccountType } from "../../types/api";

// Account-type imagery remains decorative because the adjacent text carries the meaning.
export function AccountIcon({
  accountType,
  className = "",
}: {
  accountType: AccountType;
  className?: string;
}) {
  const Icon = accountType === "CHECKING" ? WalletCards : PiggyBank;
  return (
    <span
      className={`grid size-14 shrink-0 place-items-center rounded-full bg-forest-950 text-white ${className}`}
    >
      <Icon aria-hidden="true" className="size-7" />
    </span>
  );
}
