# Submission Acceptance Evidence

Evidence was reviewed on 2026-06-29 against all 15 criteria in `SPEC.md` §21. “Satisfied” means the
repository tests and/or local verification prove the criterion. “Blocked” means an external action
is still required and is not being represented as complete.

| # | Status | Concrete evidence |
|---|---|---|
| 1 | Satisfied locally | Backend auth tests verify customer/admin login and `HttpOnly`, `Secure`, `SameSite=Strict` session cookies. The local HTTPS production smoke verified both roles and cookie attributes in Chromium. |
| 2 | Satisfied | Account/history API tests and the customer Playwright happy path verify accounts, balances, pagination, deposit, withdrawal, transfer, and exact balance deltas. |
| 3 | Satisfied | Withdrawal and transfer tests assert `INSUFFICIENT_FUNDS` and unchanged balances/history/audits. |
| 4 | Satisfied | Deposit/withdrawal/transfer status tests reject frozen/closed accounts; transfer tests reject identical accounts. |
| 5 | Satisfied | The induced post-flush transfer failure test proves both balances, parent, legs, and audit row roll back. |
| 6 | Satisfied | The PostgreSQL concurrency test runs two independent withdrawals; only one succeeds, final balance stays nonnegative, and the database check constraint is exercised. |
| 7 | Satisfied | Seed and reconciliation tests compare every stored balance with signed append-only history after money mutations. |
| 8 | Satisfied | Ownership tests return the same 404 for missing/non-owned accounts; role tests return 403 when a customer enters admin routes. |
| 9 | Satisfied | Auth tests reuse the same cookie after logout and receive 401; admin deactivation tests prove all active customer sessions are revoked. |
| 10 | Satisfied | CSRF tests reject missing/mismatched tokens with `CSRF_INVALID` and accept a matching cookie/header pair. |
| 11 | Satisfied | Admin API/UI tests cover list, detail, deactivate/reactivate, freeze/unfreeze, CSRF, and the rule that admins are not account owners. |
| 12 | Satisfied | Error/audit tests enforce the common envelope, decimal-string money, sanitized validation, and absence of tokens, cookies, credentials, SQL, account numbers, and sensitive headers in errors/logs. |
| 13 | **Blocked externally** | nginx/Compose/TLS/Supabase templates exist; local HTTPS single-origin migration/seed/API/browser smoke passes. A real DNS name, VPS, trusted certificate, and Supabase pooler credentials were unavailable, so no live deployment is claimed. |
| 14 | Satisfied | Full backend suite: 116 passed with one documented dependency warning. Frontend: 12 passed. Customer happy-path E2E: 1 passed. Local production HTTPS smoke: 2 passed. |
| 15 | **Blocked externally** | Root README, design/trade-offs, install/deploy docs, and AI disclosure exist. The required at-most-three-minute video has a complete script/checklist but has not been recorded or uploaded. |

## External Actions Required

### Criterion 13

1. Obtain a domain and point DNS at the VPS.
2. Install Docker/Compose on the VPS and clone this repository.
3. Create an ignored `.env.production` using `.env.production.example`.
4. Supply the Supabase pooler URL/password, a random production session secret, and trusted
   certificate/key host paths.
5. Follow `docs/DEPLOYMENT.md` to build, migrate, seed, and start backend/nginx.
6. Run `PRODUCTION_BASE_URL=https://REAL_DOMAIN npm run test:e2e:production`.
7. Record the live URL, cookie inspection, Supabase migration revision, and smoke results here.

### Criterion 15

1. Fill the personal placeholders in `docs/DEMO_VIDEO.md`.
2. Record a video no longer than three minutes using the checklist.
3. Upload it as public or unlisted, verify signed-out access, and add its URL to `README.md`.

## Submission Decision

**Not all 15 criteria are satisfied.** Criteria 13 and 15 remain blocked by external deployment
access/values and the user's recording/upload action. Do not submit or describe the project as
fully complete until both are evidenced.
