# SPEC.md — Simulated Online Banking Platform

> **Scope legend.** Every requirement in this document is tagged:
> **[MVP]** — required for the CS50x submission.
> **[HARDENING]** — production-hardening work, done after the MVP functions.
> **[EXTENSION]** — optional banking-domain learning extension; documented, not necessarily built.
>
> If a requirement is untagged, treat it as **[MVP]**.
>
> **Governing standard.** All authentication, session, and authorization work in this project MUST clear the bar set by the project's *Authentication & Session Security Standard*. Where this spec defers a rule item, the deferral is deliberate and recorded here, not an oversight.

---

## 1. Project Overview

A **simulated online banking web application** built to teach production-oriented full-stack software engineering. A React/TypeScript single-page app talks to a FastAPI/PostgreSQL backend that enforces realistic banking business rules: authenticated customers manage simulated accounts and move simulated money via deposits, withdrawals, and internal transfers; administrators manage customers and accounts. The system simulates the *engineering concerns* of banking (atomic money movement, ownership enforcement, auditability, integrity verification) without touching real money, real institutions, or real personal data.

The SPA and the API are served from a **single origin** so that authentication can use secure, HttpOnly cookies cleanly.

## 2. Problem Statement

Most learning projects stop at CRUD and never confront the concerns that make real systems hard: race conditions on shared state, money that must never drift, authorization that cannot be bypassed, and operations that must be all-or-nothing. This project deliberately models a domain where those concerns are unavoidable, so they must be solved correctly rather than hand-waved.

## 3. Goals

- Demonstrate a layered full-stack architecture (SPA frontend, service-oriented backend, relational DB).
- Correctly model and enforce financial business rules: ownership, account status, sufficient funds, atomic transfers.
- Guarantee money integrity under concurrency (no overdrafts, no lost updates, no drift between balance and history).
- Implement cookie-based authentication with a **server-side session store** (real, instant revocation) and authorization (role-based + resource-ownership) enforced on the backend.
- Produce a tested, documented, deployable application with a clear path to production hardening.

## 4. Non-Goals

- No connection to real financial institutions; no movement of real money. **[MVP]**
- No real banking credentials, real customer data, or regulatory compliance claims. **[MVP]**
- No multi-currency or foreign exchange — the system uses a **single currency (USD)**. **[MVP]**
- No real identity-document collection (any verification flow is simulated). **[EXTENSION]**
- No overdraft / negative balances. **[MVP]**
- No Supabase Auth — authentication lives inside the FastAPI app. **[MVP]**
- **No self-service registration and no password-reset flow** — all credentials are seeded. Consequently the governing standard's reset-token, breached-password-screening, and registration-enumeration requirements are **out of scope for the MVP**. **[MVP scope note]**
- **No AI agent** acts on a user's behalf, so §14 (AI-Agent Safety) of the governing standard is **not applicable** to this project. **[scope note]**

## 5. User Roles

| Role | Description |
|------|-------------|
| `CUSTOMER` | Owns one or more accounts; performs deposits, withdrawals, and transfers between their own accounts; views their own data only. |
| `ADMIN` | Manages customers and accounts; views aggregate and per-customer data; activates/deactivates customers and freezes/unfreezes accounts. Does **not** operate accounts as if an owner. |

## 6. User Stories

**Customer**
- As a customer, I can log in with seeded demo credentials and log out, where logout immediately ends my session server-side.
- As a customer, I can view my accounts, individual balances, and a combined balance.
- As a customer, I can view and paginate my transaction history.
- As a customer, I can make a simulated deposit to an account I own and active.
- As a customer, I can withdraw from an account I own and active, but never more than its balance.
- As a customer, I can transfer between two accounts I own, atomically, and see updated balances.
- As a customer, I am blocked (by the server) from viewing or touching any account I do not own, and from any admin endpoint.

**Administrator**
- As an admin, I can log in with seeded admin credentials and see an admin-only dashboard with summary statistics.
- As an admin, I can list customers and open a customer's detail (their accounts and transactions).
- As an admin, I can activate or deactivate a customer, and freeze or unfreeze an account.
- As an admin, I cannot perform customer money operations as though I owned the accounts.

## 7. Functional Requirements

### 7.1 Authentication **[MVP]**
- Login by email + password; password verified with Argon2id.
- On successful login the server creates a **server-side session record** and sets the session cookie(s) per §9. JavaScript never reads the auth cookie.
- `GET /auth/me` returns the current user resolved from the session.
- **Logout is a real server-side action:** it revokes the session record so the cookie can no longer authenticate, even before any expiry.

