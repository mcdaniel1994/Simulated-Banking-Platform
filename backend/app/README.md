# Application Package Guide

The `app` package will contain the backend's executable application code. It is divided by
responsibility so HTTP concerns, business rules, and persistence concerns do not collapse into
the same files.

## Package Responsibilities

| Package | What Belongs Here | What Does Not Belong Here |
|---|---|---|
| `api/` | Shared FastAPI dependencies and route organization | Banking business rules or direct balance mutations |
| `api/routes/` | Thin endpoint handlers that validate input, call services, and shape responses | SQL queries or multi-step transactions |
| `core/` | Environment-backed configuration and security utilities | Feature-specific business behavior |
| `db/` | SQLAlchemy base, engine, session factory, and request-scoped database dependency | Route handlers or banking rules |
| `models/` | SQLAlchemy models, relationships, indexes, and database constraints | Pydantic request and response validation |
| `repositories/` | Small reusable query helpers when a query is shared or complex | A full repository class for every model |
| `schemas/` | Pydantic request and response models | ORM persistence logic |
| `services/` | Business rules, authorization-sensitive operations, row locking, and atomic transactions | HTTP-specific response construction |

The following files will be added only when their implementation phase begins:

| File | Future Responsibility |
|---|---|
| `main.py` | Create the FastAPI application and include routers |
| `errors.py` | Map domain errors into the common API error envelope |
| `seed.py` | Create deterministic, idempotent demonstration data |

## Dependency Direction

```text
api/routes
  -> api dependencies and schemas
  -> services
  -> repositories when useful
  -> db and models
```

The important boundary is the service layer. For example, a future transfer route should not debit
accounts itself. It should validate the HTTP request, resolve the authenticated customer, and call
a transfer service. The service will verify ownership and account status, lock both rows in a
consistent order, write both transaction entries, and commit everything atomically.

## Rules I Want to Preserve

- Keep FastAPI routes thin.
- Validate API input with Pydantic schemas.
- Keep business rules and transaction boundaries in services.
- Use repositories only for justified query reuse or complexity.
- Use `Decimal`, never floating-point values, for money.
- Enforce authorization and ownership on the backend.
- Never log passwords, session tokens, cookies, or secrets.
- Add tests alongside each behavior rather than postponing testing.
