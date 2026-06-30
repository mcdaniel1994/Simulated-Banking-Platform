import { expect, test, type BrowserContext } from "@playwright/test";

async function expectSecureSessionCookie(context: BrowserContext) {
  const sessionCookie = (await context.cookies()).find(
    (cookie) => cookie.name === "__Host-session",
  );
  expect(sessionCookie).toMatchObject({
    httpOnly: true,
    secure: true,
    sameSite: "Strict",
    path: "/",
  });
}

test("customer uses and revokes a session through the HTTPS origin", async ({
  context,
  page,
}) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("alex.customer@demo.bank.test");
  await page.getByLabel("Password").fill("CustomerDemo!2026");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expectSecureSessionCookie(context);

  const cards = page.locator("[data-account-id]");
  await expect(cards).toHaveCount(2);
  const accountId = await cards.nth(0).getAttribute("data-account-id");
  const balanceBefore = await cards.nth(0).getAttribute("data-balance");
  expect(accountId && balanceBefore).toBeTruthy();

  // One cent proves the protected mutation path while minimizing demo-data drift.
  await page.goto(`/accounts/${accountId}/deposit`);
  await page.getByLabel("Amount (USD)").fill("0.01");
  await page.getByRole("button", { name: "Add funds" }).click();
  await expect(page.getByTestId("account-balance")).not.toHaveAttribute(
    "data-balance",
    balanceBefore!,
  );

  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/login$/);
  expect((await page.request.get("/api/auth/me")).status()).toBe(401);
});

test("administrator reaches the protected dashboard and logs out", async ({
  context,
  page,
}) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("admin@demo.bank.test");
  await page.getByLabel("Password").fill("AdminDemo!2026");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/admin$/);
  await expect(
    page.getByRole("heading", { name: "Banking activity" }),
  ).toBeVisible();
  await expectSecureSessionCookie(context);

  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/login$/);
  expect((await page.request.get("/api/auth/me")).status()).toBe(401);
});
