import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";
import { CustomerDashboard } from "../features/accounts/CustomerDashboard";
import { AccountDetail } from "../features/accounts/AccountDetail";
import { MoneyForm, TransferForm } from "../features/money/MoneyForms";
import {
  AdminDashboardPage,
  CustomerDetailPage,
  CustomerListPage,
} from "../features/admin/AdminPages";
import { AppLayout } from "../layouts/AppLayout";
import { LoginPage } from "../pages/LoginPage";
import {
  LandingPage,
  NotFoundPage,
  UnauthorizedPage,
} from "../pages/StaticPages";
import { PageState } from "../components/ui/PageState";
import type { UserRole } from "../types/api";

function RequireAuth({
  role,
  children,
}: {
  role?: UserRole;
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  if (loading)
    return (
      <PageState
        kind="loading"
        message="Resolving your secure server-side session."
        title="Checking session"
      />
    );
  if (!user) return <Navigate to="/login" replace />;
  // Role checks improve navigation only; every protected API call is authorized again by FastAPI.
  if (role && user.role !== role)
    return <Navigate to="/unauthorized" replace />;
  return children;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="unauthorized" element={<UnauthorizedPage />} />
        <Route
          path="dashboard"
          element={
            <RequireAuth role="CUSTOMER">
              <CustomerDashboard />
            </RequireAuth>
          }
        />
        <Route
          path="accounts/:accountId"
          element={
            <RequireAuth role="CUSTOMER">
              <AccountDetail />
            </RequireAuth>
          }
        />
        <Route
          path="accounts/:accountId/deposit"
          element={
            <RequireAuth role="CUSTOMER">
              <MoneyForm operation="deposit" />
            </RequireAuth>
          }
        />
        <Route
          path="accounts/:accountId/withdraw"
          element={
            <RequireAuth role="CUSTOMER">
              <MoneyForm operation="withdraw" />
            </RequireAuth>
          }
        />
        <Route
          path="transfer"
          element={
            <RequireAuth role="CUSTOMER">
              <TransferForm />
            </RequireAuth>
          }
        />
        <Route
          path="admin"
          element={
            <RequireAuth role="ADMIN">
              <AdminDashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="admin/customers"
          element={
            <RequireAuth role="ADMIN">
              <CustomerListPage />
            </RequireAuth>
          }
        />
        <Route
          path="admin/customers/:userId"
          element={
            <RequireAuth role="ADMIN">
              <CustomerDetailPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
