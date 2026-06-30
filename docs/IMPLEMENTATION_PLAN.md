# IMPLEMENTATION_PLAN.md — Simulated Online Banking Platform

A backend-first, phase-by-phase build plan derived from [SPEC.md](../SPEC.md). The spec is the
source of truth; this plan only orders the work and explains *why each step comes when it does*.
It contains **no application code** — you implement each phase manually to learn it.

---

## How to use this plan

Work **one phase at a time**, top to bottom. For each phase:

1. **Read** the phase (Objective → Concepts → Tasks).
2. **Confirm** any open decision the phase depends on.
3. **Implement** the numbered tasks manually.
4. **Test** alongside the code (tests are part of the phase, not a later milestone).
5. **Verify** manually (Swagger / curl / DB / browser).
6. **Check** the Completion Criteria — all must hold.
7. **Commit** using the suggested message.
8. **Journal** the phase in [MY_WORKFLOW.md](MY_WORKFLOW.md) and tick [PROGRESS.md](PROGRESS.md).
9. **Honor the STOP line** — do not start the next phase until the current one works, its tests
   pass, and you understand it.

### Scope-tag legend

Every milestone and phase is tagged. This mirrors the SPEC scope legend (§ refers to SPEC.md).

| Tag | Meaning | SPEC equivalent |
|---|---|---|
| `[SUBMISSION]` | Required for the CS50x submission release. | `[MVP]` |
| `[HARDENING]` | Production-oriented improvement *after* the functional system works. | `[HARDENING]` |
| `[EXTENSION]` | Optional banking-domain learning beyond submission. | `[EXTENSION]` |

The **critical path is `[SUBMISSION]` only**. Nothing tagged `[HARDENING]` or `[EXTENSION]`
blocks the submission. There is a visible **BACKEND-COMPLETE checkpoint** (after M6) and a
**SUBMISSION checkpoint** (after M12); optional work begins only after the latter.

---

## Decisions Required Before Implementation

SPEC §24 leaves a small number of items as "confirm" / "include vs defer". These are surfaced
here rather than silently resolved. Settle each one (record it in MY_WORKFLOW.md's Architecture
Decision Log) **before** starting the phase it blocks. The rest of §24 is already resolved in
the spec and is *not* repeated as an open decision.

### D1 — Session lifetimes (idle timeout + absolute expiry)
- **Decision:** Concrete numeric values for `SESSION_IDLE_MINUTES` and `SESSION_ABSOLUTE_HOURS`
  (SPEC §9.2 requires both an idle timeout and an absolute expiry; §18 lists the env vars).
- **Why it matters:** The session dependency (Ph11) compares `last_used_at` and `expires_at`
  against these to decide 401-vs-valid. They also bound the cookie `Max-Age`. Picking them late
  forces rework of the session model defaults, config, and the expiry tests.
- **Options:** (a) 30 min idle / 12 h absolute; (b) 15 min idle / 8 h absolute (stricter);
  (c) 60 min idle / 24 h absolute (more demo-friendly).
- **Recommendation:** **(a) 30 min idle / 12 h absolute** — comfortable for reviewers testing the
  demo, still demonstrates both timeout types.
- **Blocks:** Ph3 (config), Ph9–Ph11 (session model/util/dependency), Ph16 (expiry tests).

### D2 — Minimal `AuditEvent` table in the MVP vs deferred to hardening
- **Decision:** Build the `AuditEvent` table + write rows now, or defer to `[HARDENING]`
  (SPEC §10 marks it "minimal — deferrable"; §16 MVP asks for minimal audit rows; §24.5 lists it
  as open).
- **Why it matters:** If included, the model exists in the first migration (Ph5/Ph6) and the
  auth/money/admin services emit rows (Ph10–Ph26). Adding it later means a second migration and
  retrofitting service calls.
- **Options:** (a) Include a minimal table + emit rows for the §10 events; (b) defer entirely to
  M13; (c) create the table now but wire row-writing later.
- **Recommendation:** **(a) Include minimal.** It is cheap, satisfies the §16 MVP logging ask,
  and avoids a retrofit. If time runs short mid-build, downgrade to (c).
- **Blocks:** Ph5/Ph6 (models/migration) and the "emit audit row" task inside Ph10, Ph12, Ph20–Ph22,
  Ph26; consolidated in Ph27.

### D3 — Reverse proxy: Caddy vs nginx
- **Decision:** Which reverse proxy terminates TLS and serves the single origin (SPEC §17, §24.3).
- **Why it matters:** Only affects deployment config; **does not block any backend or frontend
  phase**. Listed so it is settled before M11, not earlier.
- **Options:** (a) Caddy (automatic HTTPS certificates, minimal config); (b) nginx (ubiquitous,
  more manual TLS).
- **Recorded decision:** **(b) nginx**, selected in Phase 0 and documented in
  `MY_WORKFLOW.md`. The project intentionally accepts manual certificate provisioning in exchange
  for learning the more widely used nginx configuration model.
- **Deployment-environment amendment (D31, 2026-06-30):** the selected Hostinger VPS already runs
  Coolify. For the GitHub-to-Coolify path, Coolify's configured proxy terminates public TLS and
  nginx remains the internal SPA/API gateway. The verified manual nginx-owned TLS path remains a
  fallback. This supersedes D3's operational TLS consequence without rewriting the original
  decision.
- **Blocks:** Ph37 only.

### D4 — Repository-layer depth
- **Decision:** How much of a repository layer to build (SPEC §24.6, architecture summary).
- **Why it matters:** Determines whether services call thin query helpers or a full per-entity
  repository abstraction. Over-abstracting early adds friction; the spec explicitly warns against it.
