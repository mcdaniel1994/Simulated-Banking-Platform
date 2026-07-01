# Submission Acceptance Evidence

Evidence was reviewed through 2026-06-30 against all 15 criteria in `SPEC.md` §21. “Satisfied”
means repository tests, local verification, and/or the live deployment prove the criterion.
“Blocked” means an external action is still required and is not being represented as complete.

| # | Status | Concrete evidence |
|---|---|---|
| 1 | Satisfied | Backend tests and the trusted production smoke verify customer/admin login and `HttpOnly`, `Secure`, `SameSite=Strict` session cookies. |
| 2 | Satisfied | Account/history API tests and the customer Playwright happy path verify accounts, balances, pagination, deposit, withdrawal, transfer, and exact balance deltas. |
| 3 | Satisfied | Withdrawal and transfer tests assert `INSUFFICIENT_FUNDS` and unchanged balances/history/audits. |
| 4 | Satisfied | Deposit/withdrawal/transfer status tests reject frozen/closed accounts; transfer tests reject identical accounts. |
| 5 | Satisfied | The induced post-flush transfer failure test proves both balances, parent, legs, and audit row roll back. |
| 6 | Satisfied | The PostgreSQL concurrency test runs two independent withdrawals; only one succeeds, final balance stays nonnegative, and the database check constraint is exercised. |
| 7 | Satisfied | Seed and reconciliation tests compare every stored balance with signed append-only history after money mutations. |
| 8 | Satisfied | Ownership tests return the same 404 for missing/non-owned accounts; role tests return 403 when a customer enters admin routes. |
| 9 | Satisfied | Auth tests reuse the same cookie after logout and receive 401; admin deactivation tests prove all active customer sessions are revoked. |
| 10 | Satisfied | CSRF tests reject missing/mismatched tokens with `CSRF_INVALID` and accept a matching cookie/header pair. |
| 11 | Satisfied | Admin API/UI tests cover customer creation, list/detail, deactivate/reactivate, freeze/unfreeze, CSRF, and the rule that admins are not account owners. The creation flow was also verified through the deployed UI and Supabase. |
| 12 | Satisfied | Error/audit tests enforce the common envelope, decimal-string money, sanitized validation, and absence of tokens, cookies, credentials, SQL, account numbers, and sensitive headers in errors/logs. |
| 13 | Satisfied | `https://bank.forgehub.cloud` serves the SPA and API through trusted HTTPS. Coolify deployed commit `71a9689`; migration and seed completed; the private backend and gateway are healthy; writes persist through the TLS Supabase pooler. |
| 14 | Satisfied | Full backend suite: 122 passed with one documented dependency warning. Frontend: 21 passed. Customer happy-path E2E: 1 passed. Responsive desktop/mobile suite: 4 passed. Trusted production smoke: 2 passed. |
| 15 | Satisfied | Root README, design/trade-offs, install/deploy docs, and AI disclosure exist. The public demo video is linked at `https://youtu.be/Lkm8cpRFk90`, and the URL was verified reachable while signed out. |

## Final Submission Action

All repository, deployment, verification, and video acceptance evidence is complete. The remaining
action is to review the published video once and submit the project through the CS50x submission
workflow.

## Submission Decision

**All 15 acceptance criteria are satisfied.** The project is ready for final CS50x submission.
This statement does not claim that the external submission form has already been sent.
