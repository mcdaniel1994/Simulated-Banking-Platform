import { ArrowLeft, ShieldCheck } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { ApiError } from "../../api/errors";
import { formatUsd, moneyToCents, normalizeMoneyInput } from "../../api/money";
import { AccountIcon } from "../../components/accounts/AccountIcon";
import { AlertBanner } from "../../components/ui/AlertBanner";
import { Button } from "../../components/ui/Button";
import { FormField } from "../../components/ui/FormField";
import { PageState } from "../../components/ui/PageState";
import { StatusBadge } from "../../components/ui/StatusBadge";
import type { Account } from "../../types/api";
import type { AccountDetailSuccess } from "../accounts/AccountDetail";

type Operation = "deposit" | "withdraw";

const fieldClasses =
  "min-h-12 w-full rounded-lg border border-stone-300 bg-white px-4 py-3 text-ink-950 shadow-sm outline-none transition focus:border-forest-700 focus:ring-3 focus:ring-success-200";

function AccountContext({ account }: { account: Account }) {
  return (
    <section className="flex flex-wrap items-center gap-5 rounded-xl border border-stone-200 bg-white p-5 shadow-card">
      <AccountIcon accountType={account.account_type} />
      <div className="min-w-40 flex-1">
        <p className="text-lg font-bold capitalize text-forest-950">
          {account.account_type.toLowerCase()}
        </p>
        <p className="mt-1 tracking-widest text-ink-700">
          •••• {account.account_number.slice(-4)}
        </p>
      </div>
      <div>
        <p className="mb-2 text-sm text-ink-500">Status</p>
        <StatusBadge status={account.status} />
      </div>
      <div className="min-w-40 border-t border-stone-200 pt-4 sm:border-l sm:border-t-0 sm:pl-6 sm:pt-0">
        <p className="text-sm text-ink-500">Available balance</p>
        <p className="mt-1 text-2xl font-bold tabular-nums text-forest-950">
          {formatUsd(account.balance)}
        </p>
      </div>
    </section>
  );
}

function securityNotice() {
  return (
    <aside className="flex items-start gap-4 rounded-xl border border-info-200 bg-info-50 p-5">
      <span className="grid size-12 shrink-0 place-items-center rounded-full bg-white text-info-700">
        <ShieldCheck aria-hidden="true" className="size-6" />
      </span>
      <div>
        <p className="font-bold text-ink-950">Your security matters</p>
        <p className="mt-1 leading-6 text-ink-700">
          FastAPI validates the session, CSRF token, account ownership, status,
          and available funds before completing any account movement.
        </p>
      </div>
    </aside>
  );
}

