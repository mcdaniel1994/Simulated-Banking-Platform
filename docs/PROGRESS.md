# Project Progress

Operational checklist for the build. Phase names and numbers match
[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) exactly. Update this as you go; record the
*reasoning* in [MY_WORKFLOW.md](MY_WORKFLOW.md), not here.

Status values: `NOT STARTED` · `IN PROGRESS` · `BLOCKED` · `COMPLETE` · `DEFERRED`.

## Current Status
- Current milestone: M2 — Database (in progress)
- Current phase: Phase 6 — Alembic configuration and first migration (complete)
- Current task: Review and commit the completed Phase 6 batch
- Last completed: Phase 6 — Alembic configuration and first migration
- Next action: Review and commit Phase 6, then plan Phase 7 separately
- Current blocker: none
- Last updated: 2026-06-29

## Milestone progress

| Milestone | Status | Started | Completed | Notes |
|---|---|---|---|---|
| M0 — Decisions & Prep | COMPLETE | 2026-06-29 | 2026-06-29 | D1–D4 recorded and committed |
| M1 — Repo & Backend Foundation | COMPLETE | 2026-06-29 | 2026-06-29 | Phases 1–3 complete |
| M2 — Database | IN PROGRESS | 2026-06-29 |  | Phases 4–6 complete; Phase 7 remains |
| M3 — Authentication & Authorization | NOT STARTED |  |  |  |
| M4 — Banking Domain | NOT STARTED |  |  |  |
| M5 — Admin Backend | NOT STARTED |  |  |  |
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
- [ ] Commit the completed phase

Completion evidence:
- Tests: `17 passed, 1 existing warning`; Ruff format and lint checks passed across application,
  tests, and Alembic files.
- Manual verification: Revision `0001` autogenerated all six tables; development successfully
  completed upgrade → downgrade-to-base → upgrade; PostgreSQL catalogs showed all expected tables,
  foreign keys, unique constraints, indexes, and `ck_accounts_balance_nonnegative`; a live
  negative-balance insert failed in the test database; `alembic current` reported `0001 (head)`;
  `alembic check` reported no new upgrade operations.
- Commit:
- Notes: Alembic configuration contains no database credential. Tests provide their isolated URL
  through a programmatic override and never use the development URL. The reviewed downgrade
  explicitly removes PostgreSQL enum types so re-upgrade is clean. Seed data remains Phase 7.

### Phase 7 — Deterministic, idempotent seed
Status: NOT STARTED
- [ ] Create admin + ≥2 customers (hashed passwords)
- [ ] CHECKING + SAVINGS per customer with non-zero balances
- [ ] Record opening balances as DEPOSIT transactions
- [ ] Add a spread of historical transactions
- [ ] Make the script idempotent
- [ ] Print demo credentials
- [ ] Add idempotency + reconciliation tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M3 — Authentication & Authorization `[SUBMISSION]`

### Phase 8 — Password hashing (Argon2id)
Status: NOT STARTED
- [ ] `hash_password` (Argon2id at/above floor)
- [ ] `verify_password` (constant-time)
- [ ] `needs_rehash`
- [ ] Ensure no plaintext/hash logging
- [ ] Add unit tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 9 — Session-token utility (hash-only storage)
Status: NOT STARTED
- [ ] `generate_session_token` (high entropy)
- [ ] `hash_session_token` (deterministic, optionally peppered)
- [ ] expiry helper from D1 lifetimes
- [ ] Confirm raw token never persisted
- [ ] Add unit tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 10 — Login endpoint + cookie issuance
Status: NOT STARTED
- [ ] Login request schema
- [ ] Verify password; reject inactive users
- [ ] Create session row (store token hash)
- [ ] Set auth cookie (secure attributes) + CSRF cookie
- [ ] Generic 401 on failure (no enumeration)
- [ ] Emit login success/failure audit rows (D2)
- [ ] Add API tests (session row + cookie attributes)
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 11 — Current-session / current-user dependency
Status: NOT STARTED
- [ ] Resolve session by token hash
- [ ] Reject missing/invalid/expired/revoked → 401
- [ ] Slide `last_used_at` (idle timeout)
- [ ] Load and return the User
- [ ] Implement `GET /api/auth/me`
- [ ] Add API tests (incl. expiry/revocation)
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 12 — Logout & server-side revocation
Status: NOT STARTED
- [ ] Set `revoked_at` on the current session
- [ ] Clear auth + CSRF cookies
- [ ] Emit logout audit row (D2)
- [ ] Confirm old cookie no longer authenticates
- [ ] Add revocation API test
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 13 — CSRF protection (double-submit)
Status: NOT STARTED
- [ ] Issue readable CSRF cookie at session start
- [ ] CSRF dependency: compare header vs cookie on mutations
- [ ] Reject mismatch/missing → `CSRF_INVALID`
- [ ] Exempt safe methods (GET)
- [ ] Add CSRF reject/accept tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 14 — Role authorization
Status: NOT STARTED
- [ ] `require_role(ADMIN)` dependency
- [ ] Customer-only guard where needed
- [ ] 403 `FORBIDDEN` on mismatch
- [ ] Role read only from DB user
- [ ] Add role API tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 15 — Ownership authorization (no IDOR)
Status: NOT STARTED
- [ ] Account-by-id dependency filtered to current user
- [ ] 404 `NOT_FOUND` when missing/not owned
- [ ] Single shared entry point for account-scoped routes
- [ ] Add ownership/IDOR API tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 16 — Auth/authz/CSRF test suite
Status: NOT STARTED
- [ ] Fixtures (test DB, seeded users, role clients)
- [ ] Login/invalid/inactive/expired/revoked tests
- [ ] Logout-revokes test
- [ ] CSRF reject/accept tests
- [ ] Role 403 + ownership 404 tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M4 — Banking Domain `[SUBMISSION]`

