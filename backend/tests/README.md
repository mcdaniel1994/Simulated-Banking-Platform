# Backend Test Guide

The backend test suite is organized by the kind of behavior being verified. Tests should focus on
observable rules and outcomes rather than locking the project to internal implementation details.

## Test Directories

| Path | Purpose | Example |
|---|---|---|
| `unit/` | Small, isolated functions without database or HTTP dependencies | Password hashing or session-token utilities |
| `service/` | Business rules and transaction behavior through the service layer | Withdrawal rejection or transfer rollback |
| `api/` | HTTP contracts using a FastAPI test client | Login cookies, authorization responses, or error envelopes |
| `db/` | PostgreSQL models, constraints, migrations, and concurrency behavior | Non-negative balance constraint or row locking |

`conftest.py` will be added when shared fixtures are needed. It will eventually provide test
database sessions, seeded users and accounts, authenticated clients, and cleanup between tests.

## What Each Feature Should Test

For every feature, consider:

- Successful behavior
- Input validation failures
- Authentication and role failures
- Resource-ownership violations
- Boundary values
- Database rollback behavior
- Security-sensitive behavior
- Relevant concurrency risks

Money operations require extra care. Tests must prove that balances cannot become negative, failed
operations do not partially commit, concurrent requests cannot cause lost updates, and stored
balances reconcile with the append-only transaction history.

## Test Boundaries

- Unit tests should not use a real database merely to test a pure function.
- Service tests should verify business rules without depending on browser behavior.
- API tests should verify status codes, response shapes, cookies, CSRF, and authorization.
- Database and concurrency tests must use PostgreSQL rather than SQLite when PostgreSQL behavior is
  part of the requirement.
- Tests must never connect to the production database.

## Commands

Run the full backend suite from `backend/`:

```bash
uv run pytest
```

Database tests load the ignored root `.env` and require both `DATABASE_URL` and
`TEST_DATABASE_URL`. The URLs must be different, and the test URL must target the isolated
`simulated_banking_test` database. Missing or unsafe configuration fails the suite rather than
skipping database tests or falling back to development.

Later phases may use targeted commands such as:

```bash
uv run pytest tests/api/test_auth.py -q
uv run pytest -k reconciliation -q
```

Phase 4 adds PostgreSQL integration coverage for connectivity, dependency cleanup, rollback, and
development/test database isolation.
