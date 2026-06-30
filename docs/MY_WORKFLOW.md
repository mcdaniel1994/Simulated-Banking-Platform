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

### Entry — 2026-06-29 — Phase 2: FastAPI App and Health Endpoint

#### What I Worked On

I created the central FastAPI application, added a dedicated health router, mounted it under the
shared `/api` prefix, and added an integration test for `GET /api/health`. I then ran the app with
Uvicorn and verified the health response, Swagger UI, and OpenAPI contract over real HTTP requests.

#### What I Expected to Happen

I expected the application to boot locally, expose `GET /api/health`, return a small liveness
payload, and publish the route in the generated API documentation.

#### What Actually Happened

The application started on `127.0.0.1:8000`. The health endpoint returned HTTP 200 with
`{"status":"ok"}`, `/docs` returned HTTP 200, and `/openapi.json` contained `/api/health`. The
integration test passed, and Ruff reported that all application and test files were formatted and
free of configured lint violations.

The installed FastAPI version emitted a deprecation warning for its legacy TestClient/httpx
integration. The test still passed, so I recorded the warning as technical debt instead of changing
the planned dependency stack during this phase.

#### Concepts I Learned

- The FastAPI `app` object is an ASGI application that Uvicorn can serve.
- `APIRouter` keeps endpoint definitions separate from application startup.
- Mounting a router with the `/api` prefix gives the backend one consistent public namespace.
- A liveness endpoint proves the process can respond; it should not be confused with a readiness
  check that verifies database or external-service access.
- FastAPI generates Swagger UI and an OpenAPI contract from the registered routes.
- An integration test should exercise the HTTP contract rather than call the route function
  directly.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Health route organization | Define it in `main.py`; use a dedicated router | Dedicated router | It establishes the thin-route organization that later endpoints will follow. | It adds one small module for a simple endpoint. |
| Health-check depth | Process-only liveness; include database reachability | Process-only liveness | Phase 2 has no database, and liveness should remain independent of downstream services. | A separate readiness endpoint is still needed later. |
| Test style | Call the function directly; make an HTTP request through the app | HTTP integration test | It verifies routing, prefixing, status code, and response serialization together. | It depends on FastAPI's testing integration. |

#### Problems I Encountered

- New Python files initially lacked a final newline, which caused formatting failures.
- An editor-added `type: ignore` comment hid an import warning and caused Ruff to reject the import
  block.
- The configured import rule required one blank line before a module variable rather than two.
- FastAPI's internal included-router object did not expose `.path` through the older inspection
  expression.
- The passing test emitted a TestClient/httpx deprecation warning.

#### How I Diagnosed Them

- I compared the file output and Ruff's proposed non-writing diffs.
- I verified the actual interpreter and successful FastAPI import instead of suppressing the
  editor warning.
- I inspected the generated OpenAPI paths rather than relying on FastAPI's internal route
  container.
- I read pytest's warning output and separated it from the successful test result.

#### How I Solved Them

- I used Ruff to apply the mechanical whitespace and import-order corrections.
- I removed the unnecessary type suppression and kept the real import visible to tooling.
- I verified `/api/health` through OpenAPI and then through an actual Uvicorn HTTP request.
- I recorded the deprecation warning for later dependency review instead of expanding Phase 2.

#### Tests I Added

- `tests/api/test_health.py`
  - Confirms `GET /api/health` returns HTTP 200.
  - Confirms the response body is exactly `{"status": "ok"}`.

Result: `1 passed, 1 warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest -q
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
curl -i http://127.0.0.1:8000/api/health
curl -I http://127.0.0.1:8000/docs
cd ..
```

#### Files I Changed

- `AGENTS.md`
- `backend/app/main.py`
- `backend/app/api/routes/health.py`
- `backend/tests/api/test_health.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- The health endpoint is intentionally public and returns no configuration, dependency, or secret
  information.
- The endpoint checks only process liveness, so a database outage will not incorrectly stop the
  process from reporting that it is alive.
- All application endpoints are grouped under `/api`, supporting the planned single-origin
  deployment.

#### What I Would Do Differently

I would configure my editor to use `backend/.venv/bin/python` before editing Python files so it
does not suggest unnecessary import suppressions.

#### Questions I Still Have

- When should the FastAPI TestClient/httpx deprecation be migrated to the recommended replacement?
- What database behavior should the future `/api/ready` endpoint verify?

#### Next Step

Review and commit Phase 2. Stop before Phase 3 so configuration and environment variables remain a
separate, focused change.

### Entry — 2026-06-29 — Phase 3: Configuration and Environment Variables

#### What I Worked On

I created a typed Pydantic settings model for every environment variable required by the
specification, added a cached accessor, wrote a safe root `.env.example`, and documented the local
setup in the backend guide. I added unit tests for dotenv loading, D1 session defaults, required
values, secret redaction, blank cookie-domain normalization, and settings caching.

#### What I Expected to Happen

I expected configuration to load consistently from process environment variables or the root
`.env`, reject missing database and session values, and expose typed values without leaking
credentials through normal debug output.

#### What Actually Happened

The safe template loaded as `development` with the 30-minute idle and 12-hour absolute session
defaults. Both the database URL and session secret displayed as redacted values, and a blank local
cookie domain normalized to `None`. The full suite finished with six passing tests and the existing
FastAPI TestClient warning.

#### Concepts I Learned

- Environment variables separate deploy-specific values and secrets from source code.
- `BaseSettings` converts string environment values into typed Python values.
- Complex values such as CORS-origin lists use JSON syntax in environment files.
- `SecretStr` reduces accidental credential exposure in logs and object representations.
- `lru_cache` lets the process construct settings once and reuse one consistent instance.
- Required configuration can fail clearly without embedding unsafe fallback credentials.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Local env-file location | Root; backend directory | Root `.env` | It matches the planned repository layout and keeps one environment entry point for the future full stack. | The configuration resolves the repository root for local loading. |
| Sensitive field representation | Plain strings; `SecretStr` | `SecretStr` for database URL and session secret | Both values can contain credentials that should not appear in normal output. | Consumers must explicitly request the underlying value when connecting or hashing. |
| CORS representation | Comma-separated text; JSON list | JSON list | Pydantic can parse it directly into `list[str]` without custom splitting. | Environment-file authors must use valid JSON syntax. |
| Empty cookie domain | Preserve empty string; normalize to `None` | Normalize to `None` | Local cookies should omit the Domain attribute rather than receive an empty domain. | A small validator is required. |

#### Problems I Encountered

- Ruff required its configured import ordering in the new test module.
- The first security pass protected the session secret but left the credential-bearing database
  URL as a plain string.

#### How I Diagnosed Them

- I used Ruff's safe automatic fix for the import order.
- I manually loaded `.env.example` and reviewed which values appeared in settings output.

#### How I Solved Them

- I applied only Ruff's mechanical import correction.
- I changed the database URL to `SecretStr`, expanded the redaction test, and confirmed both
  sensitive values display as `**********`.
- I added a validator and test for the blank local cookie domain.

#### Tests I Added

- Loads and parses every supported value from an isolated dotenv file.
- Uses the D1 session defaults when optional values are absent.
- Rejects missing `DATABASE_URL` and `SESSION_SECRET`.
- Redacts both the database URL and session secret.
- Reuses one cached settings instance.

Result: `6 passed, 1 existing warning` across the full backend suite.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest -q
uv run python -c "from app.core.config import Settings; print(Settings(_env_file='../.env.example'))"
cd ..
git check-ignore -v .env
git check-ignore -v .env.example
```

#### Files I Changed

- `.env.example`
- `backend/app/core/config.py`
- `backend/tests/unit/test_config.py`
- `backend/README.md`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Real `.env` files remain ignored while `.env.example` is trackable.
- No real database credential or session secret was created or committed.
- Required sensitive settings have no source-code defaults.
- Sensitive settings are redacted during normal string and representation output.
- Positive-number validation prevents zero or negative session lifetimes.
- The cached accessor avoids inconsistent configuration objects during one process lifetime.

#### What I Would Do Differently

I would classify every credential-bearing configuration field as sensitive during the initial model
design rather than catching the database URL during the security review.

#### Questions I Still Have

- How should production startup validation distinguish safe real secrets from example placeholders?
- Should a later configuration layer use separate development, test, and production subclasses, or
  will one typed model remain sufficient?

#### Next Step

Commit Phase 3, then resolve D5 before Phase 4 so the SQLAlchemy engine and session design use one
deliberate sync or async approach.

### Entry — 2026-06-29 — Phase 4: SQLAlchemy Engine, Session, Base, and DB Dependency

#### What I Worked On

I added a PostgreSQL 16 service for local development with Docker Compose while keeping FastAPI in
the local Python environment. I created separate development and test databases, a dedicated
least-privilege application role, synchronous SQLAlchemy engine/session infrastructure, a shared
declarative base, and a request-scoped FastAPI database dependency.

#### What I Expected to Happen

I expected Docker Compose to create an isolated PostgreSQL server on host port 5433, initialize
both databases in a dedicated volume, and let the application connect through a bounded SQLAlchemy
pool. I expected database tests to fail rather than risk using the development database when test
configuration was missing or unsafe.

#### What Actually Happened

The PostgreSQL service reached healthy status, both databases were initialized and owned by
`banking_user`, and that role could create schema objects without having superuser or role/database
creation privileges. The runtime engine connected to `simulated_banking_dev`; the database suite
connected only to `simulated_banking_test` and proved session cleanup and transaction rollback.

The full suite passed with 12 tests and the existing FastAPI TestClient warning. Ruff formatting
and linting also passed.

#### Concepts I Learned

- A SQLAlchemy engine owns the connection pool, while each `Session` represents one unit of work.
- A FastAPI yield dependency can guarantee rollback on request errors and close the session in a
  `finally` block.
- Test database configuration should be test-only and must not silently inherit the development
  database.
- Docker entrypoint initialization runs only when the PostgreSQL data directory is empty.
- The official PostgreSQL image treats `POSTGRES_USER` as a bootstrap superuser, so an application
  role must be created separately to achieve least privilege.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Local PostgreSQL | Homebrew service; Docker Compose | PostgreSQL 16 in Docker Compose | It isolates this project from other local PostgreSQL installations and gives development and test databases a reproducible setup. | Docker Desktop must be running. |
| Runtime placement | Containerize API and DB; containerize only DB | PostgreSQL only in Docker | Phase 4 needs database infrastructure, while backend containerization belongs to Phase 36. | The local backend connects through mapped port 5433. |
| Database identities | Application role as image bootstrap user; separate admin and application roles | Separate container bootstrap administrator and non-superuser `banking_user` | The official image makes `POSTGRES_USER` a superuser, which violates the application-role requirement. | Local `.env` contains two independent generated passwords. |
| Test configuration | Add `TEST_DATABASE_URL` to runtime settings; test-only settings | Test-only `DatabaseTestSettings` | Production code should not require or know about a test database. | Database tests have a dedicated configuration fixture. |
| Session failure handling | Close only; rollback then close | Rollback on error, always close | Failed request work must not return an active transaction to the pool. | Services still need to own intentional commit boundaries. |

#### Problems I Encountered

- The requested `POSTGRES_USER=banking_user` setup made `banking_user` the PostgreSQL bootstrap
  superuser.
- PostgreSQL does not allow its bootstrap identity to remove its own superuser attribute.
- Ruff identified two new files that needed mechanical formatting.

#### How I Diagnosed Them

- I queried `pg_roles` and found `banking_user` had superuser, database-creation, role-creation, and
  replication privileges.
- I attempted to narrow the role and read PostgreSQL's explicit bootstrap-user error.
- I used Ruff's non-writing format check before applying its formatter.

#### How I Solved Them

- I separated the container bootstrap administrator from the application identity.
- The initialization SQL reads the application credentials from container environment variables,
  creates non-superuser `banking_user`, and transfers ownership of both databases to it.
- I reset only the newly created banking Compose volume so the corrected initialization could run
  against an empty data directory. Agent OS resources were not modified.
- I applied Ruff's formatter to the two reported files.

#### Tests I Added

- Declarative metadata exists without registering Phase 5 models early.
- Missing `TEST_DATABASE_URL` fails.
- A test URL equal to the development URL fails.
- Development and test URLs target the expected separate databases with Psycopg 3.
- `get_db` executes `SELECT 1` against `simulated_banking_test` and releases the connection.
- An exception sent through `get_db` rolls back transactional PostgreSQL DDL and closes the session.

Result: `12 passed, 1 existing warning`.

#### Commands I Used

```bash
docker compose config -q
docker compose up -d postgres
docker compose ps
docker compose logs postgres
docker compose exec postgres psql ...
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest -q
```

#### Files I Changed

- `compose.yaml`
- `docker/postgres/init/01-create-test-database.sql`
- `.env.example`
- Local ignored `.env`
- `backend/app/db/base.py`
- `backend/app/db/session.py`
- `backend/tests/db/conftest.py`
- `backend/tests/db/test_session.py`
- `backend/README.md`
- `backend/tests/README.md`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Generated local credentials are stored only in the ignored `.env` with owner-only permissions.
- Runtime and tests authenticate as a non-superuser that owns only the two banking databases.
- Development and test URLs must differ; missing test configuration is a hard failure.
- The engine uses a bounded pool with pre-ping, and the request dependency rolls back errors and
  always closes sessions.
