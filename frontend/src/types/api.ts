// These public shapes mirror the frozen FastAPI response contract; sensitive ORM fields are absent.
export type UserRole = "CUSTOMER" | "ADMIN";

export interface CurrentUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    fields: Record<string, string>;
  };
}

export interface HealthResponse {
  status: "ok";
}

export type AccountStatus = "ACTIVE" | "FROZEN" | "CLOSED";
export type AccountType = "CHECKING" | "SAVINGS";

export interface Account {
  id: number;
  account_number: string;
  account_type: AccountType;
  balance: string;
  status: AccountStatus;
  created_at: string;
  updated_at: string;
}

export type TransactionType =
  "DEPOSIT" | "WITHDRAWAL" | "TRANSFER_IN" | "TRANSFER_OUT";

export interface Transaction {
  id: number;
  account_id: number;
  transaction_type: TransactionType;
  amount: string;
  description: string;
  balance_after: string;
  reference_id: number | null;
  created_at: string;
}

export interface AdminDashboard {
  customer_count: number;
  account_count: number;
  total_simulated_balance: string;
  recent_transaction_count: number;
  recent_window_days: number;
}

export interface AdminCustomer {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AdminCustomerDetail {
  customer: AdminCustomer;
  accounts: Account[];
  transactions: Transaction[];
  transaction_limit: number;
  transaction_offset: number;
}
