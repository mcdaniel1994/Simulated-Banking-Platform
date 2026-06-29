# Project Progress

Operational checklist for the build. Phase names and numbers match
[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) exactly. Update this as you go; record the
*reasoning* in [MY_WORKFLOW.md](MY_WORKFLOW.md), not here.

Status values: `NOT STARTED` · `IN PROGRESS` · `BLOCKED` · `COMPLETE` · `DEFERRED`.

## Current Status
- Current milestone: M5 — Admin Backend (in progress)
- Current phase: Phase 25 — Admin customer reads (complete)
- Current task: Commit Phase 25, then begin Phase 26
- Last completed: Phase 25 — Admin customer reads
- Next action: Commit Phase 25, then implement Phase 26 status controls
- Current blocker: none
- Last updated: 2026-06-29

## Milestone progress

| Milestone | Status | Started | Completed | Notes |
|---|---|---|---|---|
| M0 — Decisions & Prep | COMPLETE | 2026-06-29 | 2026-06-29 | D1–D4 recorded and committed |
| M1 — Repo & Backend Foundation | COMPLETE | 2026-06-29 | 2026-06-29 | Phases 1–3 complete |
| M2 — Database | COMPLETE | 2026-06-29 | 2026-06-29 | Phases 4–7 complete |
| M3 — Authentication & Authorization | COMPLETE | 2026-06-29 | 2026-06-29 | Phases 8–16 complete |
| M4 — Banking Domain | COMPLETE | 2026-06-29 | 2026-06-29 | Phases 17–23 complete |
| M5 — Admin Backend | IN PROGRESS | 2026-06-29 |  | Phases 24–25 complete |
| M6 — Backend Finalization (BACKEND-COMPLETE) | NOT STARTED |  |  | Checkpoint |
| M7 — Frontend Foundation & Auth | NOT STARTED |  |  |  |
| M8 — Customer Frontend | NOT STARTED |  |  |  |
| M9 — Admin Frontend | NOT STARTED |  |  |  |
| M10 — Frontend & E2E Testing | NOT STARTED |  |  |  |
| M11 — Deployment | NOT STARTED |  |  |  |
| M12 — Documentation & Submission (SUBMISSION) | NOT STARTED |  |  | Checkpoint |
| M13 — Production Hardening | NOT STARTED |  |  | `[HARDENING]` — off critical path |
| M14 — Extensions | NOT STARTED |  |  | `[EXTENSION]` — off critical path |

---

## M0 — Decisions & Prep `[SUBMISSION]`

### Phase 0 — Confirm open decisions
Status: COMPLETE
- [x] D1 — session lifetimes (idle / absolute) decided: 30 minutes / 12 hours
- [x] D2 — Include minimal AuditEvent table and audit writes in MVP
- [x] D3 — nginx selected as the production reverse proxy
- [x] D4 — lightweight query helpers selected; services remain primary
- [x] Record all four in MY_WORKFLOW.md ADR log
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: — (decision and documentation phase; no tests required)
- Manual verification: D1–D4 each have a recorded choice, rationale, and consequence.
- Commit: `639e578 docs: record session lifetime, audit, proxy, and repository decisions`
- Notes: Local Git repository initialized; default branch renamed to `main`.

---

## M1 — Repo & Backend Foundation `[SUBMISSION]`

### Phase 1 — Repository structure & tooling
Status: COMPLETE
- [x] Select uv for environment and dependency management
- [x] Create backend package skeleton directories
- [x] Create and activate a Python 3.12 virtual environment
- [x] Pin core dependencies with `pyproject.toml` and `uv.lock`
- [x] Add Ruff formatter + linter configuration and run both checks
- [x] Add `.gitignore` (ignore `.env`, caches, build artifacts)
- [x] Initialize git; first commit (completed during Phase 0)
- [x] Confirm pytest collects zero tests without import or collection errors
- [x] Add backend, application-package, and test-suite guides
- [x] Record decisions and learning notes in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `pytest --collect-only` found zero tests without collection errors (expected exit code 5).
- Manual verification: `import app` succeeded; all dependency imports succeeded; Ruff reported 14
  files formatted and all lint checks passing; `.venv` and secret env files are ignored.
- Commit: `9abc2a1 chore: initialize backend structure and tooling`
- Notes: Runtime and development dependencies are separated; exact versions are stored in
  `uv.lock`. No application behavior exists yet.

### Phase 2 — FastAPI app + health endpoint
Status: COMPLETE
- [x] Create the FastAPI app instance
- [x] Add `GET /api/health` router
- [x] Include the router under `/api`
- [x] Run with uvicorn locally
- [x] Add health integration test
- [x] Record decisions and learning notes in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `1 passed, 1 warning`; Ruff format and lint checks passed across `app` and `tests`.
- Manual verification: Uvicorn started on `127.0.0.1:8000`; `/api/health` returned HTTP 200 with
  `{"status":"ok"}`; `/docs` returned HTTP 200; OpenAPI included `/api/health`.