- The Compose project has its own volume and default network. Agent OS resources were untouched.

#### What I Would Do Differently

I would separate the image bootstrap identity from the application identity in the first Compose
draft because the official image intentionally grants `POSTGRES_USER` superuser privileges.

#### Questions I Still Have

- Should future production pool sizing differ from the local pool after the Supabase pooler limits
  are known?

#### Next Step

Review and commit Phase 4. Stop before Phase 5 so ORM models and relationships remain a separate
phase. Alembic initialization remains deferred to Phase 6.

### Entry — 2026-06-29 — Phase 5: Database Models and Relationships

#### What I Worked On

I defined the six MVP persistence models from SPEC §10: users, server-side sessions, accounts,
append-only transactions, transfers, and audit events. I connected them through explicit
relationships and registered all six tables with the shared SQLAlchemy metadata.

#### What I Expected to Happen

I expected SQLAlchemy to configure all relationships without ambiguity, expose the exact required
columns and indexes through metadata, preserve decimal money precision, and stop short of creating
physical tables because migrations belong to Phase 6.

#### What Actually Happened

All six tables registered successfully, mapper configuration completed without errors, and model
instances could be connected through user, account, session, transfer, transaction, and audit
relationships. Metadata inspection confirmed named enums, `NUMERIC(14,2)`, timezone-aware
timestamps, uniqueness, foreign keys, indexes, and the account balance check.

The complete suite passed with 16 tests and the existing FastAPI TestClient warning. Ruff
formatting and linting passed.

#### Concepts I Learned

- SQLAlchemy's typed `Mapped` annotations define both Python-facing attributes and ORM mapping
  intent.
- Relationships describe navigation between objects; foreign keys enforce the stored references.
- Named database enums make migrations and schema inspection deterministic.
- Declarative metadata can be tested before a migration creates any database tables.
- ORM delete cascades are dangerous for append-only financial history and audit records.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Primary-key type | Auto-incrementing integer; UUID | Integer | The specification leaves ID type open, and integers keep this learning-focused schema and foreign keys straightforward. | Public IDs are enumerable, so authorization must never rely on obscurity. |
| Enum persistence | Plain strings; named SQLAlchemy/PostgreSQL enums | Named enums | The domain values are fixed and named enums make invalid states harder to store. | Enum value changes require deliberate migrations. |
| Relationship deletion | ORM cascades; no implicit cascades | No implicit delete cascades | Transaction and audit history must not disappear because a parent object is removed. | Future deletion policies must be explicit. |
| Audit metadata attribute | Python attribute named `metadata`; mapped alias | `event_metadata` mapped to SQL column `metadata` | `metadata` is reserved by SQLAlchemy's declarative base. | Python and SQL use different names for this one field. |
| Model registration | Import models automatically from `Base`; explicit loader and model package | `load_models()` plus `app.models` exports | This avoids circular imports while giving Alembic and metadata checks one deliberate registration point. | Metadata consumers must import the model registry before inspection. |

#### Problems I Encountered

- The Phase 4 database test still asserted that declarative metadata contained no tables.
- Ruff requested import ordering and formatting for the new modules.
- Multiple account-to-transfer relationships needed explicit foreign-key selection to avoid
  ambiguity.

#### How I Diagnosed Them

- The full suite showed the obsolete metadata assertion after all six models registered.
- Ruff identified the exact files and import block needing mechanical correction.
- `configure_mappers()` exercised every relationship and confirmed the source/destination mappings.

#### How I Solved Them

- I removed the obsolete empty-metadata assertion and replaced it with stronger Phase 5 metadata
  coverage.
- I applied Ruff's import fix and formatter.
- I specified source and destination transfer foreign keys on both sides of the relationships.

#### Tests I Added

- Metadata contains exactly six expected tables and all specified columns.
- Money columns use `NUMERIC(14,2)` and all timestamps are timezone-aware.
- Enum names and values are stable.
- Required checks, indexes, unique fields, and foreign-key targets are registered.
- All models construct with exact `Decimal` values and correctly connected relationships.

Result: `16 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest -q
uv run python -c "from sqlalchemy.orm import configure_mappers; ..."
```

#### Files I Changed

- `backend/app/db/base.py`
- `backend/app/models/__init__.py`
- `backend/app/models/user.py`
- `backend/app/models/session.py`
- `backend/app/models/account.py`
- `backend/app/models/transaction.py`
- `backend/app/models/transfer.py`
- `backend/app/models/audit_event.py`
- `backend/tests/db/test_session.py`
- `backend/tests/unit/test_models.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- The session model stores only a token hash, never a raw session token.
- Monetary values use `Decimal`/`NUMERIC(14,2)`, never floating point.
- The account balance check is represented in metadata as a database integrity backstop.
- Audit rows can retain history when an actor reference is removed.
- Relationships do not silently cascade deletion into transaction or audit history.

#### What I Would Do Differently

I would remove phase-specific assertions such as "metadata must be empty" when closing the phase
that introduced them, because later phases intentionally invalidate that temporary condition.

#### Questions I Still Have

- Should account numbers remain short numeric display identifiers or gain a separate masked display
  representation later? That belongs to the account API/UI phases, not this schema phase.

#### Next Step

Review and commit Phase 5. Stop before Phase 6 so Alembic initialization, migration review, and live
constraint enforcement remain one separate database-schema phase.

### Entry — 2026-06-29 — Phase 6: Alembic Configuration and First Migration

#### What I Worked On

I configured Alembic to load the typed runtime database URL, import all six models, and compare
their shared metadata to PostgreSQL. I autogenerated revision `0001`, reviewed and annotated it,
applied it to development, and added an isolated migration test against the test database.

#### What I Expected to Happen

I expected autogenerate to detect all six model tables, required constraints, foreign keys, and
indexes. I expected upgrade and downgrade to be transactional and repeatable, with no model/schema
drift after the final upgrade.

#### What Actually Happened

Autogenerate detected all six tables and their indexes. The reviewed migration applied to both
development and test databases, rejected a negative account balance, downgraded cleanly to an empty
application schema, and upgraded again to revision `0001`.

PostgreSQL catalog inspection confirmed the expected tables, 17 constraints, and 13 indexes
including primary/unique indexes. `alembic check` reported no pending schema operations. The full
suite passed with 17 tests and only the pre-existing FastAPI TestClient warning.

#### Concepts I Learned

- Model metadata describes desired schema; a migration is the reviewed, version-controlled set of
  operations that moves a real database toward it.
- Autogenerate is a draft generator, not a substitute for reviewing constraints and downgrade
  behavior.
- PostgreSQL enum types are independent schema objects that may require explicit downgrade cleanup.
- Alembic can receive a test-only connection URL programmatically without putting credentials in
  `alembic.ini`.
- `alembic check` detects model changes that have not yet been represented by a migration.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Migration URL source | Store URL in `alembic.ini`; resolve typed settings | Resolve runtime `DATABASE_URL` in `env.py` | Credentials stay in the ignored environment and follow the existing settings boundary. | Alembic commands require valid application settings. |
| Test migration target | Override process environment; explicit Alembic attribute | Explicit test-only configuration attribute | The migration test can target `TEST_DATABASE_URL` without changing production settings or risking fallback. | Programmatic tests need a small config helper. |
| PostgreSQL enum downgrade | Rely on table drops; explicitly drop enum types | Explicit enum cleanup with `checkfirst` | It guarantees downgrade-to-base can be followed by a clean re-upgrade. | The migration includes PostgreSQL-specific cleanup. |
| Migration validation | Apply only; round trip plus drift check | Upgrade, downgrade, re-upgrade, and `alembic check` | This proves both directions and confirms models match the final schema. | Verification takes additional database operations. |

#### Problems I Encountered

- The generated migration did not explicitly remove PostgreSQL enum types during downgrade.
- Alembic warned that `prepend_sys_path` was using legacy path-separator behavior.
- Generated Python required Ruff's configured formatting and import order.

#### How I Diagnosed Them

- I reviewed the generated upgrade and downgrade operations before applying the revision.
- The targeted migration test exercised downgrade followed by re-upgrade against PostgreSQL.
- I read Alembic's deprecation message and used its recommended `path_separator = os` setting.
- Ruff identified the exact generated files needing mechanical cleanup.

#### How I Solved Them

- I added explicit, `checkfirst` enum drops after dependent tables are removed.
- I added modern path-separator configuration to `alembic.ini`.
- I formatted the reviewed revision and added comments explaining dependency order and integrity
  responsibilities.
- I strengthened the migration test to inspect live PostgreSQL uniqueness and index definitions.

#### Tests I Added

- Apply revision `0001` to `simulated_banking_test`.
- Verify all six application tables exist.
- Verify the balance check, unique constraints, and required query indexes exist in PostgreSQL.
- Prove a negative account balance raises an integrity error.
- Downgrade to base, confirm application tables are absent, and upgrade to head again.

Result: `17 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run alembic revision --autogenerate --rev-id 0001 -m "initial schema"
uv run alembic upgrade head
uv run alembic current
uv run alembic downgrade base
uv run alembic upgrade head
uv run alembic check
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest -q
```

#### Files I Changed

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/0001_initial_schema.py`
- `backend/tests/db/test_migrations.py`
- `backend/README.md`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- No database URL or password is stored in Alembic configuration or migration files.
- Migration tests require the isolated test URL and use an explicit override.
- Transactional DDL protects PostgreSQL from partially applied revisions.
- The database check constraint independently prevents negative balances.
- Enum cleanup makes destructive local downgrades repeatable without leaving hidden schema objects.

#### What I Would Do Differently

I would add Alembic's modern path-separator option to the initial configuration template before the
first run so the generated workflow begins warning-free.

#### Questions I Still Have

- Phase 7 seeding depends on Argon2id hashing scheduled for Phase 8; I need to choose whether to
  implement the hashing primitive first or keep seed password creation temporarily local and
  refactor immediately afterward, as the implementation plan permits.

#### Next Step

Review and commit Phase 6. Stop before Phase 7 so the seed/hashing dependency is resolved explicitly
before demo data is created.

### Entry — 2026-06-29 — Phase 8: Password Hashing with Argon2id

#### What I Worked On

I implemented the password-hashing primitive before Phase 7 because deterministic seed users need
real password hashes. The module hashes passwords, verifies credentials, and identifies hashes that
need upgraded parameters.

#### What I Expected to Happen

I expected equal passwords to receive different salts, correct passwords to verify, wrong or
malformed values to fail safely, and weaker historical hashes to be identified for rehashing.

#### What Actually Happened

Argon2id produced distinct salted hashes with the explicit specification floor: 19,456 KiB memory,
2 iterations, and parallelism 1. Correct verification succeeded, wrong and malformed inputs
returned false, and rehash detection distinguished weak parameters from current ones.

The complete suite passed with 22 tests and only the existing FastAPI TestClient warning. Ruff
formatting and linting passed.

#### Concepts I Learned

- Password hashing is deliberately expensive and one-way; it is not encryption.
- A random salt prevents identical passwords from creating identical stored hashes.
- Argon2id parameters must be explicit so a dependency default change does not silently change the
  application's security contract.
- Rehash-on-login lets stored credentials improve over time without knowing plaintext passwords.
- Malformed stored hashes should become generic authentication failures rather than leak parser
  details.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Phase order | Hash inline during seeding; implement Phase 8 first | Phase 8 first, then return to Phase 7 | The plan explicitly allows this sequence and it avoids duplicate temporary security code. | M3 starts before M2 is fully closed. |
| Argon2 parameters | Library defaults; explicit specification floor | 19 MiB, 2 iterations, parallelism 1 | Explicit values meet SPEC §9.1 and remain stable across dependency upgrades. | Future parameter increases require intentional rehashing. |
| Invalid stored hash | Raise parser error; return authentication failure | Return `False` | Login should not expose internal hash-format details. | Operational diagnosis must happen through safe server-side handling later. |

#### Problems I Encountered

- Phase 7 precedes Phase 8 in numbering even though seeded credentials require password hashing.
- Ruff requested its configured import grouping in the new test module.

#### How I Diagnosed Them

- The Phase 7 plan explicitly says to sequence Phase 8 first if needed or duplicate hashing inline.
- Ruff identified the exact import block and supplied a safe mechanical fix.

#### How I Solved Them

- I chose the plan-approved Phase 8-first path and recorded the intentional ordering.
- I applied Ruff's import correction without changing behavior.

#### Tests I Added

- Argon2id type and minimum memory/time/parallelism parameters.
- Distinct salted hashes for the same password.
- Correct-password success and wrong-password failure.
- Malformed-hash failure without an exception escaping.
- Rehash detection for weak versus current parameters.

Result: `22 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest tests/unit/test_security.py -q
uv run pytest -q
```

#### Files I Changed

