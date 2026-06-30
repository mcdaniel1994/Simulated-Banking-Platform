# Hostinger Deployment Workflow

This document records the external deployment process for Northstar Learning Bank. It supplements
`DEPLOYMENT.md` with the Hostinger-specific order of operations, evidence to capture, stopping
points, and security boundaries.

## Rules for This Workflow

- Work one stage at a time and verify it before continuing.
- Never paste or commit passwords, private SSH keys, database credentials, session secrets,
  cookies, tokens, or complete production connection strings.
- Record only non-sensitive evidence: dates, command names, success/failure, public hostname,
  public IP when needed, software versions, HTTP status codes, and commit hashes.
- Ask before rebuilding/reinstalling the VPS, changing billing, deleting resources, replacing DNS,
  opening additional firewall ports, or performing another destructive action.
- Keep PostgreSQL on Supabase; do not expose a database port from the VPS.
- The public host should expose only SSH as administratively required and HTTP/HTTPS for nginx.
- Do not start M13 hardening or M14 extensions during this submission deployment.

## Current State

- Date started: 2026-06-30
- Repository state: Phases 36–38 repository work committed and locally verified
- Hostinger state: VPS is running Ubuntu 24.04.4 LTS; public IP, SSH username, and port were
  verified in hPanel but are intentionally not recorded in this public-repository document
- Coolify state: Coolify is already installed on the VPS
- Planned delivery path: push this repository to GitHub, connect the Git source to Coolify, and
  deploy from the reviewed Compose configuration
- Current access method: VS Code Remote SSH using the VPS root username/IP and password
- Coolify repository state: `compose.coolify.yaml`, the internal nginx target, and the environment
  template are implemented and locally verified
- Current external task: commit the reviewed Coolify configuration and publish `main` to GitHub
- Current stopping point: stop after the clean repository is visible on GitHub; do not deploy until
  the domain and Supabase values are ready
- Not started externally: GitHub publication, Coolify application setup, DNS, Supabase, production
  environment, deployment, live smoke test, and video recording

## Deployment Architecture Adjustment — Approved

The repository's current `compose.production.yaml` was built for a manual VPS deployment where the
application's nginx container:

- binds host ports 80 and 443;
- terminates TLS itself; and
- mounts certificate/key files from the host.

Coolify already provides a reverse proxy (normally Traefik) that routes domains to application
containers and automatically issues/renews Let's Encrypt certificates. Deploying the current file
unchanged could create port conflicts and duplicate TLS ownership.

Approved Coolify architecture:

```text
GitHub repository
  -> Coolify Docker Compose build/deploy
  -> Coolify proxy terminates public HTTPS
  -> application nginx serves the SPA and proxies /api over internal HTTP
  -> private FastAPI backend
  -> Supabase PostgreSQL pooler over TLS
```

This preserves the required single browser origin and the internal nginx `/api` routing, while
making Coolify the sole public TLS owner. `compose.coolify.yaml` and
`deploy/nginx/coolify.conf` implement this separation without binding host ports 80/443 or mounting
TLS files. Do not deploy `compose.production.yaml` unchanged through Coolify.

This is an explicit operational amendment to D3. D3 originally selected nginx as the public TLS
proxy; under the approved Coolify path, the configured Coolify proxy owns public TLS and nginx
remains the internal application gateway. `SPEC.md` has not been silently rewritten.

### Local Verification Evidence

- Both `compose.coolify.yaml` and the manual `compose.production.yaml` parse successfully.
- The Coolify backend, migration, seed, and gateway images build.
- The one-shot migration exits successfully and the idempotent seed succeeds.
- Backend and gateway containers become healthy.
- Internal nginx passes `nginx -t`, serves the built SPA, and returns `/api/health` without
  stripping `/api`.
- Docker inspection confirms empty host port bindings for both gateway and backend.
- The preserved manual nginx/TLS gateway target still builds.
- Backend tests: 116 passed with the existing dependency warning.
- Frontend tests: 12 passed; format, lint, type-check, and build gates pass.

## Stage 1 — Hostinger VPS and SSH Access (Complete)

Goal: reach a stable shell on the intended VPS without deploying or changing the application.

