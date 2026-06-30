import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { MoneyForm, TransferForm } from "./MoneyForms";

it("validates and submits an exact deposit through the shared client", async () => {
  document.cookie = "csrf_token=money-csrf; Path=/";
  const fetchMock = vi
    .spyOn(globalThis, "fetch")
    .mockResolvedValue(Response.json({ balance: "12.50" }));
  render(
    <MemoryRouter initialEntries={["/accounts/1/deposit"]}>
      <Routes>
        <Route
          path="/accounts/:accountId/deposit"
          element={<MoneyForm operation="deposit" />}
        />
        <Route path="/accounts/:accountId" element={<p>refetched</p>} />
      </Routes>
    </MemoryRouter>,
  );
  await userEvent.type(screen.getByLabelText("Amount (USD)"), "12.5");
  await userEvent.click(screen.getByRole("button", { name: "Add demo funds" }));
  expect(await screen.findByText("refetched")).toBeInTheDocument();
  const init = fetchMock.mock.calls[0][1]!;
  expect(init.body).toBe(JSON.stringify({ amount: "12.50" }));
  expect(new Headers(init.headers).get("X-CSRF-Token")).toBe("money-csrf");
});

it("rejects a same-account transfer before sending a mutation", async () => {
  const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    Response.json([
      {
        id: 1,
        account_number: "1001",
        account_type: "CHECKING",
        balance: "10.00",
        status: "ACTIVE",
        created_at: "",
        updated_at: "",
      },
    ]),
  );
  render(
    <MemoryRouter>
      <TransferForm />
    </MemoryRouter>,
  );
  const options = await screen.findAllByRole("option", {
    name: "CHECKING •1001",
  });
  expect(options).toHaveLength(2);
  await userEvent.selectOptions(screen.getByLabelText("From"), "1");
  await userEvent.selectOptions(screen.getByLabelText("To"), "1");
  await userEvent.type(screen.getByLabelText("Amount (USD)"), "1.00");
  await userEvent.click(screen.getByRole("button", { name: "Transfer" }));
  expect(screen.getByRole("alert")).toHaveTextContent("two different accounts");
  expect(fetchMock).toHaveBeenCalledTimes(1);
});
