import { defineConfig, devices } from "@playwright/test";

// This suite targets an already-running single-origin deployment rather than starting dev servers.
export default defineConfig({
  testDir: "./e2e",
  testMatch: "production-smoke.spec.ts",
  fullyParallel: false,
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.PRODUCTION_BASE_URL ?? "https://localhost:8443",
    // Only the explicit local smoke may trust its temporary self-signed certificate.
    ignoreHTTPSErrors: process.env.ALLOW_SELF_SIGNED_TLS === "true",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
