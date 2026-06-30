import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";

// Keep browser-like globals predictable between component tests.
afterEach(() => {
  document.cookie = "csrf_token=; Max-Age=0; Path=/";
});
