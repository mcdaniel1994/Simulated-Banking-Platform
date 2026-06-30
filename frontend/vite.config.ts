import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// The development proxy preserves relative /api URLs, matching the production single-origin design.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/tests/setup.ts",
    restoreMocks: true,
  },
});
