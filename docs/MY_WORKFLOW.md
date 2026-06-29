# My Engineering Workflow and Learning Journal

This is where I record **what I did, why I decided it, and what I learned** — not just what got
checked off. [PROGRESS.md](PROGRESS.md) tracks *status*; this file captures *thinking*.
[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) is the roadmap; [../SPEC.md](../SPEC.md) is the
source of truth.

## How I Reached the Specification

I started by using ChatGPT to brainstorm the banking application I wanted to build. That process
helped me turn a broad project idea into something more concrete by identifying the important
features, architectural decisions, security concerns, and trade-offs I would need to understand.
Working through those questions eventually gave me enough clarity to create `SPEC.md` as the
project's source of truth.

After creating the specification, I used Claude Code to pressure-test it. We walked through the
decisions, looked for missing requirements or contradictions, and separated the work required for
the CS50x submission from production hardening and optional extensions. Claude Code then helped me
turn the specification into a phased implementation plan.

This process lets me use AI as a planning and review tool while keeping control of the development
work. Instead of asking an AI to build the entire application at once, I can work through one
feature at a time, understand why it belongs in the architecture, implement it myself, and verify
it before moving forward.

I added the `docs/` folder so each planning document has one clear responsibility:

- `IMPLEMENTATION_PLAN.md` turns the specification into an ordered roadmap with small phases,
  tests, completion criteria, and stopping points.
- `PROGRESS.md` is the operational checklist that tells me what is complete, what I am working on,
  and what comes next.
- `MY_WORKFLOW.md` is my learning journal. It records how I reached decisions, what I tried, what
  went wrong, and what I learned along the way.

Together, these files keep the product requirements, implementation order, current status, and my
reasoning separate but connected. That makes it easier for me to stay in control of the scope and
develop the application one feature at a time.

## How I Use This File

- **During each phase**, I start a dated entry from the template below and record what I expected,
  what actually happened, and what finally clicked.
- **When I make an architecture decision** (or resolve one of D1–D4), I add it to the Architecture
  Decision Log so I can remember why I made the choice.
- **When I hit a bug**, I add it to the Debugging Log after I understand the root cause.
- **When a concept finally makes sense**, I explain it in my own words under Concepts Learned.
- I keep these notes honest. "I expected X, got Y, and the cause was Z" is more useful to me than
  a polished summary that hides the learning process.

---

## Per-Phase Entry Template

Copy this section when I begin a phase.

### Entry — YYYY-MM-DD — Phase NN: Phase Name

#### What I Worked On

#### What I Expected to Happen

#### What Actually Happened

#### Concepts I Learned

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
|  |  |  |  |  |

#### Problems I Encountered

#### How I Diagnosed Them

#### How I Solved Them

#### Tests I Added

#### Commands I Used

#### Files I Changed

#### Security or Reliability Considerations

#### What I Would Do Differently

#### Questions I Still Have

#### Next Step

---

## Phase Entries

### Entry — 2026-06-29 — Phase 1: Repository Structure and Tooling

#### What I Worked On

I created the initial backend package structure and separated the application into API, core,
database, model, repository, schema, and service packages. I also created matching test areas for
unit, service, API, and database tests.

I chose uv for dependency and environment management, created a Python 3.12 virtual environment,
and separated runtime dependencies from development dependencies in `pyproject.toml`. The exact
resolved dependency versions are stored in `uv.lock`.

I configured Ruff to handle both formatting and linting, created the root `.gitignore`, and added
three backend guides explaining how the backend, application packages, and test suite fit together.

#### What I Expected to Happen

I expected to finish this phase with an importable but intentionally empty backend package, a
reproducible environment, and development tools that could run before any application behavior
existed.

#### What Actually Happened

The package imported successfully, all dependency imports worked, Ruff confirmed that all 14
Python files were formatted and free of configured lint violations, and pytest collected the empty
test suite without an import or collection error.