- `backend/app/core/security.py`
- `backend/tests/unit/test_security.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Plaintext passwords and password hashes are never logged.
- The implementation delegates comparison and hash parsing to `argon2-cffi`.
- Each hash receives a fresh random salt.
- Invalid stored hashes fail closed.
- Rehash detection supports future parameter upgrades after successful authentication.

#### What I Would Do Differently

I would place the hashing primitive immediately before seeding in the original phase numbering so
the dependency direction is visible without a documented reorder.

#### Questions I Still Have

- Demo credential values still need to be selected and documented during Phase 7.

#### Next Step

Review and commit Phase 8, then return to Phase 7 and use this shared hashing primitive for every
seeded demo credential. Do not begin Phase 9.

### Entry — 2026-06-29 — Phase 7: Deterministic, Idempotent Seed

#### What I Worked On

I created a command-line seed that builds one synthetic administrator, two synthetic customers,
four accounts, twelve historical transaction rows, and two completed internal transfers. It uses
the shared Argon2id primitive completed in Phase 8.

#### What I Expected to Happen

I expected a clean database to receive a realistic but compact demo graph, every balance to
reconcile with its signed transaction history, and a second run to preserve the same row counts
and password hashes without duplicating data.

#### What Actually Happened

The development seed ran twice and remained at 3 users, 4 accounts, 2 transfers, and 12
transactions. All four account balances reconciled exactly, and each transfer had a matching
`TRANSFER_OUT` and `TRANSFER_IN` row sharing its transfer ID.

The full suite passed with 25 tests and the existing FastAPI TestClient warning. Ruff passed, and
Alembic reported no model/schema drift.

#### Concepts I Learned

- Idempotent seed logic uses stable natural keys and does not assume generated integer IDs.
- Opening balances must be represented as transactions or reconciliation is broken from the start.
- Randomly salted password hashes can remain idempotent by reusing a valid existing hash.
- Append-only history should not be deleted merely to make reseeding convenient.
- One database transaction prevents a failed seed from leaving a partial demo graph.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Demo identities | Real-looking public domains; reserved synthetic domain | `.test` email addresses | Reserved addresses cannot accidentally identify or contact real people. | They look intentionally synthetic. |
| Demo credentials | Generated secrets; fixed public credentials | Fixed reviewer credentials | The future login page must show credentials and reseeding must restore known access. | They are never suitable for production. |
| Seed history | Opening deposits only; varied history with transfers | Opening deposits, deposits/withdrawals, and one transfer per customer | Dashboards and transaction pages will have meaningful data covering every transaction type. | The seed script is longer than a minimal fixture. |
| Rerun behavior | Delete/rebuild history; preserve existing account pairs | Preserve existing append-only activity | Reseeding cannot silently erase reviewer transactions. | Manual partial deletion is rejected instead of guessed at. |
| Transaction boundary | Commit per user; one atomic commit | One transaction | Failure cannot leave only part of the demo dataset. | A single error rolls back all seed work. |

#### Problems I Encountered

- Argon2 hashes use random salts, so blindly updating demo passwords would change rows on every run.
- Rebuilding seed history would conflict with the append-only transaction rule.
- Ruff requested mechanical formatting and import ordering in the new database test.

#### How I Diagnosed Them

- I compared password hashes before and after the second seed run.
- I traced reconciliation requirements back to the transaction log being the source of truth.
- Ruff identified the exact test file requiring mechanical changes.

#### How I Solved Them

- Existing hashes are retained when the public credential verifies and parameters remain current.
- Account history is created only with a new complete account pair; existing pairs keep later
  activity.
- Partial account pairs fail and roll back instead of risking an inconsistent reconstruction.
- I applied Ruff's import and formatting correction.

#### Tests I Added

- Seed twice and assert stable row counts and unchanged valid hashes.
- Verify all public demo credentials against stored Argon2id hashes.
- Confirm each customer owns checking and savings accounts.
- Reconcile every account's signed transactions with its stored balance.
- Confirm every transfer has two correctly typed rows sharing its ID.
- Confirm printed output contains public credentials but no Argon2 hash.

Result: `25 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run python -m app.seed
uv run python -m app.seed
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest -q
uv run alembic check
```

#### Files I Changed

- `backend/app/seed.py`
- `backend/tests/db/test_seed.py`
- `backend/README.md`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Demo credentials are intentionally public and isolated from generated local environment secrets.
- Only password hashes are persisted; seed output never prints hashes.
- Synthetic identities use the reserved `.test` domain.
- Reconciliation holds for every seeded account.
- Seed failures roll back atomically, and reruns do not delete transaction history.

#### What I Would Do Differently

I would order password hashing immediately before seed data in the original plan so the
implementation sequence matches the dependency graph without crossing milestone numbers.

#### Questions I Still Have

- Phase 9 must choose whether session-token hashing uses the existing session secret as a pepper or
  plain SHA-256 for indexed lookup.

#### Next Step

Review and commit Phase 7. M2 is then complete; continue M3 with Phase 9 only after this seed batch
is committed. Do not begin session-token work in this phase.

### Entry — 2026-06-29 — Phase 9: Session-Token Utility

#### What I Worked On

I added the security primitives needed to issue opaque server-side sessions: high-entropy token
generation, keyed deterministic hashing for indexed database lookup, and absolute-expiry
calculation from the configured D1 lifetime.

#### What I Expected to Happen

I expected tokens to be URL-safe and unique, hashes to be deterministic only under the same
session secret, and expiration to resolve exactly from a timezone-aware creation timestamp.

#### What Actually Happened

Each generated token encoded 32 random bytes into 43 URL-safe characters. HMAC-SHA256 produced a
64-character lookup value, the same token hashed consistently under one secret, and rotating the
secret changed the hash. Expiry resolved to exactly 12 hours under the real D1 configuration.

The full suite passed with 30 tests and only the existing FastAPI TestClient warning. Ruff passed,
and Alembic reported no model/schema drift.

#### Concepts I Learned

- Opaque session tokens need cryptographic randomness because possession of the raw value grants
  authentication.
- Session tokens are already high entropy, so a fast deterministic hash supports indexed lookup;
  password hashes require a deliberately slow algorithm for a different threat model.
- HMAC adds a server-held pepper, limiting what a sessions-table leak reveals by itself.
- Rotating the HMAC key invalidates every existing session because their lookup hashes change.
- Timezone-aware timestamps prevent local-time ambiguity in absolute-expiry comparisons.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Token entropy | 16, 24, or 32 random bytes | 32 bytes (256 bits) | It provides ample entropy with a cookie-friendly 43-character encoding. | Tokens are slightly longer than a minimal design. |
| Lookup hash | Plain SHA-256; concatenated pepper; HMAC-SHA256 | HMAC-SHA256 keyed by `SESSION_SECRET` | HMAC is the standard keyed construction and keeps database-only compromise from reproducing hashes. | Secret rotation revokes all sessions. |
| Expiry timestamp | Accept naive/aware values; require aware values | Require timezone-aware input and normalize to UTC | Security expiry logic should never guess a timezone. | Callers must construct correct aware timestamps. |

#### Problems I Encountered

- Ruff requested import grouping after the security test module gained new standard-library,
  application, and third-party imports.

#### How I Diagnosed Them

- Ruff identified the exact import block; all targeted behavior tests already passed.

#### How I Solved Them

- I applied Ruff's safe import correction and reran formatting, linting, the full suite, and the
  Alembic drift check.

#### Tests I Added

- Generate 100 unique URL-safe tokens with the expected entropy-derived length.
- Verify deterministic, fixed-length hashing and different-token separation.
- Verify changing `SESSION_SECRET` changes the lookup hash.
- Verify configured absolute expiry from an aware timestamp.
- Reject naive timestamps.
- Assert helper calls emit neither raw tokens nor their hashes to logs.

Result: `30 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest tests/unit/test_security.py -q
uv run pytest -q
uv run alembic check
```

#### Files I Changed

- `backend/app/core/security.py`
- `backend/tests/unit/test_security.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Raw tokens are returned only to the future cookie-issuance layer and never persisted here.
- Stored lookup values are HMAC-SHA256 hex digests compatible with the model's 64-character column.
- Session secrets are accessed through `SecretStr` and never logged.
- Key rotation provides an emergency global session-revocation mechanism.
- Expiry calculation rejects ambiguous timestamps.

#### What I Would Do Differently

I would record the global-session-revocation consequence of secret rotation alongside the original
configuration decision, because it is an operational behavior as well as a cryptographic choice.

#### Questions I Still Have

- Phase 10 must finalize cookie names, paths, and `Max-Age` behavior while preserving the spec's
  `__Host-` prefix requirement where possible.

#### Next Step

Review and commit Phase 9. Stop before Phase 10 so database session creation, cookie issuance, CSRF
cookie generation, and audit writes remain one separately reviewed login phase.

### Entry — 2026-06-29 — Phase 10: Login Endpoint and Cookie Issuance

#### What I Worked On

I implemented the first authenticated HTTP flow. The login schema normalizes credentials, the
service verifies passwords and creates server-side sessions plus audit rows, and the route issues
the secure auth/CSRF cookie pair without returning raw authentication material in the response.

#### What I Expected to Happen

I expected seeded credentials to create one hashed session row, unknown/wrong/inactive users to
receive an identical generic failure, outdated password parameters to rehash on successful login,
and both cookies to carry the required security attributes.

#### What Actually Happened

Targeted API tests verified successful login, hash-only persistence, success/failure audits,
enumeration-safe errors, inactive-user blocking, and rehash-on-login. A real Uvicorn request
returned HTTP 200 and set a redacted `__Host-session` cookie with
`HttpOnly/Secure/SameSite=Strict/Path=/` and a 12-hour Max-Age. The readable CSRF cookie used the
same secure scope without `HttpOnly`.

PostgreSQL contained only the 64-character lookup hash with a 12-hour lifetime. The complete suite
passed with 34 tests and the existing FastAPI TestClient warning; Alembic found no drift.

#### Concepts I Learned

- Authentication belongs in a service transaction; cookie construction belongs in the HTTP route.
- A dummy password hash reduces obvious timing differences between unknown-email and wrong-password
  paths.
- `__Host-` cookies require `Secure`, `Path=/`, and no `Domain` attribute.
- The CSRF token must be readable by JavaScript but independent from the HttpOnly session token.
- Successful login can safely upgrade old Argon2 parameters because the plaintext is present only
  during verified authentication.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Unknown-user verification | Return immediately; verify a dummy Argon2 hash | Dummy verification | It narrows timing differences that could reveal registered email addresses. | Unknown logins consume intentional password-hash work. |
| Auth cookie name | Always `session`; always `__Host-session`; conditional | `__Host-session` without Domain, `session` with Domain | It uses the strongest prefix whenever technically valid. | Current-session lookup must use the same helper. |
| Login response | Return user/session data; minimal status | `{"status":"authenticated"}` | Raw tokens stay cookie-only and `/auth/me` will become the user source in Phase 11. | The client needs the next request to load user details. |
| Failure handling | FastAPI `detail`; common envelope shape | Generic `UNAUTHENTICATED` envelope | It prevents enumeration and already matches the future API contract. | Phase 17 still needs to centralize exception mapping. |
| Login CSRF | Require pre-session token; issue token at login | Login establishes the CSRF cookie; later mutations require it | The selected double-submit design has no session token before login. | SameSite remains the login request's current CSRF defense. |

#### Problems I Encountered

- Ruff rejected a direct `Depends(get_db)` call in the function default.
- Database fixtures under `tests/db/conftest.py` were not visible to API tests.
- The generated API test needed mechanical formatting.

#### How I Diagnosed Them

- Ruff identified the dependency-default rule and recommended a non-call default pattern.
- Pytest listed available fixtures and showed the database fixtures were scoped only below
  `tests/db/`.
- Targeted tests isolated fixture collection before exercising login behavior.

#### How I Solved Them

- I switched the route dependency to `Annotated[DatabaseSession, Depends(get_db)]`.
- I promoted shared database configuration/engine/session fixtures to `tests/conftest.py` and
  updated existing database-test imports.
- I applied Ruff's formatter and reran targeted and full gates.

#### Tests I Added

- Successful login creates one hash-only session row and a success audit.
- Auth and CSRF cookies have the required attributes and independent values.
- Unknown email and wrong password produce identical generic 401 bodies and no session.
- Inactive users receive the same generic failure.
- Login upgrades a valid password hash with weaker Argon2 parameters.

