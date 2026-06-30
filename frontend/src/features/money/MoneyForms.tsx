import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { ApiError } from "../../api/errors";
import { normalizeMoneyInput } from "../../api/money";
import type { Account } from "../../types/api";

type Operation = "deposit" | "withdraw";

export function MoneyForm({ operation }: { operation: Operation }) {
  const { accountId } = useParams();
  const navigate = useNavigate();
  const [amount, setAmount] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    const normalized = normalizeMoneyInput(amount);
    if (!normalized)
      return setError(
        "Enter an amount greater than zero with at most two decimals.",
      );
    setError("");
    try {
      // All unsafe calls pass the one shared CSRF boundary; backend rules remain authoritative.
      await apiRequest<Account>(
        `/api/accounts/${accountId}/${operation === "deposit" ? "deposits" : "withdrawals"}`,
        { method: "POST", body: { amount: normalized } },
      );
      navigate(`/accounts/${accountId}`);
    } catch (cause) {
      setError(
        cause instanceof ApiError
          ? (cause.fields.amount ?? cause.message)
          : "Request failed.",
      );
    }
  }

  return (
    <>
      <h1>{operation === "deposit" ? "Demo deposit" : "Withdraw"}</h1>
      <form onSubmit={(event) => void submit(event)}>
        <label>
          Amount (USD)
          <input
            inputMode="decimal"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <button type="submit">
          {operation === "deposit" ? "Add demo funds" : "Withdraw"}
        </button>
      </form>
    </>
  );
}

export function TransferForm() {
  const navigate = useNavigate();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    void apiRequest<Account[]>("/api/accounts").then(setAccounts);
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const normalized = normalizeMoneyInput(amount);
    if (!normalized) return setError("Enter a valid amount greater than zero.");
    if (!source || !destination || source === destination)
      return setError("Choose two different accounts.");
    try {
      await apiRequest("/api/transfers", {
        method: "POST",
        body: {
          source_account_id: Number(source),
          destination_account_id: Number(destination),
          amount: normalized,
        },
      });
      // Remounting account detail refetches both balance and append-only history after commit.
      navigate(`/accounts/${source}`);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "Transfer failed.");
    }
  }

  return (
    <>
      <h1>Transfer between your accounts</h1>
      <form onSubmit={(event) => void submit(event)}>
        <label>
          From
          <select
            value={source}
            onChange={(event) => setSource(event.target.value)}
          >
            <option value="">Select account</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.account_type} •{account.account_number.slice(-4)}
              </option>
            ))}
          </select>
        </label>
        <label>
          To
          <select
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
          >
            <option value="">Select account</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.account_type} •{account.account_number.slice(-4)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Amount (USD)
          <input
            inputMode="decimal"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <button type="submit">Transfer</button>
      </form>
    </>
  );
}
