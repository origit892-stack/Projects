import { rm } from "node:fs/promises";
import { resolve } from "node:path";

export default async function globalTeardown() {
  await rm(resolve(".playwright-tmp"), { recursive: true, force: true });
  console.log("[teardown] Temporary Playwright game data removed; reports and screenshots preserved.");
}
