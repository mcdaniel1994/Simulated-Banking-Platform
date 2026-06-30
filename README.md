# Northstar Learning Bank

#### Source Code: [GitHub](https://github.com/mcdaniel1994/Simulated-Banking-Platform)
#### Live Demo: Not deployed yet
#### Video Demo: Not recorded yet — follow [the demo-video checklist](docs/DEMO_VIDEO.md)

## Description

Northstar Learning Bank is a full-stack simulated online banking application built as a CS50x
final project. It models the engineering problems behind banking software—authentication,
authorization, exact money arithmetic, concurrent balance updates, transaction integrity, and
auditability—without connecting to a real bank or moving real money.

Customers can sign in with seeded credentials, view checking and savings accounts, page through
transaction history, add demo funds, withdraw simulated money, and transfer between their own
accounts. Administrators have a separate dashboard for aggregate statistics, customer drill-down,
customer activation/deactivation, and account freeze/unfreeze controls. Administrators cannot use
customer money operations, and customers cannot access administrator routes or another customer's
accounts.

> **Simulated-money disclaimer:** This is educational software. It does not connect to financial
> institutions, process real funds, provide financial services, or store real customer data. Never
> enter real banking credentials or personal information.

## Architecture

```text
Browser
  -> HTTPS nginx single origin
       -> React/TypeScript static SPA at /
       -> FastAPI API at /api/*
            -> Pydantic validation
            -> SQL-backed session + CSRF + role/ownership dependencies
            -> service-layer banking rules and transaction boundaries
            -> SQLAlchemy 2.0
            -> PostgreSQL
```

The backend is the only security boundary. Frontend route guards improve the user experience, but
FastAPI independently authenticates every protected request, reads the role from PostgreSQL, and
filters customer resources by the authenticated owner. Routes stay thin; services own business
rules and atomic transactions; SQLAlchemy models and PostgreSQL constraints provide persistence
and integrity backstops.

The repository is organized as follows:

- `backend/app/api/` contains FastAPI dependencies and thin route handlers.
- `backend/app/services/` contains authentication, account, money, transfer, administration, and
  reconciliation logic.
- `backend/app/models/` and `backend/alembic/` define and migrate the PostgreSQL schema.
- `backend/tests/` covers units, API contracts, services, database constraints, rollback,
  concurrency, reconciliation, and sensitive-data redaction.
- `frontend/src/` contains the React application, typed API client, role-based layouts, and
  customer/administrator features.
- `frontend/e2e/` contains the local happy path and deployed-origin browser smoke tests.
- `deploy/nginx/`, `compose.yaml`, and `compose.production.yaml` define local and deployment
  container topologies.
- `docs/` contains the implementation plan, progress evidence, engineering journal, deployment
  runbook, acceptance checklist, and demo-video plan.

## Security Model

Authentication uses opaque server-side sessions. The browser receives a high-entropy raw token in
an `HttpOnly`, `Secure`, `SameSite=Strict` cookie, while PostgreSQL stores only its HMAC-SHA256
lookup hash. Logout and administrator deactivation revoke persisted sessions immediately. Browser
JavaScript never reads or stores the session token or a trusted role.

Every authenticated mutation also requires a double-submit CSRF token: a readable CSRF cookie must
match the `X-CSRF-Token` header. Passwords are hashed with Argon2id. Login failures are generic to
reduce user enumeration. Account ownership is enforced in SQL-filtered backend lookups; a missing
or non-owned account returns the same 404 response.

Money enters and leaves the API as decimal strings, becomes Python `Decimal`, and is stored as
PostgreSQL `NUMERIC(14,2)`. Deposits and withdrawals lock the account row. Transfers lock both
accounts in ascending ID order and persist the parent transfer, two transaction legs, both
balances, and audit event in one database transaction. A database check prevents negative
balances, and reconciliation tests prove stored balances equal signed transaction history.

## Local Installation

Requirements:

- Docker Desktop or Docker Engine with Compose
- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js 22 and npm
- Playwright Chromium for browser tests

Create local configuration:

```bash
cp .env.example .env
```

Replace every password/secret placeholder in the ignored `.env`. Keep the development and test
database URLs distinct. Then start PostgreSQL, migrate, seed, and install dependencies:

```bash
docker compose up -d postgres
cd backend
uv sync --frozen
uv run alembic upgrade head
uv run python -m app.seed
cd ../frontend
npm ci
```

Run FastAPI and Vite in separate terminals:

