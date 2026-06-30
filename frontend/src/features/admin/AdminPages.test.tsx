import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { AdminDashboardPage } from "./AdminPages";

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
  expect(
    await screen.findByText("Simulated balance:", { exact: false }),
  ).toHaveTextContent("$1,000.10");
  expect(
    screen.getByRole("link", { name: "Manage customers" }),
  ).toBeInTheDocument();
});