### 7.2 Accounts **[MVP]**
- List the authenticated customer's accounts.
- Retrieve a single account the customer owns (404 if not owned).

### 7.3 Transactions **[MVP]**
- List transactions for an owned account, paginated (limit/offset).
- List the customer's transactions across their accounts, paginated.
- Transaction history is **append-only**: no update/delete of transaction rows.

### 7.4 Deposit **[MVP]**
1. Validate `amount > 0` and within precision/limits.
2. Lock and load the account row (`SELECT ... FOR UPDATE`).
3. Confirm the account exists, is owned by the caller, and is `ACTIVE`.
4. Increase the balance.
5. Insert a `DEPOSIT` transaction with `balance_after`.
6. Commit; return the updated account.
- Deposits are presented in the UI as **demo funding**, not real deposits.

### 7.5 Withdrawal **[MVP]**
1. Validate `amount > 0`.
2. Lock and load the account row.
3. Confirm exists, owned, and `ACTIVE`.
4. Confirm `balance >= amount` (no overdraft).
5. Decrease the balance.
6. Insert a `WITHDRAWAL` transaction with `balance_after`.
7. Commit; return the updated account.

### 7.6 Transfer **[MVP]**
1. Validate `amount > 0`.
2. Confirm source ≠ destination.
3. Lock and load **both** account rows in a consistent order (e.g. by id) to avoid deadlock.
4. Confirm both exist, both owned by the caller, both `ACTIVE`.
5. Confirm source `balance >= amount`.
6. Create a `Transfer` row (status `COMPLETED`).
7. Debit source; insert `TRANSFER_OUT` (with shared `reference_id` = transfer id).
8. Credit destination; insert `TRANSFER_IN` (same `reference_id`).
9. Commit all of the above in **one atomic transaction**; any failure rolls back the whole operation.

