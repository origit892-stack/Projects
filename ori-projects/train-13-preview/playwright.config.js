import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  outputDir: "./test-results",
  globalTeardown: "./tests/e2e/global-teardown.js",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 180_000,
  expect: { timeout: 8_000 },
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report", open: "never" }]
  ],
  use: {
    ...devices["Desktop Chrome HiDPI"],
    channel: "chrome",
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    baseURL: "http://127.0.0.1:8794",
    trace: "off",
    screenshot: "only-on-failure",
    video: "off"
  },
  webServer: {
    command: "python3 -m http.server 8794",
    url: "http://127.0.0.1:8794",
    cwd: ".",
    reuseExistingServer: false,
    timeout: 15_000
  }
});
