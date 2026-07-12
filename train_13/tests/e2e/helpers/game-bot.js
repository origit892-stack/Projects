import { expect } from "@playwright/test";

export async function readGameState(page) {
  return page.evaluate(() => window.__train13.getState());
}

export async function readFpsState(page) {
  return page.evaluate(() => window.__train13.getFPS());
}

export async function beginGame(page) {
  await page.getByRole("button", { name: "עלו לרכבת" }).click();
  await page.getByRole("button", { name: "הבנתי. פתחו את הדלת." }).click();
  await expect(page.locator("#gameScreen")).toHaveClass(/is-visible/);
  await page.locator("#fpsCapture").evaluate((element) => element.click());
  await expect.poll(async () => (await readFpsState(page)).inputCaptured).toBe(true);
}

export async function dispatchPhysicalKey(page, { key, code, pressed }) {
  await page.evaluate(({ eventKey, eventCode, down }) => {
    document.dispatchEvent(new KeyboardEvent(down ? "keydown" : "keyup", {
      key: eventKey,
      code: eventCode,
      bubbles: true
    }));
  }, { eventKey: key, eventCode: code, down: pressed });
}

export async function walkToTerminals(page) {
  await page.keyboard.down("Shift");
  await page.keyboard.down("w");
  try {
    await expect.poll(async () => (await readFpsState(page)).z, {
      message: "W should move the bot to the terminal line",
      timeout: 6_000,
      intervals: [100]
    }).toBeLessThanOrEqual(-7.35);
  } finally {
    await page.keyboard.up("w");
    await page.keyboard.up("Shift");
  }
  const fps = await readFpsState(page);
  expect(fps.z).toBeGreaterThanOrEqual(-9.25);
  return fps;
}

export async function clickPhysicalControl(page, action) {
  const position = await page.evaluate((selectedAction) => {
    return window.__train13.getTestControlPosition(selectedAction);
  }, action);
  expect(position, `${action} control position`).not.toBeNull();
  expect(position.visible, `${action} control should be visible`).toBe(true);
  expect(position.distance, `${action} control should be within interaction distance`).toBeLessThanOrEqual(4.35);

  await page.locator("#trainCanvas").dispatchEvent("click", {
    bubbles: true,
    clientX: position.x,
    clientY: position.y,
    button: 0
  });
  return position;
}

export async function waitForNextCar(page, expectedProgress) {
  await expect.poll(async () => (await readGameState(page)).progress, {
    timeout: 4_000,
    intervals: [100]
  }).toBe(expectedProgress);
  if (expectedProgress < 13) {
    await expect.poll(async () => (await readGameState(page)).locked, {
      timeout: 4_000,
      intervals: [100]
    }).toBe(false);
    await expect.poll(async () => (await readFpsState(page)).z, {
      timeout: 4_000,
      intervals: [100]
    }).toBeGreaterThan(5);
  }
}
