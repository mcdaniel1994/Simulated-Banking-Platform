import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { configDefaults, defineConfig } from "vitest/config";

// The development proxy preserves relative /api URLs, matching the production single-origin design.
export default defineConfig({
  // Tailwind runs at build time only; React remains the sole browser UI runtime.
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    // Browser journeys run under Playwright; Vitest owns only isolated component/unit files.
    exclude: [...configDefaults.exclude, "e2e/**"],
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/tests/setup.ts",
    restoreMocks: true,
  },
});
