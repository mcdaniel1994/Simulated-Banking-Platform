import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { CustomerDashboard } from "./CustomerDashboard";

it("renders owned account cards and an exact combined balance", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    Response.json([
      {
        id: 1,
        account_number: "1000000001",
        account_type: "CHECKING",
        balance: "0.10",
        status: "ACTIVE",
        created_at: "",
        updated_at: "",
      },
      {
        id: 2,
        account_number: "1000000002",
        account_type: "SAVINGS",
        balance: "0.20",
        status: "ACTIVE",
        created_at: "",
        updated_at: "",
      },
    ]),
  );
  render(
    <MemoryRouter>
      <CustomerDashboard />
    </MemoryRouter>,
  );
  expect(screen.getByRole("status")).toHaveTextContent("Loading");
  expect(await screen.findByText("Combined balance")).toBeInTheDocument();
  expect(screen.getByText("$0.30")).toBeInTheDocument();
  expect(screen.getAllByRole("link", { name: "View account" })).toHaveLength(2);
  expect(screen.getAllByText("ACTIVE")).toHaveLength(2);
});