- Commit: `feat(api): add FastAPI app and /api/health endpoint`
- Notes: FastAPI emitted a deprecation warning for the legacy TestClient/httpx integration; tracked
  as technical debt. This endpoint is liveness-only and intentionally does not check a database.

### Phase 3 — Configuration & environment variables
Status: COMPLETE
- [x] Define the `Settings` model (SPEC §18 vars)
- [x] Provide a single cached settings accessor
- [x] Write `.env.example`
- [x] Confirm `.env` is git-ignored
- [x] Add settings unit tests
- [x] Record decisions and learning notes in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `6 passed, 1 existing warning`; Ruff format and lint checks passed.
- Manual verification: `.env.example` loaded as `development` with D1 defaults; database URL and
  session secret were redacted; blank `COOKIE_DOMAIN` normalized to `None`; `.env` is ignored while
  `.env.example` remains trackable.
- Commit: `feat(config): add env-driven settings and .env.example`
- Notes: No real `.env` or secrets were created. FastAPI's existing TestClient warning remains
  tracked as Phase 2 technical debt.

---

## M2 — Database `[SUBMISSION]`

### Phase 4 — SQLAlchemy engine, session, base, DB dependency
Status: COMPLETE
- [x] Create the engine from `DATABASE_URL` (sized pool)
- [x] Create the `SessionLocal` factory
- [x] Declare the `Base` / metadata
- [x] Add the `get_db` dependency
- [x] Add connectivity check + test
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `12 passed, 1 existing warning`; Ruff format and lint checks passed.
- Manual verification: Compose configuration validated; PostgreSQL 16 reached healthy status on
  host port 5433; initialization logs contained no errors; `simulated_banking_dev` and
  `simulated_banking_test` exist and are owned by non-superuser `banking_user`; the role connected
  to and created/dropped schema objects in both databases; the runtime engine connected to the
  development database; database tests used only the isolated test database and proved cleanup
  plus rollback behavior.
- Commit: `fea719f feat(db): add Docker PostgreSQL and SQLAlchemy session infrastructure`
- Notes: PostgreSQL alone runs in Docker; FastAPI remains local. The official image's bootstrap
  administrator is separate from the least-privilege application role. Initialization SQL runs
  only for an empty Compose volume. Alembic remains Phase 6 and was not initialized.

### Phase 5 — Database models & relationships
Status: COMPLETE
- [x] User model
- [x] Session model (token_hash unique, indexes)
- [x] Account model (`CHECK (balance >= 0)`, index)
- [x] Transaction model (append-only, index)
- [x] Transfer model
- [x] AuditEvent model (per D2)
- [x] Wire relationships and register on metadata
- [x] Add model unit tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `16 passed, 1 existing warning`; Ruff format and lint checks passed.
- Manual verification: SQLAlchemy mapper configuration completed without relationship errors;
  `Base.metadata` registered exactly `users`, `sessions`, `accounts`, `transactions`, `transfers`,
  and `audit_events`, with required columns, named enums, indexes, foreign keys,
  `NUMERIC(14,2)` money types, timezone-aware timestamps, uniqueness, and the nonnegative-balance
  check represented in metadata.
- Commit: `26533c3 feat(models): add banking database models and relationships`
- Notes: Integer primary keys were selected because the specification does not require UUIDs.
  Models deliberately have no implicit delete cascades. No tables or migrations were created;
  Alembic and live constraint enforcement remain Phase 6.

### Phase 6 — Alembic configuration & first migration
Status: COMPLETE
- [x] Initialize Alembic; point env.py at metadata + URL
- [x] Autogenerate the first migration
- [x] Verify CHECK / unique / indexes present
- [x] `alembic upgrade head` on dev DB
- [x] Verify downgrade/upgrade round-trip
- [x] Add DB integration test (tables + CHECK)
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `17 passed, 1 existing warning`; Ruff format and lint checks passed across application,
  tests, and Alembic files.
- Manual verification: Revision `0001` autogenerated all six tables; development successfully
  completed upgrade → downgrade-to-base → upgrade; PostgreSQL catalogs showed all expected tables,
  foreign keys, unique constraints, indexes, and `ck_accounts_balance_nonnegative`; a live
  negative-balance insert failed in the test database; `alembic current` reported `0001 (head)`;
  `alembic check` reported no new upgrade operations.