1. In Hostinger, create or locate the VPS intended for this project.
2. Confirm it runs a currently supported Ubuntu LTS release.
3. Identify the public IP address, SSH username, and SSH port.
4. Connect using the existing VS Code Remote SSH password workflow. Public-key authentication is a
   recommended later improvement, not a submission deployment blocker.
5. Review Hostinger firewall/network controls. SSH must be reachable from the developer machine;
   HTTP 80 and HTTPS 443 will be needed later.
6. Connect from the developer machine:

   ```bash
   ssh SSH_USERNAME@VPS_IP
   ```

7. Confirm the shell belongs to the intended host. Do not install Docker or clone the repository
   until this stage is recorded as verified.

Evidence to record:

- [x] VPS is running
- [x] Supported Ubuntu LTS confirmed: Ubuntu 24.04.4 LTS
- [x] Public IP, SSH username, and SSH port identified in hPanel
- [ ] SSH public key installed (optional improvement; not required for this deployment)
- [x] SSH login from the developer machine succeeded through VS Code Remote SSH
- [x] No password or private key was copied into project files or chat

## Historical Prompt for Hostinger Kodee — Stage 1

This prompt is retained as process history. Stage 1 was completed with the user's existing VS Code
Remote SSH password workflow, so public-key setup is not required before continuing.

```text
I am deploying a CS50x educational project called Northstar Learning Bank to a Hostinger VPS.
The planned architecture is GitHub -> Coolify Docker Compose, with Coolify's proxy terminating
public HTTPS, an internal nginx container serving the React SPA and proxying /api, a private
FastAPI backend container, and PostgreSQL hosted separately on Supabase.

Help me with Stage 1 only: provision or locate the correct VPS and establish secure SSH access
from my Mac. Do not deploy the application yet.

Coolify is already installed on this VPS. Do not reinstall, remove, upgrade, or reconfigure
Coolify during this stage.

Please guide me one verified step at a time:

1. Confirm the VPS is running a currently supported Ubuntu LTS release.
2. Show me where to find its public IP address, SSH username, and SSH port.
3. Help me configure SSH public-key access using my Mac's public key. Never ask me to paste or
   upload my private SSH key.
4. Explain which Hostinger firewall/network setting must allow SSH from my machine. We will need
   ports 80 and 443 later, but do not open unrelated ports.
5. Give me the exact SSH command format to run from macOS.
6. Stop once I have successfully reached the VPS shell.

Do not reinstall or rebuild the VPS, change billing, delete resources, modify DNS, install
packages, expose a database port, or request passwords, tokens, private keys, database
credentials, or other secrets without first explaining why and obtaining my explicit approval.

At the end, provide a short checklist of non-sensitive information I should record:
Ubuntu version, public IP, SSH username, SSH port, and whether public-key login succeeded.
```

## Stage 2 — Publish the Repository to GitHub

Goal: make the reviewed repository available to Coolify through an authorized Git source.

Evidence:

- [ ] GitHub repository created under the intended account/organization
- [ ] Local `main` pushed without ignored environment files or credentials
- [ ] GitHub visibility (public/private) chosen deliberately
- [ ] Remote default branch and latest commit recorded
- [ ] GitHub secret scanning shows no exposed credentials

If the repository is private, prefer Coolify's GitHub App or a repository-scoped deploy key.
Never paste a personal access token into a repository file.

## Stage 3 — Connect GitHub to Coolify

Goal: create a Coolify application from the Git repository using the Docker Compose build pack.

Evidence:

- [ ] Coolify project and production environment created
- [ ] Public repository, GitHub App, or deploy-key connection selected appropriately
- [ ] Correct repository and `main` branch selected
- [ ] Docker Compose build pack selected
- [ ] Deployment commit is at or after the Hostinger/Coolify configuration commit
- [ ] Private backend and one-shot migration/seed services are not assigned public domains

Do not deploy until the Coolify-specific proxy/TLS configuration is committed and pushed.

## Stage 4 — Domain and DNS

Goal: point the chosen deployment hostname at the VPS before requesting a trusted certificate.

Evidence:

