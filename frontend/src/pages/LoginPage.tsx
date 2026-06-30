import { ShieldCheck, UserRound } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { AlertBanner } from "../components/ui/AlertBanner";
import { Button } from "../components/ui/Button";
import { FormField } from "../components/ui/FormField";
import { ApiError } from "../api/errors";
import { useAuth } from "../features/auth/AuthContext";

const fieldClasses =
  "min-h-12 w-full rounded-lg border border-stone-300 bg-white px-4 py-3 text-ink-950 shadow-sm outline-none transition placeholder:text-ink-500 focus:border-forest-700 focus:ring-3 focus:ring-success-200";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState({
    email: "",
    password: "",
  });
  const [formError, setFormError] = useState("");
  const [pending, setPending] = useState(false);

  if (user)
    return (
      <Navigate to={user.role === "ADMIN" ? "/admin" : "/dashboard"} replace />
    );

  async function submit(event: FormEvent) {
    event.preventDefault();
    const nextErrors = {
      email: email.includes("@") ? "" : "Enter a valid email address.",
      password: password ? "" : "Enter your password.",
    };
    setFieldErrors(nextErrors);
    setFormError("");
    if (nextErrors.email || nextErrors.password) return;

    setPending(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (cause) {
      setFormError(
        cause instanceof ApiError
          ? cause.message
          : "Unable to log in right now.",
      );
    } finally {
      setPending(false);
    }
  }

  function fillDemoCredentials(role: "customer" | "admin") {
    setEmail(
      role === "customer"
        ? "alex.customer@demo.bank.test"
        : "admin@demo.bank.test",
    );
    setPassword(role === "customer" ? "CustomerDemo!2026" : "AdminDemo!2026");
    setFieldErrors({ email: "", password: "" });
    setFormError("");
  }

  return (
    <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">
      <section>
        <p className="text-sm font-bold uppercase tracking-[0.18em] text-forest-700">
          Secure demo access
        </p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-forest-950">
          Welcome to Northstar
        </h1>
        <p className="mt-4 max-w-xl text-lg leading-8 text-ink-700">
          Sign in with a seeded demonstration identity to explore exact money
          handling, secure sessions, and role-based banking workflows.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          <button
            className="rounded-xl border border-stone-200 bg-white p-5 text-left shadow-card transition hover:border-forest-700 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-forest-700"
            onClick={() => fillDemoCredentials("customer")}
            type="button"
          >
            <span className="flex items-center gap-3 font-bold text-forest-950">
              <UserRound aria-hidden="true" className="size-5" />
              Customer demo
            </span>
            <span className="mt-2 block break-all text-sm text-ink-700">
              alex.customer@demo.bank.test
            </span>
            <span className="mt-3 block text-sm font-semibold text-forest-700">
              Use customer demo
            </span>
          </button>
          <button
            className="rounded-xl border border-stone-200 bg-white p-5 text-left shadow-card transition hover:border-forest-700 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-forest-700"
            onClick={() => fillDemoCredentials("admin")}
            type="button"
          >
            <span className="flex items-center gap-3 font-bold text-forest-950">
              <ShieldCheck aria-hidden="true" className="size-5" />
              Administrator demo
            </span>
            <span className="mt-2 block break-all text-sm text-ink-700">
              admin@demo.bank.test
            </span>
            <span className="mt-3 block text-sm font-semibold text-forest-700">
              Use administrator demo
            </span>
          </button>
        </div>
      </section>

      <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-card sm:p-8">
        <h2 className="text-2xl font-bold text-ink-950">Log in</h2>
        <p className="mt-2 text-ink-700">
          Demo credentials are public and contain no real customer data.
        </p>
        {formError && (
          <div className="mt-5">
            <AlertBanner title={formError} tone="error" />
          </div>
        )}
        <form
          className="mt-6 grid gap-5"
          noValidate
          onSubmit={(event) => void submit(event)}
        >
          <FormField
            error={fieldErrors.email}
            id="login-email"
            label="Email"
            required
          >
            <input
              aria-describedby={
                fieldErrors.email ? "login-email-error" : undefined
              }
              aria-invalid={Boolean(fieldErrors.email)}
              aria-required="true"
              autoComplete="username"
              className={fieldClasses}
              id="login-email"
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              value={email}
            />
          </FormField>
          <FormField
            error={fieldErrors.password}
            id="login-password"
            label="Password"
            required
          >
            <input
              aria-describedby={
                fieldErrors.password ? "login-password-error" : undefined
              }
              aria-invalid={Boolean(fieldErrors.password)}
              aria-required="true"
              autoComplete="current-password"
              className={fieldClasses}
              id="login-password"
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              value={password}
            />
          </FormField>
          <Button className="w-full" disabled={pending} type="submit">
            {pending ? "Logging in…" : "Log in"}
          </Button>
        </form>
      </section>
    </div>
  );
}