- Commit: `c69f05b feat(db): add Alembic config and initial schema migration`
- Notes: Alembic configuration contains no database credential. Tests provide their isolated URL
  through a programmatic override and never use the development URL. The reviewed downgrade
  explicitly removes PostgreSQL enum types so re-upgrade is clean. Seed data remains Phase 7.

### Phase 7 — Deterministic, idempotent seed
Status: COMPLETE
- [x] Create admin + ≥2 customers (hashed passwords)
- [x] CHECKING + SAVINGS per customer with non-zero balances
- [x] Record opening balances as DEPOSIT transactions
- [x] Add a spread of historical transactions
- [x] Make the script idempotent
- [x] Print demo credentials
- [x] Add idempotency + reconciliation tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `25 passed, 1 existing warning`; Ruff format and lint checks passed; `alembic check`
  reported no model/schema drift.
- Manual verification: The development seed ran twice with stable counts of 3 users, 4 accounts,
  2 transfers, and 12 transactions; every account's signed transaction sum equaled its stored
  balance; each transfer had exactly two distinct transaction legs linked by `reference_id`.
- Commit: `4402852 feat(seed): add deterministic idempotent demo-data seed`
- Notes: Demo identities use synthetic `.test` addresses and intentionally public credentials.
  Passwords are stored only as Argon2id hashes. Existing account pairs preserve later append-only
  activity on rerun rather than deleting history. M2 is complete.

---

## M3 — Authentication & Authorization `[SUBMISSION]`

### Phase 8 — Password hashing (Argon2id)
Status: COMPLETE
- [x] `hash_password` (Argon2id at/above floor)
- [x] `verify_password` (constant-time)
- [x] `needs_rehash`
- [x] Ensure no plaintext/hash logging
- [x] Add unit tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `22 passed, 1 existing warning`; Ruff format and lint checks passed.
- Manual verification: A non-secret smoke check confirmed Argon2id with 19,456 KiB memory,
  2 iterations, and parallelism 1; the correct password verified, a wrong password failed, and a
  current hash did not require rehashing.
- Commit: `ed43249 feat(security): add Argon2id password hashing and verification`
- Notes: Phase 8 was intentionally sequenced before Phase 7 using the implementation plan's
  explicit dependency option. The module performs no logging and treats malformed hashes as
  authentication failures. Session-token work remains Phase 9 and was not started.

### Phase 9 — Session-token utility (hash-only storage)
Status: COMPLETE
- [x] `generate_session_token` (high entropy)
- [x] `hash_session_token` (deterministic, optionally peppered)
- [x] expiry helper from D1 lifetimes
- [x] Confirm raw token never persisted
- [x] Add unit tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `30 passed, 1 existing warning`; Ruff format and lint checks passed; `alembic check`
  reported no model/schema drift.
- Manual verification: Generated tokens contained 43 URL-safe characters from 32 random bytes;
  repeated generation was unique; HMAC-SHA256 produced a deterministic 64-character lookup hash
  without the raw token; D1 expiry calculated exactly 12 hours from an aware UTC timestamp.
- Commit: `4d0d8b8 feat(security): add opaque session token generation and hashing`
- Notes: Session-token hashes are keyed with `SESSION_SECRET`; rotating that secret intentionally
  invalidates all active sessions. Naive timestamps are rejected. No token or hash is logged or
  persisted by the utility itself. Phase 10 was not started.

### Phase 10 — Login endpoint + cookie issuance
Status: COMPLETE
- [x] Login request schema
- [x] Verify password; reject inactive users
- [x] Create session row (store token hash)
- [x] Set auth cookie (secure attributes) + CSRF cookie
- [x] Generic 401 on failure (no enumeration)
- [x] Emit login success/failure audit rows (D2)
- [x] Add API tests (session row + cookie attributes)
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `34 passed, 1 existing warning`; Ruff format and lint checks passed; `alembic check`
  reported no model/schema drift.
- Manual verification: Real Uvicorn login returned HTTP 200 and set a redacted
  `__Host-session` cookie with `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/`, and
  `Max-Age=43200`; the separate CSRF cookie was readable and otherwise identically scoped.
  PostgreSQL stored one 64-character token hash with a 12-hour lifetime and a `login_success`
  audit event.
- Commit: `8cb74b3 feat(auth): add login endpoint with server-side session and secure cookies`
- Notes: Unknown email, wrong password, and inactive user return the same 401 envelope. Unknown
  users still incur Argon2 verification to reduce timing clues. Login establishes the session and
  issues the CSRF cookie; Phase 13 will enforce double-submit CSRF on subsequent mutations.

