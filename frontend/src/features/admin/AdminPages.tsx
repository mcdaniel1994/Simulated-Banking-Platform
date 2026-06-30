import {
  ArrowLeft,
  ArrowRight,
  Landmark,
  LockKeyhole,
  ReceiptText,
  Users,
  WalletCards,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { formatUsd } from "../../api/money";
import { AccountIcon } from "../../components/accounts/AccountIcon";
import { TransactionList } from "../../components/transactions/TransactionList";
import { AlertBanner } from "../../components/ui/AlertBanner";
import { Button } from "../../components/ui/Button";
import { buttonClassName } from "../../components/ui/buttonStyles";
import { ConfirmDialog } from "../../components/ui/ConfirmDialog";
import { PageState } from "../../components/ui/PageState";
import { StatusBadge } from "../../components/ui/StatusBadge";
import type {
  Account,
  AdminCustomer,
  AdminCustomerDetail as CustomerDetail,
  AdminDashboard as Dashboard,
} from "../../types/api";

function useRemote<T>(path: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      setData(await apiRequest<T>(path));
    } catch {
      setError("Administrator data could not be loaded.");
    }
  }, [path]);

  useEffect(() => {
    // Initial retrieval synchronizes this view with the protected administrator endpoint.
    void apiRequest<T>(path)
      .then((nextData) => {
        setData(nextData);
        setError("");
      })
      .catch(() => setError("Administrator data could not be loaded."));
  }, [path]);

  return { data, error, load };
}

function AdminState({
  data,
  error,
  onRetry,
  noun,
}: {
  data: unknown;
  error: string;
  onRetry: () => void;
  noun: string;
}) {
  if (error)
    return (
      <PageState
        kind="error"
        message={error}
        onRetry={onRetry}
        title={`We could not load ${noun}`}
      />
    );
  if (!data)
    return (
      <PageState
        kind="loading"
        message={`Retrieving current ${noun} from the protected administrator API.`}
        title={`Loading ${noun}`}
      />
    );
  return null;
}

function formatDate(value: string) {
  if (!value) return "Date unavailable";
  return new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(
    new Date(value),
  );
}

export function AdminDashboardPage() {
  const remote = useRemote<Dashboard>("/api/admin/dashboard");
  const state = (
    <AdminState
      data={remote.data}
      error={remote.error}
      noun="the administrator overview"
      onRetry={() => void remote.load()}
    />
  );
  if (!remote.data || remote.error) return state;

  const metrics = [
    {
      label: "Customers",
      value: String(remote.data.customer_count),
      detail: "Registered customer profiles",
      Icon: Users,
    },
    {
      label: "Accounts",
      value: String(remote.data.account_count),
      detail: "Simulated bank accounts",
      Icon: WalletCards,
    },
    {
      label: "Simulated balance",
      value: formatUsd(remote.data.total_simulated_balance),
      detail: "Across all customer accounts",
      Icon: Landmark,
    },
    {
      label: "Recent activity",
      value: String(remote.data.recent_transaction_count),
      detail: `Transactions in the last ${remote.data.recent_window_days} days`,
      Icon: ReceiptText,
    },
  ];

  return (
    <section>
      <p className="text-sm font-bold uppercase tracking-widest text-success-700">
        Administrator overview
      </p>
      <h1 className="mt-2 text-4xl font-bold tracking-tight text-forest-950">
        Learning bank activity
      </h1>
      <p className="mt-3 max-w-3xl text-lg leading-7 text-ink-700">
        Review simulated customer and account activity without entering customer
        money workflows.
      </p>

      <div className="mt-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(({ label, value, detail, Icon }) => (
          <article
            className="rounded-xl border border-stone-200 bg-white p-5 shadow-card"
            key={label}
          >
            <span className="grid size-11 place-items-center rounded-full bg-success-50 text-forest-800">
              <Icon aria-hidden="true" className="size-5" />
            </span>
            <p className="mt-5 text-sm font-semibold text-ink-500">{label}</p>
            <p className="mt-1 text-3xl font-bold tabular-nums text-forest-950">
              {value}
            </p>
            <p className="mt-2 text-sm leading-5 text-ink-700">{detail}</p>
          </article>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap items-center justify-between gap-5 rounded-xl border border-stone-200 bg-white p-6 shadow-card">
        <div>
          <h2 className="text-xl font-bold text-forest-950">
            Customer management
          </h2>
          <p className="mt-1 text-ink-700">
            Review profiles, account statuses, and recent transaction history.
          </p>
        </div>
        <Link className={buttonClassName("primary")} to="/admin/customers">
          Manage customers
          <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
      </div>
    </section>
  );
}