Result: `34 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run pytest tests/api/test_auth.py -q
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest -q
uv run alembic check
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### Files I Changed

- `backend/app/core/security.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/api/routes/auth.py`
- `backend/app/main.py`
- `backend/tests/conftest.py`
- `backend/tests/api/test_auth.py`
- Existing database tests updated to import shared fixtures
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- The raw session token exists only in the HttpOnly cookie; SQL and audits receive no raw value.
- Login failure messages are identical for unknown, wrong-password, and inactive-user cases.
- Passwords and hashes are absent from responses and audit metadata.
- Session creation, password rehashing, and success audit commit atomically.
- Failed logins write only sanitized audit metadata.
- Secure cookie attributes are asserted from actual `Set-Cookie` headers.

#### What I Would Do Differently

I would place shared database fixtures at `tests/conftest.py` when Phase 4 first introduced them,
because later API and service suites naturally need the same isolation boundary.

#### Questions I Still Have

- Phase 11 must decide exactly when to update `last_used_at` to avoid a database write on every
  authenticated request while still enforcing the 30-minute idle timeout.

#### Next Step

Review and commit Phase 10. Stop before Phase 11 so session resolution, expiry/revocation checks,
sliding idle activity, and `/auth/me` remain one separate phase.

### Entry — 2026-06-29 — Phase 11: Current Session and Current User

#### What I Worked On

I added the FastAPI dependency that resolves the raw auth cookie to its HMAC lookup hash, loads the
server-side session and user, enforces revocation plus both expiry clocks, slides idle activity, and
provides `GET /api/auth/me`.

#### What I Expected to Happen

I expected only valid, active, non-expired SQL sessions to resolve. Missing, unknown, revoked,
absolute-expired, idle-expired, and inactive-user states should all produce the same 401 envelope,
while successful requests update `last_used_at` and return safe user fields.

#### What Actually Happened

The dependency resolved valid sessions by their indexed hash, loaded the related user, updated idle
activity, and returned the seeded administrator through `/api/auth/me`. Tests proved every invalid
state and exact idle/absolute boundaries fail closed.

A real server flow logged in, returned safe user data from `/auth/me`, then returned 401 when the
same session row was expired and the same cookie was reused. The full suite passed with 41 tests
and the existing FastAPI TestClient warning; Alembic found no drift.

#### Concepts I Learned

- Authentication dependencies turn an untrusted cookie into a validated SQL-backed principal.
- Absolute expiry never moves, while idle expiry slides only after accepted activity.
- Revocation and user activation are server-side state, so cookie possession alone is insufficient.
- Inclusive expiry boundaries avoid a session being accepted at the exact instant it expires.
- Returning a principal containing both user and session avoids repeating lookup work for logout.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Dependency result | Return user only; return user and session principal | Principal containing both | Routes use the user now, and Phase 12 can revoke the already validated session. | One small dataclass becomes part of the auth dependency boundary. |
| Idle update frequency | Thresholded writes; update every valid request | Update every valid request | The implementation plan explicitly chooses a sliding update on each request. | Authenticated reads perform one database write/commit. |
| Expiry boundary | Expire after `>`; expire at `>=` | Inclusive expiration | A session is invalid at the configured deadline, not one request later. | Boundary tests must use aware timestamps precisely. |
| Error rendering | FastAPI detail; narrow auth exception handler | Stable `UNAUTHENTICATED` envelope | All auth failures already honor the public contract before Phase 17. | Phase 17 will consolidate this narrow handler. |

#### Problems I Encountered

- There were no implementation failures after the Phase 10 fixture promotion and dependency-style
  correction.

#### How I Diagnosed Them

- Targeted tests exercised valid, missing, invalid, revoked, expired, idle-boundary, and inactive
  paths before the full suite.

#### How I Solved Them

- I used one joined session/user query, centralized validity checks in the dependency, and committed
  the idle timestamp only after every guard passed.

#### Tests I Added

- Valid `/auth/me` response contains only safe user fields.
- Valid activity slides `last_used_at`.
- Missing and unknown cookies return identical 401 envelopes.
- Revoked, absolute-expired, and exactly idle-expired sessions are rejected.
- Sessions belonging to inactive users are rejected.

Result: `41 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run pytest tests/api/test_auth.py -q
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest -q
uv run alembic check
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### Files I Changed

- `backend/app/api/deps.py`
- `backend/app/schemas/auth.py`
- `backend/app/api/routes/auth.py`
- `backend/app/main.py`
- `backend/tests/api/test_auth.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Raw cookies are HMACed before SQL lookup and never logged.
- Every invalid session state uses the same response envelope.
- Inactive users cannot continue operating with an otherwise valid session.
- Safe response schemas exclude password hashes, sessions, and audit relationships.
- Idle activity is committed only after all authentication guards succeed.

#### What I Would Do Differently

At larger scale, I would evaluate thresholded idle updates to reduce write amplification, but the
per-request update is clearer and matches this project's explicit learning plan.

#### Questions I Still Have

- Phase 12 must decide whether logout should require a currently valid session or remain idempotent
  when the cookie is already invalid; the plan currently builds logout on the valid principal.

#### Next Step

Review and commit Phase 11. Stop before Phase 12 so logout revocation, cookie clearing, and logout
audit behavior remain one separate phase.

### Entry — 2026-06-29 — Phase 12: Logout and Server-Side Revocation

#### What I Worked On

I added authenticated logout using the validated user/session principal from Phase 11. The service
sets `revoked_at` and writes a logout audit atomically, while the route expires both the HttpOnly
session cookie and readable CSRF cookie.

#### What I Expected to Happen

I expected logout to return 204, persist immediate revocation, clear both browser cookies, and make
the old raw cookie unusable even if manually restored. Missing authentication should fail with the
same 401 envelope and create no logout audit.

#### What Actually Happened

Targeted tests proved logout revocation, audit creation, cookie clearing, old-cookie rejection, and
unauthenticated rejection. A real Uvicorn flow returned login 200, logout 204, and 401 when the old
cookie was reused. PostgreSQL confirmed the revoked session and logout audit row.

The full suite passed with 43 tests and only the existing FastAPI TestClient warning. Ruff passed,
and Alembic reported no drift.

#### Concepts I Learned

- Browser cookie deletion is convenience; the persisted `revoked_at` value is the security control.
- Passing the validated principal into logout avoids a second raw-cookie/session lookup.
- Revocation and its audit should share one transaction so history cannot claim an action that did
  not persist.
- Reusing an old raw token is the strongest observable test that logout is truly server-side.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Invalid-cookie logout | Always return 204; require valid principal | Require valid principal | The phase plan builds logout on the current session and audits a concrete revocation. | Already-invalid logout attempts return 401 rather than being idempotent. |
| Revocation transaction | Commit revocation then audit; commit together | One transaction | Audit and security state cannot diverge. | An audit-write failure rolls back logout. |
| Cookie clearing | Clear auth only; clear auth and CSRF | Clear both with issuance attributes | The CSRF token belongs to the revoked authenticated browser session. | Two deletion headers are required. |

#### Problems I Encountered

- Ruff requested mechanical formatting after logout assertions expanded the API test module.

#### How I Diagnosed Them

- Targeted tests passed before formatting, isolating the issue to style rather than behavior.

#### How I Solved Them

- I applied Ruff's formatter and reran targeted tests, the full suite, and Alembic drift checking.

#### Tests I Added

- Logout marks the exact session revoked and writes a linked logout audit.
- Auth and CSRF deletion headers match the original cookie scope and security attributes.
- Manually restoring the old raw cookie still produces 401 from `/auth/me`.
- Logout without a valid session returns 401, sets no cookies, and writes no logout audit.

Result: `43 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run pytest tests/api/test_auth.py -q
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest -q
uv run alembic check
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### Files I Changed

- `backend/app/services/auth_service.py`
- `backend/app/api/routes/auth.py`
- `backend/tests/api/test_auth.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Revocation invalidates the server-side session before cookie cleanup matters.
- No raw token, cookie value, or password is written to audit metadata.
- Logout audits identify only the user and session IDs.
- Reusing a revoked cookie is covered by both automated and real-server verification.
- CSRF enforcement remains explicitly scheduled for Phase 13.

#### What I Would Do Differently

For a public production service, I would consider idempotent logout for already-invalid cookies,
but this implementation follows the current plan's valid-session dependency and explicit audit.

#### Questions I Still Have

- Phase 13 must decide whether the CSRF dependency should be attached per route or as a reusable
  dependency alias for every unsafe method.

#### Next Step

Review and commit Phase 12. Stop before Phase 13 so double-submit CSRF comparison and route
attachment remain one separate security phase.

### Entry — 2026-06-29 — Phase 13: Double-Submit CSRF Protection

#### What I Worked On

I added a reusable `CsrfProtected` dependency that compares the configured readable CSRF cookie
with `X-CSRF-Token` on unsafe HTTP methods. Logout now uses that dependency, while login remains
exempt because it creates the session/CSRF pair and safe methods remain readable without a token.

#### What I Expected to Happen

I expected missing and mismatched CSRF credentials to return the same 403 `CSRF_INVALID` envelope
before logout could revoke a session. A matching pair should reach normal authentication and
logout, and `GET /api/auth/me` should continue to work without a CSRF header.

#### What Actually Happened

Focused tests proved missing and mismatched headers are rejected without revocation or logout
audits, a matching header allows logout, and a safe GET needs no CSRF token. The full suite passed
with 45 tests and only the existing FastAPI TestClient warning. Ruff passed, and Alembic reported
no drift.

A real Uvicorn flow returned 403 for missing CSRF, kept the session usable, accepted a matching
token with 204, and then rejected the revoked session with 401.

#### Concepts I Learned

- Cookie authentication makes the browser send credentials automatically, which is why an
  independent token echoed in a custom header is needed for mutations.
- `SameSite=Strict` helps, but explicit CSRF validation makes the mutation boundary testable and
  does not depend on one browser policy alone.
- Constant-time comparison keeps token equality from becoming observable through timing.
- CSRF rejection should occur before business logic so failed requests cannot mutate state.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Dependency shape | Inline logout check; global middleware; reusable dependency | Reusable dependency alias | Future mutation routes can opt into one explicit, testable contract. | Every POST/PATCH route must remember to attach it. |
| Safe methods | Exempt GET only; exempt GET/HEAD/OPTIONS | Exempt GET/HEAD/OPTIONS | These methods are defined as read-only or protocol support and should not mutate state. | Any route that violates safe-method semantics would bypass this guard. |
| Token comparison | Normal equality; constant-time equality | `hmac.compare_digest` | It is a standard low-cost security primitive for secret comparison. | Both submitted values must be strings of the same general type. |
| Failure ordering | Authenticate first; CSRF first | CSRF first on protected routes | Rejected cross-site requests do not slide session activity or reach database-backed auth work. | An unauthenticated unsafe request with invalid CSRF receives 403 before 401. |

#### Problems I Encountered

- The managed shell initially denied access to uv's user cache during the real-server smoke
  client command.

#### How I Diagnosed Them

- The automated suite and Uvicorn server were already healthy; the error named the cache path and
  occurred before the HTTP client ran.

#### How I Solved Them

- I reran the same bounded local smoke command with approved environment access and kept all
  credentials and token values out of output.

#### Tests I Added

- Missing and mismatched CSRF headers return the identical 403 `CSRF_INVALID` contract.
- CSRF rejection leaves the current session unrevoked and emits no logout audit.
- A safe authenticated GET succeeds without a CSRF header after a rejected mutation.
- Existing successful logout now proves a matching double-submit pair is accepted.

Result: `45 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest tests/api/test_auth.py -q
uv run pytest -q
uv run alembic check
uv run uvicorn app.main:app --host 127.0.0.1 --port 8013
```

#### Files I Changed

- `backend/app/api/deps.py`
- `backend/app/api/routes/auth.py`
- `backend/app/main.py`
- `backend/tests/api/test_auth.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Missing and mismatched values share one response and neither submitted token is logged.
- CSRF failure runs before principal resolution on logout, preventing rejected requests from
  updating `last_used_at`.
- Login intentionally remains unprotected because no double-submit pair exists before login.
- Future unsafe endpoints must explicitly use `CsrfProtected`; route review and integration tests
  must enforce that convention.

#### What I Would Do Differently

For a much larger API, I would consider router-level dependencies or middleware to reduce the
chance that a new mutation omits the guard. Per-route attachment is clearer for this teaching-sized
application and preserves intentional exceptions such as login.

#### Questions I Still Have

- None for Phase 13. Phase 14 is intentionally separate.

#### Next Step

Review and commit Phase 13. Stop before Phase 14 so role authorization remains its own bounded
security phase.

### Entry — 2026-06-29 — Phase 14: Role Authorization

#### What I Worked On

I added a `require_role(...)` FastAPI dependency factory built on the authenticated SQL user, plus
named `AdminUser` and `CustomerUser` aliases for future route signatures. A role mismatch now maps
to the stable 403 `FORBIDDEN` envelope.

I also moved the existing migrated, seeded authentication test fixture into shared test
configuration so focused authorization API tests could reuse the real session and SQL-user path.

#### What I Expected to Happen

I expected each seeded user to pass the matching role guard and fail the opposite guard with the
same 403 response. Supplying a role-like request header should have no effect because the
dependency reads only `User.role` after server-side session resolution.

#### What Actually Happened

Four focused API cases passed: ADMIN and CUSTOMER each reached their matching guard, and each was
denied by the opposite guard. The denial cases included spoofed `X-Role` headers, which the backend
ignored. The full suite passed with 49 tests and the one existing TestClient warning. Ruff passed,
and Alembic reported no drift.

A real Uvicorn flow against test-only probe routes reproduced both 200 allow results and both 403
`FORBIDDEN` denials without exposing session or CSRF cookie values.

#### Concepts I Learned

- Authentication establishes identity; role authorization decides whether that authenticated
  identity may enter a category of route.
- A role mismatch is 403 because the server knows who the caller is but refuses that operation.
- Returning the authorized `User` lets later routes use one dependency for both the guard and the
  trusted principal without another lookup.
- Named role aliases make a route's security requirement visible in its function signature.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Role guard shape | Separate ADMIN/CUSTOMER functions; parameterized factory | `require_role(...)` factory with named aliases | One implementation prevents the two guards from drifting while aliases keep routes readable. | Closure-based dependencies are slightly less direct to newcomers. |
| Trusted role source | Header/body/cookie; authenticated SQL `User.role` | SQL user only | The backend database is the authorization source of truth required by the specification. | Every role-gated route performs the normal session/user database resolution. |
| Phase 14 test surface | Add premature product route; call dependency directly; test-only HTTP probes | Test-only probes | HTTP tests verify FastAPI dependency wiring and the public envelope without inventing Phase 24 admin behavior. | Manual smoke uses the test module rather than a product endpoint that does not exist yet. |