### Phase 11 — Current-session / current-user dependency
Status: COMPLETE
- [x] Resolve session by token hash
- [x] Reject missing/invalid/expired/revoked → 401
- [x] Slide `last_used_at` (idle timeout)
- [x] Load and return the User
- [x] Implement `GET /api/auth/me`
- [x] Add API tests (incl. expiry/revocation)
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `41 passed, 1 existing warning`; Ruff format and lint checks passed; `alembic check`
  reported no model/schema drift.
- Manual verification: Real Uvicorn flow completed login → `/api/auth/me` with safe user fields;
  after expiring that exact hashed session row, reuse of the same in-memory cookie returned the
  stable 401 `UNAUTHENTICATED` envelope.
- Commit: `4e44888 feat(auth): add current-user session dependency and auth-me`
- Notes: Missing, unknown, revoked, absolute-expired, idle-expired, and inactive-user sessions use
  one public failure. Absolute and idle boundaries are inclusive. Every valid request commits a
  new `last_used_at`, matching the plan's explicit sliding-window decision. Phase 12 was not started.

### Phase 12 — Logout & server-side revocation
Status: COMPLETE
- [x] Set `revoked_at` on the current session
- [x] Clear auth + CSRF cookies
- [x] Emit logout audit row (D2)
- [x] Confirm old cookie no longer authenticates
- [x] Add revocation API test
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `43 passed, 1 existing warning`; Ruff format and lint checks passed; `alembic check`
  reported no model/schema drift.
- Manual verification: Real Uvicorn flow completed login 200 → logout 204 → old-cookie
  `/api/auth/me` 401. Both cookies were cleared with `Max-Age=0`, matching path/security/SameSite
  attributes. PostgreSQL confirmed one revoked session and one logout audit event.
- Commit: `5fd1198 feat(auth): add logout with immediate server-side session revocation`
- Notes: Logout requires a currently valid principal. Revocation and its audit commit atomically;
  cookie deletion is client cleanup only. Phase 13 will add CSRF enforcement to logout and other
  authenticated mutations.

### Phase 13 — CSRF protection (double-submit)
Status: COMPLETE
- [x] Issue readable CSRF cookie at session start
- [x] CSRF dependency: compare header vs cookie on mutations
- [x] Reject mismatch/missing → `CSRF_INVALID`
- [x] Exempt safe methods (GET)
- [x] Add CSRF reject/accept tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `45 passed, 1 existing warning`; focused auth tests `15 passed`; Ruff format and lint
  checks passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn flow completed login 200 → logout without CSRF header 403
  `CSRF_INVALID` → same session `/api/auth/me` 200 → logout with matching token 204 → old-session
  `/api/auth/me` 401.
- Commit: `7564f66 feat(security): add double-submit CSRF protection for mutations`
- Notes: Unsafe requests use a reusable dependency that compares the configured readable cookie
  with `X-CSRF-Token` in constant time. Login remains exempt because it creates the pair; safe
  methods are exempt. Future POST/PATCH routes must attach `CsrfProtected`.

### Phase 14 — Role authorization
Status: COMPLETE
- [x] `require_role(ADMIN)` dependency
- [x] Customer-only guard where needed
- [x] 403 `FORBIDDEN` on mismatch
- [x] Role read only from DB user
- [x] Add role API tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `49 passed, 1 existing warning`; focused authorization tests `4 passed`; Ruff format and
  lint checks passed; `alembic check` reported no model/schema drift.
- Manual verification: A real Uvicorn test-probe flow logged in each seeded role with 200. ADMIN
  reached the ADMIN guard with 200 and received 403 `FORBIDDEN` from the CUSTOMER guard; CUSTOMER
  reached the CUSTOMER guard with 200 and received 403 `FORBIDDEN` from the ADMIN guard.
- Commit: `8c36a8e feat(auth): implement role-based authorization with require_role dependency and
  403 handling`
- Notes: `require_role(...)` receives only the authenticated `User` resolved through the
  SQL-backed session dependency. Named `AdminUser` and `CustomerUser` aliases keep future route
  signatures explicit. Client-supplied role headers are ignored. Permission-denied audit writes
  remain required by SPEC §16 but are outside Phase 14's explicit dependency-only completion scope.

### Phase 15 — Ownership authorization (no IDOR)
Status: COMPLETE
- [x] Account-by-id dependency filtered to current user
- [x] 404 `NOT_FOUND` when missing/not owned
- [x] Single shared entry point for account-scoped routes
- [x] Add ownership/IDOR API tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: `53 passed, 1 existing warning`; focused ownership tests `4 passed`; Ruff format and lint
  checks passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn test-probe flow completed customer login 200 → owned account
  200 → another customer's account 404 `NOT_FOUND` → missing account 404 `NOT_FOUND`.
- Commit: `8a1da23 feat(ownership): implement account ownership authorization with unified 404
  response`
