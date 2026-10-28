import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  base: "/projects/adaptread/",
  plugins: [react()],
  server: { proxy: { "/v1": "http://localhost:8000", "/healthz": "http://localhost:8000" } },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.ts",
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