Pytest returned exit code `5`, which initially looks like a failure but specifically means that no
tests were collected. That is expected here because the first behavior and integration test belong
to Phase 2.

#### Concepts I Learned

- A virtual environment isolates this project's Python interpreter and installed packages from the
  rest of my machine.
- `pyproject.toml` declares the direct dependencies and tool configuration, while `uv.lock`
  captures the exact resolved versions for reproducible installs.
- `__init__.py` makes the package boundaries explicit and allows Python to import the application.
- Ruff can provide both formatting and linting, so I do not need to add a second formatter without
  a specific reason.
- A `.gitignore` protects the repository from local environments, caches, secrets, and generated
  artifacts.
- Package boundaries make the future request flow easier to follow before implementation begins.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Python dependency workflow | uv; pip; Poetry | uv | It gives me a fast environment workflow, standard project metadata, and a reproducible lockfile. | Contributors need uv installed. |
| Python version | System Python 3.14; installed Python 3.12 | Python 3.12 | I wanted an explicit project interpreter rather than accidentally inheriting the newest system interpreter. | I must intentionally upgrade the project version later. |
| Formatting and linting | Ruff; Black plus another linter | Ruff | One tool covers the current formatting and linting needs without duplicated configuration. | I am adopting Ruff's formatting behavior. |
| Backend documentation | README in every package; one guide; three focused guides | Guides in `backend/`, `backend/app/`, and `backend/tests/` | Three guides explain the connections without creating a document in every small package. | The guides must be updated as the architecture evolves. |

#### Problems I Encountered

- Codex initially could not access uv's local cache because of its filesystem sandbox.
- My zsh `python` alias caused `which python` to show the alias instead of the virtual-environment
  executable.
- Pytest returned a nonzero exit code even though collection contained no errors.

#### How I Diagnosed Them

- I read the uv error and confirmed that it referred to cache access rather than project metadata.
- I inspected `sys.executable` and `sys.prefix` from inside Python instead of relying on the shell
  alias.
- I checked pytest's output and exit-code meaning to distinguish an empty suite from a collection
  failure.

#### How I Solved Them

- I approved the narrowly scoped uv cache access and reran the commands.
- I verified that Python resolved to `backend/.venv/bin/python` and used Python 3.12.13.
- I accepted pytest exit code `5` for this phase and did not add a meaningless placeholder test.

#### Tests I Added

I did not add behavior tests because the application has no behavior yet. I verified that pytest
can discover the test structure without import or collection errors.

#### Commands I Used

```bash
mkdir -p backend/app/{api/routes,core,db,models,repositories,schemas,services}
mkdir -p backend/tests/{api,db,service,unit}
uv venv backend/.venv --python 3.12
uv init --bare --name simulated-banking-backend --python 3.12 backend
uv add --project backend fastapi uvicorn sqlalchemy "psycopg[binary]" alembic pydantic-settings argon2-cffi
uv add --project backend --dev pytest httpx ruff
cd backend
uv run python -c "import app"
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest --collect-only -q
cd ..
```

#### Files I Changed

- `.gitignore`
- `backend/pyproject.toml`
- `backend/uv.lock`
- `backend/README.md`
- `backend/app/README.md`
- `backend/tests/README.md`
- Empty package files under `backend/app/` and `backend/tests/`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Real `.env` files and local virtual environments are ignored by Git.
- `.env.example` remains eligible for version control when it is added in Phase 3.
- Dependency versions are reproducible through the committed lockfile.
- Runtime and development dependencies are kept in separate groups.
- No secrets or application credentials were added.

#### What I Would Do Differently

I would initialize Git before the Phase 0 documentation commit requirement appears in the plan.
The current plan placed Git initialization in Phase 1 even though Phase 0 also expected a commit.
Initializing it during Phase 0 resolved the ordering conflict.

#### Questions I Still Have

- I still need to confirm the existing D5 decision about synchronous versus asynchronous
  SQLAlchemy before the database work begins.

#### Next Step

