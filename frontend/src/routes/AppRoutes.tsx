import { Navigate, Route, Routes } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";
import { AppLayout } from "../layouts/AppLayout";
import { LoginPage } from "../pages/LoginPage";
import {
  AdminHome,
  CustomerHome,
  LandingPage,
  NotFoundPage,
  UnauthorizedPage,
} from "../pages/StaticPages";
import type { UserRole } from "../types/api";

function RequireAuth({
  role,
  children,
}: {
  role?: UserRole;
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  if (loading) return <p role="status">Checking session…</p>;
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
              <CustomerHome />
            </RequireAuth>
          }
        />
        <Route
          path="admin"
          element={
            <RequireAuth role="ADMIN">
              <AdminHome />
            </RequireAuth>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
