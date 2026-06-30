import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { formatUsd } from "../../api/money";
import type { Account, Transaction } from "../../types/api";

const PAGE_SIZE = 10;

export function AccountDetail() {
  const { accountId } = useParams();
  const [account, setAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[] | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState("");

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
      })
      .catch(() => setError("This account could not be loaded."));
  }, [accountId, offset]);

  if (error) return <p role="alert">{error}</p>;
  if (!account || !transactions) return <p role="status">Loading account…</p>;

  return (
    <>
      <Link to="/dashboard">Back to accounts</Link>
      <h1>{account.account_type} account</h1>
      <p className="panel">Balance: {formatUsd(account.balance)}</p>
      <div className="row">
        <Link to={`/accounts/${account.id}/deposit`}>Demo deposit</Link>
        <Link to={`/accounts/${account.id}/withdraw`}>Withdraw</Link>
        <Link to="/transfer">Transfer</Link>
      </div>
      <h2>Transaction history</h2>
      {transactions.length === 0 && offset === 0 ? (
        <p>No transactions yet.</p>
      ) : (
        <ul>
          {transactions.map((transaction) => (
            <li key={transaction.id}>
              {transaction.transaction_type}: {formatUsd(transaction.amount)} —{" "}
              {transaction.description}
            </li>
          ))}
        </ul>
      )}
      <div className="row">
        <button
          type="button"
          disabled={offset === 0}
          onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
        >
          Previous
        </button>
        <button
          type="button"
          disabled={transactions.length < PAGE_SIZE}
          onClick={() => setOffset(offset + PAGE_SIZE)}
        >
          Next
        </button>
      </div>
    </>
  );
}