- Notes: `get_owned_account` composes the CUSTOMER role guard with one SQL query filtered by both
  account ID and authenticated user ID. `OwnedAccount` is the single entry point for future
  customer account-scoped routes. ADMIN receives 403 and cannot reuse customer ownership logic.

### Phase 16 — Auth/authz/CSRF test suite
Status: COMPLETE
- [x] Fixtures (test DB, seeded users, role clients)
- [x] Login/invalid/inactive/expired/revoked tests
- [x] Logout-revokes test
- [x] CSRF reject/accept tests
- [x] Role 403 + ownership 404 tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: consolidated security suite `23 passed, 1 existing warning`; full suite `53 passed,
  1 existing warning`; Ruff format and lint checks passed; `alembic check` reported no
  model/schema drift.
- Manual verification: Ran the auth, CSRF, role-authorization, and ownership API modules together;
  every SPEC §14 authentication/CSRF/authorization scenario passed.
- Commit: `8b0db62 feat(tests): consolidate security tests with shared client fixtures and add CSRF
  rejection tests`
- Notes: Shared `admin_client` and `customer_client` fixtures authenticate seeded SQL users through
  the real login route and remain isolated by the per-test database reset. Focused CSRF cases now
  live in `test_csrf.py`; no application behavior changed.

---

## M4 — Banking Domain `[SUBMISSION]`

### Phase 17 — Domain errors + exception handler + error envelope
Status: COMPLETE
- [x] Base domain exception (code/message/fields)
- [x] Concrete exceptions for the §13 code set
- [x] FastAPI handler emitting the envelope
- [x] Catch-all → `INTERNAL_ERROR` (no leakage)
- [x] Retrofit auth/CSRF routes to the envelope
- [x] Add envelope + no-leak tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused error tests `13 passed`; combined security/error tests `36 passed`; full suite
  `66 passed, 1 existing warning`; Ruff format and lint checks passed; `alembic check` reported no
  model/schema drift.
- Manual verification: Real Uvicorn flow returned 422 `VALIDATION_ERROR` without echoing a rejected
  password and 500 `INTERNAL_ERROR` for a forced failure. Response and server logs omitted planted
  SQL/token text; the safe log contained only exception type, method, and path.
- Commit: `86a681a feat(errors): add domain exceptions and common error envelope handler`
- Notes: Expected domain failures share one handler; request validation and framework HTTP errors
  are normalized separately into the same envelope. Unexpected exceptions are caught by
  application middleware before Uvicorn can print raw exception messages. Programmatic Alembic
  runs preserve existing application loggers.

### Phase 18 — Account read operations
Status: COMPLETE
- [x] Account response schema (money as string)
- [x] Service: list owned accounts; get one owned account
- [x] Thin routes; 404 on non-owned
- [x] Add account read API tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused account API tests `5 passed`; full suite `71 passed, 1 existing warning`; Ruff
  format and lint checks passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn flow completed customer login 200 → account list 200 with two
  owned accounts and string balances → owned detail 200 → another customer's detail 404
  `NOT_FOUND`.
- Commit: `fec88c3 feat(accounts): add account list and detail read endpoints`
- Notes: `AccountResponse` exposes no owner ID and converts `Decimal` directly to a two-decimal
  string. The list service filters by authenticated customer ID; detail reuses `OwnedAccount`
  without a duplicate query. ADMIN receives 403 from both customer routes.

### Phase 19 — Transaction history (paginated)
Status: COMPLETE
- [x] Transaction response schema (strings)
- [x] `GET /accounts/{id}/transactions` (owned, paginated)
- [x] `GET /transactions` (cross-account, paginated)
- [x] Validate/clamp pagination
- [x] Add pagination + ownership tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused transaction API tests `8 passed`; full suite `79 passed, 1 existing warning`;
  Ruff format and lint checks passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn flow returned two disjoint customer-wide pages, an owned
  per-account page with string money, and 404 `NOT_FOUND` for another customer's account history.
- Commit: `d7978b2 feat(transactions): add paginated account and cross-account history`
- Notes: Pagination defaults to `limit=20`, permits at most 100, and starts at `offset=0`; invalid
  bounds return 422 rather than being silently clamped. Results are ordered by `created_at DESC,
  id DESC`. Customer-wide SQL joins accounts and filters by the authenticated customer.

