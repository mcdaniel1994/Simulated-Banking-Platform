# Single-Origin Deployment

This runbook deploys the React SPA and FastAPI API from one HTTPS origin. nginx serves the built
SPA at `/` and forwards `/api/*` unchanged to the private backend container. FastAPI remains the
authentication, authorization, CSRF, ownership, and banking-rule boundary.

For the ordered Hostinger control-panel, SSH, DNS, and evidence workflow, use
[`HOSTINGER_DEPLOYMENT_WORKFLOW.md`](HOSTINGER_DEPLOYMENT_WORKFLOW.md) alongside this command
runbook.

## Selected Deployment — GitHub to Coolify

The selected production path is:

```text
GitHub -> Coolify Compose build -> Coolify HTTPS proxy
  -> internal nginx gateway on port 80
     -> React SPA at /
     -> private FastAPI at /api/*
        -> Supabase PostgreSQL pooler over TLS
```

Use `compose.coolify.yaml`, not `compose.production.yaml`, when creating the Coolify application.
The Coolify file deliberately has:

- no host `ports` mappings;
- no TLS certificate/key mounts;
- one public-eligible `gateway` service exposing container port 80;
- a private `backend` exposing port 8000 only to the Compose network; and
- a one-shot `migrate` service that must succeed before FastAPI starts.

### 1. Publish and connect the Git source

Push the reviewed repository to GitHub. In Coolify, create a Docker Compose application from the
public repository, GitHub App, or repository-scoped deploy key, then select:

- branch: `main`;
- Compose file: `/compose.coolify.yaml`;
- build pack: Docker Compose.

Do not assign a domain to `backend`, `migrate`, or `seed`. Assign the production domain only to
`gateway`.

### 2. Configure Coolify environment values

Use `.env.coolify.example` as the field checklist. Enter real values through Coolify's environment
interface, not a committed file:

- `DATABASE_URL` — Supabase pooler URL with `postgresql+psycopg` and `sslmode=require`;
- `SESSION_SECRET` — long random production-only value;
- `SESSION_IDLE_MINUTES=30`;
- `SESSION_ABSOLUTE_HOURS=12`;
- `COOKIE_DOMAIN` — blank;
- `CSRF_COOKIE_NAME=csrf_token`.

Coolify detects the `${VARIABLE:?}` declarations and must refuse deployment while required values
are missing.

### 3. Assign the domain and deploy

Assign `https://YOUR_DOMAIN` to the `gateway` service on container port 80. Coolify's proxy owns
host ports 80/443 and obtains/renews the Let's Encrypt certificate. The nginx application
container remains HTTP-only on Coolify's private network.

Deploy the stack and inspect the migration logs. The backend must not start until `alembic upgrade
head` exits successfully.

### 4. Seed the demonstration data

After the first successful migrated deployment, open Coolify's terminal for the `backend` service
and run:

```bash
python -m app.seed
```

The command is deterministic and idempotent. Run it deliberately for the demonstration
environment; do not print or copy any production secret while using the terminal.

### 5. Verify

Run the HTTP/API/browser checks in the Verification section below against the trusted Coolify
domain. Confirm that only `gateway` is public and Coolify reports `backend` healthy.

## Manual VPS Alternative

The remaining `compose.production.yaml` instructions describe the previously verified manual
alternative where application nginx binds ports 80/443 and owns certificate mounts. Do not combine
that file with Coolify's proxy.

## Required External Values

Before deployment, obtain:

- a VPS with Docker Engine and the Compose plugin;
- a DNS name whose A/AAAA record points to that VPS;
- a Supabase project and its PostgreSQL pooler URL;
- a production-only database password and random `SESSION_SECRET`;
- a trusted TLS certificate and private key for the DNS name.

The repository does not contain or generate production credentials. Copy `.env.production.example`
to an ignored `.env.production` on the VPS and replace every placeholder. Keep `COOKIE_DOMAIN`
blank so the backend can issue the host-only `__Host-session` cookie.

## Supabase Preparation

Use the Shared Pooler session-mode URL supplied by Supabase, expressed with SQLAlchemy's psycopg
driver:

```text
postgresql+psycopg://USER:PASSWORD@POOLER_HOST:5432/postgres?sslmode=require
```

Session mode is selected because FastAPI is a persistent process with a bounded SQLAlchemy pool,
and it retains prepared-statement support while providing IPv4 connectivity from the VPS. Do not
substitute the transaction-mode port 6543, which is intended for temporary/serverless clients and
does not support prepared statements. Choose a Supabase region near the VPS. Do not use a
browser/API key as the database password. Never run tests against this URL.

## TLS Provisioning

nginx expects a full certificate chain and private key at the host paths configured by
`TLS_CERTIFICATE_PATH` and `TLS_PRIVATE_KEY_PATH`. Provision and renew these with the VPS provider
or an ACME client such as Certbot. Certificate issuance requires the real DNS name and inbound
network access, so it is deliberately outside the image build.

After renewal, validate and reload the gateway:

```bash
docker compose --env-file .env.production -f compose.production.yaml exec gateway nginx -t
docker compose --env-file .env.production -f compose.production.yaml exec gateway nginx -s reload
```

## Manual First Deployment

Run migrations as a one-shot job before starting the web services:

```bash
docker compose --env-file .env.production -f compose.production.yaml build
docker compose --env-file .env.production -f compose.production.yaml run --rm migrate
docker compose --env-file .env.production -f compose.production.yaml --profile seed run --rm seed
docker compose --env-file .env.production -f compose.production.yaml up -d backend gateway
docker compose --env-file .env.production -f compose.production.yaml ps
```

The seed is deterministic and idempotent. It creates only synthetic `.test` users and preserves
append-only activity on later runs. Run it for the demonstration deployment, not as an automatic
web-container startup action.

## Verification

From a separate machine:

```bash
curl -I "http://bank.example.com/"
curl --fail "https://bank.example.com/api/health"
```

Confirm HTTP redirects to HTTPS, the SPA loads at `/`, and the health response comes from
`/api/health` (not `/health`). In browser developer tools verify:

- customer and administrator login work through the same origin;
- the session cookie is `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/`;
- the CSRF cookie is readable, `Secure`, `SameSite=Strict`, and sent back in `X-CSRF-Token`;
- logout invalidates the session;
- customer and admin dashboards remain role-restricted;
- a small simulated customer deposit succeeds and appears in history.

The automated browser smoke targets an already-running deployment:

```bash
cd frontend
PRODUCTION_BASE_URL=https://bank.example.com npm run test:e2e:production
```

The real deployment must use a trusted certificate. `ALLOW_SELF_SIGNED_TLS=true` exists only for
the temporary local verification certificate and must not be used as evidence of public TLS trust.

## Updates and Rollback

Build a new image, run `migrate`, then recreate the services. Database migrations are forward
operations; take a Supabase backup before applying a future schema revision. If an application
image must be rolled back, redeploy the previous Git commit only after confirming its code is
compatible with the current schema. Never use `alembic downgrade` against production as an
unreviewed recovery shortcut.

Supabase free-tier projects may pause while idle. A cold first request can therefore be slower;
the backend's `pool_pre_ping` discards stale connections, but uptime monitoring/keep-alive policy
belongs to post-submission hardening.