```bash
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173`. Vite proxies relative `/api` requests to FastAPI so the browser client
uses the same URL shape as production.

## Demo Credentials

These identities are synthetic, intentionally public, and restored by the idempotent seed:

| Role | Email | Password |
|---|---|---|
| Customer | `alex.customer@demo.bank.test` | `CustomerDemo!2026` |
| Administrator | `admin@demo.bank.test` | `AdminDemo!2026` |

## Docker Workflow

The existing developer workflow can run PostgreSQL alone:

```bash
docker compose up -d postgres
```

To run migrations and FastAPI in containers:

```bash
docker compose build backend migrate
docker compose run --rm migrate
docker compose up -d backend
curl http://127.0.0.1:8000/api/health
```

The backend image installs locked runtime dependencies in a build stage and runs the API as an
unprivileged user. Migrations are a one-shot deploy job, not part of every web-process startup, so
multiple replicas cannot race to change the schema.

## Production Deployment

The selected deployment pushes this repository to GitHub and lets Coolify build
`compose.coolify.yaml`. Coolify's proxy owns public HTTPS and certificate renewal; an internal
nginx container serves the SPA at `/` and proxies `/api/*` unchanged to the private FastAPI
container. PostgreSQL is reached through a TLS-enabled Supabase pooler URL.

The manual `compose.production.yaml` path remains available as a verified fallback, but it must not
be combined with Coolify because it binds host ports and owns TLS itself. Follow
[the deployment runbook](docs/DEPLOYMENT.md) and the
[Hostinger/Coolify workflow](docs/HOSTINGER_DEPLOYMENT_WORKFLOW.md).

The repository contains no domain, VPS credentials, Supabase password, or production session
secret. A real Coolify deployment must supply those external values.

## Testing

With PostgreSQL running and the ignored `.env` configured:

```bash
cd backend
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest -q
uv run alembic check
```

```bash
cd frontend
npm run format:check
npm run lint
npm run typecheck
npm test
npm run build
npm run test:e2e
```

Against an already-running trusted HTTPS deployment:

```bash
cd frontend
PRODUCTION_BASE_URL=https://bank.example.com npm run test:e2e:production
```

The complete acceptance evidence and any externally blocked criteria are recorded in
[`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md).

## Important Design Decisions and Trade-offs

- **Opaque sessions instead of JWTs:** persisted sessions make immediate revocation simple and
  avoid signature/claim-verification mistakes. A JWT rotation exercise remains an optional
  post-submission extension.
- **Single origin:** serving SPA and API together keeps strict cookies and CSRF behavior
  straightforward. It trades independent frontend hosting for a smaller security surface.
- **Coolify TLS with internal nginx:** Coolify's proxy owns public HTTPS and automatic certificate
  renewal, while nginx retains one application gateway for SPA fallback and prefix-preserving
  `/api` routing. The manual nginx-owned TLS path remains a fallback.
- **Synchronous SQLAlchemy:** the money path is easier to teach and reason about with explicit
  transactions and row locks. Connection pooling still bounds database concurrency.
- **Stored balance plus append-only history:** balance is an atomically maintained cache for fast
  reads; transaction history is the source of truth and reconciliation detects drift.
- **Offset pagination:** it is simple and matches the MVP contract, although cursor pagination
  would be preferable for a high-write production ledger.
- **No destructive reseed:** seed reruns preserve later append-only activity. This protects the
  developer database but means reviewer operations intentionally cause demo-data drift.

Production hardening such as rate limiting, structured correlation IDs, strict CSP/HSTS, readiness
checks, automated backups, dependency scanning, and monitoring is deliberately outside the CS50x
submission path and remains unimplemented.

## AI Assistance Disclosure

This project used ChatGPT, Claude Code, and OpenAI Codex as development assistants for
brainstorming, specification review, implementation planning, code/configuration suggestions,
debugging, test design, security review, and documentation. AI-generated suggestions were reviewed
against `SPEC.md`, implemented incrementally, exercised by automated and manual tests, and recorded
in `docs/MY_WORKFLOW.md`; responsibility for the submitted design and code remains with the
student. Entry-point source comments point to this disclosure so the assistance is cited in code
as required by the [CS50x 2026 final-project policy](https://cs50.harvard.edu/x/project/).

## Submission Status

Repository implementation and local verification are complete through Phase 38. The project is
not yet ready to claim all submission criteria: the real VPS/Supabase/trusted-domain deployment and
the required public/unlisted demonstration video remain external actions. See the submission
checklist for the exact evidence and next steps.
