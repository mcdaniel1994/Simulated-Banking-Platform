import { expect, test, type Page } from "@playwright/test";

async function login(page: Page, role: "customer" | "administrator") {
  await page.goto("/login");
  await page
    .getByRole("button", {
      name: role === "customer" ? /Customer access/ : /Administrator access/,
    })
    .click();
  await page.getByRole("button", { name: "Log in" }).click();
}

async function expectNoPageOverflow(page: Page) {
  expect(
    await page.evaluate(
      () =>
        document.documentElement.scrollWidth <=
        document.documentElement.clientWidth,
    ),
  ).toBe(true);
}

async function openResponsiveNavigation(page: Page) {
  const menuButton = page.getByRole("button", {
    name: "Open navigation menu",
  });
  if (await menuButton.isVisible()) {
    await menuButton.click();
    await expect(
      page.getByRole("button", { name: "Close navigation menu" }),
    ).toHaveAttribute("aria-expanded", "true");
  }
}

test("customer layout remains usable without browser-stored auth state", async ({
  page,
}) => {
  await login(page, "customer");
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(
    page.getByRole("heading", { name: "Accounts", exact: true }),
  ).toBeVisible();
  await expect(page.locator("[data-account-id]")).toHaveCount(2);
  await expectNoPageOverflow(page);

  await openResponsiveNavigation(page);
  await expect(
    page.getByRole("link", { name: "Accounts" }).last(),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => localStorage.length === 0 && sessionStorage.length === 0,
    ),
  ).toBe(true);
});

test("administrator can inspect responsive management UI without mutation", async ({
  page,
}) => {
  await login(page, "administrator");
  await expect(page).toHaveURL(/\/admin$/);
  await expect(
    page.getByRole("heading", { name: "Banking activity" }),
  ).toBeVisible();
  await expectNoPageOverflow(page);

  await openResponsiveNavigation(page);
  await page.getByRole("link", { name: "Manage customers" }).last().click();
  await expect(page).toHaveURL(/\/admin\/customers$/);
  await expect(
    page.getByRole("heading", { name: "Manage customers" }),
  ).toBeVisible();
  await expectNoPageOverflow(page);

  await page.getByRole("link", { name: /View Alex Carter/ }).click();
  await expect(
    page.getByRole("heading", { name: "Recent transactions" }),
  ).toBeVisible();
  await expectNoPageOverflow(page);

  await page.getByRole("button", { name: "Deactivate customer" }).click();
  const dialog = page.getByRole("alertdialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole("button", { name: "Cancel" })).toBeFocused();
  await dialog.getByRole("button", { name: "Cancel" }).click();
  await expect(dialog).toBeHidden();
});
