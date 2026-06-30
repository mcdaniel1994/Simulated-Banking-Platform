import { ChevronRight, Landmark, Lightbulb } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { formatUsd, addMoney } from "../../api/money";
import { AccountIcon } from "../../components/accounts/AccountIcon";
import { buttonClassName } from "../../components/ui/buttonStyles";
import { PageState } from "../../components/ui/PageState";
import { StatusBadge } from "../../components/ui/StatusBadge";
import type { Account } from "../../types/api";

export function CustomerDashboard() {
  const [accounts, setAccounts] = useState<Account[] | null>(null);
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    // The backend applies SQL ownership; the page never filters an untrusted global account list.
    void apiRequest<Account[]>("/api/accounts")
      .then((nextAccounts) => {
        setAccounts(nextAccounts);
        setError("");
      })
      .catch(() => setError("Accounts could not be loaded safely."));
  }, [requestVersion]);

  if (error)
    return (
      <PageState
        kind="error"
        message={error}
        onRetry={() => {
          setAccounts(null);
          setError("");
          setRequestVersion((version) => version + 1);
        }}
        title="We could not load your accounts"
      />
    );
  if (!accounts)
    return (
      <PageState
        kind="loading"
        message="Retrieving balances from your protected accounts."
        title="Loading accounts"
      />
    );
  if (accounts.length === 0)
    return (
      <PageState
        kind="empty"
        message="An administrator must create an account before banking exercises can begin."
        title="No accounts are available."
      />
    );

  return (
    <section>
      <h1 className="text-4xl font-bold tracking-tight text-forest-950">
        Accounts
      </h1>
      <p className="mt-3 text-lg text-ink-700">
        View your accounts, balances, and recent activity in this simulated
        environment.
      </p>

      <section className="mt-8 grid overflow-hidden rounded-xl border border-stone-200 bg-white shadow-card lg:grid-cols-2">
        <div className="p-6 sm:p-8">
          <p className="text-lg font-semibold text-ink-950">Combined balance</p>
          <p className="mt-2 text-4xl font-bold tabular-nums text-forest-950 sm:text-5xl">
            {formatUsd(addMoney(accounts.map((account) => account.balance)))}
          </p>
        </div>
        <div className="flex items-center gap-4 border-t border-stone-200 p-6 sm:p-8 lg:border-l lg:border-t-0">
          <span className="grid size-14 shrink-0 place-items-center rounded-full bg-success-50 text-forest-900">
            <Landmark aria-hidden="true" className="size-7" />
          </span>
          <div>
            <p className="font-bold text-ink-950">
              All balances are sample data
            </p>
            <p className="mt-1 leading-6 text-ink-700">
              Use this environment to practice financial skills and explore
              banking concepts.
            </p>
          </div>
        </div>
      </section>

      <h2 className="mt-8 text-xl font-bold text-forest-950">Your accounts</h2>
      <div className="mt-4 grid gap-4">
        {accounts.map((account) => (
          <article
            className="grid items-center gap-5 rounded-xl border border-stone-200 bg-white p-5 shadow-card md:grid-cols-[minmax(0,1.2fr)_minmax(9rem,0.8fr)_minmax(8rem,0.7fr)_auto]"
            key={account.id}
            data-account-id={account.id}
            data-balance={account.balance}
          >
            <div className="flex items-center gap-4">
              <AccountIcon accountType={account.account_type} />
              <div>
                <h3 className="text-xl font-bold capitalize text-forest-950">
                  {account.account_type.toLowerCase()}
                </h3>
                <p className="mt-1 tracking-wider text-ink-700">
                  •••• {account.account_number.slice(-4)}
                </p>
              </div>
            </div>
            <div className="border-t border-stone-200 pt-4 md:border-l md:border-t-0 md:pl-6 md:pt-0">
              <p className="text-sm text-ink-500">Balance</p>
              <p className="mt-1 text-2xl font-bold tabular-nums text-forest-950">
                {formatUsd(account.balance)}
              </p>
            </div>
            <div>
              <p className="mb-2 text-sm text-ink-500">Status</p>
              <StatusBadge status={account.status} />
            </div>
            <Link
              className={buttonClassName("primary", "w-full md:w-auto")}
              to={`/accounts/${account.id}`}
            >
              View account
              <ChevronRight aria-hidden="true" className="size-4" />
            </Link>
          </article>
        ))}
      </div>

      <aside className="mt-6 flex items-start gap-4 rounded-xl border border-warning-200 bg-warning-50 p-5">
        <span className="grid size-12 shrink-0 place-items-center rounded-full bg-warning-200 text-warning-700">
          <Lightbulb aria-hidden="true" className="size-6" />
        </span>
        <div>
          <p className="font-bold text-ink-950">Learning tip</p>
          <p className="mt-1 leading-6 text-ink-700">
            Review your recent transactions to see how each simulated decision
            affects your balance. You can deposit, withdraw, or transfer between
            your accounts.
          </p>
        </div>
      </aside>
    </section>
  );
}
