import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { AccountDetail } from "./AccountDetail";

it("loads account history using the backend pagination contract", async () => {
  const fetchMock = vi.spyOn(globalThis, "fetch");
  fetchMock
    .mockResolvedValueOnce(
      Response.json({
        id: 1,
        account_number: "1001",
        account_type: "CHECKING",
        balance: "10.00",
        status: "ACTIVE",
        created_at: "",
        updated_at: "",
      }),
    )
    .mockResolvedValueOnce(Response.json([]));

  render(
    <MemoryRouter initialEntries={["/accounts/1"]}>
      <Routes>
        <Route path="/accounts/:accountId" element={<AccountDetail />} />
      </Routes>
    </MemoryRouter>,
  );

  expect(
    await screen.findByRole("heading", { name: "checking account" }),
  ).toBeInTheDocument();
  expect(fetchMock.mock.calls[1][0]).toBe(
    "/api/accounts/1/transactions?limit=10&offset=0",
  );
  expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  expect(screen.getByText("Page 1")).toHaveAttribute("aria-current", "page");
});
