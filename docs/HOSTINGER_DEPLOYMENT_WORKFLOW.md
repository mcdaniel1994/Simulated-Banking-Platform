# Hostinger Deployment Workflow

This document records the external deployment process for Northstar Bank. It supplements
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
- Delivery path: public GitHub repository through Coolify using the reviewed Compose configuration
- Current access method: VS Code Remote SSH using the VPS root username/IP and password
- Coolify repository state: `compose.coolify.yaml`, the internal nginx target, and the environment
  template are implemented and locally verified
- GitHub state: the repository is public at
  `https://github.com/mcdaniel1994/Simulated-Banking-Platform`; Coolify deployed commit `71a9689`
- Current external task: record and publish the required demonstration video
- Current stopping point: follow the existing video checklist without starting M13/M14 work
- Completed externally: Coolify application setup, DNS, Supabase, production environment,
  deployment, trusted HTTPS, seed, refreshed admin/customer UI, and live Supabase persistence
- Not started externally: recorded demo video

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
- Backend tests: 122 passed with the existing dependency warning.
- Frontend tests: 21 passed; format, lint, type-check, and build gates pass.

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

- [x] GitHub repository created under the intended account
- [x] Local `main` pushed without ignored environment files or credentials
- [x] Public visibility chosen deliberately for the portfolio source code
- [x] Remote default branch is `main`; publication commit recorded as `f88fb35`
- [x] GitHub secret-scanning alerts API returned zero alerts after publication

If the repository is private, prefer Coolify's GitHub App or a repository-scoped deploy key.
Never paste a personal access token into a repository file.

## Stage 3 — Connect GitHub to Coolify

Goal: create a Coolify application from the Git repository using the Docker Compose build pack.

Evidence:

- [x] Coolify project and production environment created
- [x] Public repository connection selected appropriately
- [x] Correct repository and `main` branch selected
- [x] Docker Compose build pack selected
- [x] Coolify source revision is `HEAD` on `main`; verified branch tip `0c334d3` is after the
  Hostinger/Coolify configuration commit `f88fb35`
- [x] `migrate`, `seed`, `backend`, and `gateway` services recognized from `/compose.coolify.yaml`
- [x] Private backend and one-shot migration/seed services are not assigned public domains

Do not deploy until the Coolify-specific proxy/TLS configuration is committed and pushed.

## Stage 4 — Domain and DNS

Goal: point the chosen deployment hostname at the VPS before requesting a trusted certificate.

Evidence:

- [x] Deployment hostname selected: `bank.forgehub.cloud`
- [x] A record points to the VPS IPv4 address
- [x] No AAAA record added because IPv6 has not been configured and verified
- [x] DNS resolution confirmed from outside the VPS through the system resolver, Cloudflare, and
  Google
- [x] Ports 80 and 443 reach the VPS

## Stage 5 — Supabase Production Database

Goal: create the separate production PostgreSQL target and obtain its TLS pooler URL.

Current state: the production Supabase project has been created. Its connection fields have not
been entered into Coolify. The selected database region is East US (North Virginia), and the
Shared Pooler session-mode endpoint has been identified at
`aws-0-us-east-1.pooler.supabase.com:5432`.

Evidence:

- [x] Supabase project created
- [x] Supabase East US region confirmed reasonably close to the VPS
- [x] Shared Pooler session-mode host/port identified
- [x] Production database password stored only in an approved password manager
- [x] SQLAlchemy URL stored privately with `postgresql+psycopg` and `sslmode=require`
- [x] Test commands remain pointed at the separate local test database, not production

Never record the complete connection URL in this document.

The deployment templates use Shared Pooler session mode on port 5432 because the Coolify backend
is a persistent SQLAlchemy client and needs prepared-statement support. Transaction-mode port 6543
is reserved for temporary/serverless clients and is not the selected path.

## Stage 6 — Coolify Environment Variables

Goal: enter the required runtime values through Coolify's environment-variable interface. The
Compose file must continue to declare required variables with `${VARIABLE:?}` so missing values
fail before containers start.

Current state: all six required production values have been entered and verified in Coolify.
`DATABASE_URL` and `SESSION_SECRET` are masked/literal values, the session lifetime values match
D1, `COOKIE_DOMAIN` is blank, and `CSRF_COOKIE_NAME` remains `csrf_token`. Automated preview
deployments are not enabled, no pull request deployment is active, and Coolify keeps preview
variables separate from production variables.

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

Current state: `https://bank.forgehub.cloud` is assigned only to `gateway`. The first successful
deployment created the Traefik router and issued a browser-trusted certificate for the hostname.
The healthy `coolify-proxy` runs Traefik v3.6 and owns host ports 80/443. Although port 8080 is
bound by the proxy on the host, an external TCP probe timed out, so it is not publicly reachable.

Evidence:

- [x] Production domain assigned only to `gateway`
- [x] Certificate matches the deployment hostname
- [x] Certificate chain is trusted by a normal TLS client
- [x] Coolify/Traefik owns certificate issuance and renewal through its Let's Encrypt resolver
- [x] No application container mounts or stores the public TLS private key
- [x] Application nginx listens only on its internal HTTP port

## Stage 8 — Migrate, Seed, and Start

Use Coolify's deployment flow after validating the equivalent lifecycle:

1. Build the images.
2. Run the one-shot Alembic migration.
3. Run the deterministic demo seed.
4. Start the private backend and internal nginx gateway.
5. Confirm containers are healthy.

Do not run an unreviewed Alembic downgrade or destructively reset the production database.

Current state: after correcting the concrete Shared Pooler URL, the migration completed
successfully, backend became healthy, and gateway started. The resource reports Running/healthy.
The deterministic demonstration seed completed successfully through the running backend container.

