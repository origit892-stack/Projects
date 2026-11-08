#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { spawn, execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";

const ROOT = "/Users/Ori/Documents/Projects/BunkerGame";
const STATE_DIR = path.join(ROOT, ".opencode", "muse_bridge");
const STATE_FILE = path.join(STATE_DIR, "state.json");
const LOG_DIR = path.join(STATE_DIR, "logs");

fs.mkdirSync(LOG_DIR, { recursive: true });

function findOpenCode() {
  const candidates = [
    process.env.OPENCODE_BIN,
    "/Users/Ori/Library/Application Support/bloxbot/opencode/darwin-arm64/1.18.25/opencode",
    "/Users/Ori/Library/Application Support/bloxbot/opencode/darwin-arm64/1.18.23/opencode",
    "/opt/homebrew/bin/opencode",
    "/usr/local/bin/opencode"
  ].filter(Boolean);

  for (const candidate of candidates) {
    try {
      if (fs.existsSync(candidate)) return candidate;
    } catch {}
  }

  return "opencode";
}

const OPENCODE = findOpenCode();

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
  } catch {
    return {
      active: null,
      sessions: {}
    };
  }
}

function saveState(state) {
  fs.mkdirSync(STATE_DIR, { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function text(value) {
  return {
    content: [
      {
        type: "text",
        text: typeof value === "string"
          ? value
          : JSON.stringify(value, null, 2)
      }
    ]
  };
}

function pidAlive(pid) {
  if (!pid) return false;

  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function tailFile(file, maxBytes = 50000) {
  try {
    const stat = fs.statSync(file);
    const start = Math.max(0, stat.size - maxBytes);
    const fd = fs.openSync(file, "r");
    const buffer = Buffer.alloc(stat.size - start);
    fs.readSync(fd, buffer, 0, buffer.length, start);
    fs.closeSync(fd);
    return buffer.toString("utf8");
  } catch {
    return "";
  }
}

const server = new McpServer({
  name: "bunkergame-muse",
  version: "1.0.0"
});

/*
 * 1. muse_health
 */
server.tool(
  "muse_health",
  "Check the BunkerGame Muse/OpenCode bridge, executable, project root and active Muse process.",
  {},
  async () => {
    const state = loadState();
    const active = state.active
      ? state.sessions[state.active]
      : null;

    return text({
      healthy: true,
      project_root: ROOT,
      opencode: OPENCODE,
      state_dir: STATE_DIR,
      active_session: state.active,
      active_pid: active?.pid ?? null,
      active_process_alive: active ? pidAlive(active.pid) : false,
      agent: "bunkergame-art-director",
      model: "opencode/muse-spark-1.2-contributor-free"
    });
  }
);

/*
 * 2. muse_start
 */
server.tool(
  "muse_start",
  "Queue a real Muse/OpenCode BunkerGame art-director invocation through the independent Muse execution daemon.",
  {
    prompt: z.string().min(1).describe("Initial directive for Muse.")
  },
  async ({ prompt }) => {
    const state = loadState();

    if (state.active) {
      const previous = state.sessions[state.active];

      if (previous) {
        const previousJobFile = previous.job_file;

        if (previousJobFile) {
          try {
            const previousJob = JSON.parse(
              fs.readFileSync(previousJobFile, "utf8")
            );

            if (
              previousJob.state === "QUEUED" ||
              previousJob.state === "RUNNING"
            ) {
              return text({
                ok: false,
                error: "MUSE_ALREADY_RUNNING",
                invocation_id: state.active,
                job_state: previousJob.state,
                job_file: previousJobFile
              });
            }
          } catch {}
        }
      }
    }

    const invocationId =
      "muse_" +
      new Date().toISOString().replace(/[^0-9]/g, "").slice(0, 14) +
      "_" +
      crypto.randomBytes(4).toString("hex");

    const logFile = path.join(
      LOG_DIR,
      `${invocationId}.log`
    );

    const promptFile = path.join(
      LOG_DIR,
      `${invocationId}.directive.txt`
    );

    const runnerStatusFile = path.join(
      LOG_DIR,
      `${invocationId}.runner.json`
    );

    const jobsDir = path.join(
      STATE_DIR,
      "jobs"
    );

    fs.mkdirSync(jobsDir, { recursive: true });

    const jobFile = path.join(
      jobsDir,
      `${invocationId}.json`
    );

    fs.writeFileSync(
      promptFile,
      prompt,
      "utf8"
    );

    fs.writeFileSync(
      logFile,
      "",
      { flag: "a" }
    );

    const job = {
      invocation_id: invocationId,
      state: "QUEUED",
      created_at: new Date().toISOString(),
      project_root: ROOT,
      opencode: OPENCODE,
      agent: "bunkergame-art-director",
      model: "opencode/muse-spark-1.2-contributor-free",
      prompt_file: promptFile,
      log_file: logFile,
      runner_status_file: runnerStatusFile
    };

    const temporaryJobFile =
      `${jobFile}.${process.pid}.tmp`;

    fs.writeFileSync(
      temporaryJobFile,
      JSON.stringify(job, null, 2),
      "utf8"
    );

    fs.renameSync(
      temporaryJobFile,
      jobFile
    );

    state.active = invocationId;

    state.sessions[invocationId] = {
      invocation_id: invocationId,
      pid: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      project_root: ROOT,
      agent: "bunkergame-art-director",
      model: "opencode/muse-spark-1.2-contributor-free",
      log_file: logFile,
      prompt_file: promptFile,
      runner_status_file: runnerStatusFile,
      job_file: jobFile,
      initial_prompt: prompt
    };

    saveState(state);

    return text({
      ok: true,
      MUSE_INVOKED: "YES",
      MUSE_INVOCATION_ID: invocationId,
      execution_transport: "INDEPENDENT_DAEMON_QUEUE",
      job_state: "QUEUED",
      job_file: jobFile,
      log_file: logFile,
      project_root: ROOT
    });
  }
);

/*
 * 3. muse_send
 *
 * This launches another Muse turn rooted in the same canonical project.
 * We preserve the bridge invocation ID and append output to the same log.
 *
 * This is intentionally implemented without shell interpolation.
 */
server.tool(
  "muse_send",
  "Send an additional directive through the active BunkerGame Muse bridge.",
  {
    message: z.string().min(1).describe("Directive to send to Muse."),
    invocation_id: z.string().optional()
  },
  async ({ message, invocation_id }) => {
    const state = loadState();
    const id = invocation_id || state.active;

    if (!id || !state.sessions[id]) {
      return text({
        ok: false,
        error: "NO_MUSE_INVOCATION"
      });
    }

    const session = state.sessions[id];
    const out = fs.openSync(session.log_file, "a");
    const err = fs.openSync(session.log_file, "a");

    fs.appendFileSync(
      session.log_file,
      `\n\n===== MUSE_SEND ${new Date().toISOString()} =====\n`
    );

    const args = [
      "run",
      "--agent",
      "bunkergame-art-director",
      "-m",
      "opencode/muse-spark-1.2-contributor-free",
      "--format",
      "json"
    ];

    let child;

    try {
      child = spawn(OPENCODE, args, {
        cwd: ROOT,
        detached: true,
        stdio: ["pipe", out, err],
        env: {
          ...process.env,
          HOME: os.homedir()
        }
      });

      child.stdin.end(message + "\n");
    } catch (error) {
      return text({
        ok: false,
        error: String(error),
        invocation_id: id
      });
    }

    child.unref();

    session.pid = child.pid;
    session.updated_at = new Date().toISOString();
    session.last_message = message;

    state.active = id;
    saveState(state);

    return text({
      ok: true,
      MUSE_INVOKED: "YES",
      MUSE_INVOCATION_ID: id,
      pid: child.pid,
      message_dispatched: true
    });
  }
);

/*
 * 4. muse_status
 */
server.tool(
  "muse_status",
  "Get current status for a Muse bridge invocation.",
  {
    invocation_id: z.string().optional()
  },
  async ({ invocation_id }) => {
    const state = loadState();
    const id = invocation_id || state.active;

    if (!id || !state.sessions[id]) {
      return text({
        ok: false,
        status: "NO_SESSION"
      });
    }

    const session = state.sessions[id];

    let job = null;

    if (session.job_file) {
      try {
        job = JSON.parse(
          fs.readFileSync(session.job_file, "utf8")
        );
      } catch {}
    }

    const runnerPid =
      job?.runner_pid ??
      session.pid ??
      null;

    const alive = runnerPid
      ? pidAlive(runnerPid)
      : false;

    const jobState =
      job?.state ??
      null;

    const running =
      jobState === "QUEUED" ||
      jobState === "RUNNING" ||
      alive;

    return text({
      ok: true,
      invocation_id: id,
      pid: runnerPid,
      daemon_pid: job?.daemon_pid ?? null,
      running,
      status: running ? "RUNNING" : "NOT_RUNNING",
      job_state: jobState,
      exit_code: job?.exit_code ?? null,
      exit_signal: job?.exit_signal ?? null,
      created_at: session.created_at,
      updated_at: session.updated_at,
      log_file: session.log_file,
      log_bytes: (() => {
        try {
          return fs.statSync(session.log_file).size;
        } catch {
          return 0;
        }
      })()
    });
  }
);

/*
 * 5. muse_output
 */
server.tool(
  "muse_output",
  "Read recent output produced by the active Muse invocation.",
  {
    invocation_id: z.string().optional(),
    max_bytes: z.number().int().min(1000).max(200000).optional()
  },
  async ({ invocation_id, max_bytes }) => {
    const state = loadState();
    const id = invocation_id || state.active;

    if (!id || !state.sessions[id]) {
      return text({
        ok: false,
        error: "NO_SESSION"
      });
    }

    const session = state.sessions[id];

    let job = null;

    if (session.job_file) {
      try {
        job = JSON.parse(
          fs.readFileSync(session.job_file, "utf8")
        );
      } catch {}
    }

    const running =
      job?.state === "QUEUED" ||
      job?.state === "RUNNING";

    return text({
      ok: true,
      invocation_id: id,
      running,
      job_state: job?.state ?? null,
      daemon_pid: job?.daemon_pid ?? null,
      runner_pid: job?.runner_pid ?? null,
      exit_code: job?.exit_code ?? null,
      log_file: session.log_file,
      output: tailFile(session.log_file, max_bytes || 50000)
    });
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