- **Options:** (a) Lightweight query helpers, services primary (spec's recommendation);
  (b) full repository pattern per entity.
- **Recommendation:** **(a) Lightweight helpers.** Services hold business rules; helpers are
  small query functions. Avoid unnecessary abstraction (SPEC architecture summary).
- **Blocks:** File layout of M4/M5 service phases (Ph18–Ph26).

### Already-resolved (confirm they stay as-is; not blockers)
- **§24.1 JWT + rotating refresh** — deferred to `[EXTENSION]` (M14). Ship opaque sessions first.
- **§24.9 Ledger timing** — balance-based now; double-entry ledger stays `[EXTENSION]` (M14).
- **§24.2 CSRF** double-submit, **§24.3** single-origin, **§24.4** `NUMERIC(14,2)` — resolved in spec.

---

## Dependency Map

```
Config (env, settings)
   ↓
DB session (engine, SessionLocal, Base, get_db dependency)
   ↓
Models + relationships  →  Alembic migration
   ↓
Seed data (deterministic, idempotent)
   ↓
Password hashing (Argon2id)
   ↓
Session store (token util → session model → login → current-user dep → logout/revocation)
   ↓
CSRF (double-submit)
   ↓
Authorization (role check → ownership check)
   ↓
Error envelope + domain exceptions
   ↓
Account reads  →  Transaction history
   ↓
Deposit  →  Withdrawal  →  Transfer  →  Reconciliation/concurrency
   ↓
Admin APIs (dashboard, customer mgmt, status controls + session revocation)
   ↓
====================  BACKEND-COMPLETE CHECKPOINT  ====================
   ↓
Frontend foundation + typed API client  →  Auth flow
   ↓
Customer dashboard / money workflows  →  Admin UI
   ↓
Frontend component tests  →  one happy-path E2E
   ↓
Deployment (Docker → single-origin reverse proxy + HTTPS + Supabase + migrate + seed)
   ↓
Documentation + submission
   ↓
====================  SUBMISSION CHECKPOINT  ====================
   ↓
Hardening (M13)        Extensions (M14)        ← never block submission
```

**Strictly serial (the money path):** Config → DB → models → seed → auth → authz → error envelope
→ account reads → deposit → withdrawal → transfer → reconciliation → admin. Each link assumes the
previous one is correct and tested; reordering causes rework.

**Can proceed in parallel / opportunistically (off the critical path):**
- Frontend toolchain scaffolding (Vite/TS/lint) can be stood up any time after M1, but **wiring
  the client to the API should wait** until the backend contract is stable (after M6).
- The README skeleton, MY_WORKFLOW.md journaling, and PROGRESS.md updates are continuous.
- Choosing the reverse proxy (D3) and Supabase project setup can happen before M11.

---

## Why backend-first reduces rework

1. **The backend is the only security boundary** (SPEC §9, §15). Authz, CSRF, and revocation must
   be correct in the API regardless of the UI; proving them via tests/Swagger first means the UI
   is built on a trustworthy contract.
2. **The API contract stabilizes before the typed client exists.** The error envelope (§13),
   money-as-strings serialization (§11), and pagination shape are fixed in M4–M6. The frontend's
   typed client (Ph28) and error mapping are then written **once** against a stable surface,
   instead of being rewritten every time a route changes.
3. **The money path is exercisable without a UI.** Deposits, withdrawals, transfers, atomic
   rollback, and the concurrency guarantee are all verifiable via pytest + curl + DB inspection
   (SPEC §14 backend tests are the highest priority). Building the dashboard first would block on
   business logic that isn't done yet.
4. **Failures are isolated.** When the UI later shows a wrong balance, you already know the
   backend reconciles, so the bug is in presentation, not in the ledger.

---

## Recommended Project Structure

Reflects the SPEC architecture without over-engineering. **Do not create these directories yet**
(except `docs/`, which holds this plan). This is the target the phases build toward.

```
Simulated-Banking-Platform/
├── SPEC.md
├── README.md                         # Ph38
├── .env.example                      # Ph3  (real .env is git-ignored)
├── docker-compose.yml                # Ph36 (local Postgres for dev; backend image)
├── deploy/nginx/                     # Ph37 — reverse proxy / single origin
├── docs/
│   ├── IMPLEMENTATION_PLAN.md        # this file
│   ├── PROGRESS.md
│   └── MY_WORKFLOW.md
├── backend/
│   ├── pyproject.toml / requirements.txt
│   ├── Dockerfile                    # Ph36
│   ├── alembic.ini                   # Ph6
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/                 # migration files
│   ├── app/
│   │   ├── main.py                   # FastAPI app, router include, exception handlers
│   │   ├── core/
│   │   │   ├── config.py             # settings from env (Ph3)
│   │   │   └── security.py           # password hashing, token util (Ph8, Ph9)
│   │   ├── db/
│   │   │   ├── base.py               # declarative Base + metadata
│   │   │   └── session.py            # engine, SessionLocal, get_db dependency
│   │   ├── models/                   # SQLAlchemy models (Ph5)
│   │   │   ├── user.py  session.py  account.py  transaction.py  transfer.py  audit_event.py
│   │   ├── schemas/                  # Pydantic request/response (money as strings)
│   │   ├── services/                 # business rules (the heart of the project)
│   │   │   ├── auth_service.py  account_service.py  money_service.py
│   │   │   ├── transfer_service.py  admin_service.py  reconciliation.py
│   │   ├── repositories/             # lightweight query helpers (D4: thin, optional)
│   │   ├── api/
│   │   │   ├── deps.py               # current-session/user, role, ownership dependencies
│   │   │   └── routes/              # auth.py accounts.py transactions.py money.py
│   │   │       │                     #   transfers.py admin.py health.py
│   │   ├── errors.py                 # domain exceptions + envelope mapping (Ph17)
│   │   └── seed.py                   # deterministic seed (Ph7)
│   └── tests/
│       ├── conftest.py               # test DB, client, fixtures
│       ├── unit/  service/  api/  db/
├── frontend/
│   └── src/                          # mirrors SPEC §12
│       ├── api/  components/  features/  hooks/  layouts/  pages/  routes/  types/  utils/
│       └── tests/                    # component tests
└── e2e/                              # one happy-path E2E (Playwright/Cypress)
```

---

## Architecture boundaries (preserve these)

Request lifecycle (SPEC architecture summary, §24):

```
FastAPI route (thin)
  → Pydantic request schema (validation)
  → auth dependency (resolve+verify session) → CSRF check → role check → ownership check
  → application service (business rules, row locking, atomic transaction)
  → lightweight query helpers
  → SQLAlchemy session
  → PostgreSQL
  → Pydantic response schema (money serialized as JSON strings)
  → common error envelope on failure
```

Rules that hold for every phase:
- **Routes stay thin** — no business logic in route handlers.
- **Services own the business rules** and control transaction boundaries deliberately.
- **The transaction log is the source of truth**; `balance` is an atomically-maintained cache
  verified by reconciliation.
- **Add no abstraction the spec doesn't justify** (D4).

---

# Milestones & Phases

---

## M0 — Decisions & Prep `[SUBMISSION]`

### Phase 0 — Confirm open decisions `[SUBMISSION]`
**Objective:** Resolve D1–D4 and record them before any code exists.
**Why this phase comes now:** D1 (session lifetimes) and D2 (AuditEvent) change the config,
models, and first migration; settling them prevents an early rebuild.
**Concepts to Learn:** reading a spec for unresolved decisions; recording architecture decisions
(ADR style); distinguishing critical-path from deferrable choices.
**Decisions to Confirm:** D1, D2, D3, D4 (above).
**Files or Areas Expected to Change:** `docs/MY_WORKFLOW.md` (Architecture Decision Log);
`docs/PROGRESS.md` (Decisions awaiting confirmation).
**Implementation Tasks:**
1. Decide D1 idle/absolute values; write them down.
2. Decide D2 (recommended: include minimal AuditEvent).
3. Decide D3 (recorded choice: nginx) — can be revisited before M11.
4. Decide D4 (recommended: lightweight helpers).
5. Record all four in the Architecture Decision Log with context + consequences.
**Testing Required:** none (decisions only).
**Manual Verification:** the ADR log has four entries; PROGRESS.md "Decisions awaiting
confirmation" is cleared or annotated.
**Completion Criteria:** D1–D4 each have a recorded choice and rationale.
**Suggested Git Commit:** `docs: record session lifetime, audit, proxy, and repository decisions`
**STOP:** Do not continue until D1–D4 are decided and recorded.

---

## M1 — Repo & Backend Foundation `[SUBMISSION]`
*(SPEC §20 Phase 1)*

### Phase 1 — Repository structure & tooling `[SUBMISSION]`
**Objective:** Establish the repo layout, Python environment, formatting/linting, and `.gitignore`.
**Why this phase comes now:** Everything else lives in this structure; consistent tooling avoids
churn later.
**Concepts to Learn:** virtual environments; dependency pinning; formatter/linter config; monorepo
layout (backend + frontend + docs); `.gitignore` hygiene (never commit `.env`).
**Decisions to Confirm:** package manager (pip + `requirements.txt` vs Poetry/uv) — pick one.
**Files or Areas Expected to Change:** `backend/pyproject.toml` or `requirements.txt`;
`.gitignore`; `backend/app/__init__.py`; tool config (ruff/black, mypy optional).
**Implementation Tasks:**
1. Create the backend package skeleton directories (empty packages).
2. Create and activate a virtual environment.
3. Pin core deps: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg[binary]`, `alembic`,
   `pydantic-settings`, `argon2-cffi`, `pytest`, `httpx`.
4. Add formatter + linter config; run them on the empty package.
5. Add `.gitignore` (ignore `.env`, `__pycache__`, `node_modules`, build artifacts).
6. Initialize git; first commit.
**Testing Required:** none yet (tooling). Confirm `pytest` collects zero tests without error.
**Manual Verification:** linter/formatter run clean; `python -c "import app"` succeeds.
**Completion Criteria:** repo structure exists; deps install; tooling runs; git initialized.
**Suggested Git Commit:** `chore: initialize repo structure, tooling, and backend skeleton`
**STOP:** Do not continue until the environment installs cleanly and tooling runs.

### Phase 2 — FastAPI app + health endpoint `[SUBMISSION]`
**Objective:** A runnable FastAPI app exposing `GET /api/health` (SPEC §11 Ops).
**Why this phase comes now:** Proves the server boots and gives a trivial endpoint to verify the
toolchain end-to-end before adding complexity.
**Concepts to Learn:** ASGI app object; router inclusion; the `/api` prefix; Swagger UI / OpenAPI
auto-docs; liveness vs readiness.
**Decisions to Confirm:** API path prefix `/api` (per SPEC §11) — confirm.
**Files or Areas Expected to Change:** `backend/app/main.py`; `backend/app/api/routes/health.py`.
**Implementation Tasks:**
1. Create the FastAPI app instance in `main.py`.
2. Add a health router with `GET /api/health` returning a liveness payload.
3. Include the router under the `/api` prefix.
4. Run with uvicorn locally.
**Testing Required:** API: one integration test asserting `GET /api/health` → 200.
**Manual Verification:** open Swagger UI (`/docs`); `curl /api/health` returns 200.
**Completion Criteria:** app boots; health endpoint and Swagger UI respond; health test passes.
**Suggested Git Commit:** `feat(api): add FastAPI app and /api/health endpoint`
**STOP:** Do not continue until the app boots and the health test passes.

### Phase 3 — Configuration & environment variables `[SUBMISSION]`
**Objective:** Centralized settings loaded from env vars; `.env.example` committed (SPEC §18).
**Why this phase comes now:** The DB session, sessions, and CSRF all read config; defining it now
prevents scattering `os.getenv` calls.
**Concepts to Learn:** twelve-factor config; `pydantic-settings`; typed settings; secrets from env
not source; separating dev vs prod config; never committing real secrets.
**Decisions to Confirm:** D1 values feed `SESSION_IDLE_MINUTES`/`SESSION_ABSOLUTE_HOURS`.
**Files or Areas Expected to Change:** `backend/app/core/config.py`; `.env.example`; `.gitignore`
(confirm `.env` ignored).
**Implementation Tasks:**
1. Define a `Settings` model covering SPEC §18: `DATABASE_URL`, `SESSION_SECRET`,
   `SESSION_IDLE_MINUTES`, `SESSION_ABSOLUTE_HOURS`, `COOKIE_DOMAIN`, `CORS_ORIGINS` (dev),
   `CSRF_COOKIE_NAME`, `ENV`.
2. Provide a single cached settings accessor.
3. Write `.env.example` with placeholder (non-secret) values and comments.
4. Confirm `.env` is git-ignored; load it in local dev.
5. Read health/version from settings if useful.
**Testing Required:** unit: settings load from env; missing-required behaves as intended (a hard
error is fine for now; strict boot-time validation is `[HARDENING]` per §18).
**Manual Verification:** app boots with a local `.env`; print `ENV` at startup.
**Completion Criteria:** settings load from env; `.env.example` committed; no secrets in git.
**Suggested Git Commit:** `feat(config): add env-driven settings and .env.example`
**STOP:** Do not continue until settings load from env and `.env.example` is committed.

---

## M2 — Database `[SUBMISSION]`
*(SPEC §20 Phase 2)*

### Phase 4 — SQLAlchemy engine, session, base, and DB dependency `[SUBMISSION]`
**Objective:** Connect to PostgreSQL; provide a request-scoped DB session dependency.
**Why this phase comes now:** Models, seed, and every service need a session factory and a
`get_db` dependency.
**Concepts to Learn:** connection pooling; engine vs session; `SessionLocal` factory; declarative
`Base` / metadata; dependency injection of a per-request session; sizing the pool for a
long-lived process (SPEC §17); Supabase pooler URL.
**Decisions to Confirm:** sync vs async SQLAlchemy — recommend **sync** for teachability and
because `SELECT ... FOR UPDATE` row locking is straightforward; confirm.
**Files or Areas Expected to Change:** `backend/app/db/session.py`; `backend/app/db/base.py`.
**Implementation Tasks:**
1. Create the engine from `DATABASE_URL` with a sensible pool size.
2. Create the `SessionLocal` factory.
3. Declare the `Base` (declarative base / metadata).
4. Add a `get_db` dependency that yields a session and closes it.
5. Add a trivial DB-connectivity check (e.g. `SELECT 1`) used by a test.
**Testing Required:** DB integration: a test using `get_db` runs `SELECT 1` against a test DB.
**Manual Verification:** connect to local Postgres; confirm the app opens a connection.
**Completion Criteria:** engine connects; `get_db` yields/closes; connectivity test passes.
**Suggested Git Commit:** `feat(db): add SQLAlchemy engine, session factory, and get_db dependency`
**STOP:** Do not continue until the app connects to Postgres and the connectivity test passes.

### Phase 5 — Database models & relationships `[SUBMISSION]`
**Objective:** Define all entities from SPEC §10 with constraints and relationships.
**Why this phase comes now:** Migrations and seed derive from these models; auth and money logic
depend on the exact columns.
**Concepts to Learn:** ORM models; column types (`NUMERIC(14,2)`, `TIMESTAMPTZ` in UTC);
relationships and foreign keys; unique constraints and indexes; DB-level `CHECK` constraints;
enum columns (role, account type/status, transaction type, transfer status); append-only design.
**Decisions to Confirm:** D2 (whether `AuditEvent` is in this set now — recommended yes).
**Files or Areas Expected to Change:** `backend/app/models/{user,session,account,transaction,
transfer,audit_event}.py`; import them into `db/base.py` metadata.
**Implementation Tasks:**
1. `User`: id, email (unique), `password_hash`, names, `role` enum, `is_active`, timestamps.
2. `Session`: id, `user_id` FK, `token_hash` (unique), `created_at`, `last_used_at`,
   `expires_at`, `revoked_at` nullable, optional `user_agent`/`ip`; index `token_hash`, `user_id`.
3. `Account`: id, `user_id` FK, `account_number` unique, `account_type` enum, `balance`
   `NUMERIC(14,2)`, `status` enum, timestamps; **`CHECK (balance >= 0)`**; index `user_id`.
4. `Transaction` (append-only): id, `account_id` FK, `transaction_type` enum, `amount`,
   `description`, `balance_after`, `reference_id` nullable; index `(account_id, created_at)`.
5. `Transfer`: id, source/destination account FKs, `amount`, `status` enum, `created_at`.
6. `AuditEvent` (per D2): id, `actor_user_id` nullable FK, `event_type`, `entity_type`,
   `entity_id`, `metadata` JSON, `created_at`.
7. Wire relationships (User 1—* Account/Session; Account 1—* Transaction; Transfer ↔ two Accounts).
8. Register all models on the metadata so Alembic can see them.
**Testing Required:** unit: models import and instantiate; metadata lists all tables. (Constraint
enforcement is tested against the DB in Ph6+.)
**Manual Verification:** inspect `Base.metadata.tables` — all six tables present with expected columns.
**Completion Criteria:** all entities defined with correct types/constraints/indexes; metadata complete.
**Suggested Git Commit:** `feat(models): add user, session, account, transaction, transfer, audit models`
**STOP:** Do not continue until all models are defined and registered on the metadata.

### Phase 6 — Alembic configuration & first migration `[SUBMISSION]`
**Objective:** Version-control the schema; generate and apply the initial migration.
**Why this phase comes now:** Seed and all DB tests need real tables; migrations are the
production deploy mechanism (SPEC §17).
**Concepts to Learn:** schema migrations; autogenerate vs handwritten; `upgrade`/`downgrade`;
keeping models and migrations in sync; migrations as a deploy step.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `backend/alembic.ini`; `backend/alembic/env.py`;
`backend/alembic/versions/0001_*.py`.
**Implementation Tasks:**
1. Initialize Alembic; point `env.py` at the app metadata and `DATABASE_URL`.
2. Autogenerate the first migration from the models.
3. Review the migration: confirm the `CHECK (balance >= 0)` constraint, unique constraints, and
   indexes are present (autogenerate sometimes misses CHECK/constraints — add by hand if so).
4. Apply with `alembic upgrade head` against the dev DB.
5. Verify a clean `downgrade` then `upgrade` round-trip.
**Testing Required:** DB integration: after `upgrade head`, all six tables exist; the
`balance >= 0` CHECK rejects a negative balance insert.
**Manual Verification:** inspect the DB (psql/`\d`) — tables, indexes, constraints present.
**Completion Criteria:** migration applies cleanly; schema matches models; CHECK constraint enforced.
**Suggested Git Commit:** `feat(db): add Alembic config and initial schema migration`
**STOP:** Do not continue until the migration applies and the schema matches the models.

### Phase 7 — Deterministic, idempotent seed `[SUBMISSION]`
**Objective:** A reseedable script creating demo users, accounts, and history (SPEC §19).
**Why this phase comes now:** Auth and the dashboards need known data; determinism lets reviewers
and tests rely on fixed demo credentials.
**Concepts to Learn:** idempotent scripts (safe to re-run); deterministic data; **opening-balance
as a transaction** (so reconciliation holds from the start); not seeding real PII.
**Decisions to Confirm:** demo credentials (emails/passwords) shown on the login page later.
**Files or Areas Expected to Change:** `backend/app/seed.py`.
**Implementation Tasks:**
1. Create one `ADMIN` user and at least two `CUSTOMER` users with Argon2id-hashed passwords
   (depends on Ph8 hashing — sequence Ph8 first if needed, or hash inline and refactor).
2. Give each customer a `CHECKING` and a `SAVINGS` account with non-zero starting balances.
3. **Record each starting balance as a `DEPOSIT` transaction with `balance_after`** so the log
   equals the balance (reconciliation-safe).
4. Add a spread of historical transactions so dashboards are not empty.
5. Make the script idempotent (upsert by email/account_number; safe to re-run).
6. Print the demo credentials when run.
**Testing Required:** DB integration: after seeding twice, row counts are stable (idempotent); for
every seeded account, signed sum of transactions equals stored balance (reconciliation holds).
**Manual Verification:** run seed; inspect DB; re-run seed — no duplicates.
**Completion Criteria:** seed is deterministic and idempotent; reconciliation holds on seeded data.
**Suggested Git Commit:** `feat(seed): add deterministic idempotent demo-data seed`
**STOP:** Do not continue until reseeding is idempotent and seeded balances reconcile.

---

## M3 — Authentication & Authorization `[SUBMISSION]`
*(SPEC §20 Phase 3; SPEC §9 governs)*

### Phase 8 — Password hashing (Argon2id) `[SUBMISSION]`
**Objective:** Hash and verify passwords with Argon2id (SPEC §9.1).
**Why this phase comes now:** Login and seed both need it; it is the smallest self-contained
security primitive.
**Concepts to Learn:** password hashing vs encryption; Argon2id parameters (≥19 MiB, iterations=2,
parallelism=1); constant-time verification; rehash-on-login when parameters rise; never logging
passwords/hashes.
**Decisions to Confirm:** Argon2 parameters (at/above the §9.1 floor).
**Files or Areas Expected to Change:** `backend/app/core/security.py`.
**Implementation Tasks:**
1. Add `hash_password(plain) -> str` using `argon2-cffi` with parameters at/above the floor.
2. Add `verify_password(plain, hash) -> bool` (constant-time).
3. Add a `needs_rehash(hash)` check for parameter upgrades.
4. Ensure no function logs the plaintext or the hash.
**Testing Required:** unit: hash≠plaintext; correct password verifies; wrong password fails;
`needs_rehash` triggers on weaker params.
**Manual Verification:** in a REPL, hash and verify a sample password.
**Completion Criteria:** hashing/verification work; parameters meet the floor; nothing logged.
**Suggested Git Commit:** `feat(security): add Argon2id password hashing and verification`
**STOP:** Do not continue until hashing and verification are tested and correct.

### Phase 9 — Session-token utility (hash-only storage) `[SUBMISSION]`
**Objective:** Generate high-entropy session tokens and store **only their hash** (SPEC §9.2).
**Why this phase comes now:** Login (Ph10) issues a token; the session dependency (Ph11) resolves
by token hash. This isolates the token primitive from the endpoint logic.
**Concepts to Learn:** CSPRNG token generation; why store a hash not the raw token (DB-leak
containment); fast hash (e.g. SHA-256) for lookups vs slow hash for passwords; opaque tokens.
**Decisions to Confirm:** token length/entropy; hash algorithm for the token (SHA-256 of token,
optionally peppered with `SESSION_SECRET`).
**Files or Areas Expected to Change:** `backend/app/core/security.py` (token helpers).
**Implementation Tasks:**
1. `generate_session_token()` — high-entropy random string.
2. `hash_session_token(token)` — deterministic hash (for indexed lookup), optionally peppered.
3. Helper to compute `expires_at` from `created_at` + absolute lifetime (D1).
4. Confirm the raw token is never persisted.
**Testing Required:** unit: tokens are unique and high-entropy; the same token hashes to the same
value; different tokens differ; raw token is not derivable from the stored hash.
**Manual Verification:** generate a token, hash it, confirm lookup-by-hash matches.
**Completion Criteria:** token generation + hashing exist; only the hash is ever stored.
**Suggested Git Commit:** `feat(security): add opaque session token generation and hashing`
**STOP:** Do not continue until tokens hash deterministically and the raw token is never stored.

### Phase 10 — Login endpoint + cookie issuance `[SUBMISSION]`
**Objective:** `POST /api/auth/login` verifies credentials, creates a session row, sets cookies
(SPEC §7.1, §9.2, §9.5).
**Why this phase comes now:** It composes Ph8 (verify) + Ph9 (token) + the Session model into the
first authenticated flow.
**Concepts to Learn:** session authentication; secure cookie attributes (`HttpOnly`, `Secure`,
`SameSite=Strict`, scoped `Path`, `__Host-` prefix, `Max-Age` ≤ lifetime); generic auth-failure
messages (no enumeration); blocking inactive users; issuing the readable CSRF cookie at session start.
**Decisions to Confirm:** D1 (cookie `Max-Age`); D2 (emit `login success/failure` audit rows).
**Files or Areas Expected to Change:** `backend/app/api/routes/auth.py`;
`backend/app/services/auth_service.py`; `backend/app/schemas/auth.py`.
**Implementation Tasks:**
1. Define the login request schema (email, password).
2. In the auth service: look up the user; verify password; reject if `is_active = false`.
3. On success: generate a token (Ph9), store its hash in a `sessions` row with `expires_at`/
   `last_used_at`.
4. Set the auth cookie (raw token) with all secure attributes; set the CSRF cookie (readable).
5. Return a generic 401 envelope on any failure (no enumeration).
6. Emit `login success` / `login failure` audit rows (D2).
**Testing Required:** API: successful login creates a session row and sets a cookie with
`HttpOnly`/`Secure`/`SameSite`; invalid credentials → generic 401; inactive user → blocked.
**Manual Verification:** Swagger/curl login; inspect `Set-Cookie` headers and the new `sessions` row.
**Completion Criteria:** valid login issues a session + cookies; invalid/inactive are rejected generically.
**Suggested Git Commit:** `feat(auth): add login endpoint with server-side session and secure cookies`
**STOP:** Do not continue until login creates a session and sets correctly-attributed cookies.

### Phase 11 — Current-session / current-user dependency `[SUBMISSION]`
**Objective:** Resolve the authenticated user from the cookie; enforce idle + absolute expiry and
revocation (SPEC §7.1, §9.2).
**Why this phase comes now:** Every protected route and `GET /auth/me` depends on it; expiry/
revocation rules live here.
**Concepts to Learn:** auth dependency injection; resolving a session by token hash; idle timeout
(`last_used_at`) vs absolute expiry (`expires_at`); revoked sessions (`revoked_at`); sliding
`last_used_at` update; 401 on invalid/expired/revoked.
**Decisions to Confirm:** D1 timeout values; whether to slide `last_used_at` on each request (yes).
**Files or Areas Expected to Change:** `backend/app/api/deps.py`;
`backend/app/api/routes/auth.py` (`GET /api/auth/me`).
**Implementation Tasks:**
1. Read the auth cookie; hash the token; look up a non-revoked, non-expired session.
2. Reject (401 `UNAUTHENTICATED`) if missing/invalid/expired/revoked or idle-timed-out.
3. On success, update `last_used_at` (idle-timeout sliding window).
4. Load and return the associated `User`.
5. Implement `GET /api/auth/me` returning the current user.
**Testing Required:** API: valid session → `auth/me` returns the user; missing/invalid/expired/
revoked session → 401; idle-timeout boundary behaves correctly.
**Manual Verification:** login then call `/auth/me`; manually expire/revoke a session row and confirm 401.
**Completion Criteria:** dependency resolves valid sessions and rejects invalid/expired/revoked ones.
**Suggested Git Commit:** `feat(auth): add current-user session dependency and /auth/me`
**STOP:** Do not continue until `/auth/me` works and expired/revoked sessions are rejected.

### Phase 12 — Logout & server-side revocation `[SUBMISSION]`
**Objective:** `POST /api/auth/logout` revokes the session so the same cookie can no longer
authenticate (SPEC §7.1, §9.2, acceptance §21.9).
**Why this phase comes now:** Revocation is the payoff of server-side sessions and a named
acceptance criterion; it builds directly on Ph11.
**Concepts to Learn:** real revocation vs cookie deletion; flagging `revoked_at`; clearing cookies;
why a server-side store enables instant revocation.
**Decisions to Confirm:** D2 (emit `logout` audit row).
**Files or Areas Expected to Change:** `backend/app/api/routes/auth.py`;
`backend/app/services/auth_service.py`.
**Implementation Tasks:**
1. Resolve the current session; set `revoked_at = now()`.
2. Clear the auth and CSRF cookies in the response.
3. Emit a `logout` audit row (D2).
4. Confirm a subsequent request with the same cookie is rejected by Ph11.
**Testing Required:** API: after logout, **the same cookie no longer authenticates** (401 on
`/auth/me`); the session row shows `revoked_at`.
**Manual Verification:** login → logout → reuse the old cookie via curl → 401.
**Completion Criteria:** logout revokes server-side; the prior cookie is dead immediately.
**Suggested Git Commit:** `feat(auth): add logout with immediate server-side session revocation`
**STOP:** Do not continue until logout revokes the session and the old cookie fails to authenticate.

### Phase 13 — CSRF protection (double-submit) `[SUBMISSION]`
**Objective:** Reject state-changing requests lacking a valid `X-CSRF-Token` (SPEC §9.3, §21.10).
**Why this phase comes now:** All money/admin mutations are CSRF-protected; the guard must exist
before those endpoints are built so they are protected from the first commit.
**Concepts to Learn:** CSRF on cookie-auth; double-submit pattern (readable CSRF cookie echoed in
a header); why `SameSite`/CORS are defense-in-depth, not CSRF protection; safe (GET) vs unsafe methods.
**Decisions to Confirm:** `CSRF_COOKIE_NAME`; header name `X-CSRF-Token` (per spec).
**Files or Areas Expected to Change:** `backend/app/api/deps.py` (CSRF dependency);
`backend/app/api/routes/auth.py` (issue CSRF cookie at login, already in Ph10).
**Implementation Tasks:**
1. Issue a readable (non-HttpOnly) CSRF cookie at session start (confirm Ph10 does this).
2. Add a CSRF dependency for state-changing methods: compare the `X-CSRF-Token` header to the
   CSRF cookie; reject mismatch/missing with `CSRF_INVALID`.
3. Exempt safe methods (GET).
4. Plan to attach this dependency to every POST/PATCH route.
**Testing Required:** API: a POST without/with-wrong `X-CSRF-Token` → `CSRF_INVALID`; with a
matching token → passes; GET requires no token.
**Manual Verification:** curl a POST without the header (rejected) and with it (accepted).
**Completion Criteria:** state-changing requests require a matching CSRF token; GETs do not.
**Suggested Git Commit:** `feat(security): add double-submit CSRF protection for mutations`
**STOP:** Do not continue until CSRF rejects mismatched tokens and allows matching ones.

### Phase 14 — Role authorization `[SUBMISSION]`
**Objective:** Enforce `CUSTOMER` vs `ADMIN` from SQL on protected routes (SPEC §9.4, §21.8).
**Why this phase comes now:** Admin endpoints (M5) need it; ownership (Ph15) layers on top.
**Concepts to Learn:** role-based access control; trusting roles from SQL not the client; 403 vs 404.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `backend/app/api/deps.py` (role dependencies).
**Implementation Tasks:**
1. Add a `require_role(ADMIN)` dependency built on the current-user dependency.
2. Add a customer-only guard where appropriate.
3. Return 403 `FORBIDDEN` on role mismatch.
4. Never read the role from request input — only from the DB user.
**Testing Required:** API: a customer hitting an admin-only route → 403; an admin allowed through.
**Manual Verification:** call an admin route as a customer (403) and as an admin (allowed).
**Completion Criteria:** role checks resolve from SQL and reject mismatches with 403.
**Suggested Git Commit:** `feat(authz): add role-based authorization dependency`
**STOP:** Do not continue until role checks reject customers from admin routes.

### Phase 15 — Ownership authorization (no IDOR) `[SUBMISSION]`
**Objective:** Customers can only reach accounts/transactions they own; others return **404**
(SPEC §8, §9.4, §21.8).
**Why this phase comes now:** Account reads and every money route depend on a single shared
ownership check; defining it once prevents IDOR bugs across endpoints.
**Concepts to Learn:** resource ownership; IDOR prevention; filtering every query by the
authenticated principal; 404 (not 403) to avoid existence disclosure.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `backend/app/api/deps.py` (ownership/account dependency).
**Implementation Tasks:**
1. Add a dependency that loads an account by id **filtered to the current user**.
2. Return 404 `NOT_FOUND` when the account does not exist or is not owned.
3. Make it the single shared entry point for all account-scoped routes.
**Testing Required:** API: a customer requesting another customer's `account_id` → 404; their own → 200.
**Manual Verification:** request someone else's account id (404) vs your own (200).
**Completion Criteria:** ownership is enforced via one shared dependency; not-owned → 404, no IDOR.
**Suggested Git Commit:** `feat(authz): add resource-ownership dependency (404 on non-owned)`
**STOP:** Do not continue until non-owned account access returns 404 via the shared dependency.

### Phase 16 — Auth/authz/CSRF test suite `[SUBMISSION]`
**Objective:** Consolidate and complete the security tests for M3 (SPEC §14 auth/CSRF/authz block).
**Why this phase comes now:** Locks the security boundary before money endpoints are built on top.
**Concepts to Learn:** integration testing of auth flows; test fixtures for logged-in clients;
asserting cookie attributes; testing negative paths.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `backend/tests/api/test_auth.py`,
`test_authz.py`, `test_csrf.py`; `backend/tests/conftest.py`.
**Implementation Tasks:**
1. Fixtures: test DB, seeded users, customer/admin logged-in clients.
2. Tests: login success (session row + cookie attributes), invalid creds (generic), inactive
   blocked, missing/invalid/expired/revoked → 401.
3. Test: logout revokes (same cookie fails afterward).
4. Tests: CSRF reject/accept; role 403; ownership 404 (no IDOR).
**Testing Required:** all of the above (this *is* the testing phase for M3).
**Manual Verification:** run the auth test module; all green.
**Completion Criteria:** every SPEC §14 auth/CSRF/authz scenario has a passing test.
**Suggested Git Commit:** `test(auth): cover login, session expiry, revocation, CSRF, and authz`
**STOP:** Do not continue until the full auth/authz/CSRF suite passes.

---

## M4 — Banking Domain `[SUBMISSION]`
*(SPEC §20 Phase 4; SPEC §7.4–7.6, §8)*

### Phase 17 — Domain errors + exception handler + error envelope `[SUBMISSION]`
**Objective:** A single exception handler maps typed domain errors to the common envelope (SPEC §13).
**Why this phase comes now:** Account reads and money services raise typed errors; defining the
envelope first keeps routes thin and the API contract stable for the frontend.
**Concepts to Learn:** typed domain exceptions; centralized exception handling; error envelope
design; mapping errors → status codes; **no leakage** of stack traces/SQL/tokens; thin routes.
**Decisions to Confirm:** the initial code set (SPEC §13): `VALIDATION_ERROR`, `UNAUTHENTICATED`,
`FORBIDDEN`, `NOT_FOUND`, `CSRF_INVALID`, `INSUFFICIENT_FUNDS`, `INACTIVE_ACCOUNT`,
`SAME_ACCOUNT_TRANSFER`, `INACTIVE_USER`, `INTERNAL_ERROR`.
**Files or Areas Expected to Change:** `backend/app/errors.py`; `backend/app/main.py`
(register handlers); retrofit existing routes (auth/CSRF) to use the envelope.
**Implementation Tasks:**
1. Define a base domain exception carrying a machine `code`, message, and optional `fields`.
2. Define the concrete exceptions for the codes above.
3. Register a FastAPI exception handler emitting `{ "error": { code, message, fields } }`.
4. Map a catch-all to `INTERNAL_ERROR` (log server-side, never leak internals).
5. Retrofit Ph10–Ph15 responses to the envelope.
**Testing Required:** API: each domain error renders the envelope with the right code/status;
an unexpected error renders `INTERNAL_ERROR` with no stack trace/SQL in the body.
**Manual Verification:** trigger a validation error and a forced internal error; inspect the JSON.
**Completion Criteria:** all errors use the envelope; internals never leak; routes stay thin.
**Suggested Git Commit:** `feat(errors): add domain exceptions and common error envelope handler`
**STOP:** Do not continue until all errors render the envelope and internals never leak.

### Phase 18 — Account read operations `[SUBMISSION]`
**Objective:** `GET /api/accounts` and `GET /api/accounts/{id}` (SPEC §7.2).
**Why this phase comes now:** Simplest authenticated, ownership-scoped, money-serializing endpoints
— a foundation to validate the response contract before mutations.
**Concepts to Learn:** service-layer reads; lightweight query helpers (D4); **money serialized as
JSON strings** (SPEC §11); applying the ownership dependency (Ph15).
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `backend/app/api/routes/accounts.py`;
`backend/app/services/account_service.py`; `backend/app/schemas/account.py`.
**Implementation Tasks:**
1. Account response schema serializing `balance` as a string.
2. Service: list the current user's accounts; get one owned account (via Ph15 dependency).
3. Routes (thin) returning the schemas; 404 on non-owned.
**Testing Required:** API: list returns only the caller's accounts; get-by-id returns an owned
account; non-owned → 404; `balance` is a JSON string.
**Manual Verification:** Swagger/curl list + get; confirm money is a string.
**Completion Criteria:** account reads work, are ownership-scoped, and serialize money as strings.
**Suggested Git Commit:** `feat(accounts): add account list and detail read endpoints`
**STOP:** Do not continue until account reads are ownership-scoped and money is string-serialized.

### Phase 19 — Transaction history (paginated) `[SUBMISSION]`
**Objective:** Per-account and cross-account transaction history with limit/offset (SPEC §7.3).
**Why this phase comes now:** Needed to *verify* deposits/withdrawals/transfers in later phases
and for reconciliation; append-only reads are low-risk.
**Concepts to Learn:** pagination (limit/offset); append-only reads; ordering by `(account_id,
created_at)`; ownership-scoped queries across multiple accounts.
**Decisions to Confirm:** default/max page size.
**Files or Areas Expected to Change:** `backend/app/api/routes/transactions.py`;
`backend/app/services/account_service.py` (or a transactions service); `backend/app/schemas/transaction.py`.
**Implementation Tasks:**
1. Transaction response schema (money + `balance_after` as strings).
2. `GET /api/accounts/{id}/transactions?limit&offset` for an owned account.
3. `GET /api/transactions?limit&offset` across the caller's accounts.
4. Validate/clamp pagination params.
**Testing Required:** API: pagination returns the right slice/order; per-account history is
ownership-scoped (non-owned → 404); cross-account history only includes the caller's accounts.
**Manual Verification:** page through seeded history via curl.
**Completion Criteria:** both history endpoints paginate correctly and are ownership-scoped.
**Suggested Git Commit:** `feat(transactions): add paginated account and cross-account history`
**STOP:** Do not continue until both history endpoints paginate and respect ownership.

### Phase 20 — Deposit `[SUBMISSION]`
**Objective:** `POST /api/accounts/{id}/deposits` with row locking and an atomic balance+log
update (SPEC §7.4).
**Why this phase comes now:** First money mutation; establishes the lock→validate→update→log→commit
pattern that withdrawal and transfer reuse.
**Concepts to Learn:** atomic transactions; `SELECT ... FOR UPDATE` row locking; `Decimal` money
with half-up rounding; writing `balance_after`; account-status gating; CSRF-protected mutation.
**Decisions to Confirm:** amount precision/limits; D2 (emit deposit audit row).
**Files or Areas Expected to Change:** `backend/app/api/routes/money.py`;
`backend/app/services/money_service.py`; `backend/app/schemas/money.py`.
**Implementation Tasks:**
1. Deposit request schema (`amount` as a string/Decimal; validate `> 0` and precision).
2. Service (one transaction): lock the account row (`FOR UPDATE`); confirm exists + owned + ACTIVE;
   increase balance; insert a `DEPOSIT` transaction with `balance_after`; commit.
3. Route (thin) with the CSRF + ownership dependencies; return the updated account.
4. Reject non-ACTIVE accounts with `INACTIVE_ACCOUNT`; non-positive amount with `VALIDATION_ERROR`.
5. Emit a deposit audit row (D2).
**Testing Required:** service/API: success increases balance + appends a transaction with correct
`balance_after`; amount ≤ 0 rejected; deposit to frozen/closed → `INACTIVE_ACCOUNT`; CSRF enforced.
**Manual Verification:** check balance before/after via curl; confirm the new transaction row.
**Completion Criteria:** deposits atomically update balance + log, gate on status, and are CSRF-protected.
**Suggested Git Commit:** `feat(money): add atomic deposit with row locking and balance_after`
**STOP:** Do not continue until deposits update balance+log atomically and gate on account status.

### Phase 21 — Withdrawal `[SUBMISSION]`
**Objective:** `POST /api/accounts/{id}/withdrawals` with the no-overdraft rule (SPEC §7.5, §8).
**Why this phase comes now:** Reuses the deposit pattern and adds the sufficient-funds rule that
the concurrency test (Ph23) will stress.
**Concepts to Learn:** invariants enforced in the service **and** the DB (`CHECK (balance >= 0)`);
sufficient-funds checks; reusing the locked-update pattern.
**Decisions to Confirm:** D2 (emit withdrawal audit row).
**Files or Areas Expected to Change:** `backend/app/services/money_service.py`;
`backend/app/api/routes/money.py`; `backend/app/schemas/money.py`.
**Implementation Tasks:**
1. Withdrawal request schema (validate `amount > 0`).
2. Service (one transaction): lock the row; confirm exists + owned + ACTIVE; confirm
   `balance >= amount`; decrease balance; insert `WITHDRAWAL` with `balance_after`; commit.
3. Reject insufficient funds with `INSUFFICIENT_FUNDS` (no balance change).
4. Emit a withdrawal audit row (D2).
**Testing Required:** service/API: success decreases balance + logs; insufficient funds →
`INSUFFICIENT_FUNDS` and no change; frozen/closed → `INACTIVE_ACCOUNT`; CSRF enforced.
**Manual Verification:** attempt to overdraw via curl → rejected, balance unchanged.
**Completion Criteria:** withdrawals enforce no-overdraft in service + DB; rejected attempts change nothing.
**Suggested Git Commit:** `feat(money): add atomic withdrawal with no-overdraft enforcement`
**STOP:** Do not continue until overdraw attempts are rejected with no balance change.

### Phase 22 — Transfer (atomic, order-locked) `[SUBMISSION]`
**Objective:** `POST /api/transfers` and `GET /api/transfers/{id}` moving money between two owned
accounts in one atomic transaction (SPEC §7.6).
**Why this phase comes now:** The hardest correctness case — two-row locking, deadlock avoidance,
two transaction legs, and all-or-nothing rollback. It builds on deposit/withdrawal mechanics.
**Concepts to Learn:** multi-row locking in a **consistent order** (by id) to avoid deadlock;
atomic multi-step transactions; the `Transfer` parent row + two legs sharing `reference_id`;
same-account rejection; rollback-on-failure.
**Decisions to Confirm:** D2 (emit transfer audit row).
**Files or Areas Expected to Change:** `backend/app/api/routes/transfers.py`;
`backend/app/services/transfer_service.py`; `backend/app/schemas/transfer.py`.
**Implementation Tasks:**
1. Transfer request schema (source, destination, amount); reject source == destination
   (`SAME_ACCOUNT_TRANSFER`).
2. Service (one transaction): lock **both** rows ordered by id; confirm both exist + both owned +
   both ACTIVE; confirm source `balance >= amount`.
3. Create a `Transfer` row (status `COMPLETED`).
4. Debit source + insert `TRANSFER_OUT` (`reference_id = transfer.id`); credit destination +
   insert `TRANSFER_IN` (same `reference_id`).
5. Commit atomically; on any failure, roll back the whole operation.
6. `GET /api/transfers/{id}` returns an owned transfer.
7. Emit a transfer audit row (D2).
**Testing Required:** service/API: success moves money + writes both legs with shared
`reference_id`; same-account → `SAME_ACCOUNT_TRANSFER`; not-owned source/dest → 404; insufficient
funds → `INSUFFICIENT_FUNDS`; **induced mid-operation failure rolls back both balances** (assert
no change and no orphan rows).
**Manual Verification:** transfer via curl; confirm both balances and both legs; inspect the
`Transfer` row.
**Completion Criteria:** transfers are atomic, order-locked, two-legged, and roll back fully on failure.
**Suggested Git Commit:** `feat(transfers): add atomic two-account transfer with rollback safety`
**STOP:** Do not continue until a forced failure leaves both balances unchanged.

### Phase 23 — Reconciliation & concurrency verification `[SUBMISSION]`
**Objective:** Prove balance integrity: reconciliation holds and concurrent withdrawals cannot
overdraw (SPEC §8, §14, §21.6–21.7).
**Why this phase comes now:** These are core acceptance criteria and only meaningful once all
money operations exist.
**Concepts to Learn:** reconciliation (`sum of signed transactions == stored balance`); the
balance-as-cache / log-as-truth model; testing concurrency (parallel requests); how row locking
prevents lost updates.
**Decisions to Confirm:** whether to expose reconciliation as an admin tool now (`[EXTENSION]`)
or keep it a test only (recommended: test only for MVP, per §8).
**Files or Areas Expected to Change:** `backend/app/services/reconciliation.py` (helper);
`backend/tests/db/test_reconciliation.py`; `backend/tests/db/test_concurrency.py`.
**Implementation Tasks:**
1. Reconciliation helper: for an account, compute signed sum of transactions and compare to balance.
2. Reconciliation test across all seeded + freshly-mutated accounts.
3. Concurrency test: fire two parallel withdrawals that together exceed the balance; assert only
   one succeeds and the account never goes negative.
4. Assert the `CHECK (balance >= 0)` backstop holds under the race.
**Testing Required:** DB integration: reconciliation passes for every account; concurrency test
proves no overdraft and no lost update.
**Manual Verification:** run the reconciliation helper against the seeded DB.
**Completion Criteria:** reconciliation passes everywhere; concurrent overdraw is impossible.
**Suggested Git Commit:** `test(money): verify reconciliation and concurrent-overdraw protection`
**STOP:** Do not continue until reconciliation passes and concurrent overdraw is proven impossible.

---

## M5 — Admin Backend `[SUBMISSION]`
*(SPEC §20 Phase 5; SPEC §7.7)*

### Phase 24 — Admin dashboard summary `[SUBMISSION]`
**Objective:** `GET /api/admin/dashboard` returning summary statistics (SPEC §7.7).
**Why this phase comes now:** First admin (role-gated) endpoint; read-only, low-risk start to M5.
**Concepts to Learn:** aggregate queries; role-gated endpoints; admins-are-not-owners separation.
**Decisions to Confirm:** which stats (customer count, account count, total simulated balance,
recent transaction count).
**Files or Areas Expected to Change:** `backend/app/api/routes/admin.py`;
`backend/app/services/admin_service.py`; `backend/app/schemas/admin.py`.
**Implementation Tasks:**
1. Admin service computing the summary aggregates.
2. Route gated by `require_role(ADMIN)` (Ph14); money serialized as strings.
**Testing Required:** API: admin gets the dashboard; customer → 403.
**Manual Verification:** call the dashboard as admin and as customer.
**Completion Criteria:** admin-only dashboard returns correct aggregates; customers are blocked (403).
**Suggested Git Commit:** `feat(admin): add admin dashboard summary endpoint`
**STOP:** Do not continue until the dashboard is admin-gated and aggregates are correct.

### Phase 25 — Customer list & detail `[SUBMISSION]`
**Objective:** `GET /api/admin/users` and `GET /api/admin/users/{id}` with accounts + transactions
drill-down (SPEC §7.7, consolidation note §11).
**Why this phase comes now:** Admin management UI (M9) depends on these reads; consolidates global
account/transaction lists into customer drill-downs.
**Concepts to Learn:** admin read access without ownership reuse; drill-down composition; pagination reuse.
**Decisions to Confirm:** none (global list pages fold into detail per §11 MVP decision).
**Files or Areas Expected to Change:** `backend/app/api/routes/admin.py`;
`backend/app/services/admin_service.py`; `backend/app/schemas/admin.py`.
**Implementation Tasks:**
1. List customers (admin-only).
2. Customer detail: the customer's accounts + (paginated) transactions.
3. Ensure admin reads do **not** reuse the customer ownership dependency.
**Testing Required:** API: admin lists/opens any customer; customer → 403.
**Manual Verification:** open a customer detail as admin.
**Completion Criteria:** admin can list and drill into any customer; customers are blocked.
**Suggested Git Commit:** `feat(admin): add customer list and customer-detail drill-down`
**STOP:** Do not continue until admin reads work and remain separate from ownership logic.

### Phase 26 — Status controls (deactivate / freeze) `[SUBMISSION]`
**Objective:** `PATCH /api/admin/users/{id}/status` (activate/deactivate; deactivation revokes the
customer's sessions) and `PATCH /api/admin/accounts/{id}/status` (freeze/unfreeze) (SPEC §7.7,
§21.9, §21.11).
**Why this phase comes now:** Mutating admin actions with cross-cutting effects (session
revocation, status gating already enforced by money ops) complete the admin backend.
**Concepts to Learn:** admin-driven session revocation; status state machines; CSRF on admin
mutations; the link between `is_active`/account `status` and the rules enforced in M3/M4.
**Decisions to Confirm:** D2 (emit activation/deactivation + freeze/unfreeze audit rows).
**Files or Areas Expected to Change:** `backend/app/api/routes/admin.py`;
`backend/app/services/admin_service.py`.
**Implementation Tasks:**
1. Activate/deactivate a customer; **on deactivation, revoke all that user's active sessions**.
2. Freeze/unfreeze an account.
3. CSRF-protect both; emit audit rows (D2).
4. Confirm a deactivated user cannot authenticate and a frozen account rejects money ops (rules
   already enforced in M3/M4 — assert here).
**Testing Required:** API: deactivation revokes the customer's sessions (their cookie now 401s);
freeze blocks money ops; admins cannot run customer money operations as an owner; CSRF enforced.
**Manual Verification:** deactivate a logged-in customer; confirm their session dies; freeze an
account and attempt a deposit.
**Completion Criteria:** status changes apply; deactivation revokes sessions; frozen accounts
reject money movement; admins are not owners.
**Suggested Git Commit:** `feat(admin): add user activation and account freeze with session revocation`
**STOP:** Do not continue until deactivation revokes sessions and frozen accounts reject money ops.

---

## M6 — Backend Finalization `[SUBMISSION]`
*(SPEC §20 Phase 9 backend portion; consolidation before frontend)*

### Phase 27 — Error consistency, redaction, audit wiring, full backend pass `[SUBMISSION]`
**Objective:** Confirm the whole backend is consistent, leak-free, audited, and fully tested
before any frontend work (SPEC §13, §14, §16).
**Why this phase comes now:** The BACKEND-COMPLETE checkpoint — the frontend's contract freezes here.
**Concepts to Learn:** log redaction (never log passwords/hashes/raw tokens/cookies/headers; mask
account numbers); consistent envelopes; audit completeness; end-to-end backend verification via Swagger.
**Decisions to Confirm:** D2 final (all required audit rows present).
**Files or Areas Expected to Change:** `backend/app/errors.py`, logging config, `app/seed.py`
(reseed), `backend/tests/` (gap-filling).
**Implementation Tasks:**
1. Audit every route: errors use the envelope; money serialized as strings; CSRF on all mutations.
2. Verify logging redaction (no secrets/tokens/cookies in logs or error bodies); mask account numbers.
3. Confirm AuditEvent rows are written for all §10 MVP events (or record the deferral if D2 = defer).
4. Reseed; run the full backend suite; walk every endpoint through Swagger/curl as both roles.
**Testing Required:** full backend pytest pass; a redaction test asserting logs/error responses
contain no tokens/cookies/secrets (SPEC §14).
**Manual Verification:** a complete Swagger walkthrough: login → accounts → deposit → withdraw →
transfer → history → admin actions, as customer and admin.
**Completion Criteria:** entire backend suite green; envelope/redaction/audit consistent; Swagger
walkthrough succeeds for both roles.
**Suggested Git Commit:** `test(backend): finalize error consistency, redaction, and audit coverage`
**STOP — BACKEND-COMPLETE CHECKPOINT:** Do not start the frontend until the full backend suite
passes and the Swagger walkthrough works end-to-end for both roles.

> **>>> BACKEND-COMPLETE CHECKPOINT <<<** The API is fully usable via Swagger/curl/pytest. The
> contract (routes, envelope, money-as-strings, CSRF, pagination) is now frozen for the frontend.

---

## M7 — Frontend Foundation & Auth `[SUBMISSION]`
*(SPEC §20 Phase 6; SPEC §12)*

### Phase 28 — Frontend project foundation + typed API client `[SUBMISSION]`
**Objective:** Stand up the React/TS SPA and a small typed API client (SPEC §12).
**Why this phase comes now:** The client encapsulates money parsing, error mapping, and CSRF-header
injection against the now-frozen backend contract — written once.
**Concepts to Learn:** Vite + React + TypeScript; `fetch` with credentials; reading the CSRF cookie
and injecting `X-CSRF-Token`; parsing money strings → Decimal-safe display; mapping the error
envelope to messages/field errors; the auth cookie being invisible to JS by design.
**Decisions to Confirm:** test runner (Vitest/Jest) and component-test lib.
**Files or Areas Expected to Change:** `frontend/` scaffold; `frontend/src/api/` (client, money,
errors, csrf); `frontend/src/types/`.
**Implementation Tasks:**
1. Scaffold Vite + React + TS with lint/format.
2. Build a typed API client that sends credentials, attaches `X-CSRF-Token` from the CSRF cookie
   on mutations, and parses the response.
3. Add money parsing utilities (strings, not floats) and an error-envelope mapper.
4. Configure the dev proxy / CORS (dev only) so the SPA can call `/api`.
**Testing Required:** component/unit: CSRF header is attached on a mutating call; the error mapper
turns an envelope into a message + field errors; money parsing is exact.
**Manual Verification:** the SPA calls `/api/health` (or `/auth/me` while logged out) successfully.
**Completion Criteria:** SPA builds; client attaches CSRF + credentials and maps errors/money.
**Suggested Git Commit:** `feat(frontend): scaffold SPA and typed API client with CSRF + money parsing`
**STOP:** Do not continue until the client reaches `/api` with CSRF + credentials wired.

### Phase 29 — Auth flow (login, auth state, protected routes, logout) `[SUBMISSION]`
**Objective:** Login page (demo creds shown), auth state derived from `GET /auth/me`, protected
route groups, logout (SPEC §12, §21.1).
**Why this phase comes now:** Every customer/admin page lives behind authentication; deriving state
from `/auth/me` (not a stored token) is the chosen pattern.
**Concepts to Learn:** deriving auth state from the server on load; React Context for auth; route
guards; redirect-on-401; showing demo credentials for reviewers; logout calling the revoking endpoint.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `frontend/src/features/auth/`; `frontend/src/routes/`;
`frontend/src/layouts/`; `frontend/src/pages/` (Login, Landing, Unauthorized, Not-Found).
**Implementation Tasks:**
1. Auth Context that loads `GET /auth/me` on mount and exposes user/role/loading.
2. Login page (with demo credentials displayed) posting to `/auth/login`.
3. Public, customer, and admin route groups; redirect unauthenticated users; role-based guards.
4. Logout calling `/auth/logout` and clearing client auth state.
**Testing Required:** component: login form validation; successful vs failed login rendering;
protected-route redirect when unauthenticated; role-specific navigation.
**Manual Verification:** log in via the browser as customer and admin; confirm guards and logout.
**Completion Criteria:** auth state derives from `/auth/me`; protected routes guard correctly;
logout ends the session.
**Suggested Git Commit:** `feat(frontend): add login, auth context, protected routes, and logout`
**STOP:** Do not continue until browser login/logout and route guards work for both roles.

---

## M8 — Customer Frontend `[SUBMISSION]`
*(SPEC §20 Phase 7; SPEC §12)*

### Phase 30 — Customer dashboard `[SUBMISSION]`
**Objective:** Account cards + combined balance (SPEC §12, §21.2).
**Why this phase comes now:** First authenticated data view; validates the read contract in the UI.
**Concepts to Learn:** rendering money from strings; explicit loading/empty/error states;
responsive cards; computing a combined balance without float drift.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `frontend/src/features/accounts/`; `frontend/src/pages/Dashboard`.
**Implementation Tasks:**
1. Fetch `/api/accounts`; render account cards.
2. Show a combined balance computed safely from strings.
3. Loading/empty/error states.
**Testing Required:** component: dashboard renders accounts; error state renders the mapped message.
**Manual Verification:** log in as the demo customer; see seeded accounts and a correct combined balance.
**Completion Criteria:** dashboard shows accounts + combined balance with proper states.
**Suggested Git Commit:** `feat(frontend): add customer dashboard with account cards and combined balance`
**STOP:** Do not continue until the dashboard renders seeded accounts and the combined balance is correct.

### Phase 31 — Account detail & transaction history `[SUBMISSION]`
**Objective:** Account detail page with paginated history (SPEC §12, §21.2).
**Why this phase comes now:** Lets you *see* the effects of the money workflows built next.
**Concepts to Learn:** pagination UI (limit/offset); list rendering; empty/error states.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `frontend/src/features/transactions/`;
`frontend/src/pages/AccountDetail`, `TransactionHistory`.
**Implementation Tasks:**
1. Account detail showing balance + recent transactions.
2. Paginated transaction history (limit/offset controls).
3. Loading/empty/error states.
**Testing Required:** component: history renders a page; pagination control behavior.
**Manual Verification:** page through the demo customer's history in the browser.
**Completion Criteria:** account detail + paginated history render with proper states.
**Suggested Git Commit:** `feat(frontend): add account detail and paginated transaction history`
**STOP:** Do not continue until account detail and paginated history render correctly.

### Phase 32 — Deposit / withdrawal / transfer interfaces `[SUBMISSION]`
**Objective:** Forms for the three money workflows with CSRF wired in (SPEC §12, §21.2–21.4).
**Why this phase comes now:** Completes the customer journey on top of the verified backend.
**Concepts to Learn:** controlled forms; client-side validation mirroring server rules; attaching
the CSRF header on mutations; rendering field-level + envelope errors (`INSUFFICIENT_FUNDS`,
`INACTIVE_ACCOUNT`, `SAME_ACCOUNT_TRANSFER`); optimistic vs refetch balance updates.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `frontend/src/features/transfers/`,
`frontend/src/features/accounts/`; `frontend/src/pages/{Deposit,Withdrawal,Transfer}`.
**Implementation Tasks:**
1. Deposit, withdrawal, and transfer forms with client validation.
2. Submit via the typed client (CSRF header attached); refetch balances after success.
3. Map server errors to field/form messages.
**Testing Required:** component: form validation; CSRF header attached on submit; API-error
rendering (e.g. insufficient funds) shown to the user.
**Manual Verification:** in the browser, deposit → withdraw → transfer and watch balances update;
trigger an overdraw and see the error.
**Completion Criteria:** all three workflows succeed, attach CSRF, update balances, and render errors.
**Suggested Git Commit:** `feat(frontend): add deposit, withdrawal, and transfer forms`
**STOP:** Do not continue until all three money workflows work end-to-end in the browser.

---

## M9 — Admin Frontend `[SUBMISSION]`
*(SPEC §20 Phase 8; SPEC §12)*

### Phase 33 — Admin dashboard, customer management, status controls `[SUBMISSION]`
**Objective:** Admin stats, customer list/detail, and status controls (SPEC §12, §21.11).
**Why this phase comes now:** Last UI surface; depends on M5 admin APIs and the M7 auth shell.
**Concepts to Learn:** role-specific UI; admin drill-down; mutation + refetch; hiding unauthorized
features for UX while the backend stays the boundary.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `frontend/src/features/admin/`; admin pages/layout.
**Implementation Tasks:**
1. Admin dashboard rendering summary stats.
2. Customer list → customer detail (accounts + transactions drill-down).
3. Activate/deactivate and freeze/unfreeze controls (CSRF-protected) with refetch.
**Testing Required:** component: admin nav renders for admins only; status-control action issues a
CSRF-protected mutation; customer is denied admin UI.
**Manual Verification:** as admin, deactivate a customer and freeze an account; confirm effects.
**Completion Criteria:** admin can view stats, drill into customers, and change statuses from the UI.
**Suggested Git Commit:** `feat(frontend): add admin dashboard, customer detail, and status controls`
**STOP:** Do not continue until admin management works in the browser and is role-restricted.

---

## M10 — Frontend & E2E Testing `[SUBMISSION]`
*(SPEC §20 Phase 9 frontend portion; SPEC §14)*

### Phase 34 — Frontend component tests `[SUBMISSION]`
**Objective:** Complete the §14 frontend test layer.
**Why this phase comes now:** Consolidates component coverage before the single E2E.
**Concepts to Learn:** component testing; mocking the API client; asserting CSRF attachment and
error rendering.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `frontend/src/**/__tests__` / `frontend/tests/`.
**Implementation Tasks:**
1. Cover: login validation, success/fail rendering, protected-route behavior, dashboard
   rendering, money-form validation, CSRF-header attachment, API-error rendering, role-specific nav.
**Testing Required:** the component suite above passes.
**Manual Verification:** run the frontend test command; all green.
**Completion Criteria:** the §14 frontend scenarios are covered and passing.
**Suggested Git Commit:** `test(frontend): cover auth, dashboard, money forms, CSRF, and errors`
**STOP:** Do not continue until the frontend component suite passes.

### Phase 35 — End-to-end happy path `[SUBMISSION]`
**Objective:** One E2E: login → dashboard → deposit → withdraw → transfer → verify history
(SPEC §14, §21.14).
**Why this phase comes now:** Proves the whole stack works together against a real backend + DB.
**Concepts to Learn:** end-to-end testing; driving a real browser; seeding/resetting test data;
asserting balances/history after operations.
**Decisions to Confirm:** E2E tool (Playwright vs Cypress).
**Files or Areas Expected to Change:** `e2e/`.
**Implementation Tasks:**
1. Seed a known state; run the customer happy-path flow end-to-end.
2. Assert balances and history reflect the operations.
**Testing Required:** the single happy-path E2E passes.
**Manual Verification:** run the E2E locally against the running stack.
**Completion Criteria:** the happy-path E2E passes reliably.
**Suggested Git Commit:** `test(e2e): add customer happy-path end-to-end flow`
**STOP:** Do not continue until the happy-path E2E passes against the real stack.

---

## M11 — Deployment `[SUBMISSION]`
*(SPEC §20 Phase 10; SPEC §17 — note §17 tags Docker/proxy `[HARDENING → completed before final
submission]`, so they are on the submission critical path here)*

### Phase 36 — Dockerize the backend `[SUBMISSION]`
**Objective:** A reproducible backend container (SPEC §17).
**Why this phase comes now:** The single-origin deploy serves the SPA via the proxy and runs the
backend as a container; the image must exist first.
**Concepts to Learn:** containerizing a Python service; running migrations as a deploy step;
pooled connections to Supabase; the free-tier idle-pause caveat.
**Decisions to Confirm:** base image; how migrations run on deploy (`alembic upgrade head`).
**Files or Areas Expected to Change:** `backend/Dockerfile`; `docker-compose.yml` (local).
**Implementation Tasks:**
1. Write the backend `Dockerfile`.
2. Add a compose file for local Postgres + backend.
3. Define the migration step (`alembic upgrade head`) for deploy.
**Testing Required:** build the image; run it against a DB; `GET /api/health` responds from the container.
**Manual Verification:** `docker compose up`; hit `/api/health`.
**Completion Criteria:** the backend image builds and serves health from a container.
**Suggested Git Commit:** `build(docker): containerize the FastAPI backend with migration step`
**STOP:** Do not continue until the container builds and serves the API.

### Phase 37 — Single-origin reverse proxy + HTTPS + Supabase `[SUBMISSION]`
**Objective:** Deploy from a single origin on the VPS: proxy serves the SPA at `/` and proxies
`/api` to FastAPI, with TLS, Supabase Postgres, migrations, and seed (SPEC §17, §21.13).
**Why this phase comes now:** Single origin is what makes `HttpOnly` + `SameSite=Strict` cookies
work cleanly (SPEC §17); it is the final infra step before docs.
**Concepts to Learn:** reverse proxying; nginx TLS termination per D3; same-origin
cookie behavior; production migrations + seed; pooler connection + idle-pause keep-alive.
**Decisions to Confirm:** domain; certificate provisioning; whether a keep-alive guards the
idle-pause. D3 itself is resolved to nginx.
**Files or Areas Expected to Change:** `deploy/nginx/`; deploy scripts/notes;
production `.env` (not committed).
**Implementation Tasks:**
1. Build the SPA; have the proxy serve the static build at `/`.
2. Proxy `/api/*` to the backend container (same origin).
3. Terminate TLS in nginx using externally provisioned certificate/key files.
4. Point the backend at the Supabase pooler URL; run `alembic upgrade head`; run the seed.
5. Verify cookies are `Secure` and `SameSite=Strict` in production.
**Testing Required:** smoke: the deployed site serves the SPA and the API on one origin over HTTPS;
login works; cookie attributes are correct in production.
**Manual Verification:** log in on the live URL as customer and admin; inspect cookie attributes;
perform a deposit.
**Completion Criteria:** the app runs from a single HTTPS origin with Supabase, migrations, and
seed applied; cookies are `HttpOnly`/`Secure`/`SameSite=Strict`.
**Suggested Git Commit:** `build(deploy): single-origin reverse proxy, HTTPS, and Supabase deploy`
**STOP:** Do not continue until the app works on the live single origin with correct cookies.

---

## M12 — Documentation & Submission `[SUBMISSION]`
*(SPEC §20 Phase 13; SPEC §21.15)*

### Phase 38 — README, design write-up, AI citation, demo video `[SUBMISSION]`
**Objective:** Produce the submission documentation and verify all acceptance criteria (SPEC §21).
**Why this phase comes now:** The functional, deployed system can now be documented, demonstrated,
and submitted.
**Concepts to Learn:** technical writing; documenting design decisions and trade-offs; CS50x
honesty/AI-assistance citation; producing a demo video.
**Decisions to Confirm:** none.
**Files or Areas Expected to Change:** `README.md`; possibly `docs/` design notes (this plan +
MY_WORKFLOW.md feed the write-up).
**Implementation Tasks:**
1. README: overview, architecture, install/run, deploy steps, demo credentials, design decisions.
2. Cite AI assistance per CS50x policy.
3. Record the demo video.
4. **Walk the full §21 acceptance criteria (1–15) and confirm each holds** (use the mapping table below).
**Testing Required:** the full backend + frontend + E2E suites pass on a clean checkout; reseed runs.
**Manual Verification:** a reviewer-style run-through using only the README + demo credentials.
**Completion Criteria:** all 15 §21 acceptance criteria hold; README + video exist; AI assistance cited.
**Suggested Git Commit:** `docs: add README, design write-up, AI citation, and demo video`
**STOP — SUBMISSION CHECKPOINT:** The project is complete enough to document, demonstrate, and
submit. Do not start hardening/extensions until you have submitted (or decided to).

> **>>> SUBMISSION CHECKPOINT <<<** All `[SUBMISSION]` work is done and verified against SPEC §21.
> Everything below is optional and must never have blocked this point.

---

## M13 — Production Hardening `[HARDENING]`
*(SPEC §20 Phase 11; §23 — ordered by educational value. Not required for submission.)*

Each item below is its own small phase; apply the same per-phase discipline (objective → tasks →
tests → verify → commit). They do not block submission and can be done in any order, though the
listed order maximizes learning.

- **H1 — Structured JSON logging + per-request correlation IDs** (SPEC §16).
- **H2 — Idempotency keys** honored on deposit/withdrawal/transfer (SPEC §11, §23).
- **H3 — Login/refresh rate limiting and lockout** (SPEC §9.6, §23).
- **H4 — CI running the full suite on push** (SPEC §23).
- **H5 — Security headers + strict CSP + HSTS; reverse-proxy hardening** (SPEC §9.6, §15).
- **H6 — `/api/ready` readiness check (DB reachability)** (SPEC §11).
- **H7 — Production env validation on boot** (refuse insecure/default secrets) (SPEC §18).
- **H8 — DB backup strategy, deploy runbook, rollback docs** (SPEC §23).
- **H9 — Dependency vulnerability scanning; security-review checklist; basic monitoring** (SPEC §23).

**STOP discipline still applies per item:** finish, test, and understand each before the next.

---

## M14 — Extensions `[EXTENSION]`
*(SPEC §20 Phase 12; §22 — optional banking-domain learning. Not required for submission.)*

- **E1 — JWT access token + rotating refresh token** with reuse-detection / family revocation
  (the original JWT learning goal, as a deliberate refactor of the auth layer) (SPEC §22, §24.1).
  Refresh-rotation reuse tests apply only here.
- **E2 — Reconciliation as an admin tool** (expose the Ph23 check in the admin UI) (SPEC §8).
- **E3 — Admin UI to browse `AuditEvent`s; fraud-flag events** (SPEC §16).
- **E4 — Append-only corrections via compensating transactions**; `REVERSAL`/`ADJUSTMENT`/`FEE`/
  `INTEREST` transaction types (SPEC §10, §22).
- **E5 — Double-entry ledger** refactor (SPEC §24.9).
- **E6 — Customer profile editing; simulated identity workflow; (self-registration / password
  reset are out of MVP scope by §4)** (SPEC §22).
- **E7 — Admin approval workflow** for deposits/withdrawals (pending-state machine) (SPEC §22).

---

# Acceptance-criteria coverage map (SPEC §21)

Proof that every submission acceptance criterion maps to phase(s) and test(s).

| # | §21 Acceptance Criterion | Phase(s) | Covering test(s) |
|---|---|---|---|
| 1 | Demo customer & admin login; cookie `HttpOnly`/`Secure`/`SameSite=Strict` | Ph7, Ph10, Ph29, Ph37 | Ph16 login/cookie-attribute tests; Ph37 prod smoke |
| 2 | Customer views accounts/balances/history; deposit, withdraw, transfer; correct balances | Ph18–Ph22, Ph30–Ph32 | Ph18/19/20/21/22 API tests; Ph35 E2E |
| 3 | Over-balance withdrawals/transfers rejected `INSUFFICIENT_FUNDS`; no change | Ph21, Ph22 | Ph21/Ph22 insufficient-funds tests |
| 4 | Inactive/frozen account ops rejected; same-account transfer rejected | Ph20–Ph22, Ph26 | Ph20/21/22 status + same-account tests |
| 5 | A transfer failing midway leaves both balances unchanged | Ph22 | Ph22 induced-failure rollback test |
| 6 | Two concurrent withdrawals cannot overdraw; `CHECK (balance >= 0)` holds | Ph5, Ph21, Ph23 | Ph23 concurrency test; Ph6 CHECK test |
| 7 | Stored balance == signed sum of transactions (reconciliation) | Ph7, Ph23 | Ph7 + Ph23 reconciliation tests |
| 8 | Customer cannot read/mutate others' accounts (404) nor reach admin (403) | Ph14, Ph15 | Ph16 authz (403) + ownership (404) tests |
| 9 | Logout invalidates session server-side; deactivation revokes sessions | Ph12, Ph26 | Ph16 revocation test; Ph26 deactivation-revoke test |
| 10 | State-changing request without valid CSRF → `CSRF_INVALID` | Ph13 | Ph16 CSRF reject/accept tests |
| 11 | Admin lists/opens/deactivates customer, freezes account; admin not an owner | Ph24–Ph26, Ph33 | Ph24/25/26 admin tests; admins-not-owners test |
| 12 | All errors use the envelope; money as strings; logs/errors contain no secrets | Ph17, Ph18, Ph27 | Ph17 envelope tests; Ph27 redaction test |
| 13 | Deployed single-origin HTTPS; Supabase; migrations + seed applied | Ph36, Ph37 | Ph37 deploy smoke test |
| 14 | Backend auth/CSRF/business/rollback/concurrency/reconciliation + 1 E2E pass | Ph16, Ph23, Ph27, Ph35 | full backend suite + Ph35 E2E |
| 15 | README documents design/install/deploy + AI citation; demo video exists | Ph38 | manual verification (reviewer run-through) |

---

# Quick phase index

| Milestone | Phases | Tag |
|---|---|---|
| M0 Decisions & Prep | Ph0 | SUBMISSION |
| M1 Repo & Backend Foundation | Ph1–Ph3 | SUBMISSION |
| M2 Database | Ph4–Ph7 | SUBMISSION |
| M3 Authentication & Authorization | Ph8–Ph16 | SUBMISSION |
| M4 Banking Domain | Ph17–Ph23 | SUBMISSION |
| M5 Admin Backend | Ph24–Ph26 | SUBMISSION |
| M6 Backend Finalization (CHECKPOINT) | Ph27 | SUBMISSION |
| M7 Frontend Foundation & Auth | Ph28–Ph29 | SUBMISSION |
| M8 Customer Frontend | Ph30–Ph32 | SUBMISSION |
| M9 Admin Frontend | Ph33 | SUBMISSION |
| M10 Frontend & E2E Testing | Ph34–Ph35 | SUBMISSION |
| M11 Deployment | Ph36–Ph37 | SUBMISSION |
| M12 Documentation & Submission (CHECKPOINT) | Ph38 | SUBMISSION |
| M13 Production Hardening | H1–H9 | HARDENING |
| M14 Extensions | E1–E7 | EXTENSION |
