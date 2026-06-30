import { Menu, UserRound, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

import { AlertBanner } from "../components/ui/AlertBanner";
import { buttonClassName } from "../components/ui/buttonStyles";
import { NorthstarMark } from "../components/ui/NorthstarMark";
import { useAuth } from "../features/auth/AuthContext";

function navLinkClass({ isActive }: { isActive: boolean }) {
  return `relative inline-flex min-h-11 items-center px-1 text-sm font-semibold text-white transition after:absolute after:inset-x-0 after:bottom-0 after:h-1 after:rounded-full after:bg-gold-300 after:transition-opacity hover:text-gold-300 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-gold-300 ${
    isActive ? "after:opacity-100" : "after:opacity-0"
  }`;
}

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [logoutPending, setLogoutPending] = useState(false);
  const [logoutError, setLogoutError] = useState("");

  useEffect(() => {
    if (!menuOpen) return;
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setMenuOpen(false);
        menuButtonRef.current?.focus();
      }
    }
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [menuOpen]);

  async function handleLogout() {
    setLogoutError("");
    setLogoutPending(true);
    try {
      await logout();
      navigate("/login");
    } catch {
      setLogoutError("Log out could not be completed. Please try again.");
    } finally {
      setLogoutPending(false);
    }
  }

  const customerLinks =
    user?.role === "CUSTOMER"
      ? [{ to: "/dashboard", label: "Accounts", end: false }]
      : [];
  const adminLinks =
    user?.role === "ADMIN"
      ? [
          { to: "/admin", label: "Overview", end: true },
          {
            to: "/admin/customers",
            label: "Manage customers",
            end: false,
          },
        ]
      : [];
  const links = [...customerLinks, ...adminLinks];

  return (
    <div className="min-h-screen bg-ivory-50 text-ink-950">
      <a
        className="fixed left-4 top-4 z-[60] inline-flex min-h-11 -translate-y-24 items-center rounded-md bg-white px-4 py-2 font-semibold text-forest-950 shadow-lg transition focus:translate-y-0"
        href="#main-content"
      >
        Skip to main content
      </a>
      <header className="bg-forest-950 text-white shadow-md">
        <div className="mx-auto flex min-h-20 max-w-7xl items-center gap-3 px-4 sm:gap-7 sm:px-6 lg:px-8">
          <Link
            className="flex min-h-11 items-center gap-2 whitespace-nowrap rounded-md text-base font-bold text-white no-underline focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-gold-300 sm:gap-3 sm:text-xl"
            to="/"
          >
            <NorthstarMark className="size-8 shrink-0 text-gold-300 sm:size-9" />
            <span>Northstar Bank</span>
          </Link>

          <nav
            aria-label="Primary navigation"
            className="hidden self-stretch md:flex md:items-center md:gap-6"
          >
            {links.map((link) => (
              <NavLink
                className={navLinkClass}
                end={link.end}
                key={link.to}
                to={link.to}
              >
                {link.label}
              </NavLink>
            ))}
            {!user && (
              <NavLink className={navLinkClass} to="/login">
                Log in
              </NavLink>
            )}
          </nav>

          <div className="ml-auto hidden items-center gap-4 md:flex">
            {user && (
              <div className="flex items-center gap-2 text-sm">
                <UserRound aria-hidden="true" className="size-5" />
                <span>
                  {user.first_name} {user.last_name} ·{" "}
                  {user.role === "ADMIN" ? "Administrator" : "Customer"}
                </span>
              </div>
            )}
            {user && (
              <button
                className={buttonClassName(
                  "ghost",
                  "border border-white/70 text-white hover:bg-white/10",
                )}
                disabled={logoutPending}
                onClick={() => void handleLogout()}
                type="button"
              >
                {logoutPending ? "Logging out…" : "Log out"}
              </button>
            )}
          </div>

          <button
            aria-expanded={menuOpen}
            aria-label={
              menuOpen ? "Close navigation menu" : "Open navigation menu"
            }
            className="ml-auto grid min-h-11 min-w-11 place-items-center rounded-lg border border-white/70 md:hidden"
            onClick={() => setMenuOpen((open) => !open)}
            ref={menuButtonRef}
            type="button"
          >
            {menuOpen ? (
              <X aria-hidden="true" className="size-6" />
            ) : (
              <Menu aria-hidden="true" className="size-6" />
            )}
          </button>
        </div>

        {menuOpen && (
          <div className="border-t border-white/15 px-4 py-4 md:hidden">
            <nav
              aria-label="Mobile primary navigation"
              className="mx-auto grid max-w-7xl gap-2"
            >
              {links.map((link) => (
                <NavLink
                  className={navLinkClass}
                  end={link.end}
                  key={link.to}
                  onClick={() => setMenuOpen(false)}
                  to={link.to}
                >
                  {link.label}
                </NavLink>
              ))}
              {!user && (
                <NavLink
                  className={navLinkClass}
                  onClick={() => setMenuOpen(false)}
                  to="/login"
                >
                  Log in
                </NavLink>
              )}
              {user && (
                <div className="mt-2 flex flex-col gap-3 border-t border-white/15 pt-4 sm:flex-row sm:items-center sm:justify-between">
                  <span className="flex items-center gap-2 text-sm">
                    <UserRound aria-hidden="true" className="size-5" />
                    {user.first_name} {user.last_name} ·{" "}
                    {user.role === "ADMIN" ? "Administrator" : "Customer"}
                  </span>
                  <button
                    className={buttonClassName(
                      "ghost",
                      "border border-white/70 text-white hover:bg-white/10",
                    )}
                    disabled={logoutPending}
                    onClick={() => void handleLogout()}
                    type="button"
                  >
                    {logoutPending ? "Logging out…" : "Log out"}
                  </button>
                </div>
              )}
            </nav>
          </div>
        )}
      </header>

      <main
        className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8"
        id="main-content"
      >
        {logoutError && (
          <div className="mb-6">
            <AlertBanner
              onDismiss={() => setLogoutError("")}
              title={logoutError}
              tone="error"
            />
          </div>
        )}
        <Outlet />
      </main>
      <footer className="border-t border-stone-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-5 text-center text-sm text-ink-600 sm:px-6 lg:px-8">
          Northstar Bank is a simulated banking application. No real funds or
          financial services are provided.
        </div>
      </footer>
    </div>
  );
}