export function MoneyForm({ operation }: { operation: Operation }) {
  const { accountId } = useParams();
  const navigate = useNavigate();
  const [account, setAccount] = useState<Account | null>(null);
  const [loadError, setLoadError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [amount, setAmount] = useState("");
  const [amountError, setAmountError] = useState("");
  const [formError, setFormError] = useState("");
  const [pending, setPending] = useState(false);

  useEffect(() => {
    void apiRequest<Account>(`/api/accounts/${accountId}`)
      .then((nextAccount) => {
        setAccount(nextAccount);
        setLoadError("");
      })
      .catch(() => setLoadError("The selected account could not be loaded."));
  }, [accountId, requestVersion]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!account || pending) return;

    const normalized = normalizeMoneyInput(amount);
    if (!normalized) {
      setAmountError(
        "Enter an amount greater than zero with at most two decimals.",
      );
      return;
    }
    if (
      operation === "withdraw" &&
      moneyToCents(normalized) > moneyToCents(account.balance)
    ) {
      setAmountError(
        `Enter an amount less than or equal to ${formatUsd(account.balance)}.`,
      );
      return;
    }

    setAmountError("");
    setFormError("");
    setPending(true);
    try {
      // All unsafe calls pass the one shared CSRF boundary; backend rules remain authoritative.
      await apiRequest<Account>(
        `/api/accounts/${accountId}/${operation === "deposit" ? "deposits" : "withdrawals"}`,
        { method: "POST", body: { amount: normalized } },
      );
      const success: AccountDetailSuccess =
        operation === "deposit"
          ? {
              title: "Funds added",
              message: `${formatUsd(normalized)} was added to your account.`,
            }
          : {
              title: "Withdrawal successful",
              message: `${formatUsd(normalized)} was withdrawn from your account.`,
            };
      navigate(`/accounts/${accountId}`, { state: { success } });
    } catch (cause) {
      if (cause instanceof ApiError && cause.fields.amount) {
        setAmountError(cause.fields.amount);
      } else {
        setFormError(
          cause instanceof ApiError ? cause.message : "Request failed.",
        );
      }
    } finally {
      setPending(false);
    }
  }

  if (loadError)
    return (
      <PageState
        kind="error"
        message={loadError}
        onRetry={() => {
          setAccount(null);
          setLoadError("");
          setRequestVersion((version) => version + 1);
        }}
        title="We could not prepare this transaction"
      />
    );
  if (!account)
    return (
      <PageState
        kind="loading"
        message="Retrieving the selected account and available balance."
        title="Preparing transaction"
      />
    );

  const isDeposit = operation === "deposit";
  return (
    <section>
      <button
        className="inline-flex min-h-11 items-center gap-2 rounded-md font-semibold text-forest-800 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-forest-700"
        onClick={() => navigate(`/accounts/${accountId}`)}
        type="button"
      >
        <ArrowLeft aria-hidden="true" className="size-4" />
        Back to account
      </button>
      <h1 className="mt-4 text-4xl font-bold tracking-tight text-forest-950">
        {isDeposit ? "Add funds" : "Withdraw"}
      </h1>
      <p className="mt-3 text-lg text-ink-700">
        {isDeposit
          ? "Add funds to the selected account."
          : "Withdraw funds without exceeding the available balance."}
      </p>

      <div className="mt-7">
        <AccountContext account={account} />
      </div>

      {formError && (
        <div className="mt-6">
          <AlertBanner
            onDismiss={() => setFormError("")}
            title={
              isDeposit
                ? "We could not add funds"
                : "We could not complete the withdrawal"
            }
            tone="error"
          >
            {formError}
          </AlertBanner>
        </div>
      )}

      <form
        className="mt-6 rounded-xl border border-stone-200 bg-white p-6 shadow-card"
        noValidate
        onSubmit={(event) => void submit(event)}
      >
        <FormField
          error={amountError}
          hint={
            isDeposit
              ? "Enter the amount to add to this account."
              : `You can withdraw up to ${formatUsd(account.balance)}.`
          }
          id="money-amount"
          label="Amount (USD)"
          required
        >
          <div className="relative">
            <span
              aria-hidden="true"
              className="absolute left-4 top-1/2 -translate-y-1/2 font-semibold text-ink-700"
            >
              $
            </span>
            <input
              aria-describedby={[
                amountError ? "money-amount-error" : "",
                "money-amount-hint",
              ]
                .filter(Boolean)
                .join(" ")}
              aria-invalid={Boolean(amountError)}
              aria-required="true"
              className={`${fieldClasses} pl-9`}
              id="money-amount"
              inputMode="decimal"
              onChange={(event) => setAmount(event.target.value)}
              value={amount}
            />
          </div>
        </FormField>
        <div className="mt-6 flex flex-col-reverse gap-3 border-t border-stone-200 pt-5 sm:flex-row sm:justify-end">
          <Button
            disabled={pending}
            onClick={() => navigate(`/accounts/${accountId}`)}
            type="button"
            variant="secondary"
          >
            Cancel
          </Button>
          <Button disabled={pending} type="submit">
            {pending ? "Processing…" : isDeposit ? "Add funds" : "Withdraw"}
          </Button>
        </div>
      </form>
      <div className="mt-6">{securityNotice()}</div>
    </section>
  );
}

