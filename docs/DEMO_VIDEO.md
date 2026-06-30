# CS50x Demo Video Plan

No demo video has been recorded or uploaded yet. This document is a ready-to-use script and
checklist; replace every bracketed placeholder before recording.

The current CS50x 2026 instructions require a video no longer than three minutes. Its opening must
display the project title, your name, GitHub and edX usernames, city/country, and recording date.
The upload may be public or unlisted, but not private.

## Opening Card (0:00–0:12)

- Project: **Northstar Learning Bank**
- Name: `[YOUR NAME]`
- GitHub username: `[YOUR GITHUB USERNAME]`
- edX username: `[YOUR EDX USERNAME]`
- Location: `[CITY, COUNTRY]`
- Recorded: `[YYYY-MM-DD]`
- Disclaimer: **Educational simulation only—no real money or banking data**

## Suggested Script

**0:12–0:30 — Problem and architecture**

“Northstar Learning Bank is a simulated banking platform built to demonstrate the engineering
concerns behind secure financial software. A React and TypeScript SPA shares one HTTPS origin with
a FastAPI API behind nginx. PostgreSQL stores users, hashed server-side sessions, accounts,
append-only transactions, transfers, and audit events.”

**0:30–1:35 — Customer flow**

1. Show the login page and public demo credentials.
2. Log in as `alex.customer@demo.bank.test`.
3. Show the two account cards and combined balance.
4. Open an account and show paginated history.
5. Add a small amount of demo funding.
6. Withdraw a smaller amount.
7. Transfer between the customer's two accounts.
8. Show updated balances and DEPOSIT/WITHDRAWAL/TRANSFER history.
9. Mention that amounts are exact decimal strings and the backend locks rows atomically.
10. Log out.

**1:35–2:20 — Administrator and security boundaries**

1. Log in as `admin@demo.bank.test`.
2. Show aggregate dashboard statistics and the customer list/detail.
3. Briefly show customer activation and account freeze controls without leaving the demo user in
   an unusable state.
4. Explain that roles and ownership come from PostgreSQL; frontend guards are not trusted.
5. Mention HttpOnly server-side sessions, immediate revocation, strict cookies, double-submit
   CSRF, Argon2id password hashing, 404 anti-IDOR behavior, and no real customer data.
6. Log out.

**2:20–2:50 — Integrity and testing**

“Transfers write both account changes and both ledger legs in one transaction. Tests induce a
mid-transfer failure, race concurrent withdrawals, reconcile every balance with history, verify
CSRF and ownership, and scan errors/logs for sensitive data. The suite includes backend,
component, and real-browser end-to-end coverage.”

**2:50–3:00 — Close**

“This project is an educational simulation, not a real bank. The design prioritizes a small,
auditable security boundary and leaves production hardening as deliberate post-submission work.”

## Recording Checklist

- [ ] Deploy to the real trusted HTTPS URL or prepare a stable local demonstration.
- [ ] Reseed immediately before recording; do not destructively reset unrelated data.
- [ ] Restore the customer to active and both demo accounts to active.
- [ ] Close unrelated apps/tabs and hide terminals containing environment variables.
- [ ] Display the complete required opening card.
- [ ] Keep the final recording at or below 3:00.
- [ ] Demonstrate customer login, dashboard, history, deposit, withdrawal, transfer, and logout.
- [ ] Demonstrate admin login, dashboard, customer detail/status controls, and logout.
- [ ] State the simulated-money disclaimer verbally or visibly.
- [ ] Do not display cookies, session tokens, database URLs, passwords beyond public demo
  credentials, environment files, or sensitive headers.
- [ ] Upload to YouTube as public or unlisted (not private).
- [ ] Paste the final URL into the `Video Demo` line in `README.md`.
- [ ] Watch the uploaded video end-to-end while signed out to verify reviewer access.
