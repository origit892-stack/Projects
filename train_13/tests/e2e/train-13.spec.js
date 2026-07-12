import { test, expect } from "@playwright/test";
import {
  assertDiagnosticsClean,
  captureMilestone,
  installDiagnostics,
  measurePerformance,
  prepareArtifacts
} from "./helpers/diagnostics.js";
import {
  beginGame,
  clickPhysicalControl,
  dispatchPhysicalKey,
  readFpsState,
  readGameState,
  waitForNextCar,
  walkToTerminals
} from "./helpers/game-bot.js";

test.describe("Train 13 autonomous gameplay bot", () => {
  test("debugs input, UI, performance, failures, and the complete 13-car loop", async ({ page }, testInfo) => {
    await prepareArtifacts();
    const diagnostics = installDiagnostics(page, "http://127.0.0.1:8794");
    let screenshotIndex = 1;

    try {
      await page.goto("/", { waitUntil: "networkidle" });
      await expect(page).toHaveTitle(/רכבת 13/);
      await captureMilestone(page, screenshotIndex++, "start-screen");

      await page.getByRole("button", { name: "עלו לרכבת" }).click();
      await expect(page.locator("#briefingScreen")).toHaveClass(/is-visible/);
      await captureMilestone(page, screenshotIndex++, "briefing-rules");
      await page.getByRole("button", { name: "הבנתי. פתחו את הדלת." }).click();
      await expect(page.locator("#gameScreen")).toHaveClass(/is-visible/);
      await page.locator("#fpsCapture").evaluate((element) => element.click());
      await expect.poll(async () => (await readFpsState(page)).inputCaptured).toBe(true);
      await captureMilestone(page, screenshotIndex++, "first-playable-frame");

      const initial = await readFpsState(page);
      await dispatchPhysicalKey(page, { key: "צ", code: "KeyW", pressed: true });
      await page.waitForTimeout(350);
      await dispatchPhysicalKey(page, { key: "צ", code: "KeyW", pressed: false });
      const afterHebrewW = await readFpsState(page);
      expect(afterHebrewW.z, "physical KeyW must work under a Hebrew keyboard layout").toBeLessThan(initial.z - 0.35);
      await captureMilestone(page, screenshotIndex++, "hebrew-layout-w-movement");

      await page.evaluate(() => window.__train13.setTestPosition(0, 5.3, 0, 0));
      await page.keyboard.down("ArrowUp");
      await page.waitForTimeout(250);
      await page.keyboard.up("ArrowUp");
      expect((await readFpsState(page)).z, "ArrowUp must not move the player").toBeCloseTo(5.3, 1);

      await page.keyboard.down("d");
      await page.waitForTimeout(300);
      await page.keyboard.up("d");
      expect((await readFpsState(page)).x, "D must strafe right").toBeGreaterThan(0.25);
      await page.keyboard.down("a");
      await page.waitForTimeout(300);
      await page.keyboard.up("a");
      expect(Math.abs((await readFpsState(page)).x), "A must strafe back toward center").toBeLessThan(0.25);

      await page.waitForTimeout(500);
      const performance = await measurePerformance(page);
      console.log(`[performance] ${JSON.stringify(performance)}`);
      if (performance.fps < 20) console.log(`[performance:warning] Headless FPS below target: ${performance.fps}`);
      expect(performance.fps).toBeGreaterThan(8);
      expect(performance.documentWidth).toBeLessThanOrEqual(performance.viewport.width + 1);
      testInfo.annotations.push({ type: "performance", description: JSON.stringify(performance) });

      const anomalyIds = await page.evaluate(() => window.__train13.getTestAnomalyIds());
      expect(anomalyIds).toHaveLength(14);
      for (const anomalyId of anomalyIds) {
        const applied = await page.evaluate((id) => window.__train13.setTestAnomaly(id), anomalyId);
        expect(applied, `anomaly ${anomalyId} must be constructible in the 3D carriage`).toBe(true);
        await page.waitForTimeout(anomalyId === "lights" ? 450 : 120);
        await captureMilestone(page, screenshotIndex++, `anomaly-audit-${anomalyId}`);
      }
      await page.evaluate(() => window.__train13.setTestAnomaly(null));

      await page.evaluate(() => window.__train13.setTestPosition(0, 5.3, 0, 0));
      await walkToTerminals(page);
      await clickPhysicalControl(page, "alarm");
      await expect.poll(async () => (await readGameState(page)).mistakes).toBe(1);
      await captureMilestone(page, screenshotIndex++, "wrong-lever-regression");

      await page.reload({ waitUntil: "networkidle" });
      await beginGame(page);

      const actions = new Set();
      for (let car = 1; car <= 13; car += 1) {
        const before = await readGameState(page);
        expect(before.progress).toBe(car - 1);
        expect(before.locked).toBe(false);
        const action = before.anomaly ? "alarm" : "door";
        actions.add(action);
        await walkToTerminals(page);
        await clickPhysicalControl(page, action);
        await captureMilestone(page, screenshotIndex++, `car-${String(car).padStart(2, "0")}-${before.anomaly || "normal"}-${action}`);
        await waitForNextCar(page, car);
      }

      await expect(page.locator("#endingScreen")).toHaveClass(/is-visible/);
      const finalState = await readGameState(page);
      expect(finalState.progress).toBe(13);
      expect(finalState.mistakes).toBe(0);
      expect(actions.has("door")).toBe(true);
      expect(actions.has("alarm")).toBe(true);
      await captureMilestone(page, screenshotIndex++, "ending-success");
      assertDiagnosticsClean(diagnostics);
    } catch (error) {
      await captureMilestone(page, 99, "failure-state").catch(() => {});
      throw error;
    } finally {
      await page.evaluate(async () => {
        localStorage.clear();
        sessionStorage.clear();
        if ("caches" in window) {
          await Promise.all((await caches.keys()).map((key) => caches.delete(key)));
        }
        if (document.pointerLockElement) document.exitPointerLock?.();
      }).catch(() => {});
    }
  });
});
