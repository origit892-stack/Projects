import subprocess, os, sys

prompt_path = sys.argv[1]
inner_timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 100
prompt = open(prompt_path).read()
print("PROMPT_BYTES=", len(prompt))
print("PROMPT_HEAD=", prompt[:160].replace("\n", " | "))

env = os.environ.copy()
env.pop("FORCE_NO_TTY", None)
cmd = [
    "/Users/Ori/.npm-global/bin/cn",
    "-p",
    "--config",
    "/Users/Ori/.continue/config.yaml",
    "--auto",
    "--format",
    "json",
    prompt,
]
log_path = "/tmp/cn_repl.log"
with open(log_path, "w") as log:
    p = subprocess.Popen(
        cmd,
        cwd="/Users/Ori/Documents/Projects/BunkerGame",
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        text=True,
    )
    try:
        rc = p.wait(timeout=inner_timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        rc = "TIMEOUT"
print("RC=", rc)
print("LOG_BYTES=", os.path.getsize(log_path))
print("LOG_HEAD=", open(log_path).read()[:400])