- [ ] Deployment hostname selected
- [ ] A record points to the VPS IPv4 address
- [ ] AAAA record is added only if IPv6 is correctly configured
- [ ] DNS resolution confirmed from outside the VPS
- [ ] Ports 80 and 443 reach the VPS

## Stage 5 — Supabase Production Database

Goal: create the separate production PostgreSQL target and obtain its TLS pooler URL.

Evidence:

- [ ] Supabase project created in a region reasonably close to the VPS
- [ ] Pooler host/port identified
- [ ] Production database password stored only in an approved secret location
- [ ] SQLAlchemy URL uses `postgresql+psycopg` and `sslmode=require`
- [ ] Test commands are not pointed at production

Never record the complete connection URL in this document.

## Stage 6 — Coolify Environment Variables

Goal: enter the required runtime values through Coolify's environment-variable interface. The
Compose file must continue to declare required variables with `${VARIABLE:?}` so missing values
fail before containers start.

Required runtime values:

- `DATABASE_URL`
- `SESSION_SECRET`
- `SESSION_IDLE_MINUTES`
- `SESSION_ABSOLUTE_HOURS`
- `COOKIE_DOMAIN`
- `CSRF_COOKIE_NAME`

Keep `COOKIE_DOMAIN` blank to retain the stronger `__Host-session` cookie. Coolify should store
secret values; they must not be copied into Git, build arguments, or deployment logs. The public
domain is assigned to the `gateway` service in Coolify's domain field rather than passed as an
application environment variable.

## Stage 7 — Coolify Domain and Trusted TLS

Goal: assign the real `https://` domain to the application gateway service so Coolify's proxy
requests and renews the Let's Encrypt certificate.

Evidence:

- [ ] Certificate matches the deployment hostname
- [ ] Certificate chain is trusted by a normal browser
- [ ] Coolify owns certificate issuance and renewal
- [ ] No application container mounts or stores the public TLS private key
- [ ] Application nginx listens only on its internal HTTP port

## Stage 8 — Migrate, Seed, and Start

Use Coolify's deployment flow after validating the equivalent lifecycle:

1. Build the images.
2. Run the one-shot Alembic migration.
3. Run the deterministic demo seed.
4. Start the private backend and internal nginx gateway.
5. Confirm containers are healthy.

Do not run an unreviewed Alembic downgrade or destructively reset the production database.

## Stage 9 — Live Verification

Evidence:

- [ ] HTTP redirects to HTTPS
- [ ] `/` serves the React SPA
- [ ] `/api/health` returns HTTP 200 without stripping `/api`
- [ ] Customer login, dashboard, deposit, and logout succeed
- [ ] Administrator login, dashboard, and logout succeed
- [ ] Session cookie is `HttpOnly`, `Secure`, `SameSite=Strict`, and `Path=/`
- [ ] Revoked session reuse returns 401
- [ ] Production Playwright smoke passes against the trusted URL
- [ ] No secrets appear in browser output, container logs, or committed files

## Stage 10 — Close the Submission Blockers

1. Update `SUBMISSION_CHECKLIST.md` criterion 13 with the real deployment evidence.
2. Follow `DEMO_VIDEO.md`, record the video, upload it as public/unlisted, and add the URL to
   `README.md`.
3. Mark criterion 15 complete only after the uploaded video works while signed out.
4. Update `PROGRESS.md` and append the actual deployment results to `MY_WORKFLOW.md`.
5. Run final gates, commit the evidence updates, and submit to CS50x.

## Deployment Journal

Append verified milestones here without secrets.

| Date | Stage | Result | Non-sensitive evidence | Next action |
|---|---|---|---|---|
| 2026-06-30 | 1 — VPS and SSH | COMPLETE | VPS running Ubuntu 24.04.4 LTS; connection values verified in hPanel; existing VS Code Remote SSH password login confirmed; Coolify already installed | Prepare Coolify-specific repository configuration |
| 2026-06-30 | Architecture | COMPLETE LOCALLY | Coolify owns public TLS; internal nginx serves SPA and preserves `/api`; backend stays private; no host ports; manual nginx/TLS path still builds | Commit and publish clean `main` to GitHub |
