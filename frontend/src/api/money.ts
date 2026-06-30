const MONEY_PATTERN = /^(0|[1-9]\d{0,11})\.(\d{2})$/;

// Exact cents are represented as BigInt so totals never cross a binary floating-point boundary.
export function moneyToCents(value: string): bigint {
  const match = MONEY_PATTERN.exec(value);
  if (!match)
    throw new Error(
      "Money must be a non-negative decimal string with two places",
    );
  return BigInt(match[1]) * 100n + BigInt(match[2]);
}

export function centsToMoney(cents: bigint): string {
  const sign = cents < 0n ? "-" : "";
  const absolute = cents < 0n ? -cents : cents;
  return `${sign}${absolute / 100n}.${(absolute % 100n).toString().padStart(2, "0")}`;
}

export function addMoney(values: string[]): string {
  return centsToMoney(
    values.reduce((sum, value) => sum + moneyToCents(value), 0n),
  );
}

export function formatUsd(value: string): string {
  const cents = moneyToCents(value);
  const whole = (cents / 100n).toLocaleString("en-US");
  return `$${whole}.${(cents % 100n).toString().padStart(2, "0")}`;
}

// Form input is normalized without Number parsing; the backend remains authoritative on bounds.
export function normalizeMoneyInput(value: string): string | undefined {
  const trimmed = value.trim();
  if (!/^\d+(\.\d{1,2})?$/.test(trimmed)) return undefined;
  const [whole, fraction = ""] = trimmed.split(".");
  const normalized = `${BigInt(whole)}.${fraction.padEnd(2, "0")}`;
  return moneyToCents(normalized) > 0n ? normalized : undefined;
}
