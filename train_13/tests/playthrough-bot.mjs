import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const ROOT = new URL("../", import.meta.url).pathname;
const PORT = 8793;
const DEBUG_PORT = 9273;
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

let server;
let chrome;
let socket;
const profile = mkdtempSync(join(tmpdir(), "train13-bot-"));

function cleanup() {
  try { socket?.close(); } catch {}
  try { chrome?.kill("SIGTERM"); } catch {}
  try { server?.kill("SIGTERM"); } catch {}
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}

async function waitForJson(url, timeout = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    try {
      const response = await fetch(url);
      if (response.ok) return response.json();
    } catch {}
    await sleep(250);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

function createCdp(webSocketUrl) {
  socket = new WebSocket(webSocketUrl);
  let nextId = 0;
  const pending = new Map();
  const runtimeErrors = [];

  const opened = new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });

  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.method === "Runtime.exceptionThrown") {
      runtimeErrors.push(message.params.exceptionDetails.text);
    }
    if (message.id && pending.has(message.id)) {
      pending.get(message.id).resolve(message);
      pending.delete(message.id);
    }
  });

  socket.addEventListener("close", () => {
    for (const { reject } of pending.values()) reject(new Error("Chrome DevTools connection closed"));
    pending.clear();
  });

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, { resolve, reject });
      socket.send(JSON.stringify({ id, method, params }));
    });
  }

  async function evaluate(expression) {
    const response = await send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (response.result.exceptionDetails) {
      throw new Error(response.result.exceptionDetails.exception?.description || response.result.exceptionDetails.text);
    }
    return response.result.result.value;
  }

  return { opened, send, evaluate, runtimeErrors };
}

async function key(cdp, type, value, code) {
  await cdp.send("Input.dispatchKeyEvent", { type, key: value, code });
}

async function holdKey(cdp, value, code, milliseconds) {
  await key(cdp, "keyDown", value, code);
  await sleep(milliseconds);
  await key(cdp, "keyUp", value, code);
  await sleep(80);
}

async function walkToTerminals(cdp) {
  await key(cdp, "keyDown", "Shift", "ShiftLeft");
  await key(cdp, "keyDown", "w", "KeyW");
  let fps = null;
  for (let attempt = 0; attempt < 45; attempt += 1) {
    await sleep(100);
    fps = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getFPS())"));
    if (fps.z <= -7.35) break;
  }
  await key(cdp, "keyUp", "w", "KeyW");
  await key(cdp, "keyUp", "Shift", "ShiftLeft");
  await sleep(120);

  fps = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getFPS())"));
  if (fps.z > -7.1) throw new Error(`Bot did not reach the terminals; z=${fps.z}`);
  return fps;
}

async function clickPhysicalControl(cdp, action) {
  const position = JSON.parse(
    await cdp.evaluate(`JSON.stringify(__train13.getTestControlPosition(${JSON.stringify(action)}))`),
  );
  if (!position || !position.visible) throw new Error(`${action} control is not visible`);
  if (position.distance > 4.35) throw new Error(`${action} control is too far: ${position.distance}`);
  if (position.x < 0 || position.x > 1280 || position.y < 0 || position.y > 800) {
    throw new Error(`${action} control projected outside viewport: ${JSON.stringify(position)}`);
  }
  console.log(`  control ${action}: x=${position.x.toFixed(1)} y=${position.y.toFixed(1)} d=${position.distance.toFixed(2)}`);

  await cdp.evaluate(`trainCanvas.dispatchEvent(new MouseEvent("click", {
    bubbles: true,
    clientX: ${position.x},
    clientY: ${position.y},
    button: 0
  })); true`);
  return position;
}

