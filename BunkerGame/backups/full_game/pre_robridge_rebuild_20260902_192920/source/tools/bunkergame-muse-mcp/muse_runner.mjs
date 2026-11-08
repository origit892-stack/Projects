import fs from "node:fs";
import { spawn } from "node:child_process";

const [
  opencode,
  root,
  agent,
  model,
  promptPath,
  logPath,
  statusPath
] = process.argv.slice(2);

if (!opencode || !root || !promptPath || !logPath || !statusPath) {
  console.error("MUSE_RUNNER_ARGUMENT_ERROR");
  process.exit(2);
}

const MAX_ATTEMPTS = 5;
const BACKOFF_SECONDS = [0, 10, 20, 40, 60];

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function append(line) {
  fs.appendFileSync(
    logPath,
    line.endsWith("\n") ? line : line + "\n",
    "utf8"
  );
}

function writeStatus(data) {
  fs.writeFileSync(
    statusPath,
    JSON.stringify(
      {
        ...data,
        updated_at: new Date().toISOString()
      },
      null,
      2
    ),
    "utf8"
  );
}

function classify(text) {
  const serverError =
    /Unexpected server error|server_error|server error/i.test(text);

  const stepStart =
    /"type"\s*:\s*"step_start"/.test(text);

  const textEvent =
    /"type"\s*:\s*"text"/.test(text);

  const toolUse =
    /"type"\s*:\s*"tool_use"/.test(text);

  return {
    serverError,
    stepStart,
    textEvent,
    toolUse,
    meaningful: textEvent || toolUse
  };
}

async function runAttempt(attempt, prompt) {
  return await new Promise(resolve => {
    const args = [
      "run",
      "--agent",
      agent,
      "-m",
      model,
      "--format",
      "json"
    ];

    append("");
    append("============================================================");
    append(`MUSE_RUNNER_ATTEMPT=${attempt}`);
    append(`MUSE_RUNNER_TIME=${new Date().toISOString()}`);
    append("============================================================");

    let combined = "";

    const child = spawn(opencode, args, {
      cwd: root,
      stdio: ["pipe", "pipe", "pipe"],
      env: {
        ...process.env,
        HOME: process.env.HOME
      }
    });

    writeStatus({
      state: "RUNNING",
      attempt,
      pid: child.pid
    });

    const consume = chunk => {
      const text = chunk.toString();
      combined += text;
      fs.appendFileSync(logPath, text, "utf8");
    };

    child.stdout.on("data", consume);
    child.stderr.on("data", consume);

    child.on("error", error => {
      append(`MUSE_RUNNER_SPAWN_ERROR=${String(error)}`);

      resolve({
        code: null,
        signal: null,
        output: combined + String(error),
        spawnError: true
      });
    });

    child.on("exit", (code, signal) => {
      resolve({
        code,
        signal,
        output: combined,
        spawnError: false
      });
    });

    child.stdin.end(prompt + "\n");
  });
}

async function main() {
  const prompt = fs.readFileSync(promptPath, "utf8");

  writeStatus({
    state: "STARTING",
    attempt: 0,
    pid: null
  });

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const delay = BACKOFF_SECONDS[attempt - 1];

    if (delay > 0) {
      append(`MUSE_PROVIDER_BACKOFF=${delay}s`);

      writeStatus({
        state: "BACKOFF",
        attempt,
        delay_seconds: delay
      });

      await sleep(delay * 1000);
    }

    const result = await runAttempt(attempt, prompt);
    const info = classify(result.output);

    append("");
    append(`MUSE_ATTEMPT_EXIT_CODE=${String(result.code)}`);
    append(`MUSE_ATTEMPT_EXIT_SIGNAL=${String(result.signal)}`);
    append(`MUSE_ATTEMPT_SERVER_ERROR=${info.serverError ? "YES" : "NO"}`);
    append(`MUSE_ATTEMPT_STEP_START=${info.stepStart ? "YES" : "NO"}`);
    append(`MUSE_ATTEMPT_TEXT=${info.textEvent ? "YES" : "NO"}`);
    append(`MUSE_ATTEMPT_TOOL_USE=${info.toolUse ? "YES" : "NO"}`);

    /*
     * Retry only the transient provider failure class.
     *
     * If Muse has produced meaningful text/tool activity, never silently
     * create a second Director execution.
     */
    if (info.meaningful) {
      writeStatus({
        state: result.code === 0 ? "COMPLETE" : "EXITED_AFTER_ACTIVITY",
        attempt,
        exit_code: result.code,
        meaningful_activity: true
      });

      process.exit(result.code ?? 1);
    }

    if (result.code === 0 && !info.serverError) {
      writeStatus({
        state: "COMPLETE",
        attempt,
        exit_code: 0
      });

      process.exit(0);
    }

    if (info.serverError && attempt < MAX_ATTEMPTS) {
      append(`MUSE_PROVIDER_RETRY_NEXT=${attempt + 1}`);

      writeStatus({
        state: "RETRY_PROVIDER_ERROR",
        attempt,
        exit_code: result.code
      });

      continue;
    }

    writeStatus({
      state: "FAILED",
      attempt,
      exit_code: result.code,
      server_error: info.serverError
    });

    process.exit(result.code ?? 1);
  }

  writeStatus({
    state: "FAILED",
    reason: "MAX_ATTEMPTS_EXHAUSTED"
  });

  process.exit(1);
}

main().catch(error => {
  append(`MUSE_RUNNER_FATAL=${String(error)}`);

  writeStatus({
    state: "FAILED",
    reason: String(error)
  });

  process.exit(1);
});
