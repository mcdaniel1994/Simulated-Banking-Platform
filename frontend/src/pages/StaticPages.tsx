import { BookOpen, Landmark, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

import { buttonClassName } from "../components/ui/buttonStyles";

export function LandingPage() {
  return (
    <section>
      <div className="grid items-center gap-10 py-6 lg:grid-cols-[1.1fr_0.9fr] lg:py-14">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.18em] text-forest-700">
            Learn production-oriented engineering
          </p>
          <h1 className="mt-4 max-w-3xl text-4xl font-bold tracking-tight text-forest-950 sm:text-6xl">
            Simulated banking, exact by design.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-ink-700">
            Explore secure sessions, account ownership, atomic transfers, and
            append-only transaction history without connecting real money or a
            financial institution.
          </p>
          <div className="mt-8">
            <Link className={buttonClassName("primary")} to="/login">
              Use the demo
            </Link>
          </div>
        </div>
        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
          {[
            {
              icon: ShieldCheck,
              title: "Secure by design",
              body: "Server-side sessions, CSRF protection, roles, and ownership stay authoritative in FastAPI.",
            },
            {
              icon: Landmark,
              title: "Exact money",
              body: "Decimal strings and integer cents avoid floating-point drift throughout the browser.",
            },
            {
              icon: BookOpen,
              title: "Built to teach",
              body: "The interface explains the engineering ideas without presenting itself as a real bank.",
            },
          ].map(({ icon: Icon, title, body }) => (
            <article
              className="rounded-xl border border-stone-200 bg-white p-5 shadow-card"
              key={title}
            >
              <Icon aria-hidden="true" className="size-6 text-forest-700" />
              <h2 className="mt-3 font-bold text-ink-950">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-ink-700">{body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function MessagePage({ title, message }: { title: string; message: string }) {
  return (
    <section className="mx-auto max-w-xl rounded-2xl border border-stone-200 bg-white p-8 text-center shadow-card">
      <h1 className="text-3xl font-bold text-forest-950">{title}</h1>
      <p className="mt-4 leading-7 text-ink-700">{message}</p>
      <Link className={buttonClassName("primary", "mt-6")} to="/">
        Return home
      </Link>
    </section>
  );
}

export function UnauthorizedPage() {
  return (
    <MessagePage
      message="Your signed-in role does not have access to this page."
      title="Access unavailable"
    />
  );
}

export function NotFoundPage() {
  return (
    <MessagePage
      message="The page you requested does not exist or may have moved."
      title="Page not found"
    />
  );
}