async function main() {
  server = spawn("python3", ["-m", "http.server", String(PORT)], {
    cwd: ROOT,
    stdio: "ignore",
  });
  chrome = spawn(CHROME, [
    "--headless",
    "--hide-scrollbars",
    `--remote-debugging-port=${DEBUG_PORT}`,
    `--user-data-dir=${profile}`,
    "--window-size=1280,800",
    "about:blank",
  ], { stdio: "ignore" });

  const pages = await waitForJson(`http://127.0.0.1:${DEBUG_PORT}/json/list`);
  const page = pages.find((entry) => entry.type === "page");
  if (!page) throw new Error("Chrome did not expose a page target");
  const cdp = createCdp(page.webSocketDebuggerUrl);
  await cdp.opened;
  await cdp.send("Runtime.enable");
  await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/?bot=${Date.now()}` });
  await sleep(3400);

  const boot = JSON.parse(await cdp.evaluate(
    "JSON.stringify({api:!!window.__train13,webgl:window.__train13?.hasWebGL(),error:window.__train13WebGLError||null})",
  ));
  if (!boot.api || !boot.webgl || boot.error) throw new Error(`Game boot failed: ${JSON.stringify(boot)}`);

  const anomalyIds = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getTestAnomalyIds())"));
  for (const anomalyId of anomalyIds) {
    const changed = await cdp.evaluate(`__train13.setTestAnomaly(${JSON.stringify(anomalyId)})`);
    if (!changed) throw new Error(`Could not preview anomaly ${anomalyId}`);
    await sleep(35);
  }
  await cdp.evaluate("__train13.setTestAnomaly(null)");
  console.log(`✓ Rendered all ${anomalyIds.length} anomaly variants without exceptions`);

  await cdp.evaluate("__train13.start();fpsCapture.click();true");
  await sleep(250);
  const initial = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getFPS())"));
  if (!initial.inputCaptured) throw new Error("FPS controls were not captured");

  await holdKey(cdp, "ArrowUp", "ArrowUp", 260);
  const afterArrow = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getFPS())"));
  if (Math.abs(afterArrow.z - initial.z) > 0.01) throw new Error("ArrowUp moved the player; only WASD should work");

  await holdKey(cdp, "d", "KeyD", 280);
  const afterD = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getFPS())"));
  if (afterD.x < 0.25) throw new Error(`D strafe failed: x=${afterD.x}`);
  await holdKey(cdp, "a", "KeyA", 280);
  const afterA = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getFPS())"));
  if (Math.abs(afterA.x) > 0.22) throw new Error(`A strafe did not return toward center: x=${afterA.x}`);
  console.log("✓ Controls: ArrowUp ignored; A/D strafing verified");

  await cdp.evaluate("__train13.setTestPosition(0,5.3,0,0);true");
  await walkToTerminals(cdp);
  await clickPhysicalControl(cdp, "alarm");
  await sleep(2500);
  const wrong = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getState())"));
  if (wrong.progress !== 0 || wrong.mistakes !== 1 || wrong.locked) {
    throw new Error(`Wrong physical lever regression failed: ${JSON.stringify(wrong)}`);
  }
  console.log("✓ Wrong physical lever: mistake recorded and car reset");
  await cdp.evaluate("__train13.start();fpsCapture.click();true");
  await sleep(300);
  const reset = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getState())"));
  if (reset.progress !== 0 || reset.mistakes !== 0) throw new Error(`Restart did not reset state: ${JSON.stringify(reset)}`);

  const journey = [];
  for (let expectedProgress = 0; expectedProgress < 13; expectedProgress += 1) {
    const before = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getState())"));
    if (before.progress !== expectedProgress || before.locked) {
      throw new Error(`Unexpected state before car ${expectedProgress + 1}: ${JSON.stringify(before)}`);
    }
    const action = before.anomaly ? "alarm" : "door";
    const fps = await walkToTerminals(cdp);
    const position = await clickPhysicalControl(cdp, action);
    await sleep(expectedProgress === 12 ? 2600 : 1850);
    const after = JSON.parse(await cdp.evaluate("JSON.stringify(__train13.getState())"));
    if (after.progress !== expectedProgress + 1) {
      throw new Error(`Physical ${action} click failed on car ${expectedProgress + 1}: ${JSON.stringify(after)}`);
    }
    journey.push({ car: expectedProgress + 1, anomaly: before.anomaly || "normal", action, z: fps.z, distance: Number(position.distance.toFixed(2)) });
    console.log(`✓ Car ${String(expectedProgress + 1).padStart(2, "0")}: ${before.anomaly || "normal"} → ${action}`);
  }

  const ending = JSON.parse(await cdp.evaluate(
    "JSON.stringify({state:__train13.getState(),ending:endingScreen.classList.contains('is-visible')})",
  ));
  if (!ending.ending || ending.state.progress !== 13 || ending.state.mistakes !== 0) {
    throw new Error(`Ending validation failed: ${JSON.stringify(ending)}`);
  }
  if (cdp.runtimeErrors.length) throw new Error(`Runtime errors: ${cdp.runtimeErrors.join("; ")}`);
  if (!journey.some((entry) => entry.action === "alarm")) throw new Error("Bot run did not exercise the physical emergency lever");
  if (!journey.some((entry) => entry.action === "door")) throw new Error("Bot run did not exercise the physical normal button");

  console.log(`\nTrain 13 bot completed all ${journey.length} cars with 0 mistakes.`);
  console.log(`Physical controls tested: ${[...new Set(journey.map((entry) => entry.action))].join(", ")}`);
  console.log("Runtime errors: 0");
}

process.on("SIGINT", () => { cleanup(); process.exit(130); });
process.on("SIGTERM", () => { cleanup(); process.exit(143); });

try {
  await main();
} finally {
  cleanup();
}
