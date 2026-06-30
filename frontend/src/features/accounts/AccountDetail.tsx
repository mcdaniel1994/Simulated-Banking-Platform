import {
  ArrowDownToLine,
  ArrowLeft,
  ArrowLeftRight,
  ArrowUpFromLine,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { formatUsd } from "../../api/money";
import { AccountIcon } from "../../components/accounts/AccountIcon";
import { TransactionList } from "../../components/transactions/TransactionList";
import { AlertBanner } from "../../components/ui/AlertBanner";
import { Button } from "../../components/ui/Button";
import { buttonClassName } from "../../components/ui/buttonStyles";
import { PageState } from "../../components/ui/PageState";
import { StatusBadge } from "../../components/ui/StatusBadge";
import type { Account, Transaction } from "../../types/api";

const PAGE_SIZE = 10;

export interface AccountDetailSuccess {
  title: string;
  message: string;
}

export function AccountDetail() {
  const { accountId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [account, setAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[] | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [success, setSuccess] = useState<AccountDetailSuccess | null>(
    (location.state as { success?: AccountDetailSuccess } | null)?.success ??
      null,
  );

  useEffect(() => {
    if (!success) return;
    // Clear history state so a refreshed page cannot repeat a completed-operation notice.
    navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, navigate, success]);

  useEffect(() => {
    // Both endpoints independently enforce ownership, including guessed URL identifiers.
    void Promise.all([
      apiRequest<Account>(`/api/accounts/${accountId}`),
      apiRequest<Transaction[]>(
        `/api/accounts/${accountId}/transactions?limit=${PAGE_SIZE}&offset=${offset}`,
      ),
    ])
      .then(([nextAccount, nextTransactions]) => {
        setAccount(nextAccount);
        setTransactions(nextTransactions);
        setError("");
      })
      .catch(() => setError("This account could not be loaded."));
  }, [accountId, offset, requestVersion]);

  if (error)
    return (
      <PageState
        kind="error"
        message={error}
        onRetry={() => {
          setAccount(null);
          setTransactions(null);
          setError("");
          setRequestVersion((version) => version + 1);
        }}
        title="We could not load this account"
      />
    );
  if (!account || !transactions)
    return (
      <PageState
        kind="loading"
        message="Retrieving the balance and append-only history."
        title="Loading account"
      />
    );

  const currentPage = offset / PAGE_SIZE + 1;

  return (
    <section>
      <Link
        className="inline-flex min-h-11 items-center gap-2 rounded-md font-semibold text-forest-800 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-forest-700"
        to="/dashboard"
      >
        <ArrowLeft aria-hidden="true" className="size-4" />
        Back to accounts
      </Link>

      <section className="mt-5 grid items-center gap-6 rounded-xl border border-stone-200 bg-white p-6 shadow-card md:grid-cols-[minmax(0,1fr)_auto_auto]">
        <div className="flex items-center gap-5">
          <AccountIcon accountType={account.account_type} />
          <div>
            <h1 className="text-3xl font-bold capitalize text-forest-950">
              {account.account_type.toLowerCase()} account
            </h1>
            <p className="mt-2 tracking-widest text-ink-700">
              •••• {account.account_number.slice(-4)}
            </p>
          </div>
        </div>
        <div>
          <p className="mb-2 text-sm text-ink-500">Status</p>
          <StatusBadge status={account.status} />
        </div>
        <div className="border-t border-stone-200 pt-5 md:border-l md:border-t-0 md:pl-8 md:pt-0">
          <p className="text-sm text-ink-500">Current balance</p>
          <p
            className="mt-1 text-4xl font-bold tabular-nums text-forest-950"
            data-testid="account-balance"
            data-balance={account.balance}
          >
            {formatUsd(account.balance)}
          </p>
        </div>
      </section>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          className={buttonClassName("primary")}
          to={`/accounts/${account.id}/deposit`}
        >
          <ArrowDownToLine aria-hidden="true" className="size-5" />
          Demo deposit
        </Link>
        <Link
          className={buttonClassName("secondary")}
          to={`/accounts/${account.id}/withdraw`}
        >
          <ArrowUpFromLine aria-hidden="true" className="size-5" />
          Withdraw
        </Link>
        <Link className={buttonClassName("secondary")} to="/transfer">
          <ArrowLeftRight aria-hidden="true" className="size-5" />
          Transfer
        </Link>
      </div>

      {success && (
        <div className="mt-6">
          <AlertBanner
            onDismiss={() => setSuccess(null)}
            title={success.title}
            tone="success"
          >
            {success.message}
          </AlertBanner>
        </div>
      )}

      <section className="mt-6 rounded-xl border border-stone-200 bg-white p-5 shadow-card sm:p-7">
        <h2 className="text-2xl font-bold text-ink-950">Transaction history</h2>
        {transactions.length === 0 && offset === 0 ? (
          <div className="py-10 text-center text-ink-700">
            No transactions yet.
          </div>
        ) : (
          <div className="mt-4">
            <TransactionList transactions={transactions} />
          </div>
        )}
        <div className="mt-6 flex items-center justify-center gap-3 border-t border-stone-200 pt-5">
          <Button
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            type="button"
            variant="secondary"
          >
            Previous
          </Button>
          <span
            aria-current="page"
            className="grid min-h-11 min-w-11 place-items-center rounded-lg bg-forest-900 px-3 font-bold text-white"
          >
            Page {currentPage}
          </span>
          <Button
            disabled={transactions.length < PAGE_SIZE}
            onClick={() => setOffset(offset + PAGE_SIZE)}
            type="button"
            variant="secondary"
          >
            Next
          </Button>
        </div>
      </section>
    </section>
  );
}