#### Problems I Encountered

- The reusable authenticated-client fixture was local to `test_auth.py`, so a focused
  authorization module could not consume it cleanly.
- The first full-suite command could not initialize uv's cache under the managed filesystem.

#### How I Diagnosed Them

- I inspected fixture scope and avoided importing one test module from another.
- The uv error identified its user-cache path before pytest started.

#### How I Solved Them

- I moved the unchanged fixture setup into `tests/conftest.py`, where pytest shares it naturally.
- I reran the bounded `uv run` gate with the already approved cache access.

#### Tests I Added

- An ADMIN SQL user passes the ADMIN guard.
- A CUSTOMER SQL user passes the CUSTOMER guard.
- A CUSTOMER receives 403 `FORBIDDEN` from the ADMIN guard despite an `X-Role: ADMIN` header.
- An ADMIN receives 403 `FORBIDDEN` from the CUSTOMER guard despite an `X-Role: CUSTOMER` header.

Result: `49 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest tests/api/test_authorization.py -q
uv run pytest -q
uv run alembic check
uv run uvicorn tests.api.test_authorization:app --host 127.0.0.1 --port 8014
```

#### Files I Changed

- `backend/app/api/deps.py`
- `backend/app/main.py`
- `backend/tests/conftest.py`
- `backend/tests/api/test_auth.py`
- `backend/tests/api/test_authorization.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Role values from headers, request bodies, and cookies never enter the authorization decision.
- Both roles use the same deny contract, which reveals no extra permission detail.
- The guard returns the exact authenticated SQL user, preserving one trusted principal path.
- Permission-denied audit writes required by SPEC §16 remain future work; Phase 14's explicit scope
  contains only the reusable role boundary and its response contract.

#### What I Would Do Differently

Once real customer and admin routes exist, I will keep these dependency-level tests and add route
contract tests at those product endpoints instead of relying only on probes.

#### Questions I Still Have

- Which later phase should own persistence of permission-denied audit events before final MVP
  acceptance? Phase 17's centralized errors or the first real role-gated routes are natural points.

#### Next Step

Review and commit Phase 14. Stop before Phase 15 so ownership authorization and its 404 anti-IDOR
behavior remain a separate bounded phase.

### Entry — 2026-06-29 — Phase 15: Ownership Authorization

#### What I Worked On

I added `get_owned_account`, which requires an authenticated CUSTOMER and loads an account using
one SQL query filtered by both `account_id` and the authenticated user's ID. The `OwnedAccount`
alias gives every future customer account route one reusable ownership boundary.

Missing and non-owned accounts now map to the same stable 404 `NOT_FOUND` envelope.

#### What I Expected to Happen

I expected a customer to load an owned account, receive an indistinguishable 404 for another
customer's account or a nonexistent ID, and never expose customer ownership behavior to ADMIN.

#### What Actually Happened

All four focused tests passed. The own-account request returned 200; another customer's account and
a missing account returned the identical 404 response; ADMIN was rejected by the CUSTOMER role
guard with 403. The full suite passed with 53 tests and the existing TestClient warning. Ruff
passed, and Alembic reported no drift.

A real Uvicorn flow reproduced login 200, owned account 200, other account 404 `NOT_FOUND`, and
missing account 404 `NOT_FOUND`.

#### Concepts I Learned

- IDOR prevention requires authorization inside the database lookup, not merely hidden frontend
  links or an account ID check after loading.
- Combining resource ID and owner ID in one query ensures another customer's row never crosses the
  application boundary.
- Returning 404 for both absent and non-owned resources prevents callers from discovering which
  account IDs exist.
- Role and ownership checks compose: CUSTOMER establishes the allowed actor class, then ownership
  narrows access to that customer's resource.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Ownership lookup | Load by ID then compare; query by ID and owner together | Filter by ID and owner together | It prevents another customer's row from entering application logic and naturally unifies missing/non-owned results. | Future admin lookups need a separate path instead of reusing this dependency. |
| Dependency composition | Current user only; CUSTOMER role plus ownership | CUSTOMER role plus ownership | The specification says admins are not owners, and protected customer routes need all three layers. | ADMIN receives 403 before account existence is considered. |
| Shared route type | Repeat checks in routes; `OwnedAccount` alias | `OwnedAccount` alias | One visible annotation reduces the chance of inconsistent account-scoped authorization. | Every future customer account route must deliberately use the alias. |

#### Problems I Encountered

- The first full-suite command could not initialize uv's cache under the managed filesystem.

#### How I Diagnosed Them

- The error identified uv's user-cache path and occurred before pytest began.

#### How I Solved Them

- I reran the bounded `uv run` verification with approved cache access.

#### Tests I Added

- A CUSTOMER can load an account they own.
- Another customer's account returns 404 `NOT_FOUND`.
- A nonexistent account returns the identical 404 `NOT_FOUND`.
- ADMIN receives 403 and cannot enter the customer ownership boundary.

Result: `53 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest tests/api/test_ownership.py -q
uv run pytest -q
uv run alembic check
uv run uvicorn tests.api.test_ownership:app --host 127.0.0.1 --port 8015
```

#### Files I Changed

- `backend/app/api/deps.py`
- `backend/app/main.py`
- `backend/tests/api/test_ownership.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Owner identity comes only from the SQL-backed authenticated user, never a request field.
- Non-owned account rows are not loaded before the authorization decision.
- Missing and non-owned resources share status, code, message, and fields.
- Future customer account-scoped routes must use `OwnedAccount`; admin resource access requires a
  distinct admin service/query path.

#### What I Would Do Differently

When Phase 18 adds real account routes, I will retain these boundary tests and add product-route
tests proving those routes actually declare `OwnedAccount`.

#### Questions I Still Have

- None for Phase 15.

#### Next Step

Review and commit Phase 15. Stop before Phase 16 so security-suite consolidation remains a
separate phase.

### Entry — 2026-06-29 — Phase 16: Auth, Authorization, and CSRF Test Suite

#### What I Worked On

I consolidated the M3 security suite around shared `admin_client` and `customer_client` fixtures.
Both fixtures use the existing migrated, seeded PostgreSQL context and authenticate through the
real login route. I moved focused CSRF rejection coverage from the broad authentication module
into `test_csrf.py` and refactored role and ownership tests to use the role fixtures.

#### What I Expected to Happen

I expected all existing security behavior to remain unchanged while the suite gained clearer
boundaries: authentication/session/logout in `test_auth.py`, CSRF in `test_csrf.py`, role checks in
`test_authorization.py`, and IDOR prevention in `test_ownership.py`.

#### What Actually Happened

The consolidated security command passed 23 tests. The full suite remained at 53 passing tests,
with only the existing FastAPI TestClient warning. Ruff passed, and Alembic reported no schema
drift. No application files changed.

#### Concepts I Learned

- A fixture should model a trusted system state, not bypass the behavior under test; these role
  clients authenticate through the public login contract.
- Fixture dependencies preserve isolation because each authenticated client receives the same
  per-test context and teardown as the original unauthenticated client.
- Organizing tests by security boundary makes failures easier to diagnose without weakening
  end-to-end API assertions.
- A consolidation phase should preserve test count and assertions unless a deliberate coverage
  change is documented.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Role-client fixtures | Mock current user; set cookies directly; call real login | Call real login with seeded users | This preserves the SQL role and session boundary in every authorization test. | Role tests perform Argon2 work and are slightly slower. |
| Test organization | One large auth module; security-boundary modules | Separate auth, CSRF, role, and ownership modules | Failures point directly to the affected boundary and Phase 16 matches the planned suite shape. | Shared fixtures become an important test dependency. |
| Fixture lifetime | Module/session authenticated clients; function-scoped clients | Function-scoped | Each test gets fresh database rows, cookies, and session state. | Migrations and seeding repeat, favoring safety over maximum speed. |

#### Problems I Encountered

- uv cache access was denied under the managed filesystem on unapproved verification commands.
- The test guide still described `conftest.py` as future work.

#### How I Diagnosed Them

- The uv error named its cache path before pytest started.
- I compared the test guide with the existing fixture implementation.

#### How I Solved Them

- I reran the bounded `uv run` gates with approved cache access.
- I updated the test guide to describe the real database and authenticated-role fixtures.

#### Tests I Added

No new behavior scenario was required; Phase 16 consolidated and reran the complete M3 security
matrix:

- Login success, generic failure, inactive user, and password rehash.
- Missing, invalid, revoked, absolute-expired, idle-expired, and inactive-user sessions.
- Server-side logout revocation and cookie clearing.
- CSRF missing, mismatch, matching, and safe-method behavior.
- ADMIN/CUSTOMER allow and deny behavior.
- Owned, non-owned, missing, and wrong-role account access.

Result: security suite `23 passed`; full suite `53 passed`; one existing warning.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest tests/api/test_auth.py tests/api/test_csrf.py \
  tests/api/test_authorization.py tests/api/test_ownership.py -q
uv run pytest -q
uv run alembic check
```

#### Files I Changed

- `backend/tests/conftest.py`
- `backend/tests/api/test_auth.py`
- `backend/tests/api/test_csrf.py`
- `backend/tests/api/test_authorization.py`
- `backend/tests/api/test_ownership.py`
- `backend/tests/README.md`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Tests never set role or authentication dependencies directly; login and SQL remain authoritative.
- Function-scoped clients prevent cookies or revoked sessions from leaking between cases.
- The database safety check still rejects a test URL equal to the development URL.
- CSRF rejection still proves no revocation or misleading logout audit is written.

#### What I Would Do Differently

If repeated migration and Argon2 work becomes a material bottleneck, I would profile the suite
before changing fixture scope. Faster shared authenticated clients would weaken isolation.

#### Questions I Still Have

- None for Phase 16.

#### Next Step

Review and commit Phase 16. Stop before Phase 17 so centralized domain errors remain a separate M4
implementation phase.

### Entry — 2026-06-29 — Phase 17: Domain Errors and Common Error Envelope

#### What I Worked On

I created `app/errors.py` with one `DomainError` base and concrete errors for the ten initial codes
in SPEC §13. Expected domain failures now use one handler, while request validation and
framework-generated HTTP errors are normalized into the same envelope.

Authentication, CSRF, role, and ownership dependencies now raise the centralized errors. Login
failure moved into the service as an enumeration-safe `UnauthenticatedError`, which removed the
route-local `try/except` and `JSONResponse`.

Unexpected exceptions are caught by application middleware, logged with only exception type,
method, and path, and returned as generic 500 `INTERNAL_ERROR`.

#### What I Expected to Happen

I expected every error path to return `{error: {code, message, fields}}`, validation to omit
rejected input values, and unexpected failures to expose no SQL, token, password, cookie, or
traceback details in responses or logs.

#### What Actually Happened

Thirteen focused error tests covered all ten domain errors, validation redaction, unknown routes,
and forced internal failures. The combined security/error suite passed 36 tests, and the full
suite passed 66 tests with only the existing TestClient warning. Ruff passed, and Alembic reported
no drift.

The first real-Uvicorn smoke revealed that Starlette re-raised exceptions after an outer
`Exception` handler returned a safe response, allowing Uvicorn to print the original planted
SQL/token message. Moving the catch-all into application middleware prevented propagation. The
repeated smoke returned the same safe 500 while logs contained only the exception type, method,
and path.

#### Concepts I Learned

- Typed domain errors separate public failure contracts from route and service implementation.
- Validation errors need deliberate serialization because framework error objects include rejected
  input values.
- A safe response is not enough if the hosting server later logs the raw exception.
- Middleware ordering determines whether an unexpected exception is converted before or after the
  server's traceback logger.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Error contract | Per-route responses; per-error handlers; typed base plus one handler | Typed base plus one handler | Services and dependencies can express failures without duplicating HTTP envelopes. | Concrete errors carry HTTP status metadata. |
| Validation fields | Return FastAPI details; echo messages/inputs; sanitized field map | Sanitized field map | It preserves useful field names without reflecting passwords or rejected values. | Reasons are intentionally generic. |
| Unexpected failures | Outer exception handler; catch-all middleware | Catch-all middleware | It prevents Starlette/Uvicorn from re-raising and logging secret-bearing exception messages. | Middleware must remain outer to route execution and delegate expected errors normally. |
| Internal logging | Full traceback; exception message; type/method/path only | Type, method, and path only | These diagnostics are useful without risking SQL, credential, token, or cookie leakage. | Root-cause detail is intentionally limited until secure structured logging exists. |

#### Problems I Encountered

- The original catch-all returned a safe body but Uvicorn still logged the raw exception traceback.
- Programmatic Alembic migrations disabled the existing `app.errors` logger in combined tests.
- The older Starlette 422 constant emitted a new deprecation warning.

#### How I Diagnosed Them

- I ran a real Uvicorn probe with planted SQL/token text and inspected server output, not only the
  HTTP response.
- I compared isolated and combined test runs and traced logger state to `logging.fileConfig`.
- The warning named the replacement 422 constant.

#### How I Solved Them

- I caught unexpected failures in application middleware before the outer server-error layer.
- I configured Alembic with `disable_existing_loggers=False`.
- I used `HTTP_422_UNPROCESSABLE_CONTENT`.

#### Tests I Added

- Every initial domain error code renders the common envelope with its expected status.
- Request validation omits a planted rejected password.
- Unknown routes return the common 404 `NOT_FOUND` envelope.
- Forced internal errors return generic 500 `INTERNAL_ERROR`.
- Planted SQL/token fragments appear in neither the internal response nor application logs.
- The safe internal log retains exception type, request method, and path.

Result: `66 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest tests/api/test_errors.py -q
uv run pytest tests/api/test_auth.py tests/api/test_csrf.py \
  tests/api/test_authorization.py tests/api/test_ownership.py tests/api/test_errors.py -q
