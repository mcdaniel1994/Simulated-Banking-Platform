import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiRequest } from "../../api/client";
import { formatUsd } from "../../api/money";
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
    // Initial retrieval synchronizes this view with the protected admin endpoint.
    void apiRequest<T>(path)
      .then(setData)
      .catch(() => setError("Administrator data could not be loaded."));
  }, [path]);
  return { data, error, load };
}

export function AdminDashboardPage() {
  const { data, error } = useRemote<Dashboard>("/api/admin/dashboard");
  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">Loading dashboard…</p>;
  return (
    <>
      <h1>Admin dashboard</h1>
      <div className="cards">
        <p className="panel">Customers: {data.customer_count}</p>
        <p className="panel">Accounts: {data.account_count}</p>
        <p className="panel">
          Simulated balance: {formatUsd(data.total_simulated_balance)}
        </p>
        <p className="panel">
          Recent transactions: {data.recent_transaction_count}
        </p>
      </div>
      <Link to="/admin/customers">Manage customers</Link>
    </>
  );
}

export function CustomerListPage() {
  const { data, error } = useRemote<AdminCustomer[]>("/api/admin/users");
  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">Loading customers…</p>;
  if (!data.length) return <p>No customers found.</p>;
  return (
    <>
      <h1>Customers</h1>
      <ul>
        {data.map((customer) => (
          <li key={customer.id}>
            <Link to={`/admin/customers/${customer.id}`}>
              {customer.first_name} {customer.last_name}
            </Link>{" "}
            — {customer.is_active ? "Active" : "Inactive"}
          </li>
        ))}
      </ul>
    </>
  );
}

export function CustomerDetailPage() {
  const { userId } = useParams();
  const { data, error, load } = useRemote<CustomerDetail>(
    `/api/admin/users/${userId}?limit=10&offset=0`,
  );
  const [mutationError, setMutationError] = useState("");

  async function setCustomerStatus(is_active: boolean) {
    try {
      await apiRequest<AdminCustomer>(`/api/admin/users/${userId}/status`, {
        method: "PATCH",
        body: { is_active },
      });
      await load();
    } catch {
      setMutationError("Customer status could not be changed.");
    }
  }

  async function setAccountStatus(account: Account) {
    const status = account.status === "ACTIVE" ? "FROZEN" : "ACTIVE";
    try {
      await apiRequest<Account>(`/api/admin/accounts/${account.id}/status`, {
        method: "PATCH",
        body: { status },
      });
      await load();
    } catch {
      setMutationError("Account status could not be changed.");
    }
  }

  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">Loading customer…</p>;
  return (
    <>
      <h1>
        {data.customer.first_name} {data.customer.last_name}
      </h1>
      <p>{data.customer.email}</p>
      <button
        type="button"
        onClick={() => void setCustomerStatus(!data.customer.is_active)}
      >
        {data.customer.is_active ? "Deactivate customer" : "Activate customer"}
      </button>
      {mutationError && <p role="alert">{mutationError}</p>}
      <h2>Accounts</h2>
      {data.accounts.map((account) => (
        <article className="panel" key={account.id}>
          <p>
            {account.account_type} •{account.account_number.slice(-4)} —{" "}
            {account.status}
          </p>
          <button
            type="button"
            disabled={account.status === "CLOSED"}
            onClick={() => void setAccountStatus(account)}
          >
            {account.status === "ACTIVE"
              ? "Freeze account"
              : "Unfreeze account"}
          </button>
        </article>
      ))}
    </>
  );
}
