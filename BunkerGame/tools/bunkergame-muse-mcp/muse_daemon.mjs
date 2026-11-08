import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const ROOT = "/Users/Ori/Documents/Projects/BunkerGame";
const BRIDGE = path.join(ROOT, ".opencode", "muse_bridge");
const JOBS = path.join(BRIDGE, "jobs");
const RUNNER = path.join(
  ROOT,
  "tools",
  "bunkergame-muse-mcp",
  "muse_runner.mjs"
);

fs.mkdirSync(JOBS, { recursive: true });

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

function atomicWrite(file, data) {
  const tmp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
  fs.renameSync(tmp, file);
}

async function processJob(file) {
  let job;

  try {
    job = JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return;
  }

  if (job.state !== "QUEUED")
    return;

  job.state = "RUNNING";
  job.daemon_pid = process.pid;
  job.started_at = new Date().toISOString();
  atomicWrite(file, job);

  const args = [
    RUNNER,
    job.opencode,
    ROOT,
    job.agent,
    job.model,
    job.prompt_file,
    job.log_file,
    job.runner_status_file
  ];

  const child = spawn(process.execPath, args, {
    cwd: ROOT,
    detached: false,
    stdio: ["ignore", "ignore", "ignore"],
    env: { ...process.env }
  });

  job.runner_pid = child.pid;
  atomicWrite(file, job);

  child.on("exit", (code, signal) => {
    let latest = job;

    try {
      latest = JSON.parse(fs.readFileSync(file, "utf8"));
    } catch {}

    latest.state = code === 0 ? "COMPLETE" : "FAILED";
    latest.exit_code = code;
    latest.exit_signal = signal;
    latest.completed_at = new Date().toISOString();

    atomicWrite(file, latest);
  });
}

console.log(`MUSE_DAEMON_READY pid=${process.pid}`);

while (true) {
  let files = [];

  try {
    files = fs.readdirSync(JOBS)
      .filter(name => name.endsWith(".json"))
      .sort();
  } catch {}

  for (const name of files) {
    await processJob(path.join(JOBS, name));
  }

  await sleep(500);
}
