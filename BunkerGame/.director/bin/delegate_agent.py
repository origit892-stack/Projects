from pathlib import Path
import argparse
import json
import subprocess
import sys

PROJECT = Path("/Users/Ori/Documents/Projects/BunkerGame")
D = PROJECT / ".director"
WORKER = Path.home() / ".local/bin/qwen-worker"
SPECS = D / "frontdoor" / "tasks"

SPECS.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "role",
        choices=[
            "researcher",
            "implementer",
            "verifier",
        ],
    )

    parser.add_argument("task_id")
    parser.add_argument("objective")
    parser.add_argument("acceptance")

    parser.add_argument(
        "--timeout",
        type=int,
        default=7200,
    )

    parser.add_argument(
        "--read",
        action="append",
        default=[],
    )

    parser.add_argument(
        "--write",
        action="append",
        default=[],
    )

    args = parser.parse_args()

    objective_path = (
        SPECS
        / f"{args.task_id}-objective.md"
    )

    acceptance_path = (
        SPECS
        / f"{args.task_id}-acceptance.md"
    )

    objective_path.write_text(
        args.objective.strip() + "\n",
        encoding="utf-8",
    )

    acceptance_path.write_text(
        args.acceptance.strip() + "\n",
        encoding="utf-8",
    )

    command = [
        str(WORKER),
        "create",
        args.role,
        args.task_id,
        str(objective_path),
        str(acceptance_path),
        str(args.timeout),
    ]

    for scope in args.read:
        command.extend([
            "--read",
            scope,
        ])

    for scope in args.write:
        command.extend([
            "--write",
            scope,
        ])

    created = subprocess.run(
        command,
        cwd=str(PROJECT),
        capture_output=True,
        text=True,
    )

    if created.returncode != 0:
        print("DELEGATION_CREATE=FAILED")
        print(created.stderr.strip())
        raise SystemExit(
            created.returncode
        )

    launched = subprocess.run(
        [
            str(WORKER),
            "start",
            args.task_id,
        ],
        cwd=str(PROJECT),
        capture_output=True,
        text=True,
    )

    if launched.returncode != 0:
        print("DELEGATION_START=FAILED")
        print(launched.stderr.strip())
        raise SystemExit(
            launched.returncode
        )

    try:
        data = json.loads(
            launched.stdout
        )
    except Exception:
        print("DELEGATION_START_OUTPUT_INVALID")
        print(launched.stdout.strip())
        raise SystemExit(1)

    print("DELEGATION=STARTED")
    print(f"TASK_ID={args.task_id}")
    print(f"ROLE={args.role}")
    print(f"JOB_ID={data['job_id']}")
    print(f"PID={data['pid']}")


if __name__ == "__main__":
    main()
