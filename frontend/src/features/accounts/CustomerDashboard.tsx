import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { formatUsd, addMoney } from "../../api/money";
import type { Account } from "../../types/api";

export function CustomerDashboard() {
  const [accounts, setAccounts] = useState<Account[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // The backend applies SQL ownership; the page never filters an untrusted global account list.
    void apiRequest<Account[]>("/api/accounts")
      .then(setAccounts)
      .catch(() => setError("Accounts could not be loaded safely."));
  }, []);

  if (error) return <p role="alert">{error}</p>;
  if (!accounts) return <p role="status">Loading accounts…</p>;
  if (accounts.length === 0) return <p>No accounts are available.</p>;

  return (
    <>
      <p className="eyebrow">Customer overview</p>
      <h1>Your accounts</h1>
      <p className="panel">
        Combined balance:{" "}
        <strong>
          {formatUsd(addMoney(accounts.map((account) => account.balance)))}
        </strong>
      </p>
      <div className="cards">
        {accounts.map((account) => (
          <article
            className="panel"
            key={account.id}
            data-account-id={account.id}
            data-balance={account.balance}
          >
            <h2>{account.account_type}</h2>
            <p>Account ending {account.account_number.slice(-4)}</p>
            <p>{formatUsd(account.balance)}</p>
            <p>Status: {account.status}</p>
            <Link to={`/accounts/${account.id}`}>View account</Link>
          </article>
        ))}
      </div>
    </>
  );
}
