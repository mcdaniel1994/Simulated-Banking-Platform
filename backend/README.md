# Backend Guide

This directory contains the FastAPI backend for the simulated banking platform. Its job is to
enforce authentication, authorization, banking rules, transaction integrity, and data access.
The React frontend will call this backend through the `/api` path, but the backend remains the
security boundary and never relies on the frontend to enforce permissions.

The requirements come from [`SPEC.md`](../SPEC.md), and the implementation order comes from
[`docs/IMPLEMENTATION_PLAN.md`](../docs/IMPLEMENTATION_PLAN.md).

## Directory Map

| Path | Purpose |
|---|---|
| `app/` | Application packages and, later, the FastAPI entry point |
| `tests/` | Unit, service, API, and database tests |
| `pyproject.toml` | Python version, dependencies, and tool configuration |
| `uv.lock` | Exact dependency versions used for reproducible installs |
| `.venv/` | Local virtual environment; never committed |
| `alembic/` | Database migration environment, added in Phase 6 |
| `alembic.ini` | Alembic configuration, added in Phase 6 |
| `Dockerfile` | Production image definition, added in Phase 36 |

## How a Request Will Move Through the Backend

```text
HTTP request
  -> FastAPI route
  -> Pydantic request schema
  -> authentication, CSRF, role, and ownership dependencies
  -> application service
  -> lightweight query helper when useful
  -> SQLAlchemy session
  -> PostgreSQL
  -> Pydantic response schema
```

Each layer has a distinct responsibility:

- Routes translate HTTP requests and responses.
- Schemas validate external data.
- Dependencies establish who is making the request and what they may access.
- Services enforce business rules and transaction boundaries.
- Query helpers keep reusable database queries out of services without hiding business logic.
- Models describe persisted data and database relationships.

Dependencies should generally point inward toward services and persistence. Database models should
not import API routes, and services should not depend on frontend behavior.

## Development Commands

Create a local environment file from the safe template before running configuration-dependent code:

```bash
cp ../.env.example ../.env
```

Replace the placeholder database credentials and session secret in `.env`. The real file is
git-ignored and must never be committed.

Run backend commands from this directory:

```bash
uv sync
uv run ruff format --check app tests
uv run ruff check app tests
uv run pytest
```

The test suite is currently empty, so pytest exits with code `5` until the first behavior test is
added in Phase 2.

## Current State

Phase 1 establishes only the package structure and development tooling. The empty packages are
intentional. Application behavior will be added one phase at a time according to the implementation
plan.
