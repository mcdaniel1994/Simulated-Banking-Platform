# CS50x Demo Video Plan

The application is live at `https://bank.forgehub.cloud/login`. The completed public demo video is
available at `https://youtu.be/Lkm8cpRFk90`. The published link was verified reachable without an
authenticated YouTube session.

## Recording Layout

1. Start with [`intro.md`](intro.md) rendered full-screen for approximately 12 seconds.
2. Switch to a side-by-side layout:
   - **Left:** Northstar Bank in a private browser window.
   - **Right:** Supabase Table Editor showing only synthetic account and transaction data.
3. Before recording, filter Supabase to the seeded customer/account rows used in the demo.
4. Keep both sides large enough to read; browser zoom around 80–90% may help.

### Supabase Safety Boundary

- Show only the `accounts` and `transactions` tables needed to prove live persistence.
- Do not open `users`, `sessions`, or configuration screens. Those surfaces contain password or
  session hashes and operational metadata that do not belong in a public video.
- Never show Project Settings, the Connect dialog, API keys, database URLs/passwords, cookies,
  request headers, environment variables, or terminal output containing secrets.
- Use only the public synthetic demo identities and simulated balances.
- Refresh the filtered table after an application action so the relevant balance or transaction
  row visibly changes.

## Suggested Script and Screen Actions

**0:00–0:12 — Opening card**

Display `docs/intro.md` full-screen. No narration is required beyond briefly introducing the
project.

**0:12–0:30 — Product and architecture**

“Northstar Bank is a simulated banking platform built as my CS50x final project. The React and
TypeScript interface shares one secure HTTPS origin with a FastAPI backend, while PostgreSQL on
Supabase stores accounts, transactions, transfers, sessions, and audit records.”

Switch to the split-screen layout. Keep the application login page on the left and a filtered
Supabase `accounts` view on the right.

**0:30–1:35 — Customer flow with live persistence**

1. Use the public customer credentials shown on the login page.
2. Show the account cards and combined balance.
3. Open one account and briefly show transaction history.
4. Add a small amount, withdraw a smaller amount, and transfer between the two owned accounts.
5. Refresh the filtered Supabase `accounts` view to show the exact balance changes.
6. Switch the right side to the filtered `transactions` table and refresh it to show the new
   `DEPOSIT`, `WITHDRAWAL`, `TRANSFER_OUT`, and `TRANSFER_IN` rows.
7. Say: “Money uses exact decimal values, and the backend locks account rows so these changes stay
   atomic and consistent.”
8. Log out.

**1:35–2:20 — Administrator workflow and security boundary**

1. Log in with the public administrator credentials.
2. Show the aggregate dashboard and Manage Customers page.
3. Open the Add Customer form and customer detail/status controls. Do not submit another customer
   unless you intentionally want a permanent additional synthetic record.
4. Say: “The backend—not the browser—enforces administrator roles, account ownership, CSRF
   protection, and immediate server-side session revocation. Passwords are hashed with Argon2id.”
5. Log out.

**2:20–2:50 — Integrity and verification**

“Transfers update both balances and both transaction legs in one database transaction. The test
suite covers rollback, concurrent withdrawals, reconciliation, authorization, CSRF, secret
redaction, responsive interfaces, and real-browser workflows. The deployed application writes
through Coolify to Supabase over TLS.”

**2:50–3:00 — Close**

“Northstar Bank is a simulation and provides no real funds or financial services. The project is
live at bank.forgehub.cloud.”

## Recording Checklist

The video is published. Unchecked content items remain a final self-review checklist before
submitting to CS50x.

- [x] Deploy the refreshed application to the trusted HTTPS URL.
- [x] Complete the required opening card in `docs/intro.md`.
- [ ] Confirm the seeded customer is active and both demo accounts are active.
- [ ] Arrange the private application window on the left and safe Supabase tables on the right.
- [ ] Filter Supabase to synthetic `accounts` and `transactions` rows before recording.
- [ ] Close unrelated tabs and hide all configuration, credentials, hashes, tokens, and secrets.
- [ ] Keep the final recording at or below 3:00.
- [ ] Demonstrate login, balances, history, add funds, withdrawal, transfer, and logout.
- [ ] Demonstrate administrator dashboard, customer management, and logout.
- [ ] Show the resulting safe balance/transaction changes in Supabase.
- [ ] State the simulation/no-real-funds disclosure verbally or visibly.
- [x] Upload to YouTube as public or unlisted, not private.
- [x] Paste the final URL into the `Video Demo` line in `README.md`.
- [x] Verify the published URL is reachable while signed out.
