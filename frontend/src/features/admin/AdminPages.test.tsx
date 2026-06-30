import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import {
  AdminDashboardPage,
  CustomerDetailPage,
  CustomerListPage,
} from "./AdminPages";

const customer = {
  id: 7,
  email: "jordan@example.test",
  first_name: "Jordan",
  last_name: "Lee",
  is_active: true,
  created_at: "2025-05-12T12:00:00Z",
};

const checking = {
  id: 11,
  account_number: "0003",
  account_type: "CHECKING",
  balance: "2175.01",
  status: "ACTIVE",
  created_at: "2025-05-12T12:00:00Z",
  updated_at: "2025-05-12T12:00:00Z",
};

const closedSavings = {
  ...checking,
  id: 12,
  account_number: "0004",
  account_type: "SAVINGS",
  balance: "0.00",
  status: "CLOSED",
};

const detail = {
  customer,
  accounts: [checking, closedSavings],
  transactions: [
    {
      id: 20,
      account_id: 11,
      transaction_type: "DEPOSIT",
      amount: "500.00",
      description: "Initial deposit",
      balance_after: "2175.01",
      reference_id: null,
      created_at: "2025-05-12T15:24:00Z",
    },
  ],
  transaction_limit: 10,
  transaction_offset: 0,
};

it("renders exact administrator aggregates", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    Response.json({
      customer_count: 2,
      account_count: 4,
      total_simulated_balance: "1000.10",
      recent_transaction_count: 3,
      recent_window_days: 30,
    }),
  );
  render(
    <MemoryRouter>
      <AdminDashboardPage />
    </MemoryRouter>,
  );
  expect(await screen.findByText("$1,000.10")).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Manage customers" }),
  ).toBeInTheDocument();
});

it("renders responsive customer identity and status controls", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(Response.json([customer]));
  render(
    <MemoryRouter>
      <CustomerListPage />
    </MemoryRouter>,
  );

  expect(await screen.findByText("Jordan Lee")).toBeInTheDocument();
  expect(screen.getByText("jordan@example.test")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "View Jordan Lee" })).toHaveAttribute(
    "href",
    "/admin/customers/7",
  );
});

it("renders returned transactions and confirms an account status mutation", async () => {
  document.cookie = "csrf_token=admin-csrf; Path=/";
  const refetchedDetail = {
    ...detail,
    accounts: [{ ...checking, status: "FROZEN" }, closedSavings],
  };
  const fetchMock = vi
    .spyOn(globalThis, "fetch")
    .mockResolvedValueOnce(Response.json(detail))
    .mockResolvedValueOnce(Response.json({ ...checking, status: "FROZEN" }))
    .mockResolvedValueOnce(Response.json(refetchedDetail));
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={["/admin/customers/7"]}>
      <Routes>
        <Route
          path="/admin/customers/:userId"
          element={<CustomerDetailPage />}
        />
      </Routes>
    </MemoryRouter>,
  );

  expect(await screen.findAllByText("Initial deposit")).toHaveLength(2);
  expect(screen.getAllByText("+$500.00")).toHaveLength(2);
  expect(screen.getByRole("button", { name: "Account closed" })).toBeDisabled();

  const freezeButton = screen.getByRole("button", {
    name: "Freeze account",
  });
  await user.click(freezeButton);
  expect(screen.getByRole("alertdialog")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Cancel" })).toHaveFocus();

  await user.keyboard("{Escape}");
  expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument();
  expect(freezeButton).toHaveFocus();

  await user.click(freezeButton);
  await user.click(
    within(screen.getByRole("alertdialog")).getByRole("button", {
      name: "Freeze account",
    }),
  );

  expect(await screen.findByText("Account frozen.")).toBeInTheDocument();
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
  const mutationInit = fetchMock.mock.calls[1][1]!;
  expect(mutationInit.body).toBe(JSON.stringify({ status: "FROZEN" }));
  expect(new Headers(mutationInit.headers).get("X-CSRF-Token")).toBe(
    "admin-csrf",
  );
});