### 7.7 Admin **[MVP]**
- Dashboard summary statistics (counts of customers, accounts, total simulated balance, recent transaction count).
- List customers; open customer detail (their accounts + transactions).
- Activate / deactivate a customer (deactivation also revokes that customer's active sessions).
- Freeze / unfreeze an account.

## 8. Business Rules

- **Money type:** all amounts are `Decimal`, stored as `NUMERIC(14,2)`; rounding is half-up to 2 decimal places. No floats anywhere in the money path.
- **No overdraft:** withdrawals and transfer debits require `balance >= amount`; enforced in the service **and** by a DB `CHECK (balance >= 0)` constraint.
- **Ownership:** customers may only read or mutate accounts they own; enforced server-side via a shared dependency on every account-scoped route. Not-owned resources return **404**.
- **Account status gates operations:** only `ACTIVE` accounts accept deposits, withdrawals, and transfers. `FROZEN` and `CLOSED` accounts reject all money movement.
- **Inactive users cannot authenticate or operate:** `is_active = false` blocks login, and deactivating a user revokes their sessions.
- **Balance is a cache, the log is truth:** the stored `balance` is updated atomically with each transaction; the transaction log is the source of truth. A reconciliation check (`sum of signed transactions == stored balance`) must hold. **[MVP test]** / **[EXTENSION as admin tool]**
- **Concurrency:** balance-mutating operations lock the affected account row(s) for the duration of the transaction to prevent lost updates and races.
- **Append-only history:** transaction rows are never updated or deleted; corrections happen via new compensating transactions. **[EXTENSION]**
- **Admins are not owners:** admin endpoints never reuse customer ownership logic to operate accounts.

## 9. Authentication & Authorization Requirements

> This section is the project's binding interpretation of the governing standard. The backend is the only security boundary; the SQL database is the source of truth for users, roles, and active sessions.

### 9.1 Password handling **[MVP]**
- Argon2id with parameters at or above the standard's floor (≥19 MiB memory, iterations=2, parallelism=1). Use `argon2-cffi`. Verify in constant time; re-hash on login if parameters rise.
- Passwords are never stored in plaintext and never logged.

### 9.2 Session mechanism — chosen approach **[MVP]**
- **Opaque server-side sessions.** On login the server generates a high-entropy random session token, stores its **hash** in a `sessions` table (never the raw token), and sets it in a cookie. Each request resolves the session by looking up the hashed token; an invalid, expired, or revoked session yields 401.
- Cookie attributes (per §9.5): `HttpOnly`, `Secure`, `SameSite=Strict`, scoped `Path`, `__Host-` prefix where possible, `Max-Age` ≤ session lifetime.
- Sessions have an **absolute expiry** and an **idle timeout**; both are enforced server-side.
- **Logout, password change, and admin deactivation revoke the session immediately** by flagging the DB record — this is the payoff of a server-side store.
- Rationale for choosing opaque sessions over JWT for the MVP: instant revocation for free, no signature/`alg`/claim verification footguns, simplest correct option, and it satisfies the standard's *recommended* (server-side session) tier. See §24 for the JWT alternative.

### 9.3 CSRF protection **[MVP]**
- Because authentication rides on cookies, **every state-changing request (POST/PATCH) must carry CSRF protection**, verified server-side. `SameSite` and CORS are defense-in-depth, **not** CSRF protection on their own.
- Chosen pattern: **double-submit token** — a readable (non-HttpOnly) CSRF cookie is issued at session start and must be echoed in an `X-CSRF-Token` request header; the server rejects state-changing requests where the header and cookie do not match.
- Safe methods (GET) do not require the CSRF token.

### 9.4 Authorization **[MVP]**
- Three server-side layers on every protected route: (1) authenticated-session dependency, (2) role check (`CUSTOMER` vs `ADMIN`), (3) resource-ownership check.
- No IDOR: every account/transaction query is filtered by the authenticated principal; changing an ID in the URL never reaches another user's data (404).
- Roles come from SQL, resolved per request; a client-supplied role is never trusted.

### 9.5 General requirements **[MVP]**
- HTTPS/TLS only; cookies set `Secure`.
- Generic auth-failure messages ("invalid email or password") — no user enumeration.
- Secrets (session signing/pepper key, DB URL) come from environment variables.
- Sensitive data is never placed in cookies beyond the opaque token; PII and permissions stay in SQL.

### 9.6 Deferred (still required for production) **[HARDENING]**
- Refresh-token rotation with reuse-detection and family revocation (only relevant if/when switching to the JWT model in §24).
- Login / token-refresh **rate limiting and lockout**.
- Strict Content-Security-Policy and the full security-header set.
- Step-up / re-authentication for sensitive operations.

## 10. Database Entities & Relationships

> Money columns: `NUMERIC(14,2)`. Timestamps: `TIMESTAMPTZ`, stored in UTC.

### User **[MVP]**
`id`, `email` (unique), `password_hash`, `first_name`, `last_name`, `role` (`CUSTOMER`|`ADMIN`), `is_active`, `created_at`, `updated_at`.

### Session **[MVP]**
`id`, `user_id` (FK → User), `token_hash` (unique; raw token never stored), `created_at`, `last_used_at`, `expires_at`, `revoked_at` (nullable), `user_agent`/`ip` (optional, for audit).
Index on `token_hash`; index on `user_id`. Resolving a request finds a non-revoked, non-expired session by `token_hash`.
> If the JWT alternative in §24 is chosen, this becomes a `refresh_tokens` table with a `family_id` and rotation semantics.

### Account **[MVP]**
`id`, `user_id` (FK → User), `account_number` (unique, generated), `account_type` (`CHECKING`|`SAVINGS`), `balance` `NUMERIC(14,2)`, `status` (`ACTIVE`|`FROZEN`|`CLOSED`), `created_at`, `updated_at`.
Constraints: `CHECK (balance >= 0)`; index on `user_id`.

### Transaction **[MVP]** (append-only)
`id`, `account_id` (FK → Account), `transaction_type` (`DEPOSIT`|`WITHDRAWAL`|`TRANSFER_IN`|`TRANSFER_OUT`), `amount` `NUMERIC(14,2)`, `description`, `balance_after` `NUMERIC(14,2)`, `reference_id` (nullable; links the two legs of a transfer), `created_at`.
Index on `account_id, created_at`.

### Transfer **[MVP, minimal]**
`id`, `source_account_id` (FK), `destination_account_id` (FK), `amount` `NUMERIC(14,2)`, `status` (`COMPLETED`|`FAILED`), `created_at`.
Parents the two transaction legs (`reference_id = transfer.id`); enables reconciliation; foreshadows a future ledger.

### AuditEvent **[MVP, minimal — deferrable]**
`id`, `actor_user_id` (nullable FK), `event_type`, `entity_type`, `entity_id`, `metadata` (JSON), `created_at`.
MVP events: login success, login failure, logout, customer deposit/withdrawal/transfer, customer activation/deactivation, account freeze/unfreeze, permission-denied. If time is short, this table moves to **[HARDENING]**.

**Relationships:** User 1—* Account; User 1—* Session; Account 1—* Transaction; Transfer references two Accounts and is referenced by two Transactions via `reference_id`; AuditEvent optionally references an actor User.

### Later transaction types **[EXTENSION]**
`REVERSAL`, `ADJUSTMENT`, `FEE`, `INTEREST` — add only when a specific learning goal needs them.

## 11. API Capability Map

> Same-origin: the SPA and API share a host, so these are relative paths under `/api`. Money amounts are serialized as **JSON strings**, not numbers. All errors use the envelope in §13. State-changing requests require the `X-CSRF-Token` header (§9.3).

**Auth [MVP]**
```
POST /api/auth/login      -> verify credentials, create session, set HttpOnly cookie + CSRF cookie
POST /api/auth/logout     -> revoke session server-side, clear cookies
GET  /api/auth/me         -> current user from session
```
**Accounts [MVP]**
```
GET  /api/accounts
GET  /api/accounts/{account_id}
```
**Transactions [MVP]**
```
GET  /api/accounts/{account_id}/transactions   ?limit=&offset=
GET  /api/transactions                          ?limit=&offset=
```
**Money operations [MVP]** (CSRF-protected)
```
POST /api/accounts/{account_id}/deposits
POST /api/accounts/{account_id}/withdrawals
POST /api/transfers
GET  /api/transfers/{transfer_id}
```
**Admin [MVP]** (CSRF-protected for mutations)
```
GET   /api/admin/dashboard
GET   /api/admin/users
GET   /api/admin/users/{user_id}
PATCH /api/admin/users/{user_id}/status        (activate/deactivate; deactivation revokes sessions)
PATCH /api/admin/accounts/{account_id}/status  (freeze/unfreeze)
```
**Ops [MVP]**
```
GET  /api/health          -> liveness
```
**[HARDENING]**
```
GET  /api/ready           -> readiness (DB reachable)
POST /api/auth/refresh    -> only if the JWT + rotating-refresh model (§24) is adopted
```
Money POSTs accept an optional `Idempotency-Key` header (ignored in MVP, honored in hardening). **[HARDENING]**

Consolidation note: global `/admin/accounts` and `/admin/transactions` *list* pages fold into customer-detail drill-downs for the MVP. **[MVP decision]**

## 12. Frontend Pages & Routing

```
frontend/src/
  api/          # typed client, money parsing, error mapping, CSRF header injection
  components/   # reusable UI (forms, cards, states)
  features/     # auth, accounts, transactions, transfers, admin
  hooks/
  layouts/      # public, customer, admin shells
  pages/
  routes/       # public / customer / admin route groups
  types/
  utils/
```

**Public:** Landing, Login (with demo credentials shown), Unauthorized, Not-Found.
**Customer:** Dashboard (account cards + combined balance), Account Detail, Transaction History, Deposit, Withdrawal, Transfer. Profile **[EXTENSION]**.
**Admin:** Dashboard (stats), Customer List, Customer Detail (accounts + transactions drill-down), status controls. Audit/flagged views **[EXTENSION]**.

Frontend rules: the auth cookie is invisible to JS by design; the client reads the **CSRF cookie** and injects `X-CSRF-Token` on state-changing calls. Auth state is derived from `GET /auth/me` on load (and held in React Context), not from any client-stored token. Explicit loading/empty/error states; responsive layouts. The frontend hides unauthorized features for UX; the backend remains the security boundary.

State: React Context for auth state; native `fetch` via a small typed API client (sends credentials, attaches CSRF header). No Redux/Zustand/React Query unless a concrete need emerges.

## 13. Error-Handling Strategy **[MVP]**

- **Common envelope:** `{ "error": { "code": "<MACHINE_CODE>", "message": "<human readable>", "fields": { "<name>": "<reason>" } } }`.
- **Defined codes (initial):** `VALIDATION_ERROR`, `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `CSRF_INVALID`, `INSUFFICIENT_FUNDS`, `INACTIVE_ACCOUNT`, `SAME_ACCOUNT_TRANSFER`, `INACTIVE_USER`, `INTERNAL_ERROR`.
- **Mapping:** services raise typed domain errors; a single FastAPI exception handler maps them to status codes + the envelope. Routes stay thin.
- **No leakage:** internal exceptions never expose stack traces, SQL, tokens, or cookies to clients; they log server-side and return `INTERNAL_ERROR`.
- **Frontend:** the API client maps the envelope to user-facing messages and field-level form errors.

## 14. Testing Strategy

**Backend [MVP] (highest priority):**
- Auth: successful login (session created, cookie set with `HttpOnly`/`Secure`/`SameSite`); invalid credentials (generic message, no enumeration); inactive-user login blocked; missing/invalid/expired session → 401.
- **Logout revokes the session** (the same cookie no longer authenticates); admin deactivation revokes the customer's sessions.
- **CSRF:** a state-changing request without a valid `X-CSRF-Token` is rejected (`CSRF_INVALID`); with a valid one it succeeds.
- Authorization: customer denied admin endpoints (403); customer cannot reach another customer's account by ID (404, no IDOR).
- Deposit: success; amount ≤ 0; deposit to inactive/frozen account.
- Withdrawal: success; insufficient funds; inactive/frozen account.
- Transfer: success; same-account; account not owned; **rollback on induced failure** (assert no balance changed); **concurrency test** (two parallel withdrawals cannot overdraw).
- Reconciliation: stored balance equals signed sum of transactions.
- Error consistency: validation/DB errors return the common envelope; **logs/error responses contain no tokens, cookies, or secrets** (assert redaction).

**Frontend [MVP]:** login form validation, successful/failed login rendering, protected-route behavior, dashboard account rendering, deposit/withdrawal/transfer form validation, CSRF-header attachment on mutations, API-error rendering, role-specific navigation.

**End-to-end [MVP, one flow]:** Customer login → dashboard → deposit → withdraw → transfer → verify history. **[HARDENING]:** Admin deactivates a customer → that customer's active session is rejected on next request.

Priority order: backend auth/CSRF/business-rule/rollback/concurrency tests first; a thin layer of frontend component tests; a single happy-path E2E. Refresh-rotation reuse tests apply only under the §24 JWT model.

## 15. Security Requirements

- Backend enforces all authn/authz; frontend never trusted. **[MVP]**
- Argon2id hashing; no plaintext passwords; generic login errors. **[MVP]**
- Opaque session token stored **hashed** in SQL; raw token only in the cookie. **[MVP]**
- Cookies set `HttpOnly`, `Secure`, `SameSite=Strict`, scoped `Path`, `__Host-` prefix where possible. **[MVP]**
- CSRF token (double-submit) on all state-changing requests. **[MVP]**
- Real server-side revocation on logout / password change / deactivation. **[MVP]**
- Same-origin deployment; CORS configured narrowly (only needed for local dev cross-port). **[MVP]**
- Secrets from environment; none committed. **[MVP]**
- Never log passwords, hashes, raw tokens, cookies, or `Authorization`/`Cookie` headers; mask account numbers. **[MVP]**
- Not-owned resources return 404 (avoid existence disclosure). **[MVP]**
- `CHECK (balance >= 0)` integrity backstop. **[MVP]**
- Security headers (HSTS, `X-Content-Type-Options: nosniff`, frame/referrer policy) and a strict CSP; login rate limiting/lockout; dependency vulnerability scanning; security-review checklist. **[HARDENING]**

## 16. Logging & Audit Requirements

- **MVP:** application logs to stdout with sensitive fields redacted (per the standard's logging rules). Log auth events — login success/failure, logout, permission-denied — with user ID, timestamp, and a correlation ID, never the credentials. Minimal `AuditEvent` rows for the events in §10 (deferrable if time-constrained).
- **Hardening:** structured (JSON) logging, per-request **request/correlation IDs** propagated through logs, centralized error logging, audit-event retention; refresh-reuse-detection events (under the JWT model).
- **Extension:** admin UI to browse audit events; fraud-flag events.

## 17. Deployment Architecture

```
[ Browser ]
     │  HTTPS
[ Reverse proxy on Hostinger VPS  (Caddy or nginx, TLS termination) ]
     ├── serves the built React SPA at  /
     └── proxies  /api/*  to the FastAPI app (same origin → clean SameSite=Strict cookies)
                         │  pooled connection (Supabase pooler URL)
                  [ Supabase: PostgreSQL ]
```
- **Single origin on the VPS** (e.g. `https://bank.example.com`): the reverse proxy serves the static SPA build and proxies `/api` to FastAPI. This is the deployment decision that makes HttpOnly + `SameSite=Strict` cookies work without cross-site complications. **[MVP]**
- **Vercel is dropped** from the MVP (it was only needed for the split-origin design). It may return later as an optional CDN/edge experiment, but co-locating is the chosen path. **[decision]**
- Backend Dockerized; reverse proxy provides HTTPS (Caddy gives automatic certificates). **[HARDENING → completed before final submission]**
- PostgreSQL on Supabase: align region with the VPS; use the **pooler** connection string; size the SQLAlchemy pool for a long-lived process. Note the free-tier **idle-pause** — add a keep-alive or warn reviewers. **[MVP note]**
- Production migrations via `alembic upgrade head` as a defined deploy step.
- Fallback: if VPS ops becomes a time sink, a PaaS can host the combined app, at the cost of the reverse-proxy lesson. **[decision]**

## 18. Environment Strategy

- Environments: **local dev**, **production**.
- Config via environment variables: `DATABASE_URL`, `SESSION_SECRET` (pepper/signing key), `SESSION_IDLE_MINUTES`, `SESSION_ABSOLUTE_HOURS`, `COOKIE_DOMAIN`, `CORS_ORIGINS` (dev only), `CSRF_COOKIE_NAME`, `ENV`.
- In local dev the SPA dev server and API may run on different ports → enable a narrow CORS allowlist with credentials for dev only; in production they share an origin and CORS is effectively unused.
- `.env.example` committed; real `.env` git-ignored.
- Separate dev and prod databases; never run tests against prod.
- Production startup validation: app refuses to boot if required env vars are missing or a default/insecure secret is detected. **[HARDENING]**

## 19. Demo-Data Requirements **[MVP]**

- **Deterministic, idempotent seed script** creating: one `ADMIN` user; at least two `CUSTOMER` users; each customer with a `CHECKING` and a `SAVINGS` account holding non-zero starting balances; and a spread of historical transactions so dashboards are not empty.
- Demo credentials for both roles are **printed on the login page** for reviewers.
- **Drift handling (decided):** an idempotent reseed script run before submission; in-session drift from reviewer testing is accepted.
- Seed never contains real personal data.

## 20. Milestones

| Phase | Outcome | Scope |
|------|---------|-------|
| 0 | Scope, user stories, acceptance criteria, this SPEC frozen | MVP |
| 1 | Repos, env, lint/format, structure | MVP |
| 2 | Postgres + SQLAlchemy models (incl. `sessions`) + Alembic + seed | MVP |
| 3 | Argon2id, cookie login, server-side sessions, CSRF, current-user dep, role checks + tests | MVP |
| 4 | Accounts, deposit, withdrawal, transfer w/ locking + atomicity + tests | MVP |
| 5 | Admin dashboard, customer/account management + authz tests | MVP |
| 6 | Frontend routing, landing, login, auth state from `/auth/me`, protected routes | MVP |
| 7 | Customer dashboard + money workflows (CSRF header wired in) | MVP |
| 8 | Admin dashboard + management UI | MVP |
| 9 | Error handling, validation, test pass, one E2E | MVP |
| 10 | Deploy: single origin on VPS (reverse proxy serves SPA + proxies /api), HTTPS, Supabase, migrations, seed | MVP |
| 11 | Logging, correlation IDs, rate limiting, CSP/headers, health/ready, CI, backups, runbook | HARDENING |
| 12 | JWT + rotating refresh upgrade; fraud rules; reconciliation tool; identity workflow; ledger | EXTENSION |
| 13 | README, design write-up, install/deploy docs, AI-assistance citation, video | MVP |

## 21. MVP Acceptance Criteria

The MVP is complete when all of the following hold:

1. A reviewer can log in as the demo customer and the demo admin using credentials shown on the login page; the auth cookie is `HttpOnly`, `Secure`, `SameSite=Strict`.
2. A customer can view accounts, balances, and paginated history; perform a deposit, a withdrawal, and an internal transfer; and see correct updated balances after each.
3. Withdrawals and transfers exceeding the balance are rejected with `INSUFFICIENT_FUNDS`; no balance changes.
4. Operations on inactive/frozen accounts are rejected; same-account transfers are rejected.
5. A transfer that fails midway leaves both balances unchanged (verified by test).
6. Two concurrent withdrawals cannot overdraw an account (verified by test); `CHECK (balance >= 0)` holds.
7. For every account, stored balance equals the signed sum of its transactions (reconciliation test passes).
8. A customer cannot read or mutate another customer's account (404) and cannot reach admin endpoints (403).
9. **Logout immediately invalidates the session server-side** (the same cookie can no longer authenticate); admin deactivation revokes the customer's sessions.
10. A state-changing request without a valid CSRF token is rejected (`CSRF_INVALID`).
11. An admin can list customers, open a customer's detail, deactivate a customer, and freeze an account; an admin cannot operate customer accounts as an owner.
12. All API errors use the common envelope; money is serialized as strings; logs/errors contain no tokens, cookies, or secrets.
13. The app is deployed from a **single origin** on the VPS behind HTTPS, with the DB on Supabase and migrations + seed applied.
14. Backend auth/CSRF/business-rule/rollback/concurrency/reconciliation tests pass; the one happy-path E2E passes.
15. README documents the project, design decisions, install/deploy steps, and cites AI assistance; the demo video exists.

## 22. Deferred Features

- **JWT access token + rotating refresh token** upgrade of the auth layer (satisfies the original JWT learning goal as a deliberate refactor). **[EXTENSION / HARDENING]**
- Admin approval workflow for deposits/withdrawals (pending-state machine). **[EXTENSION]**
- `REVERSAL`/`ADJUSTMENT`/`FEE`/`INTEREST` transaction types. **[EXTENSION]**
- Customer profile editing; self-registration; password reset. **[EXTENSION]**
- Step-up / re-authentication for sensitive operations. **[HARDENING]**
- Multi-currency / FX. **[NON-GOAL]**

## 23. Production-Hardening Backlog

Ordered by educational value:

1. Structured JSON logging + per-request correlation IDs.
2. Idempotency keys honored on deposit/withdrawal/transfer.
3. Login/refresh rate limiting and lockout.
4. CI running the full test suite on push.
5. Dockerized backend + reverse-proxy hardening + HSTS/CSP/security headers.
6. `/ready` readiness check (DB reachability).
7. **JWT access + rotating refresh token with reuse-detection / family revocation** (the JWT learning upgrade).
8. DB backup strategy, deployment runbook, rollback documentation.
9. Production env validation on boot; dependency vulnerability scanning.
10. Basic monitoring; security-review checklist.

## 24. Open Decisions

1. **Session mechanism — RESOLVED for MVP: opaque server-side sessions in an HttpOnly cookie.** Open sub-decision: whether to upgrade to **short JWT access token + rotating refresh token** during hardening (Phase 12) to exercise the original JWT learning goal, or keep opaque sessions. *Recommendation: ship opaque sessions, refactor to JWT later as a learning exercise.*
2. **CSRF mechanism — RESOLVED: double-submit token** (`X-CSRF-Token` header vs CSRF cookie). Confirm vs synchronizer-token-in-session.
3. **Deployment — RESOLVED: single origin on the VPS; Vercel dropped.** Confirm the reverse proxy choice (Caddy for auto-TLS vs nginx).
4. **Money precision** — `NUMERIC(14,2)`; confirm.
5. **Minimal AuditEvent table in MVP** — include vs defer to hardening.
6. **Repository layer depth** — recommended lightweight/optional, services primary; confirm.
7. **Session lifetimes** — pick idle timeout and absolute expiry values.
8. **VPS vs PaaS** for hosting if VPS ops becomes a time sink.
9. **Ledger timing** — balance-based first, refactor toward double-entry as an extension; confirm it stays deferred.

---

### Architecture summary (request lifecycle)

```
HTTP request (cookie auth + X-CSRF-Token on mutations)
  → reverse proxy (TLS, serves SPA, proxies /api)
  → FastAPI route (thin)
  → Pydantic request schema (validation)
  → session dependency (resolve + verify session from SQL) → CSRF check → role + ownership checks
  → application service (business rules, row locking, atomic tx)
  → SQLAlchemy session / lightweight query helpers
  → PostgreSQL
  → Pydantic response schema (money as strings)
  → common error envelope on failure
```
The **service layer is the heart of the project**; keep it well-tested. Repositories are lightweight helpers, not a mandated per-entity layer. The transaction log is the source of truth; the stored balance is an atomically-maintained cache verified by reconciliation. Authentication is cookie-based with a server-side session store, giving real revocation; CSRF protection guards every state-changing route.
