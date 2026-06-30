import { ArrowDownToLine, ArrowUpFromLine, ArrowLeftRight } from "lucide-react";

import { formatUsd } from "../../api/money";
import type { Account, Transaction, TransactionType } from "../../types/api";

const incomingTypes = new Set<TransactionType>(["DEPOSIT", "TRANSFER_IN"]);

function transactionLabel(type: TransactionType) {
  const labels: Record<TransactionType, string> = {
    DEPOSIT: "Deposit",
    WITHDRAWAL: "Withdrawal",
    TRANSFER_IN: "Transfer in",
    TRANSFER_OUT: "Transfer out",
  };
  return labels[type];
}

function TransactionIcon({ type }: { type: TransactionType }) {
  if (type === "DEPOSIT")
    return <ArrowDownToLine aria-hidden="true" className="size-4" />;
  if (type === "WITHDRAWAL")
    return <ArrowUpFromLine aria-hidden="true" className="size-4" />;
  return <ArrowLeftRight aria-hidden="true" className="size-4" />;
}

function formatDate(value: string) {
  if (!value) return "Date unavailable";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function signedAmount(transaction: Transaction) {
  const incoming = incomingTypes.has(transaction.transaction_type);
  return `${incoming ? "+" : "−"}${formatUsd(transaction.amount)}`;
}

function accountLabel(transaction: Transaction, accounts?: Account[]) {
  const account = accounts?.find(
    (candidate) => candidate.id === transaction.account_id,
  );
  return account
    ? `${account.account_type} •${account.account_number.slice(-4)}`
    : `Account ${transaction.account_id}`;
}

// One semantic dataset renders as a desktop table and compact mobile cards.
export function TransactionList({
  transactions,
  accounts,
  showAccount = false,
}: {
  transactions: Transaction[];
  accounts?: Account[];
  showAccount?: boolean;
}) {
  return (
    <div aria-label="Transaction history" role="list">
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="border-b border-stone-200 text-xs uppercase tracking-wide text-ink-500">
              <th className="px-4 py-3 font-semibold" scope="col">
                Date
              </th>
              <th className="px-4 py-3 font-semibold" scope="col">
                Description
              </th>
              {showAccount && (
                <th className="px-4 py-3 font-semibold" scope="col">
                  Account
                </th>
              )}
              <th className="px-4 py-3 font-semibold" scope="col">
                Type
              </th>
              <th className="px-4 py-3 text-right font-semibold" scope="col">
                Amount
              </th>
              <th className="px-4 py-3 text-right font-semibold" scope="col">
                Balance
              </th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => {
              const incoming = incomingTypes.has(transaction.transaction_type);
              return (
                <tr
                  className="border-b border-stone-200 last:border-0"
                  key={transaction.id}
                >
                  <td className="whitespace-nowrap px-4 py-4 text-sm text-ink-700">
                    {formatDate(transaction.created_at)}
                  </td>
                  <td className="px-4 py-4 text-sm text-ink-950">
                    {transaction.description}
                  </td>
                  {showAccount && (
                    <td className="whitespace-nowrap px-4 py-4 text-sm text-ink-700">
                      {accountLabel(transaction, accounts)}
                    </td>
                  )}
                  <td className="px-4 py-4">
                    <span className="inline-flex items-center gap-2 text-sm text-ink-700">
                      <TransactionIcon type={transaction.transaction_type} />
                      {transactionLabel(transaction.transaction_type)}
                      <span className="sr-only">
                        {transaction.transaction_type}
                      </span>
                    </span>
                  </td>
                  <td
                    className={`whitespace-nowrap px-4 py-4 text-right font-semibold tabular-nums ${
                      incoming ? "text-success-700" : "text-ink-950"
                    }`}
                  >
                    {signedAmount(transaction)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-4 text-right text-sm tabular-nums text-ink-700">
                    {formatUsd(transaction.balance_after)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <ul className="divide-y divide-stone-200 md:hidden" role="presentation">
        {transactions.map((transaction) => {
          const incoming = incomingTypes.has(transaction.transaction_type);
          return (
            <li
              className="grid gap-3 py-5"
              key={transaction.id}
              role="listitem"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-ink-950">
                    {transaction.description}
                  </p>
                  <p className="mt-1 text-sm text-ink-500">
                    {formatDate(transaction.created_at)}
                  </p>
                </div>
                <p
                  className={`font-bold tabular-nums ${
                    incoming ? "text-success-700" : "text-ink-950"
                  }`}
                >
                  {signedAmount(transaction)}
                </p>
              </div>
              <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-ink-700">
                <span className="inline-flex items-center gap-2">
                  <TransactionIcon type={transaction.transaction_type} />
                  {transactionLabel(transaction.transaction_type)}
                  <span className="sr-only">
                    {transaction.transaction_type}
                  </span>
                </span>
                {showAccount && (
                  <span>{accountLabel(transaction, accounts)}</span>
                )}
                <span>Balance {formatUsd(transaction.balance_after)}</span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
