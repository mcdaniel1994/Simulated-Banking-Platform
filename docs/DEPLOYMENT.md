# Single-Origin Deployment

This runbook deploys the React SPA and FastAPI API from one HTTPS origin. nginx serves the built
SPA at `/` and forwards `/api/*` unchanged to the private backend container. FastAPI remains the
authentication, authorization, CSRF, ownership, and banking-rule boundary.

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

Use the pooler URL supplied by Supabase, expressed with SQLAlchemy's psycopg driver:

```text
postgresql+psycopg://USER:PASSWORD@POOLER_HOST:PORT/postgres?sslmode=require
```

Choose a Supabase region near the VPS. The backend is a long-lived process with a bounded
SQLAlchemy pool; do not use a browser/API key as the database password. Never run tests against
this URL.

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

## First Deployment

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
