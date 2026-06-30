import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import {
  AdminDashboardPage,
  CreateCustomerPage,
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
  expect(screen.getByRole("link", { name: "Add customer" })).toHaveAttribute(
    "href",
    "/admin/customers/new",
  );
});

it("keeps customer creation available when the list is empty", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(Response.json([]));
  render(
    <MemoryRouter>
      <CustomerListPage />
    </MemoryRouter>,
  );

  expect(await screen.findByText("No customers found")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Add customer" })).toHaveAttribute(
    "href",
    "/admin/customers/new",
  );
});

it("validates confirmation and creates a customer with CSRF", async () => {
  document.cookie = "csrf_token=create-customer-csrf; Path=/";
  const createdCustomer = {
    ...customer,
    id: 9,
    email: "morgan@example.test",
    first_name: "Morgan",
    last_name: "Rivera",
  };
  const createdDetail = {
    customer: createdCustomer,
    accounts: [{ ...checking, id: 21, balance: "0.00" }],
    transactions: [],
    transaction_limit: 10,
    transaction_offset: 0,
  };
  const fetchMock = vi
    .spyOn(globalThis, "fetch")
    .mockResolvedValueOnce(Response.json(createdCustomer, { status: 201 }))
    .mockResolvedValueOnce(Response.json(createdDetail));
  const user = userEvent.setup();
  render(
    <MemoryRouter initialEntries={["/admin/customers/new"]}>
      <Routes>
        <Route path="/admin/customers/new" element={<CreateCustomerPage />} />
        <Route
          path="/admin/customers/:userId"
          element={<CustomerDetailPage />}
        />
      </Routes>
    </MemoryRouter>,
  );

  await user.type(screen.getByLabelText("First name"), "Morgan");
  await user.type(screen.getByLabelText("Last name"), "Rivera");
  await user.type(screen.getByLabelText("Email"), "morgan@example.test");
  await user.type(
    screen.getByLabelText("Initial password"),
    "Secure-passphrase",
  );
  await user.type(screen.getByLabelText("Confirm password"), "different");
  await user.click(screen.getByRole("button", { name: "Create customer" }));
  expect(screen.getByText("The passwords do not match.")).toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();

  await user.clear(screen.getByLabelText("Confirm password"));
  await user.type(
    screen.getByLabelText("Confirm password"),
    "Secure-passphrase",
  );
  await user.click(screen.getByRole("button", { name: "Create customer" }));

  expect(
    await screen.findByText("Customer and checking account created."),
  ).toBeInTheDocument();
  expect(await screen.findByText("Morgan Rivera")).toBeInTheDocument();
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  const createInit = fetchMock.mock.calls[0][1]!;
  expect(createInit.body).toBe(
    JSON.stringify({
      first_name: "Morgan",
      last_name: "Rivera",
      email: "morgan@example.test",
      password: "Secure-passphrase",
    }),
  );
  expect(createInit.body).not.toContain("confirm");
  expect(new Headers(createInit.headers).get("X-CSRF-Token")).toBe(
    "create-customer-csrf",
  );
});

it("renders duplicate email feedback on the customer form", async () => {
  document.cookie = "csrf_token=create-customer-csrf; Path=/";
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    Response.json(
      {
        error: {
          code: "EMAIL_ALREADY_EXISTS",
          message: "A customer with this email already exists",
          fields: {
            email: "A customer with this email already exists.",
          },
        },
      },
      { status: 409 },
    ),
  );
  const user = userEvent.setup();
  render(
    <MemoryRouter>
      <CreateCustomerPage />
    </MemoryRouter>,
  );

  await user.type(screen.getByLabelText("First name"), "Morgan");
  await user.type(screen.getByLabelText("Last name"), "Rivera");
  await user.type(screen.getByLabelText("Email"), "existing@example.test");
  await user.type(
    screen.getByLabelText("Initial password"),
    "Secure-passphrase",
  );
  await user.type(
    screen.getByLabelText("Confirm password"),
    "Secure-passphrase",
  );
  await user.click(screen.getByRole("button", { name: "Create customer" }));

  expect(
    await screen.findByText("A customer with this email already exists."),
  ).toBeInTheDocument();
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
