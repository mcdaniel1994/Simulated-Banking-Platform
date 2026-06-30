import {
  addMoney,
  centsToMoney,
  formatUsd,
  moneyToCents,
  normalizeMoneyInput,
} from "./money";

describe("exact money utilities", () => {
  it("round-trips and totals decimal strings without floating point", () => {
    expect(moneyToCents("900719925474.09")).toBe(90071992547409n);
    expect(centsToMoney(90071992547409n)).toBe("900719925474.09");
    expect(addMoney(["0.10", "0.20"])).toBe("0.30");
    expect(formatUsd("1234567.89")).toBe("$1,234,567.89");
  });

  it("normalizes form input and rejects invalid or zero values", () => {
    expect(normalizeMoneyInput(" 12.5 ")).toBe("12.50");
    expect(normalizeMoneyInput("0")).toBeUndefined();
    expect(normalizeMoneyInput("1.001")).toBeUndefined();
  });
});
