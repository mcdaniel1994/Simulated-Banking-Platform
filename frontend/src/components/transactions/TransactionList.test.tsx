import { render, screen } from "@testing-library/react";

import { TransactionList } from "./TransactionList";

it("renders friendly signed transaction amounts and balance-after values", () => {
  render(
    <TransactionList
      transactions={[
        {
          id: 1,
          account_id: 1,
          transaction_type: "DEPOSIT",
          amount: "10.00",
          description: "Demo funding deposit",
          balance_after: "110.00",
          reference_id: null,
          created_at: "2026-06-30T12:00:00Z",
        },
        {
          id: 2,
          account_id: 1,
          transaction_type: "WITHDRAWAL",
          amount: "5.00",
          description: "Demo withdrawal",
          balance_after: "105.00",
          reference_id: null,
          created_at: "2026-06-30T13:00:00Z",
        },
      ]}
    />,
  );

  expect(screen.getByRole("table")).toBeInTheDocument();
  expect(
    screen.getByRole("list", { name: "Transaction history" }),
  ).toBeInTheDocument();
  expect(screen.getAllByText("+$10.00").length).toBeGreaterThan(0);
  expect(screen.getAllByText("−$5.00").length).toBeGreaterThan(0);
  expect(screen.getAllByText("$105.00").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Withdrawal").length).toBeGreaterThan(0);
});