Review this entry, update the Phase 1 completion record, and commit the finished foundation. After
that commit is verified, begin Phase 2 with only the FastAPI application and health endpoint.

---

## Long-Term Logs

### Architecture Decision Log

This log started with the open decisions from `IMPLEMENTATION_PLAN.md`. I fill in the reason and
consequences when I resolve each one, then add new rows when other important decisions come up.

| ID | Date | Decision | Context | Alternatives | Reason | Consequences |
|---|---|---|---|---|---|---|
| D1 | 2026-06-29 | `SESSION_IDLE_MINUTES=30`; `SESSION_ABSOLUTE_HOURS=12` | SPEC §9.2/§18/§24.7; feeds config + session dependency | 30/12 (rec); 15/8; 60/24 | I chose a 30-minute idle timeout to limit abandoned-session risk while keeping the 12-hour absolute expiry practical for development and reviewers. | This defines session expiry and cookie lifetime and feeds configuration and expiry-related tests. |
| D2 | 2026-06-29 | Include a minimal `AuditEvent` table and audit writes in the MVP | SPEC §10/§16/§24.5; affects first migration + service rows | Include minimal (rec); defer to hardening; table-now-rows-later | I chose to include audit events now because they satisfy the MVP audit requirements and save me from retrofitting the database and services later. | I will add `AuditEvent` to the first migration and emit required audit rows from authentication, money-operation, authorization, and administrative services. |
| D3 | 2026-06-29 | Use nginx as the production reverse proxy | SPEC §17/§24.3; deploy only | Caddy auto-TLS (rec); nginx | I chose nginx because it is widely used in production, so learning its configuration gives me experience I can transfer to more projects even though TLS setup will be more manual than with Caddy. | In Phase 37, I will configure nginx to terminate TLS, serve the React build, and proxy `/api/*` to FastAPI from the same origin. |
| D4 | 2026-06-29 | Use lightweight query helpers with services as the primary business-logic layer | SPEC §24.6; service file layout | Lightweight helpers (rec); full per-entity repo | I chose lightweight helpers because a full repository per entity would add unnecessary abstraction and make the banking rules harder to follow while I am learning the system. | I will keep business rules and transaction boundaries in services and add small query helpers only when a query is reused or complex enough to justify one. |
| D5 |  | Sync vs async SQLAlchemy | SPEC §17; row locking for money path | Sync (rec, simpler `FOR UPDATE`); async | _(pending)_ | _(pending)_ |
| D6 | 2026-06-29 | Use uv for Python environment and dependency management | IMPLEMENTATION_PLAN Phase 1; backend tooling and dependency workflow | uv; pip + `requirements.txt`; Poetry | I chose uv because it is already installed, uses the standard `pyproject.toml` format, and provides fast installs with a reproducible lockfile without the extra workflow complexity of Poetry. | I will manage the backend environment and dependencies with uv, commit `pyproject.toml` and `uv.lock`, and run Python tools through `uv run`. |

### Debugging Log

| Date | Problem | Root Cause | Fix | Prevention |
|---|---|---|---|---|
|  |  |  |  |  |

### Concepts Learned

I fill these in using my own words once each concept clicks and note where I used it.