uv run pytest -q
uv run alembic check
uv run uvicorn tests.api.test_errors:app --host 127.0.0.1 --port 8017
```

#### Files I Changed

- `backend/app/errors.py`
- `backend/app/main.py`
- `backend/app/api/deps.py`
- `backend/app/api/routes/auth.py`
- `backend/app/services/auth_service.py`
- `backend/alembic/env.py`
- `backend/tests/api/test_auth.py`
- `backend/tests/api/test_csrf.py`
- `backend/tests/api/test_authorization.py`
- `backend/tests/api/test_ownership.py`
- `backend/tests/api/test_errors.py`
- `backend/app/README.md`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Validation responses never serialize rejected input values.
- Unexpected errors never return exception messages or tracebacks.
- The catch-all logs no exception message, SQL, headers, cookies, or token values.
- Expected login, authentication, CSRF, role, and ownership semantics remain unchanged.
- Alembic no longer disables application loggers when migrations run in the same process.

#### What I Would Do Differently

I would include a real-server log inspection in the first catch-all test plan, because in-process
response tests cannot prove what Uvicorn logs after the response is sent.

#### Questions I Still Have

- Correlation IDs and secure structured logging remain scheduled for hardening; the current
  minimal log deliberately favors secrecy over deep diagnostics.

#### Next Step

Review and commit Phase 17. Stop before Phase 18 so account reads and money serialization remain a
separate bounded phase.

### Entry — 2026-06-29 — Phase 18: Account Read Operations

#### What I Worked On

I added `GET /api/accounts` and `GET /api/accounts/{account_id}` for authenticated customers.
`list_owned_accounts` filters the SQL query by the authenticated customer's ID, while account
detail reuses the existing `OwnedAccount` dependency instead of performing a second lookup.

I also created `AccountResponse`, which exposes safe account fields and converts SQLAlchemy
`Decimal` balances directly to two-decimal strings.

#### What I Expected to Happen

I expected a customer to list only their two seeded accounts, retrieve an owned account, receive
404 for another customer's account, and see balances represented as JSON strings. ADMIN should be
rejected because these are customer routes.

#### What Actually Happened

Five focused API tests passed. They proved exact account membership and order, two-decimal string
balances, safe response fields, owned detail access, cross-customer 404 behavior, ADMIN 403
behavior, and a string balance in OpenAPI. The full suite passed 71 tests with the existing
TestClient warning. Ruff passed, and Alembic reported no drift.

A real Uvicorn flow returned login 200, account list 200 with two accounts and a string balance,
owned detail 200, and another customer's account 404 `NOT_FOUND`.

#### Concepts I Learned

- JSON numbers cannot guarantee decimal money semantics across JavaScript clients, so the API
  contract uses strings.
- Converting `Decimal` directly to a formatted string avoids binary floating-point entirely.
- A response schema is a security boundary because omitted ORM fields such as `user_id` and
  relationships cannot leak accidentally.
- A route can stay thin by returning an already-authorized dependency result rather than inventing
  a pass-through service or repeating the query.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Balance schema type | JSON number; Decimal field with serializer; string field with pre-validation | String field converted from `Decimal` | Runtime JSON and OpenAPI both clearly promise strings, and no float enters the path. | Clients must parse money with decimal-safe logic. |
| Account detail flow | Re-query in service; pass-through service; return `OwnedAccount` | Return `OwnedAccount` | Phase 15 already performs the complete ID-and-owner SQL lookup. | Detail reads use a dependency while list reads use a service. |
| List ordering | Database default; account number; ID | Account ID | Deterministic ordering keeps API output and tests stable without adding a new product decision. | A future UI may request a different explicit sort. |

#### Problems I Encountered

- Ruff required one mechanical formatting adjustment in the new account service.

#### How I Diagnosed Them

- The format check named the exact file before tests ran.

#### How I Solved Them

- I applied Ruff's formatter to that file and reran format, lint, and tests.

#### Tests I Added

- The account list contains only the authenticated customer's seeded accounts.
- Balances are exact two-decimal JSON strings and OpenAPI declares a string.
- Response objects omit `user_id` and unrelated ORM state.
- An owned detail request succeeds.
- Another customer's account returns 404 `NOT_FOUND`.
- ADMIN receives 403 from both customer account routes.

Result: `71 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest tests/api/test_accounts.py -q
uv run pytest -q
uv run alembic check
uv run uvicorn app.main:app --host 127.0.0.1 --port 8018
```

#### Files I Changed

- `backend/app/schemas/account.py`
- `backend/app/services/account_service.py`
- `backend/app/api/routes/accounts.py`
- `backend/app/main.py`
- `backend/tests/api/test_accounts.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- List queries filter by the SQL-authenticated customer ID.
- Detail queries use the shared `OwnedAccount` IDOR boundary.
- ADMIN cannot reuse customer account routes.
- Response validation prevents ownership identifiers and relationships from leaking.
- Money never passes through floating point.

#### What I Would Do Differently

If account list ordering becomes a product requirement, I would specify it explicitly rather than
relying on the current ID ordering chosen for deterministic behavior.

#### Questions I Still Have

- Phase 19 must choose the default and maximum transaction page size before adding history reads.

#### Next Step

Review and commit Phase 18. Stop before Phase 19 so pagination and transaction-history ordering
remain a separate bounded phase.

### Entry — 2026-06-29 — Phase 19: Paginated Transaction History

#### What I Worked On

I added paginated transaction history for one owned account and across all accounts owned by the
authenticated customer. Both services return newest-first pages ordered by `created_at DESC` and
`id DESC`.

I created `TransactionResponse`, which exposes the owning account ID for combined-feed context and
serializes both `amount` and `balance_after` directly from `Decimal` to two-decimal strings.

#### What I Expected to Happen

I expected stable, non-overlapping `limit`/`offset` pages; only the customer's transactions in the
combined feed; 404 for another customer's per-account history; 403 for ADMIN; and validation
errors for unsafe pagination bounds.

#### What Actually Happened

Eight focused tests passed. They proved per-account and cross-account ordering, page slicing,
ownership filtering, role denial, pagination validation, string money, and OpenAPI string types.
The full suite passed 79 tests with the existing TestClient warning. Ruff passed, and Alembic
reported no drift.

A real Uvicorn flow returned two disjoint customer-wide pages, an owned per-account page with a
string amount, and 404 `NOT_FOUND` for another customer's history.

#### Concepts I Learned

- Offset pagination needs a deterministic unique ordering or rows with equal timestamps can move
  between pages.
- `created_at DESC, id DESC` gives a useful newest-first feed and a stable tie-breaker.
- Cross-account ownership belongs in the SQL join predicate, not in post-query filtering.
- Rejecting an excessive page size makes the API contract observable instead of silently changing
  the caller's request.

#### Decisions I Made

| Decision | Options Considered | Choice | Reason | Trade-off |
|---|---|---|---|---|
| Page bounds | Default 20/50; max 100/200; silent clamp; validation error | Default 20, max 100, reject invalid | It is practical for UI pages, caps query work, and makes invalid input explicit. | Clients must correct requests above the maximum. |
| History order | Oldest first; account-grouped; newest first | `created_at DESC, id DESC` | Users usually need recent activity first, and ID uniquely stabilizes timestamp ties. | Offset pagination can still shift when newer rows are inserted between requests. |
| Cross-account service | Filter rows in Python; join accounts in SQL | SQL join filtered by customer ID | Other customers' rows never cross the persistence boundary. | The query depends on the account ownership join. |

#### Problems I Encountered

- Ruff requested one mechanical formatting change in the transaction test module.

#### How I Diagnosed Them

- The format check identified the file before tests ran.

#### How I Solved Them

- I applied Ruff's formatter and reran format, lint, focused tests, and the full suite.

#### Tests I Added

- Owned account history is newest-first and paginated.
- Customer-wide pages are chronological, disjoint, and contain only owned account IDs.
- Another customer's account history returns 404 `NOT_FOUND`.
- Limits below 1 or above 100 and negative offsets return 422 `VALIDATION_ERROR`.
- ADMIN receives 403 from both transaction-history routes.
- `amount` and `balance_after` are strings in runtime responses and OpenAPI.

Result: `79 passed, 1 existing warning`.

#### Commands I Used

```bash
cd backend
uv run ruff format --check app tests alembic
uv run ruff check app tests alembic
uv run pytest tests/api/test_transactions.py -q
uv run pytest -q
uv run alembic check
uv run uvicorn app.main:app --host 127.0.0.1 --port 8019
```

#### Files I Changed

- `backend/app/schemas/transaction.py`
- `backend/app/services/transaction_service.py`
- `backend/app/api/routes/transactions.py`
- `backend/app/main.py`
- `backend/tests/api/test_transactions.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Per-account history uses the shared `OwnedAccount` dependency.
- Customer-wide history filters ownership in SQL.
- ADMIN cannot use customer history routes.
- Page size is bounded to limit database work.
- Money never passes through floating point.

#### What I Would Do Differently

For a high-write production ledger, I would prefer cursor pagination because offset pages can shift
when new transactions arrive. Limit/offset is the explicit MVP contract and is simpler to teach.

#### Questions I Still Have

- Phase 20 must confirm the permitted deposit amount precision and upper limit before accepting
  money input.

#### Next Step

Review and commit Phase 19. Stop before Phase 20 so the first money mutation, locking, CSRF, and
audit behavior remain a separate bounded phase.

### Entry — 2026-06-29 — Phase 20: Atomic Deposit

#### What I Worked On

I added the first money mutation: a CSRF-protected deposit route, exact decimal-string validation,
and a service that re-loads the owned account under `SELECT ... FOR UPDATE`. Balance, the DEPOSIT
history row with `balance_after`, and the D2 audit event commit together.

#### What I Expected to Happen

Valid deposits should increase an ACTIVE owned account exactly once. Invalid precision, floats,
non-positive values, inactive accounts, and missing CSRF should produce the common error envelope
without balance, history, or audit writes.

#### What Actually Happened

Nine focused tests and all 88 backend tests passed. Real Uvicorn verification rejected missing
CSRF, accepted the matching pair, increased the balance by `1.00`, and persisted matching
transaction and audit rows. Ruff and Alembic checks passed.

#### Concepts I Learned

- Authorization and locking are separate responsibilities: the route dependency proves access,
  while the service re-queries under a row lock for mutation.
- Exact money input starts as a string and becomes `Decimal`; JSON floats are rejected.
- Balance, append-only history, and audit evidence belong to one database transaction.

#### Decisions I Made

| Decision | Choice | Reason | Consequence |
|---|---|---|---|
| Money input | Required decimal string, max 14 digits/2 decimals | Prevent binary floats and match `NUMERIC(14,2)` | Invalid precision and numeric JSON return 422 |
| Result limit | Reject balances above `999999999999.99` | Avoid database overflow becoming an internal error | Service returns field-specific validation |
| Lock point | Re-query owned account with `FOR UPDATE` | The balance must be read only after the lock is held | One extra authorized lookup occurs |

#### Tests I Added

- Atomic balance, DEPOSIT history, `balance_after`, and audit persistence.
- Invalid amount, precision, maximum, and JSON-float rejection.
- FROZEN/CLOSED rejection with no writes.
- Missing CSRF rejection before mutation.

Result: `88 passed, 1 existing warning`.

#### Files I Changed

- `backend/app/schemas/money.py`
- `backend/app/services/money_service.py`
- `backend/app/api/routes/money.py`
- `backend/app/main.py`
- `backend/tests/api/test_deposit.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- The lock, balance update, history row, and audit row share one transaction.
- Ownership is filtered again in the locking query.
- Account numbers and credentials never enter audit metadata.

#### Next Step

Commit Phase 20 and implement Phase 21 withdrawal separately.

### Entry — 2026-06-29 — Phase 21: Atomic Withdrawal

#### What I Worked On

I added CSRF-protected withdrawals by reusing the deposit schema, ownership boundary, locked
account lookup, and transaction pattern. The service checks sufficient funds while holding the row
lock, then atomically updates balance and adds WITHDRAWAL history and audit rows.

#### What Actually Happened

Five focused tests and all 93 backend tests passed. A real Uvicorn overdraw returned
`INSUFFICIENT_FUNDS` and left the balance unchanged. Ruff and Alembic checks passed.

#### Concepts I Learned

- The sufficient-funds check must occur after acquiring the lock or concurrent requests can both
  approve against the same stale balance.
