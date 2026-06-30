import { Link, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <>
      <nav aria-label="Primary navigation">
        <Link to="/">Northstar Learning Bank</Link>
        {user?.role === "CUSTOMER" && <Link to="/dashboard">Accounts</Link>}
        {user?.role === "ADMIN" && <Link to="/admin">Admin</Link>}
        {!user && <Link to="/login">Log in</Link>}
        {user && (
          <button
            type="button"
            onClick={() => void logout().then(() => navigate("/login"))}
          >
            Log out
          </button>
        )}
      </nav>
      <main>
        <Outlet />
      </main>
    </>
  );
}