| Concept | My Explanation | Where It Appears in the Project |
|---|---|---|
| Dependency injection |  | FastAPI `get_db`, current-user, role/ownership deps (Ph4, Ph11, Ph14, Ph15) |
| Database sessions |  | `SessionLocal` / `get_db` (Ph4) |
| ORM models & relationships |  | `app/models/` (Ph5) |
| Database migrations |  | Alembic (Ph6) |
| Idempotent seeding |  | `app/seed.py` (Ph7) |
| Password hashing (Argon2id) |  | `core/security.py` (Ph8) |
| Opaque server-side sessions |  | session token util + dependency (Ph9–Ph11) |
| Session token hashing (store hash, not raw) |  | Ph9 |
| Secure cookie attributes |  | login cookie issuance (Ph10) |
| Server-side revocation |  | logout + deactivation (Ph12, Ph26) |
| CSRF (double-submit) |  | CSRF dependency (Ph13) |
| Role authorization |  | `require_role` (Ph14) |
| Resource ownership / IDOR prevention |  | ownership dependency (Ph15) |
| Error envelope / typed domain errors |  | `app/errors.py` (Ph17) |
| Decimal money (no floats) |  | money path (Ph18–Ph22) |
| Atomic transactions |  | deposit/withdrawal/transfer (Ph20–Ph22) |
| Row locking (`SELECT ... FOR UPDATE`) |  | money services (Ph20–Ph22) |
| Deadlock avoidance (consistent lock order) |  | transfer (Ph22) |
| Reconciliation (balance == signed sum) |  | Ph7, Ph23 |
| Concurrency testing |  | Ph23 |
| Service-layer design / thin routes |  | `app/services/` throughout |
| Pagination (limit/offset) |  | transaction history (Ph19, Ph31) |
| Auth state from `/auth/me` (no stored token) |  | frontend auth context (Ph29) |
| Integration vs component vs E2E testing |  | Ph16/Ph23/Ph34/Ph35 |
| Reverse proxying / single origin |  | deploy (Ph37) |
| Log redaction |  | Ph27 |

---

## Useful Commands

I keep the commands I actually use here. Anything marked `# TBD` stays a placeholder until I
introduce that tool and choose the exact command or flags.

### Git

```bash
git status
git add -A && git commit -m "type(scope): describe my change"
git log --oneline --graph --decorate
```

### Python and Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt        # or the package manager I choose
python -c "import app"                          # smoke-import the package
# TBD: lint/format commands (ruff/black) once configured in Ph1
```

### FastAPI

```bash
# TBD: exact module path once app exists (Ph2)
uvicorn app.main:app --reload --app-dir backend
# Swagger UI: http://localhost:8000/docs
curl -i http://localhost:8000/api/health
```

### pytest

```bash
# TBD: run from backend/ once tests exist (Ph2+)
pytest -q
pytest backend/tests/api/test_auth.py -q        # targeted module (Ph16)
pytest -k reconciliation -q                      # targeted by keyword (Ph23)
```

### PostgreSQL

```bash
# TBD: connection string from .env (Ph3+)
psql "$DATABASE_URL" -c "\dt"                    # list tables (after Ph6)
psql "$DATABASE_URL" -c "\d accounts"            # inspect constraints/indexes
psql "$DATABASE_URL" -c "select id, balance from accounts;"
```

### Alembic

```bash
# TBD: from backend/ once configured (Ph6)
alembic revision --autogenerate -m "describe the migration"
alembic upgrade head
alembic downgrade -1
alembic history
```

### React and Frontend

```bash
# TBD: once the SPA is scaffolded (Ph28)
npm install
npm run dev
npm run build
```

### Frontend Tests

```bash
# TBD: Vitest/Jest once chosen (Ph28/Ph34)
npm run test
```

### Docker

```bash
# TBD: once Dockerfile/compose exist (Ph36)
docker build -t banking-backend backend/
docker compose up --build
```

### Deployment

```bash
# TBD: reverse proxy + VPS steps (Ph37)
# nginx config test / systemctl reload commands ...
# alembic upgrade head   (production migration step)
# python -m app.seed     (production seed)
```

---

## Questions for Review

I put questions here when I want to bring them to an AI mentor, a CS50x forum, or future me. I
add the resolution and date when I have an answer.

| Date | Question | Context / Phase | Resolution |
|---|---|---|---|
|  |  |  |  |

---

## Project Retrospective

I will answer these at the SUBMISSION checkpoint after Phase 38.

- **What architecture decisions worked well?**
- **What caused the most rework?**
- **What security mistakes did I avoid or correct?**
- **Which tests provided the most value?**
- **How did the project change from the original specification?**
- **What would need to change before real users could use it?** (See SPEC §9.6, §15, §23 hardening.)
- **What would I build differently a second time?**