export function TransferForm() {
  const navigate = useNavigate();
  const [accounts, setAccounts] = useState<Account[] | null>(null);
  const [loadError, setLoadError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [amount, setAmount] = useState("");
  const [fieldErrors, setFieldErrors] = useState({
    source: "",
    destination: "",
    amount: "",
  });
  const [formError, setFormError] = useState("");
  const [pending, setPending] = useState(false);

  useEffect(() => {
    void apiRequest<Account[]>("/api/accounts")
      .then((nextAccounts) => {
        setAccounts(nextAccounts);
        setLoadError("");
      })
      .catch(() => setLoadError("Your accounts could not be loaded."));
  }, [requestVersion]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!accounts || pending) return;

    const normalized = normalizeMoneyInput(amount);
    const sourceAccount = accounts.find(
      (account) => String(account.id) === source,
    );
    const nextErrors = {
      source: source ? "" : "Choose the account to transfer from.",
      destination: destination
        ? source === destination
          ? "Choose two different accounts."
          : ""
        : "Choose the account to transfer to.",
      amount: normalized
        ? sourceAccount &&
          moneyToCents(normalized) > moneyToCents(sourceAccount.balance)
          ? `Enter an amount less than or equal to ${formatUsd(sourceAccount.balance)}.`
          : ""
        : "Enter an amount greater than zero with at most two decimals.",
    };
    setFieldErrors(nextErrors);
    setFormError("");
    if (nextErrors.source || nextErrors.destination || nextErrors.amount)
      return;

    setPending(true);
    try {
      await apiRequest("/api/transfers", {
        method: "POST",
        body: {
          source_account_id: Number(source),
          destination_account_id: Number(destination),
          amount: normalized,
        },
      });
      const success: AccountDetailSuccess = {
        title: "Transfer successful",
        message: `${formatUsd(normalized!)} moved between your accounts.`,
      };
      navigate(`/accounts/${source}`, { state: { success } });
    } catch (cause) {
      setFormError(
        cause instanceof ApiError ? cause.message : "Transfer failed.",
      );
    } finally {
      setPending(false);
    }
  }

  if (loadError)
    return (
      <PageState
        kind="error"
        message={loadError}
        onRetry={() => {
          setAccounts(null);
          setLoadError("");
          setRequestVersion((version) => version + 1);
        }}
        title="We could not prepare your transfer"
      />
    );
  if (!accounts)
    return (
      <PageState
        kind="loading"
        message="Retrieving eligible accounts and balances."
        title="Preparing transfer"
      />
    );

  const sourceAccount = accounts.find(
    (account) => String(account.id) === source,
  );

  return (
    <section>
      <button
        className="inline-flex min-h-11 items-center gap-2 rounded-md font-semibold text-forest-800 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-forest-700"
        onClick={() => navigate("/dashboard")}
        type="button"
      >
        <ArrowLeft aria-hidden="true" className="size-4" />
        Back to accounts
      </button>
      <h1 className="mt-4 text-4xl font-bold tracking-tight text-forest-950">
        Transfer
      </h1>
      <p className="mt-3 text-lg text-ink-700">
        Move funds between accounts you own.
      </p>

      {formError && (
        <div className="mt-6">
          <AlertBanner
            onDismiss={() => setFormError("")}
            title="We could not complete your transfer"
            tone="error"
          >
            {formError}
          </AlertBanner>
        </div>
      )}

      <form
        className="mt-7 rounded-xl border border-stone-200 bg-white p-6 shadow-card"
        noValidate
        onSubmit={(event) => void submit(event)}
      >
        <div className="grid gap-5 md:grid-cols-2">
          <FormField
            error={fieldErrors.source}
            id="transfer-source"
            label="From"
            required
          >
            <select
              aria-describedby={
                fieldErrors.source ? "transfer-source-error" : undefined
              }
              aria-invalid={Boolean(fieldErrors.source)}
              aria-required="true"
              className={fieldClasses}
              id="transfer-source"
              onChange={(event) => setSource(event.target.value)}
              value={source}
            >
              <option value="">Select account</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.account_type} •{account.account_number.slice(-4)} —{" "}
                  {formatUsd(account.balance)}
                </option>
              ))}
            </select>
          </FormField>
          <FormField
            error={fieldErrors.destination}
            id="transfer-destination"
            label="To"
            required
          >
            <select
              aria-describedby={
                fieldErrors.destination
                  ? "transfer-destination-error"
                  : undefined
              }
              aria-invalid={Boolean(fieldErrors.destination)}
              aria-required="true"
              className={fieldClasses}
              id="transfer-destination"
              onChange={(event) => setDestination(event.target.value)}
              value={destination}
            >
              <option value="">Select account</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.account_type} •{account.account_number.slice(-4)} —{" "}
                  {formatUsd(account.balance)}
                </option>
              ))}
            </select>
          </FormField>
        </div>
        <div className="mt-5 max-w-xl">
          <FormField
            error={fieldErrors.amount}
            hint={
              sourceAccount
                ? `Available to transfer: ${formatUsd(sourceAccount.balance)}.`
                : "Choose a source account to see its available balance."
            }
            id="transfer-amount"
            label="Amount (USD)"
            required
          >
            <div className="relative">
              <span
                aria-hidden="true"
                className="absolute left-4 top-1/2 -translate-y-1/2 font-semibold text-ink-700"
              >
                $
              </span>
              <input
                aria-describedby={[
                  fieldErrors.amount ? "transfer-amount-error" : "",
                  "transfer-amount-hint",
                ]
                  .filter(Boolean)
                  .join(" ")}
                aria-invalid={Boolean(fieldErrors.amount)}
                aria-required="true"
                className={`${fieldClasses} pl-9`}
                id="transfer-amount"
                inputMode="decimal"
                onChange={(event) => setAmount(event.target.value)}
                value={amount}
              />
            </div>
          </FormField>
        </div>
        <div className="mt-6 flex flex-col-reverse gap-3 border-t border-stone-200 pt-5 sm:flex-row sm:justify-end">
          <Button
            disabled={pending}
            onClick={() => navigate("/dashboard")}
            type="button"
            variant="secondary"
          >
            Cancel
          </Button>
          <Button disabled={pending} type="submit">
            {pending ? "Transferring…" : "Transfer"}
          </Button>
        </div>
      </form>
      <div className="mt-6">{securityNotice()}</div>
    </section>
  );
}