### Phase 17 — Domain errors + exception handler + error envelope
Status: NOT STARTED
- [ ] Base domain exception (code/message/fields)
- [ ] Concrete exceptions for the §13 code set
- [ ] FastAPI handler emitting the envelope
- [ ] Catch-all → `INTERNAL_ERROR` (no leakage)
- [ ] Retrofit auth/CSRF routes to the envelope
- [ ] Add envelope + no-leak tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 18 — Account read operations
Status: NOT STARTED
- [ ] Account response schema (money as string)
- [ ] Service: list owned accounts; get one owned account
- [ ] Thin routes; 404 on non-owned
- [ ] Add account read API tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 19 — Transaction history (paginated)
Status: NOT STARTED
- [ ] Transaction response schema (strings)
- [ ] `GET /accounts/{id}/transactions` (owned, paginated)
- [ ] `GET /transactions` (cross-account, paginated)
- [ ] Validate/clamp pagination
- [ ] Add pagination + ownership tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 20 — Deposit
Status: NOT STARTED
- [ ] Deposit request schema (validate `> 0`, precision)
- [ ] Service: lock row, confirm owned+ACTIVE, increase, log, commit
- [ ] Thin route with CSRF + ownership deps
- [ ] Reject inactive/frozen; non-positive amount
- [ ] Emit deposit audit row (D2)
- [ ] Add deposit service/API tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 21 — Withdrawal
Status: NOT STARTED
- [ ] Withdrawal request schema (`> 0`)
- [ ] Service: lock, confirm owned+ACTIVE, `balance >= amount`, decrease, log, commit
- [ ] Reject insufficient funds (`INSUFFICIENT_FUNDS`, no change)
- [ ] Emit withdrawal audit row (D2)
- [ ] Add withdrawal service/API tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 22 — Transfer (atomic, order-locked)
Status: NOT STARTED
- [ ] Transfer request schema; reject same-account
- [ ] Lock both rows by id; confirm both owned+ACTIVE; source funds
- [ ] Create Transfer row (COMPLETED)
- [ ] Debit + TRANSFER_OUT; credit + TRANSFER_IN (shared reference_id)
- [ ] Commit atomically; rollback on failure
- [ ] `GET /transfers/{id}` (owned)
- [ ] Emit transfer audit row (D2)
- [ ] Add success/same-account/not-owned/insufficient/rollback tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 23 — Reconciliation & concurrency verification
Status: NOT STARTED
- [ ] Reconciliation helper (signed sum vs balance)
- [ ] Reconciliation test (seeded + mutated accounts)
- [ ] Concurrency test (two parallel withdrawals, no overdraw)
- [ ] Assert `CHECK (balance >= 0)` under the race
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

---

## M5 — Admin Backend `[SUBMISSION]`

### Phase 24 — Admin dashboard summary
Status: NOT STARTED
- [ ] Admin service computing aggregates
- [ ] Route gated by `require_role(ADMIN)`; money as strings
- [ ] Add admin/customer 403 tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

### Phase 25 — Customer list & detail
Status: NOT STARTED
- [ ] List customers (admin-only)
- [ ] Customer detail (accounts + paginated transactions)
- [ ] Ensure admin reads don't reuse ownership dep
- [ ] Add admin read tests
- [ ] Record decisions in `MY_WORKFLOW.md`
- [ ] Commit the completed phase

Completion evidence:
- Tests:
- Manual verification:
- Commit:
- Notes:

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
