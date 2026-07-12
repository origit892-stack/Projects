import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const ARTIFACT_DIR = resolve("output/playwright/train-13");

function safeName(value) {
  return value.toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-|-$/g, "");
}

export async function prepareArtifacts() {
  await mkdir(ARTIFACT_DIR, { recursive: true });
}

export async function captureMilestone(page, order, label) {
  const filename = `${String(order).padStart(2, "0")}-${safeName(label)}.png`;
  const path = resolve(ARTIFACT_DIR, filename);
  const session = await page.context().newCDPSession(page);
  try {
    const { data } = await session.send("Page.captureScreenshot", {
      format: "png",
      fromSurface: true,
      captureBeyondViewport: false
    });
    await writeFile(path, Buffer.from(data, "base64"));
  } finally {
    await session.detach().catch(() => {});
  }
  console.log(`[screenshot] ${path}`);
  return path;
}

export function installDiagnostics(page, baseURL) {
  const diagnostics = {
    consoleErrors: [],
    consoleWarnings: [],
    pageErrors: [],
    failedRequests: [],
    badResponses: []
  };
  const origin = new URL(baseURL).origin;

  page.on("console", (message) => {
    const entry = {
      type: message.type(),
      text: message.text(),
      location: message.location()
    };
    if (message.type() === "error") diagnostics.consoleErrors.push(entry);
    if (message.type() === "warning") diagnostics.consoleWarnings.push(entry);
    if (["error", "warning"].includes(message.type())) {
      console.log(`[browser:${message.type()}] ${entry.text}`);
    }
  });

  page.on("pageerror", (error) => {
    diagnostics.pageErrors.push(error.stack || error.message);
    console.log(`[pageerror] ${error.stack || error.message}`);
  });

  page.on("requestfailed", (request) => {
    const url = request.url();
    const entry = { url, reason: request.failure()?.errorText || "unknown" };
    if (url.startsWith(origin)) diagnostics.failedRequests.push(entry);
    console.log(`[requestfailed] ${entry.reason} ${url}`);
  });

  page.on("response", (response) => {
    if (response.url().startsWith(origin) && response.status() >= 400) {
      diagnostics.badResponses.push({ url: response.url(), status: response.status() });
      console.log(`[http:${response.status()}] ${response.url()}`);
    }
  });

  return diagnostics;
}

export function assertDiagnosticsClean(diagnostics) {
  const failures = {
    consoleErrors: diagnostics.consoleErrors,
    pageErrors: diagnostics.pageErrors,
    failedRequests: diagnostics.failedRequests,
    badResponses: diagnostics.badResponses
  };
  const total = Object.values(failures).reduce((sum, entries) => sum + entries.length, 0);
  if (total) throw new Error(`Browser diagnostics found ${total} failure(s):\n${JSON.stringify(failures, null, 2)}`);
}

export async function measurePerformance(page) {
  return page.evaluate(async () => {
    const navigation = performance.getEntriesByType("navigation")[0];
    let frames = 0;
    const started = performance.now();
    await new Promise((resolve) => {
      function frame(now) {
        frames += 1;
        if (now - started >= 1200) resolve();
        else requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    });
    const duration = performance.now() - started;
    return {
      fps: Number(((frames * 1000) / duration).toFixed(1)),
      domContentLoadedMs: navigation ? Number(navigation.domContentLoadedEventEnd.toFixed(1)) : null,
      loadMs: navigation ? Number(navigation.loadEventEnd.toFixed(1)) : null,
      resourceCount: performance.getEntriesByType("resource").length,
      viewport: { width: innerWidth, height: innerHeight },
      documentWidth: document.documentElement.scrollWidth,
      documentHeight: document.documentElement.scrollHeight
    };
  });
}
