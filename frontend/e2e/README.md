# Browser E2E

The Playwright happy path uses the local PostgreSQL development database without dropping,
truncating, or reseeding it. It reads the current two demo-account balances and asserts exact
balance deltas plus new transaction types after a small deposit, withdrawal, and transfer.

Start PostgreSQL once from the repository root, then run the browser suite from `frontend/`:

```bash
docker compose up -d postgres
npm run test:e2e
```

Playwright starts or reuses readiness-checked FastAPI and Vite servers. On failure it retains a
trace and screenshot under ignored report directories so diagnostics never pollute commits.