### Phase 20 — Deposit
Status: COMPLETE
- [x] Deposit request schema (validate `> 0`, precision)
- [x] Service: lock row, confirm owned+ACTIVE, increase, log, commit
- [x] Thin route with CSRF + ownership deps
- [x] Reject inactive/frozen; non-positive amount
- [x] Emit deposit audit row (D2)
- [x] Add deposit service/API tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused deposit tests `9 passed`; full suite `88 passed, 1 existing warning`; Ruff passed;
  `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn flow rejected missing CSRF with 403, accepted a matching token,
  increased the balance by exactly `1.00`, and persisted the DEPOSIT transaction and audit event.
- Commit: `46a3490 feat(money): add atomic deposit with row locking and balance_after`
- Notes: Money input must be a JSON decimal string, positive, at most 14 digits and 2 decimal
  places. The service re-loads the authorized account under `FOR UPDATE`; balance, history, and
  audit commit atomically.

### Phase 21 — Withdrawal
Status: COMPLETE
- [x] Withdrawal request schema (`> 0`)
- [x] Service: lock, confirm owned+ACTIVE, `balance >= amount`, decrease, log, commit
- [x] Reject insufficient funds (`INSUFFICIENT_FUNDS`, no change)
- [x] Emit withdrawal audit row (D2)
- [x] Add withdrawal service/API tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused withdrawal tests `5 passed`; full suite `93 passed, 1 existing warning`; Ruff
  passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn overdraw returned 409 `INSUFFICIENT_FUNDS`; the stored balance
  remained unchanged.
- Commit: `d3a7654 feat(money): add atomic withdrawal with no-overdraft enforcement`
- Notes: The sufficient-funds check runs while the account row lock is held. Successful balance,
  WITHDRAWAL history, and audit writes commit atomically; all rejection paths roll back.

### Phase 22 — Transfer (atomic, order-locked)
Status: COMPLETE
- [x] Transfer request schema; reject same-account
- [x] Lock both rows by id; confirm both owned+ACTIVE; source funds
- [x] Create Transfer row (COMPLETED)
- [x] Debit + TRANSFER_OUT; credit + TRANSFER_IN (shared reference_id)
- [x] Commit atomically; rollback on failure
- [x] `GET /transfers/{id}` (owned)
- [x] Emit transfer audit row (D2)
- [x] Add success/same-account/not-owned/insufficient/rollback tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused transfer tests `7 passed`; full suite `100 passed, 1 existing warning`; Ruff
  passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn transfer returned 201, moved exactly `1.00` between owned
  accounts, persisted a COMPLETED parent and two legs, and the owned detail returned 200.
- Commit: `a68f63c feat(transfers): add atomic two-account transfer with rollback safety`
- Notes: Both rows lock in ascending ID order. An induced post-flush failure proved both balances,
  the parent, legs, and audit roll back. Non-owned either side returns 404.

### Phase 23 — Reconciliation & concurrency verification
Status: COMPLETE
- [x] Reconciliation helper (signed sum vs balance)
- [x] Reconciliation test (seeded + mutated accounts)
- [x] Concurrency test (two parallel withdrawals, no overdraw)
- [x] Assert `CHECK (balance >= 0)` under the race
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused reconciliation/concurrency tests `2 passed`; full suite `102 passed, 1 existing
  warning`; Ruff passed; `alembic check` reported no model/schema drift.
- Manual verification: Reconciliation helper checked all four development accounts after real
  deposit and transfer smoke mutations; every stored balance matched signed history.
- Commit: `879957f test(money): verify reconciliation and concurrent-overdraw protection`
- Notes: Reconciliation stays test-only for MVP. Two independent PostgreSQL sessions concurrently
  withdrew `80.00` from `100.00`; one succeeded, one failed, final balance was `20.00`, and exactly
  one history/audit pair was added.

---

## M5 — Admin Backend `[SUBMISSION]`

### Phase 24 — Admin dashboard summary
Status: COMPLETE
- [x] Admin service computing aggregates
- [x] Route gated by `require_role(ADMIN)`; money as strings
- [x] Add admin/customer 403 tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [x] Commit the completed phase

Completion evidence:
- Tests: focused dashboard tests `3 passed`; full suite `105 passed, 1 existing warning`; Ruff
  passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn returned the dashboard to ADMIN with string total balance and
  returned 403 `FORBIDDEN` to CUSTOMER.
- Commit: `f836821 feat(admin): add admin dashboard summary endpoint`
- Notes: Summary includes customer count, account count, total simulated balance, and transaction
  count over an explicit 30-day window. Customer endpoints and ownership logic are not reused.

### Phase 25 — Customer list & detail
Status: COMPLETE
- [x] List customers (admin-only)
- [x] Customer detail (accounts + paginated transactions)
- [x] Ensure admin reads don't reuse ownership dep
- [x] Add admin read tests
- [x] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests: focused admin/customer pagination tests `12 passed`; full suite `109 passed, 1 existing
  warning`; Ruff passed; `alembic check` reported no model/schema drift.
- Manual verification: Real Uvicorn admin list returned two customers; detail returned two
  accounts, a two-row transaction page, and string money.
- Commit:
- Notes: Admin queries filter CUSTOMER users directly and do not use customer ownership
  dependencies. Customer detail reuses the shared 20/100 pagination contract.

### Phase 26 — Status controls (deactivate / freeze)
Status: NOT STARTED
- [ ] Activate/deactivate user; revoke sessions on deactivate
- [ ] Freeze/unfreeze account
- [ ] CSRF-protect both; emit audit rows (D2)
- [ ] Assert deactivated user can't auth; frozen rejects money ops
- [ ] Add deactivation-revoke + freeze + admins-not-owners tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M6 — Backend Finalization `[SUBMISSION]` — BACKEND-COMPLETE CHECKPOINT

### Phase 27 — Error consistency, redaction, audit wiring, full backend pass
Status: NOT STARTED
- [ ] Audit all routes: envelope + money-strings + CSRF
- [ ] Verify log redaction; mask account numbers
- [ ] Confirm AuditEvent rows for all §10 MVP events (or record deferral)
- [ ] Reseed; run full backend suite
- [ ] Swagger/curl walkthrough as customer and admin
- [ ] Add redaction test
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase
- [ ] **CHECKPOINT:** backend suite green + walkthrough succeeds before any frontend work

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M7 — Frontend Foundation & Auth `[SUBMISSION]`

### Phase 28 — Frontend project foundation + typed API client
Status: NOT STARTED
- [ ] Scaffold Vite + React + TS with lint/format
- [ ] Typed API client (credentials + CSRF header injection)
- [ ] Money parsing utils + error-envelope mapper
- [ ] Dev proxy / CORS (dev only)
- [ ] Add client unit/component tests (CSRF, errors, money)
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 29 — Auth flow (login, auth state, protected routes, logout)
Status: NOT STARTED
- [ ] Auth Context loading `GET /auth/me` on mount
- [ ] Login page (demo credentials shown)
- [ ] Public/customer/admin route groups + guards
- [ ] Logout calling `/auth/logout`
- [ ] Add auth component tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M8 — Customer Frontend `[SUBMISSION]`

### Phase 30 — Customer dashboard
Status: NOT STARTED
- [ ] Fetch accounts; render cards
- [ ] Combined balance (string-safe)
- [ ] Loading/empty/error states
- [ ] Add dashboard component tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 31 — Account detail & transaction history
Status: NOT STARTED
- [ ] Account detail (balance + recent transactions)
- [ ] Paginated history (limit/offset controls)
- [ ] Loading/empty/error states
- [ ] Add history component tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 32 — Deposit / withdrawal / transfer interfaces
Status: NOT STARTED
- [ ] Deposit/withdrawal/transfer forms with validation
- [ ] Submit via client (CSRF header); refetch balances
- [ ] Map server errors to field/form messages
- [ ] Add form + CSRF + error-render tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M9 — Admin Frontend `[SUBMISSION]`

### Phase 33 — Admin dashboard, customer management, status controls
Status: NOT STARTED
- [ ] Admin dashboard (stats)
- [ ] Customer list → detail drill-down
- [ ] Activate/deactivate + freeze/unfreeze (CSRF) with refetch
- [ ] Add admin UI tests (role nav, CSRF mutation, customer denied)
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M10 — Frontend & E2E Testing `[SUBMISSION]`

### Phase 34 — Frontend component tests
Status: NOT STARTED
- [ ] Login validation + success/fail rendering
- [ ] Protected-route behavior
- [ ] Dashboard rendering
- [ ] Money-form validation + CSRF attachment + error rendering
- [ ] Role-specific navigation
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 35 — End-to-end happy path
Status: NOT STARTED
- [ ] Seed known state
- [ ] login → dashboard → deposit → withdraw → transfer → verify history
- [ ] Assert balances/history after operations
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M11 — Deployment `[SUBMISSION]`

### Phase 36 — Dockerize the backend
Status: NOT STARTED
- [ ] Backend `Dockerfile`
- [ ] Compose file (local Postgres + backend)
- [ ] Migration step (`alembic upgrade head`)
- [ ] Build + run; health from container
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 37 — Single-origin reverse proxy + HTTPS + Supabase
Status: NOT STARTED
- [ ] Proxy serves SPA at `/`
- [ ] Proxy `/api/*` to backend (same origin)
- [ ] TLS termination (Caddy auto-cert per D3)
- [ ] Supabase pooler URL; `alembic upgrade head`; seed
- [ ] Verify prod cookies `Secure` + `SameSite=Strict`
- [ ] Deploy smoke test
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M12 — Documentation & Submission `[SUBMISSION]` — SUBMISSION CHECKPOINT

### Phase 38 — README, design write-up, AI citation, demo video
Status: NOT STARTED
- [ ] README (overview, architecture, install/run, deploy, demo creds, decisions)
- [ ] Cite AI assistance per CS50x policy
- [ ] Record demo video
- [ ] Walk §21 acceptance criteria 1–15 and confirm each holds
- [ ] Full suites pass on clean checkout; reseed runs
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase
- [ ] **SUBMISSION CHECKPOINT reached** — submit before optional work

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M13 — Production Hardening `[HARDENING]` (off critical path)

Status: NOT STARTED
- [ ] H1 — Structured JSON logging + correlation IDs
- [ ] H2 — Idempotency keys on money ops
- [ ] H3 — Login rate limiting + lockout
- [ ] H4 — CI running the full suite on push
- [ ] H5 — Security headers + CSP + HSTS; proxy hardening
- [ ] H6 — `/api/ready` readiness check
- [ ] H7 — Production env validation on boot
- [ ] H8 — Backups, deploy runbook, rollback docs
- [ ] H9 — Dependency scanning + security-review checklist + monitoring

## M14 — Extensions `[EXTENSION]` (off critical path)

Status: NOT STARTED
- [ ] E1 — JWT access + rotating refresh (reuse-detection)
- [ ] E2 — Reconciliation as an admin tool
- [ ] E3 — Audit-event browser UI; fraud-flag events
- [ ] E4 — Compensating transactions; REVERSAL/ADJUSTMENT/FEE/INTEREST
- [ ] E5 — Double-entry ledger refactor
- [ ] E6 — Customer profile editing; simulated identity workflow
- [ ] E7 — Admin approval workflow (pending-state machine)

---

# Standing sections

## Current blockers
| Date | Phase | Blocker | Needed to unblock | Status |
|---|---|---|---|---|
|  |  |  |  |  |

## Decisions awaiting confirmation
| ID | Decision | Recommendation | Blocks | Resolved? |
|---|---|---|---|---|
| D1 | Session lifetimes (idle/absolute) | 30 min / 12 h | Ph3, Ph9–11, Ph16 | Yes — 30 min / 12 h |
| D2 | AuditEvent in MVP vs defer | Include minimal | Ph5/6, money/admin phases, Ph27 | Yes — include minimal |
| D3 | Reverse proxy Caddy vs nginx | Caddy (auto-TLS) | Ph37 | Yes — nginx |
| D4 | Repository-layer depth | Lightweight helpers | Ph18–26 layout | Yes — lightweight helpers |
| D5 | Sync vs async SQLAlchemy | Sync | Ph4 onward | Yes — synchronous SQLAlchemy |

## Deferred work
| Item | From phase | Reason | Revisit when |
|---|---|---|---|
|  |  |  |  |

## Bugs discovered
| Date | Phase | Bug | Severity | Status | Fix commit |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Technical debt
| Item | Introduced in | Why accepted | Pay-down plan |
|---|---|---|---|
| FastAPI TestClient warns that its legacy httpx integration is deprecated | Phase 2 | The health integration test passes, and changing the planned client dependency would expand this phase | Review FastAPI's supported replacement before the broader API test suite in Phase 16 |

## Submission readiness checklist (SPEC §21)
- [ ] 1. Demo customer & admin login; cookie `HttpOnly`/`Secure`/`SameSite=Strict`
- [ ] 2. Customer: accounts/balances/history; deposit, withdraw, transfer; correct balances
- [ ] 3. Over-balance withdraw/transfer → `INSUFFICIENT_FUNDS`; no change
- [ ] 4. Inactive/frozen ops rejected; same-account transfer rejected
- [ ] 5. Mid-transfer failure leaves both balances unchanged (test)
- [ ] 6. Concurrent withdrawals cannot overdraw (test); `CHECK (balance >= 0)` holds
- [ ] 7. Stored balance == signed sum of transactions (reconciliation test)
- [ ] 8. Customer cannot reach others' accounts (404) or admin (403)
- [ ] 9. Logout invalidates session server-side; deactivation revokes sessions
- [ ] 10. State-changing request without valid CSRF → `CSRF_INVALID`
- [ ] 11. Admin lists/opens/deactivates customer, freezes account; admin not an owner
- [ ] 12. All errors use the envelope; money as strings; no secrets in logs/errors
- [ ] 13. Deployed single-origin HTTPS; Supabase; migrations + seed applied
- [ ] 14. Backend auth/CSRF/business/rollback/concurrency/reconciliation + 1 E2E pass
- [ ] 15. README documents design/install/deploy + AI citation; demo video exists