export function CustomerListPage() {
  const remote = useRemote<AdminCustomer[]>("/api/admin/users");
  const state = (
    <AdminState
      data={remote.data}
      error={remote.error}
      noun="customers"
      onRetry={() => void remote.load()}
    />
  );
  if (!remote.data || remote.error) return state;
  if (!remote.data.length)
    return (
      <PageState
        kind="empty"
        message="Customer records will appear here when they are available."
        title="No customers found"
      />
    );

  return (
    <section>
      <p className="text-sm font-bold uppercase tracking-widest text-success-700">
        Administrator
      </p>
      <h1 className="mt-2 text-4xl font-bold tracking-tight text-forest-950">
        Manage customers
      </h1>
      <p className="mt-3 text-lg text-ink-700">
        Review customer access and open a profile to manage its accounts.
      </p>

      <ul className="mt-8 grid gap-4">
        {remote.data.map((customer) => (
          <li
            className="rounded-xl border border-stone-200 bg-white p-5 shadow-card"
            key={customer.id}
          >
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
              <span
                aria-hidden="true"
                className="grid size-14 shrink-0 place-items-center rounded-full bg-success-200 text-lg font-bold text-forest-900"
              >
                {customer.first_name[0]}
                {customer.last_name[0]}
              </span>
              <div className="min-w-0 flex-1">
                <h2 className="text-lg font-bold text-forest-950">
                  {customer.first_name} {customer.last_name}
                </h2>
                <p className="mt-1 break-all text-sm text-ink-700">
                  {customer.email}
                </p>
              </div>
              <StatusBadge
                status={customer.is_active ? "ACTIVE_USER" : "INACTIVE_USER"}
              />
              <Link
                aria-label={`View ${customer.first_name} ${customer.last_name}`}
                className={buttonClassName("secondary")}
                to={`/admin/customers/${customer.id}`}
              >
                View details
                <ArrowRight aria-hidden="true" className="size-4" />
              </Link>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

type PendingAction =
  | { kind: "customer"; nextActive: boolean }
  | { kind: "account"; account: Account; nextStatus: "ACTIVE" | "FROZEN" };

function confirmationCopy(action: PendingAction | null) {
  if (!action) return { title: "", description: "", confirmLabel: "" };
  if (action.kind === "customer") {
    return action.nextActive
      ? {
          title: "Activate customer?",
          description:
            "This restores the customer’s ability to sign in and use eligible accounts.",
          confirmLabel: "Activate customer",
        }
      : {
          title: "Deactivate customer?",
          description:
            "This prevents the customer from signing in and using every account. Existing balances and history remain unchanged.",
          confirmLabel: "Deactivate customer",
        };
  }
  return action.nextStatus === "FROZEN"
    ? {
        title: `Freeze ${action.account.account_type.toLowerCase()} account?`,
        description:
          "This prevents withdrawals and transfers from this account. Its balance and history remain unchanged.",
        confirmLabel: "Freeze account",
      }
    : {
        title: `Unfreeze ${action.account.account_type.toLowerCase()} account?`,
        description:
          "This restores eligible withdrawals and transfers for this account.",
        confirmLabel: "Unfreeze account",
      };
}

export function CustomerDetailPage() {
  const { userId } = useParams();
  const remote = useRemote<CustomerDetail>(
    `/api/admin/users/${userId}?limit=10&offset=0`,
  );
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(
    null,
  );
  const [mutationPending, setMutationPending] = useState(false);
  const [mutationError, setMutationError] = useState("");
  const [success, setSuccess] = useState("");

  async function confirmMutation() {
    if (!pendingAction || mutationPending) return;
    setMutationError("");
    setSuccess("");
    setMutationPending(true);
    try {
      if (pendingAction.kind === "customer") {
        await apiRequest<AdminCustomer>(`/api/admin/users/${userId}/status`, {
          method: "PATCH",
          body: { is_active: pendingAction.nextActive },
        });
        setSuccess(
          pendingAction.nextActive
            ? "Customer access restored."
            : "Customer access deactivated.",
        );
      } else {
        await apiRequest<Account>(
          `/api/admin/accounts/${pendingAction.account.id}/status`,
          {
            method: "PATCH",
            body: { status: pendingAction.nextStatus },
          },
        );
        setSuccess(
          pendingAction.nextStatus === "FROZEN"
            ? "Account frozen."
            : "Account unfrozen.",
        );
      }
      setPendingAction(null);
      await remote.load();
    } catch {
      setMutationError(
        "The status change could not be completed. No administrator setting was changed.",
      );
    } finally {
      setMutationPending(false);
    }
  }

  const state = (
    <AdminState
      data={remote.data}
      error={remote.error}
      noun="this customer"
      onRetry={() => void remote.load()}
    />
  );
  if (!remote.data || remote.error) return state;

  const { customer, accounts, transactions } = remote.data;
  const copy = confirmationCopy(pendingAction);

  return (
    <section>
      <Link
        className="inline-flex min-h-11 items-center gap-2 rounded-md font-semibold text-forest-800 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-forest-700"
        to="/admin/customers"
      >
        <ArrowLeft aria-hidden="true" className="size-4" />
        Back to customers
      </Link>
      <h1 className="mt-4 text-4xl font-bold tracking-tight text-forest-950">
        Customer details
      </h1>

      {success && (
        <div className="mt-6">
          <AlertBanner
            onDismiss={() => setSuccess("")}
            title={success}
            tone="success"
          />
        </div>
      )}
      {mutationError && (
        <div className="mt-6">
          <AlertBanner
            onDismiss={() => setMutationError("")}
            title="Status change unsuccessful"
            tone="error"
          >
            {mutationError}
          </AlertBanner>
        </div>
      )}

      <article className="mt-7 rounded-xl border border-stone-200 bg-white shadow-card">
        <div className="flex flex-col gap-5 p-6 md:flex-row md:items-center">
          <span
            aria-hidden="true"
            className="grid size-16 shrink-0 place-items-center rounded-full bg-success-200 text-xl font-bold text-forest-900"
          >
            {customer.first_name[0]}
            {customer.last_name[0]}
          </span>
          <div className="min-w-0 flex-1">
            <h2 className="text-2xl font-bold text-forest-950">
              {customer.first_name} {customer.last_name}
            </h2>
            <p className="mt-1 break-all text-ink-700">{customer.email}</p>
          </div>
          <div>
            <p className="mb-2 text-sm text-ink-500">Status</p>
            <StatusBadge
              status={customer.is_active ? "ACTIVE_USER" : "INACTIVE_USER"}
            />
          </div>
          <div className="border-t border-stone-200 pt-4 md:border-l md:border-t-0 md:pl-6 md:pt-0">
            <p className="text-sm text-ink-500">Customer since</p>
            <p className="mt-1 font-semibold text-ink-950">
              {formatDate(customer.created_at)}
            </p>
          </div>
          <Button
            onClick={() =>
              setPendingAction({
                kind: "customer",
                nextActive: !customer.is_active,
              })
            }
            type="button"
            variant={customer.is_active ? "danger" : "secondary"}
          >
            {customer.is_active ? "Deactivate customer" : "Activate customer"}
          </Button>
        </div>
        <p className="border-t border-stone-200 px-6 py-3 text-sm text-ink-700">
          Deactivation prevents sign-in and account use; it does not alter
          balances or transaction records.
        </p>
      </article>

      <section className="mt-8" aria-labelledby="customer-accounts">
        <h2
          className="text-xl font-bold text-forest-950"
          id="customer-accounts"
        >
          Accounts ({accounts.length})
        </h2>
        {accounts.length ? (
          <div className="mt-4 grid gap-4">
            {accounts.map((account) => (
              <article
                className="flex flex-col gap-5 rounded-xl border border-stone-200 bg-white p-5 shadow-card md:flex-row md:items-center"
                key={account.id}
              >
                <AccountIcon accountType={account.account_type} />
                <div className="min-w-36 flex-1">
                  <h3 className="text-lg font-bold capitalize text-forest-950">
                    {account.account_type.toLowerCase()}
                  </h3>
                  <p className="mt-1 tracking-widest text-ink-700">
                    •••• {account.account_number.slice(-4)}
                  </p>
                </div>
                <div className="min-w-36">
                  <p className="text-sm text-ink-500">Balance</p>
                  <p className="mt-1 text-xl font-bold tabular-nums text-forest-950">
                    {formatUsd(account.balance)}
                  </p>
                </div>
                <div className="min-w-28">
                  <p className="mb-2 text-sm text-ink-500">Status</p>
                  <StatusBadge status={account.status} />
                </div>
                <Button
                  disabled={account.status === "CLOSED"}
                  onClick={() =>
                    setPendingAction({
                      kind: "account",
                      account,
                      nextStatus:
                        account.status === "ACTIVE" ? "FROZEN" : "ACTIVE",
                    })
                  }
                  type="button"
                  variant={account.status === "ACTIVE" ? "danger" : "secondary"}
                >
                  <LockKeyhole aria-hidden="true" className="size-4" />
                  {account.status === "CLOSED"
                    ? "Account closed"
                    : account.status === "ACTIVE"
                      ? "Freeze account"
                      : "Unfreeze account"}
                </Button>
              </article>
            ))}
          </div>
        ) : (
          <p className="mt-4 rounded-xl border border-stone-200 bg-white p-5 text-ink-700">
            This customer has no accounts.
          </p>
        )}
      </section>

      <section
        aria-labelledby="recent-transactions"
        className="mt-8 rounded-xl border border-stone-200 bg-white shadow-card"
      >
        <div className="border-b border-stone-200 p-5">
          <h2
            className="text-xl font-bold text-forest-950"
            id="recent-transactions"
          >
            Recent transactions
          </h2>
          <p className="mt-1 text-sm text-ink-700">
            The latest activity supplied by the existing administrator detail
            endpoint.
          </p>
        </div>
        {transactions.length ? (
          <div className="px-5 pb-2">
            <TransactionList
              accounts={accounts}
              showAccount
              transactions={transactions}
            />
          </div>
        ) : (
          <p className="p-6 text-ink-700">
            No transactions are available for this customer.
          </p>
        )}
      </section>

      <ConfirmDialog
        confirmLabel={copy.confirmLabel}
        description={copy.description}
        onCancel={() => {
          if (!mutationPending) setPendingAction(null);
        }}
        onConfirm={() => void confirmMutation()}
        open={Boolean(pendingAction)}
        pending={mutationPending}
        title={copy.title}
      />
    </section>
  );
}