- Rejected business rules should raise before any history or audit object is added.
- The database non-negative check remains a final backstop, not the primary user-facing rule.

#### Tests I Added

- Atomic withdrawal balance/history/audit success.
- Insufficient funds with no balance, transaction, or audit change.
- FROZEN/CLOSED rejection.
- Invalid amount and missing-CSRF rejection.

Result: `93 passed, 1 existing warning`.

#### Files I Changed

- `backend/app/services/money_service.py`
- `backend/app/api/routes/money.py`
- `backend/tests/api/test_withdrawal.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Next Step

Commit Phase 21 and implement Phase 22 transfer separately.

### Entry — 2026-06-29 — Phase 22: Atomic Transfer

#### What I Worked On

I added transfer creation and owned transfer detail. The service rejects same-account requests,
locks both owned rows in ascending ID order, validates status and funds, creates the parent,
updates both balances, appends TRANSFER_OUT/TRANSFER_IN legs with one reference ID, and writes the
audit event in one transaction.

#### What Actually Happened

Seven focused tests and all 100 backend tests passed. An induced failure after database flush but
before commit left both balances and all transfer/audit tables unchanged. Real Uvicorn verification
moved exactly `1.00`, created two legs, and returned the owned parent. Ruff and Alembic passed.

#### Concepts I Learned

- Consistent lock order prevents opposite-direction transfers from deadlocking each other.
- The parent must be flushed for its ID before both ledger legs can share that reference.
- A post-flush failure is the meaningful rollback test because SQL statements have executed but
  the transaction is not committed.

#### Tests I Added

- Atomic transfer parent, balance changes, two legs, `balance_after`, audit, and detail read.
- Same-account, non-owned source/destination, insufficient funds, inactive account, and CSRF.
- Induced post-flush failure with complete rollback.

Result: `100 passed, 1 existing warning`.

#### Files I Changed

- `backend/app/schemas/transfer.py`
- `backend/app/services/transfer_service.py`
- `backend/app/api/routes/transfers.py`
- `backend/app/main.py`
- `backend/tests/api/test_transfers.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Next Step

Commit Phase 22 and prove reconciliation and concurrent-overdraw safety in Phase 23.

### Entry — 2026-06-29 — Phase 23: Reconciliation and Concurrency

#### What I Worked On

I added a test-only reconciliation helper that computes signed history and compares it with the
stored balance. I also added a real PostgreSQL concurrency test using two independent sessions and
simultaneous withdrawals.

#### What Actually Happened

Reconciliation passed after fresh deposit, withdrawal, and transfer mutations. Two simultaneous
`80.00` withdrawals against `100.00` produced one success and one insufficient-funds result; the
final balance was `20.00` with one new history/audit pair. All 102 tests passed. The development
database's four accounts also reconciled after the real-server money smokes.

#### Concepts I Learned

- The transaction log is the source of truth and the balance is a cache that can be verified.
- Concurrency correctness requires separate sessions/connections; sequential tests cannot prove
  row-lock behavior.
- The service rule gives the useful error while the database nonnegative check is the backstop.

#### Tests I Added

- Reconciliation across seeded and freshly mutated accounts.
- Parallel withdrawals proving no lost update or overdraft.

Result: `102 passed, 1 existing warning`.

#### Files I Changed

- `backend/app/services/reconciliation.py`
- `backend/tests/db/test_reconciliation.py`
- `backend/tests/db/test_concurrency.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Next Step

Commit Phase 23 and begin M5 with the admin dashboard.

### Entry — 2026-06-29 — Phase 24: Admin Dashboard

#### What I Worked On

I added the first ADMIN-only endpoint with SQL aggregate queries for customer count, account count,
total simulated balance, and transactions in the last 30 days. Money remains a JSON string.

#### What Actually Happened

Three focused tests and all 105 backend tests passed. Real Uvicorn returned the dashboard to ADMIN
and 403 to CUSTOMER. The development total reflected prior smoke-test activity while the isolated
seed test remained deterministic.

#### Decisions I Made

| Decision | Choice | Reason |
|---|---|---|
| Customer count | Exclude ADMIN users | The metric represents managed customers |
| Recent window | 30 days | Explicit and conventional rather than an ambiguous "recent" |
| Admin boundary | `AdminUser`, no ownership dependency | Admin reads are not customer ownership |

#### Files I Changed

- `backend/app/schemas/admin.py`
- `backend/app/services/admin_service.py`
- `backend/app/api/routes/admin.py`
- `backend/app/main.py`
- `backend/tests/api/test_admin_dashboard.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Next Step

Commit Phase 24 and add administrator customer list/detail reads in Phase 25.

### Entry — 2026-06-29 — Phase 25: Admin Customer Reads

#### What I Worked On

I added ADMIN-only customer listing and customer detail with safe identity fields, accounts, and a
paginated newest-first transaction slice. Admin queries deliberately bypass customer ownership
dependencies while still filtering the selected user to the CUSTOMER role.

#### What Actually Happened

The focused admin and shared pagination suites passed 12 tests; all 109 backend tests passed. Real
Uvicorn returned two customer records and a drill-down with two accounts, string balances, and a
two-row history page.

#### Security or Reliability Considerations

- Password hashes, sessions, and ADMIN identities are excluded.
- Missing IDs and ADMIN user IDs share 404.
- CUSTOMER callers receive 403.
- Shared pagination constants prevent admin/customer history contracts from drifting.

#### Files I Changed