## Stage 9 — Live Verification

Evidence:

- [x] HTTP redirects to HTTPS
- [x] `/` serves the React SPA
- [x] `/api/health` returns HTTP 200 without stripping `/api`
- [x] Customer login, dashboard, and deposit succeed
- [x] Deposit updates the displayed balance/history and persists in Supabase
- [x] Customer logout succeeds and protected dashboard access redirects to login
- [x] Administrator login and dashboard succeed
- [x] Administrator customer creation succeeds and persists the new customer/account in Supabase
- [x] Administrator logout succeeds and protected dashboard access redirects to login
- [x] Session cookie is `HttpOnly`, `Secure`, `SameSite=Strict`, host-only, and `Path=/`
- [x] Revoked session reuse returns 401
- [x] Production Playwright smoke passes against the trusted URL
- [x] No secrets appear in application/browser output, container logs, or committed files

## Stage 10 — Close the Submission Blockers

1. Follow `DEMO_VIDEO.md`, record the video, upload it as public/unlisted, and add the URL to
   `README.md`.
2. Mark criterion 15 complete only after the uploaded video works while signed out.
3. Run final documentation checks, commit the video URL/evidence updates, and submit to CS50x.

## Deployment Journal

Append verified milestones here without secrets.

| Date | Stage | Result | Non-sensitive evidence | Next action |
|---|---|---|---|---|
| 2026-06-30 | 1 — VPS and SSH | COMPLETE | VPS running Ubuntu 24.04.4 LTS; connection values verified in hPanel; existing VS Code Remote SSH password login confirmed; Coolify already installed | Prepare Coolify-specific repository configuration |
| 2026-06-30 | Architecture | COMPLETE LOCALLY | Coolify owns public TLS; internal nginx serves SPA and preserves `/api`; backend stays private; no host ports; manual nginx/TLS path still builds | Commit and publish clean `main` to GitHub |
| 2026-06-30 | 2 — GitHub publication | COMPLETE | Public repository published; remote `main` matched `f88fb35`; GitHub secret-scanning alerts API returned zero alerts | Connect the repository to Coolify |
| 2026-06-30 | 3 — Coolify connection | COMPLETE | `Northstar Learning Bank` project and `production` environment created; Public GitHub source uses `main`/`HEAD` at verified tip `0c334d3`; `/compose.coolify.yaml` loaded; expected four services recognized; no domains assigned | Prepare the deployment hostname and DNS without deploying |
| 2026-06-30 | 4 — Domain and DNS | COMPLETE | `bank.forgehub.cloud` A record created; system, Cloudflare, and Google resolvers return the VPS IPv4 address; no AAAA record; TCP ports 80 and 443 reachable | Prepare the Supabase production database |
| 2026-06-30 | 5 — Supabase database | COMPLETE | East US region confirmed near VPS; unused Data API disabled; Shared Pooler session endpoint on port 5432; password and TLS SQLAlchemy URL stored in password manager; local tests remain isolated | Assign the production domain only to the Coolify gateway |
| 2026-06-30 | 6 — Coolify environment | COMPLETE | Six production variables entered and verified; secrets masked/literal; cookie domain blank; automated previews not enabled; no values recorded in Git or this journal | Complete the remaining Stage 5 region/isolation confirmation |
| 2026-06-30 | 7 — Domain and TLS | COMPLETE | Gateway-only domain assigned; Traefik v3.6 owns 80/443; trusted certificate issued; HTTP redirects to HTTPS; HTTPS SPA and `/api/health` return 200 | Seed deliberate demonstration data |
| 2026-06-30 | 8 — First deployment | BLOCKED SAFELY | Two attempts stopped at `migrate`; container log identified literal `POOLER_HOST` template token causing DNS failure; no database connection or schema change occurred | Replace all generic URL tokens with the concrete Shared Pooler values and verify without printing them |
| 2026-06-30 | 8 — Deployment recovery | COMPLETE | Concrete URL corrected; migration exited successfully; backend healthy; gateway running; resource healthy; public SPA/API health verified; deterministic demo seed succeeded | Begin live customer/admin functional and security verification |
| 2026-06-30 | 9 — Customer verification | COMPLETE | Live customer login and dashboard succeeded; a simulated deposit updated the balance and transaction history; the corresponding production data change was visible in Supabase; logout returned to login and protected dashboard reuse was denied | Verify the administrator flow |
| 2026-06-30 | 9 — Administrator verification | COMPLETE | Live administrator login succeeded; the dashboard loaded customer, account, balance, and transaction summaries; logout returned to login and protected dashboard reuse was denied | Verify production cookie attributes and revoked API-session behavior |
| 2026-06-30 | 9 — Cookie verification | COMPLETE | Browser storage showed the `__Host-session` cookie with HttpOnly, Secure, SameSite Strict, path `/`, and host-only scope; the inspected session was immediately revoked by logout | Run the automated production smoke |
| 2026-06-30 | 9 — Automated smoke | COMPLETE | Production Playwright smoke passed 2/2 against trusted HTTPS; both roles authenticated and logged out; secure cookie assertions passed; customer mutation succeeded; post-logout `/api/auth/me` returned 401 | Complete the production secret-output audit |
| 2026-06-30 | 9 — Secret-output audit | COMPLETE | Coolify deployment/container logs contained no database URL, session secret, password, connection string, or traceback; tracked URL/secret matches were placeholders or isolated test values; no application output exposed secrets | Record and publish the required demonstration video |
| 2026-06-30 | 9 — Refreshed application | COMPLETE | Coolify deployed commit `71a9689`; professional UI and admin customer creation are live; application mutations were observed in Supabase; public login and `/api/health` return 200 | Record and publish the required demonstration video |
