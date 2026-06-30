import { expect, test } from "@playwright/test";

function cents(value: string): bigint {
  const [whole, fraction] = value.split(".");
  return BigInt(whole) * 100n + BigInt(fraction);
}

test("customer login and exact money happy path", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("alex.customer@demo.bank.test");
  await page.getByLabel("Password").fill("CustomerDemo!2026");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  // Read current state instead of destructively resetting the developer database.
  const cards = page.locator("[data-account-id]");
  await expect(cards).toHaveCount(2);
  const sourceId = await cards.nth(0).getAttribute("data-account-id");
  const destinationId = await cards.nth(1).getAttribute("data-account-id");
  const sourceBefore = await cards.nth(0).getAttribute("data-balance");
  const destinationBefore = await cards.nth(1).getAttribute("data-balance");
  expect(
    sourceId && destinationId && sourceBefore && destinationBefore,
  ).toBeTruthy();

  await page.goto(`/accounts/${sourceId}/deposit`);
  await page.getByLabel("Amount (USD)").fill("10.00");
  await page.getByRole("button", { name: "Add demo funds" }).click();
  await expect(page.getByTestId("account-balance")).toHaveAttribute(
    "data-balance",
    `${(cents(sourceBefore!) + 1000n) / 100n}.${((cents(sourceBefore!) + 1000n) % 100n).toString().padStart(2, "0")}`,
  );

  await page.goto(`/accounts/${sourceId}/withdraw`);
  await page.getByLabel("Amount (USD)").fill("5.00");
  await page.getByRole("button", { name: "Withdraw" }).click();

  await page.goto("/transfer");
  await page.getByLabel("From").selectOption(sourceId!);
  await page.getByLabel("To").selectOption(destinationId!);
  await page.getByLabel("Amount (USD)").fill("1.00");
  await page.getByRole("button", { name: "Transfer" }).click();

  await expect(page.getByTestId("account-balance")).toHaveAttribute(
    "data-balance",
    `${(cents(sourceBefore!) + 400n) / 100n}.${((cents(sourceBefore!) + 400n) % 100n).toString().padStart(2, "0")}`,
  );
  const history = page.getByRole("list", { name: "Transaction history" });
  await expect(history).toContainText("DEPOSIT");
  await expect(history).toContainText("WITHDRAWAL");
  await expect(history).toContainText("TRANSFER_OUT");

  await page.goto(`/accounts/${destinationId}`);
  await expect(page.getByTestId("account-balance")).toHaveAttribute(
    "data-balance",
    `${(cents(destinationBefore!) + 100n) / 100n}.${((cents(destinationBefore!) + 100n) % 100n).toString().padStart(2, "0")}`,
  );
});