- `backend/app/api/pagination.py`
- `backend/app/api/routes/transactions.py`
- `backend/app/api/routes/admin.py`
- `backend/app/schemas/admin.py`
- `backend/app/services/admin_service.py`
- `backend/tests/api/test_admin_customers.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Next Step

Commit Phase 25 and implement status controls in Phase 26.

### Entry — 2026-06-29 — Phase 26: Administrative Status Controls

#### What I Worked On

I added CSRF-protected customer activation/deactivation and account freeze/unfreeze endpoints.
Deactivation bulk-revokes all active sessions in the same transaction; every transition writes a
D2 audit event. The account endpoint accepts only ACTIVE/FROZEN and cannot reopen CLOSED accounts.

#### What Actually Happened

Five focused tests and all 114 backend tests passed. Real Uvicorn proved a live customer session
became 401 immediately after deactivation, activation restored login, freeze blocked deposits, and
unfreeze restored ACTIVE.

#### Security or Reliability Considerations

- Admin status mutations require both SQL ADMIN role and CSRF.
- Deactivation, revocation, and audit are atomic.
- ADMIN remains unable to call customer money routes.
- Status audit metadata contains only IDs and state, never account numbers or credentials.

#### Files I Changed

- `backend/app/schemas/admin.py`
- `backend/app/services/admin_service.py`
- `backend/app/api/routes/admin.py`
- `backend/tests/api/test_admin_status.py`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Next Step

Commit Phase 26 and perform the Phase 27 BACKEND-COMPLETE audit and walkthrough.

### Entry — 2026-06-29 — Phase 27: BACKEND-COMPLETE Finalization

#### What I Worked On

I audited every production route for role/ownership enforcement, CSRF on mutations, common error
envelopes, and string money. I added shared permission-denied auditing at role, account, and
transfer ownership boundaries, plus sanitized stdout auth/authorization logs.

I added an end-to-end audit-event test covering every required SPEC §10 event and a redaction test
with planted password, cookie, account-number, and header-name values. I reseeded development,
walked every OpenAPI route as both roles, and reconciled all accounts after real mutations.

#### What I Expected to Happen

The backend checkpoint required a green suite, complete error and money contracts, CSRF on every
mutation, all required audit events, no sensitive response/log leakage, and a successful real
customer/admin walkthrough.

#### What Actually Happened

All 116 tests passed with the one existing TestClient warning, Ruff passed, and Alembic reported no
drift. The walkthrough covered all 17 production paths and all authorization/CSRF boundaries.
Reconciliation passed after deposit, withdrawal, and transfer. The final required `login_failure`
event was deliberately generated and the complete 11-event audit set was confirmed.

The first live logging check showed INFO auth logs were filtered by Uvicorn's inherited logger
configuration. An explicit duplicate-safe stdout handler for the `app` namespace made sanitized
login success/failure/logout logs observable without exposing request data.

#### Concepts I Learned

- Security verification must cover responses, persistence, and real server logs; any one view can
  miss a leak or missing event.
- Permission-denied auditing belongs at shared authorization boundaries so future routes inherit
  it automatically.
- Logging redaction is strongest when sensitive values are never passed to the logger.
- A backend contract is ready to freeze only after real role-based walkthroughs match automated
  tests and OpenAPI.

#### Decisions I Made

| Decision | Choice | Reason | Consequence |
|---|---|---|---|
| Permission auditing | Shared role/ownership boundaries | Prevent route-by-route omissions | Denied role and IDOR attempts write one safe audit row |
| Auth logs | Event name plus numeric IDs only | Useful operational evidence without credentials or tokens | Deeper correlation/structured logging remains hardening |
| D2 final | All required MVP audit rows included | The schema and services already support them | No audit-event deferral remains |

#### Tests I Added

- End-to-end presence of all 11 required audit event types.
- Auth and authorization log/response redaction for planted sensitive values.
- Existing unexpected-error redaction remains enforced.

Result: `116 passed, 1 existing warning`.

#### Manual Walkthrough

- Public: health and complete OpenAPI contract.
- Customer: login, `/auth/me`, account list/detail, both history feeds, CSRF rejection, deposit,
  withdrawal, transfer/detail, admin denial, logout, revoked-session rejection.
- Admin: login, dashboard, customer list/detail, customer-money denial, freeze/unfreeze,
  deactivate/activate.
- Integrity: all accounts reconciled and all required audit events existed.

#### Files I Changed

- `backend/app/services/audit_service.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/transfer_service.py`
- `backend/app/api/deps.py`
- `backend/app/main.py`
- `backend/tests/api/test_backend_audit.py`
- `backend/README.md`
- `docs/MY_WORKFLOW.md`
- `docs/PROGRESS.md`

#### Security or Reliability Considerations

- Permission-denied records contain numeric IDs/role names, never account numbers.
- Auth logs exclude emails, passwords, hashes, tokens, cookies, and headers.
- Correlation IDs and structured centralized logging remain explicitly scheduled hardening.
- The frontend contract is frozen at this checkpoint.

#### Technical Debt

- FastAPI's current TestClient integration emits one documented httpx deprecation warning.

#### Next Step

Stop at BACKEND-COMPLETE. Do not begin Phase 28 frontend work without explicit authorization.

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
| D5 | 2026-06-29 | Use synchronous SQLAlchemy sessions and database operations | SPEC §17; row locking for money path | Sync (rec, simpler `FOR UPDATE`); async | I chose synchronous SQLAlchemy because it keeps transaction boundaries, row locking, rollback behavior, and tests easier to follow without adding async complexity that the current requirements do not need. | Routes that perform blocking database work will use normal synchronous dependencies and services; the design favors clarity over the additional I/O concurrency available from an async stack. |
| D6 | 2026-06-29 | Use uv for Python environment and dependency management | IMPLEMENTATION_PLAN Phase 1; backend tooling and dependency workflow | uv; pip + `requirements.txt`; Poetry | I chose uv because it is already installed, uses the standard `pyproject.toml` format, and provides fast installs with a reproducible lockfile without the extra workflow complexity of Poetry. | I will manage the backend environment and dependencies with uv, commit `pyproject.toml` and `uv.lock`, and run Python tools through `uv run`. |
| D7 | 2026-06-29 | Run PostgreSQL 16 in Docker Compose with separate dev/test databases and a non-superuser app role | Phase 4 local database isolation | Homebrew PostgreSQL; Docker Compose | Compose gives the banking project a dedicated volume/network while explicit test URL checks protect development data. | FastAPI stays local; host 5433 maps to container 5432; the bootstrap admin is separate from `banking_user`; initialization runs only on an empty volume. |
| D8 | 2026-06-29 | Use integer primary keys, named domain enums, and no implicit ORM delete cascades | Phase 5 model design | Integer vs UUID; strings vs enums; cascades vs explicit retention | These choices keep the schema teachable while preserving domain validity and append-only history. | IDs remain enumerable and require strict authorization; enum changes need migrations; future deletions must be explicit. |
| D9 | 2026-06-29 | Resolve Alembic runtime URLs from settings and inject test URLs explicitly | Phase 6 migration safety | URL in config; process env override; Alembic config attribute | Credentials remain outside source control and migration tests cannot silently target development. | CLI commands require application settings; tests construct a dedicated Alembic config for the isolated database. |
| D10 | 2026-06-29 | Complete Phase 8 password hashing before Phase 7 seed data | Phase 7 requires Argon2id-hashed demo credentials | Hash inline and refactor; sequence Phase 8 first | Reusing one tested security primitive avoids temporary duplicate credential code. | M3 begins before M2 closes; after the Phase 8 commit, work returns to Phase 7 before Phase 9. |
| D11 | 2026-06-29 | Seed fixed synthetic users and varied reconciliation-safe history without deleting existing account activity | Phase 7 demo data | Minimal opening balances; delete/rebuild; create-once history | Stable natural keys and create-once history make reruns safe while preserving append-only transactions. | Public `.test` credentials are fixed; partial account-pair drift fails; full pre-submission reset would require an explicit destructive workflow. |
| D12 | 2026-06-29 | Generate 256-bit opaque tokens and store HMAC-SHA256 lookup hashes keyed by `SESSION_SECRET` | Phase 9 token storage | Plain SHA-256; concatenated pepper; HMAC-SHA256 | HMAC is a standard deterministic keyed construction that supports indexed lookup while limiting database-only compromise. | Raw tokens stay cookie-only; hashes are 64 hex characters; rotating `SESSION_SECRET` invalidates all sessions. |
| D13 | 2026-06-29 | Use enumeration-resistant login, host-prefixed auth cookies, and minimal cookie-only session output | Phase 10 login composition | Early unknown-user return; generic timing; normal vs host cookie; return user vs status | Dummy Argon2 work, generic envelopes, and `__Host-session` strengthen the first auth boundary without exposing raw tokens. | Domain cookies fall back to `session`; `/auth/me` supplies user state later; Phase 17 centralizes the envelope. |
| D14 | 2026-06-29 | Return a user/session principal, expire inclusively, and slide idle activity on every valid request | Phase 11 session resolution | User only vs principal; exclusive vs inclusive boundary; thresholded vs every request | The principal supports logout reuse, inclusive deadlines fail closed, and per-request sliding matches the approved plan. | Authenticated requests commit `last_used_at`; Phase 12 can revoke the resolved session directly. |
| D15 | 2026-06-29 | Require a valid principal for logout and atomically pair revocation with its audit | Phase 12 logout | Idempotent invalid logout; valid-only logout; separate vs shared commit | A concrete resolved session supports durable revocation proof and consistent audit history. | Invalid cookies return 401; both cookies are cleared only after revocation commits; Phase 13 adds CSRF. |
| D16 | 2026-06-29 | Use an explicit reusable CSRF dependency with constant-time comparison before authentication | Phase 13 mutation protection | Inline checks; global middleware; per-route dependency; auth-first vs CSRF-first | A named dependency keeps mutation protection visible and reusable, while early rejection avoids session activity from invalid cross-site requests. | Login and safe methods are exempt; every future POST/PATCH route must attach `CsrfProtected`; invalid unsafe requests receive 403 before authentication runs. |
| D17 | 2026-06-29 | Build parameterized SQL-backed role guards and expose named ADMIN/CUSTOMER aliases | Phase 14 role authorization | Separate guard functions; one factory; inline route checks | One factory prevents policy drift, while aliases keep each route's required role visible and return the already authenticated SQL user. | Client role input is ignored; mismatches share a 403 `FORBIDDEN` envelope; future protected routes must choose the appropriate alias. |
| D18 | 2026-06-29 | Filter customer account lookups by resource ID and authenticated owner ID in one query | Phase 15 ownership authorization | Load then compare; combined filter; route-local checks | A combined query keeps non-owned rows outside application logic and naturally gives missing and non-owned resources one 404 outcome. | Customer account routes use `OwnedAccount`; ADMIN cannot reuse customer ownership logic and needs separate admin queries. |
| D19 | 2026-06-29 | Use function-scoped authenticated role fixtures that call the real login route | Phase 16 security-suite consolidation | Mock principals; inject cookies; real seeded login; broader fixture scope | Real login preserves the SQL user, session, and cookie boundary while function scope prevents state leakage. | Authorization tests perform more Argon2/database work but remain realistic and isolated. |
| D20 | 2026-06-29 | Centralize typed domain errors and catch unexpected failures before server traceback logging | Phase 17 error boundary | Route-local responses; per-error handlers; outer exception handler; application middleware | One domain handler keeps contracts stable, while middleware prevents Uvicorn from logging raw secret-bearing exception messages. | Validation fields are sanitized; internal logs retain only exception type, method, and path until structured logging hardening. |
| D21 | 2026-06-29 | Publish account balances as two-decimal strings converted directly from `Decimal` | Phase 18 account reads | JSON number; serialized Decimal; schema-level string | A string contract is exact across JSON and JavaScript, and the schema advertises the representation clearly. | Frontend aggregation must use decimal-safe parsing; `user_id` remains omitted from customer responses. |
| D22 | 2026-06-29 | Use limit/offset pagination with default 20, maximum 100, and newest-first stable ordering | Phase 19 transaction history | Different page sizes; silent clamp; oldest/account-grouped/newest order | Bounded explicit validation limits work; `created_at DESC, id DESC` gives a useful feed and stable timestamp ties. | Invalid bounds return 422; offset pages can shift under concurrent inserts, so cursor pagination remains a future production option. |
| D23 | 2026-06-29 | Require decimal-string money input and re-lock owned accounts inside mutation services | Phase 20 deposit | JSON number vs string; mutate dependency row vs locked re-query | Exact strings prevent float drift; the locked query makes the balance read concurrency-safe. | Money requests reject floats and excess precision; mutations perform a second ownership-filtered lookup. |
| D24 | 2026-06-29 | Check withdrawal funds while holding the account row lock | Phase 21 withdrawal | Pre-lock validation; locked validation; database constraint only | Locked validation prevents concurrent requests from approving against one stale balance while returning a useful domain error. | Overdraw returns `INSUFFICIENT_FUNDS`; the database check remains a final backstop. |
| D25 | 2026-06-29 | Lock transfer accounts in ascending ID order and test rollback after flush | Phase 22 transfer | Request order; sorted order; shallow pre-flush failure; post-flush failure | Sorted locks avoid deadlocks; post-flush failure proves database atomicity after statements execute. | Transfer parent, balances, two legs, and audit share one commit and fully roll back together. |
| D26 | 2026-06-29 | Keep reconciliation test-only for the MVP and verify concurrency with independent PostgreSQL sessions | Phase 23 integrity verification | Admin endpoint; helper plus DB tests; sequential simulation | The MVP requires proof, not an admin feature; independent sessions exercise real row locks. | M4 closes with reconciliation and no-overdraft evidence without extension scope. |
| D27 | 2026-06-29 | Define recent dashboard activity as a 30-day transaction count and exclude ADMIN from customer totals | Phase 24 admin dashboard | All-time vs windowed activity; all users vs customers | Explicit semantics make aggregates testable and match the management domain. | Static seed may show zero recent rows; real activity updates the metric naturally. |
| D28 | 2026-06-29 | Keep admin customer drill-down queries separate from customer ownership dependencies | Phase 25 admin reads | Reuse `OwnedAccount`; dedicated admin queries | Admins need management visibility but must not become account owners. | Admin reads filter CUSTOMER identities directly and share only response/pagination contracts. |
| D29 | 2026-06-29 | Restrict account status controls to ACTIVE/FROZEN and atomically revoke sessions on deactivation | Phase 26 admin controls | Free-form status; reopen CLOSED; separate revocation/audit commits | A narrow state machine prevents accidental reopening; one transaction prevents active sessions surviving a recorded deactivation. | CLOSED requires a future explicit workflow; all status mutations require ADMIN plus CSRF. |
| D30 | 2026-06-29 | Complete D2 audit wiring and log only sanitized event names plus numeric identifiers | Phase 27 backend finalization | Defer audit gaps; route-local auditing; shared boundaries; rich log context | Shared boundaries prevent omissions, and excluding sensitive values by construction is safer than masking after interpolation. | All 11 MVP event types are present; correlation IDs and structured logging remain hardening. |

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

### Entry — 2026-06-29 — Phase 28: Frontend Foundation and Typed API Client

#### What I Worked On

I scaffolded the React/TypeScript Vite application and centralized browser requests in a typed
native-fetch client. The client always includes cookies, echoes the readable CSRF token only on
unsafe requests, maps the stable backend error envelope, and keeps API money as decimal strings.

#### Concepts I Learned

- The HttpOnly session cookie is intentionally invisible to JavaScript; `GET /auth/me` will be the
  only source of authenticated-user state.
- `bigint` integer cents can total formatted money without binary floating-point drift.
- A development proxy keeps `/api` relative in development and the production single-origin
  architecture.

#### Tests I Added

Vitest coverage proves credential and CSRF behavior, stable error mapping, exact money conversion
and addition, USD formatting, and safe form-value normalization.

#### Commands I Used

```bash
cd frontend
npm test -- --run
npm run lint
npm run typecheck
npm run build
npm run format:check
```

#### Security or Reliability Considerations

The frontend never reads or stores the session cookie, tokens, or trusted roles. Malformed error
responses collapse to safe wording, and all server money remains a decimal string at the API edge.

#### Next Step

Implement Phase 29 authentication state, login, guards, role navigation, and server-side logout.

---

### Entry — 2026-06-29 — Phase 29: Authentication Flow

Auth Context now resolves the current SQL-backed user through `/api/auth/me`, while login and
logout use the shared cookie/CSRF request boundary. Public, customer, and administrator routes
render role-specific navigation without treating frontend guards as authorization. Component tests
cover anonymous redirect, form validation, and customer navigation. Real-browser checks proved
customer login, logout, and administrator login against the running FastAPI/PostgreSQL stack.

---

### Entry — 2026-06-29 — Phase 30: Customer Dashboard

The customer dashboard loads only the authenticated customer's `/api/accounts`, renders responsive
accessible cards, masks account numbers to the last four digits, and totals decimal-string
balances through `bigint` cents. Tests cover loading, cards, and the exact `0.10 + 0.20 = 0.30`
case that binary floating point commonly mishandles.

---

### Entry — 2026-06-29 — Phase 31: Account Detail and Transaction History

Account detail loads the owned resource and its newest-first transaction page from separate
backend-authorized endpoints. Previous/next controls use the frozen `limit`/`offset` contract, and
the UI explicitly covers loading, empty, and safe error states.

---

### Entry — 2026-06-29 — Phase 32: Money Interfaces

Deposit, withdrawal, and transfer forms normalize user input without `Number` money arithmetic and
send every mutation through the CSRF-aware API client. Successful operations return to account
detail so both balance and append-only history refetch. Backend field/domain errors become concise
form messages; account activity, ownership, sufficient funds, and transfer atomicity remain server
rules.

---

### Entry — 2026-06-29 — Phase 33: Administrator Interface

The admin UI now displays exact aggregate statistics, lists safe customer identity fields, drills
into customer accounts, and offers activation/freeze controls. Every mutation uses CSRF and
refetches protected detail data after success. Browser verification used a real ADMIN session;
frontend role guards remain convenience controls over independently authorized API endpoints.

---

### Entry — 2026-06-29 — Phase 34: Consolidated Frontend Tests

The focused suite now covers authentication initialization and failure, guards and role navigation,
dashboard exact totals, history pagination, money normalization, mutation CSRF, same-account
validation, and administrator aggregates. I avoided duplicating service-level banking tests already
proved more strongly in the backend suite. All frontend static and production-build gates pass
without lint warnings.

---

### Entry — 2026-06-29 — Phase 35: End-to-End Happy Path

Playwright now exercises one real customer journey against Vite, FastAPI, and PostgreSQL. The test
does not destructively reset the developer database: it reads current demo balances, deposits
`10.00`, withdraws `5.00`, transfers `1.00`, and proves exact source/destination deltas plus the
new history types. Server readiness is checked automatically, while failure traces and screenshots
stay in ignored diagnostic directories.

The final regression pass produced 12 frontend tests, one Chromium E2E, and all 116 backend tests.
Formatting, linting, type-checking, production build, Ruff, and Alembic drift gates all passed. The
existing FastAPI TestClient/httpx deprecation warning remains the only known warning.

#### Next Step

Stop at the frontend/E2E-complete checkpoint. Phase 36 deployment work has not started.

---

### Entry — 2026-06-29 — Phase 36: Dockerize the Backend

#### What I Worked On

I created a multi-stage backend image from the locked uv dependencies and kept migrations outside
the web-process command. Compose now retains the original PostgreSQL-only workflow while adding a
one-shot `migrate` service and a health-checked backend service.

#### Architectural Fit and Decisions

The web image contains only application/runtime files and runs as the dedicated unprivileged
`banking` user. Containers use PostgreSQL's Compose service name instead of host `localhost`.
`alembic upgrade head` must complete before the API starts; keeping it as a deploy job avoids
multiple replicas racing to migrate. Secrets remain runtime environment values from the ignored
root `.env`, never image layers.

#### Problems I Encountered

Docker's local credential helper hung while resolving public images. I diagnosed it by isolating a
direct pull, then used an empty temporary Docker client configuration for anonymous public-image
pulls. The first container start also found the Phase 35 Uvicorn process still holding port 8000;
I stopped only that stale process and preserved PostgreSQL plus all developer data.

#### Verification

- Compose configuration parsed successfully.
- The locked backend image built to 65 MB for `linux/arm64`.
- The migration service completed successfully against the existing development database.
- The backend health check became healthy and `/api/health` returned `{"status":"ok"}`.
- Container identity was `uid=100(banking) gid=101(banking)`.
- Ruff format/lint passed; all 116 backend tests passed with the one documented warning; Alembic
  reported no schema drift.

#### Files I Changed

- `backend/Dockerfile`
- `backend/.dockerignore`
- `compose.yaml`
- `backend/README.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/PROGRESS.md`
- `docs/MY_WORKFLOW.md`

#### Next Step

Commit Phase 36, then implement Phase 37 with the recorded nginx D3 decision. Do not start M13 or
M14.

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
