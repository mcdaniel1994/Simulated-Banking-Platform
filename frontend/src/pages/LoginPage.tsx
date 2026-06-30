import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../api/errors";
import { useAuth } from "../features/auth/AuthContext";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  if (user)
    return (
      <Navigate to={user.role === "ADMIN" ? "/admin" : "/dashboard"} replace />
    );

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (!email.includes("@") || !password) {
      setError("Enter a valid email and password.");
      return;
    }
    try {
      await login(email, password);
      navigate("/");
    } catch (cause) {
      setError(
        cause instanceof ApiError
          ? cause.message
          : "Unable to log in right now.",
      );
    }
  }

  return (
    <>
      <p className="eyebrow">Secure demo access</p>
      <h1>Log in</h1>
      <form onSubmit={(event) => void submit(event)}>
        <label>
          Email
          <input
            type="email"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Log in</button>
      </form>
      <section aria-label="Demo credentials" className="panel">
        <p>Customer: alex.customer@demo.bank.test / CustomerDemo!2026</p>
        <p>Admin: admin@demo.bank.test / AdminDemo!2026</p>
      </section>
    </>
  );
}
