import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  use: { baseURL: "http://127.0.0.1:8000" },
  webServer: {
    command: "../.venv/bin/python -m uvicorn adaptread.api.app:app --host 127.0.0.1 --port 8000",
    port: 8000,
    reuseExistingServer: true,
  },
});
