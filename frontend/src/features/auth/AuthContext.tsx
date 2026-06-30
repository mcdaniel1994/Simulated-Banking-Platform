/* eslint-disable react-refresh/only-export-components -- Provider and its focused consumer hook form one auth boundary. */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { apiRequest } from "../../api/client";
import { ApiError } from "../../api/errors";
import type { CurrentUser } from "../../types/api";

interface AuthState {
  user: CurrentUser | null;
  loading: boolean;
  login(email: string, password: string): Promise<void>;
  logout(): Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setUser(await apiRequest<CurrentUser>("/api/auth/me"));
    } catch (error) {
      // A 401 is ordinary anonymous state; other errors are left for page-level requests to show.
      if (!(error instanceof ApiError) || error.status !== 401) throw error;
      setUser(null);
    }
  }, []);

  useEffect(() => {
    // Promise callbacks synchronize React with the external session endpoint after mount.
    void apiRequest<CurrentUser>("/api/auth/me")
      .then(setUser)
      .catch((error: unknown) => {
        if (!(error instanceof ApiError) || error.status !== 401) throw error;
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      // Login intentionally has no CSRF prerequisite; the response establishes the cookie pair.
      await apiRequest("/api/auth/login", {
        method: "POST",
        body: { email, password },
      });
      await refresh();
    },
    [refresh],
  );

  const logout = useCallback(async () => {
    // The shared client echoes the readable CSRF cookie before server-side session revocation.
    await apiRequest<void>("/api/auth/logout", { method: "POST" });
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
