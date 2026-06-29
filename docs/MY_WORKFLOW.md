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
