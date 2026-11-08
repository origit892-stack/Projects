from pathlib import Path
import json
import subprocess
import sys

WORKER = Path.home() / ".local/bin/qwen-worker"

if len(sys.argv) != 2:
    raise SystemExit(2)

job_id = sys.argv[1]

result = subprocess.run(
    [
        str(WORKER),
        "job-status",
        job_id,
    ],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("STATUS_ERROR")
    raise SystemExit(
        result.returncode
    )

data = json.loads(
    result.stdout
)

print(data["status"])
