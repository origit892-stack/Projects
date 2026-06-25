import { test, expect } from '@playwright/test';

test('game boots and canvas renders', async ({ page }) => {
  await page.goto('/');
  const canvas = page.locator('canvas');
  await expect(canvas).toBeVisible();
  await page.keyboard.press('KeyD');
  await page.waitForTimeout(250);
});
