import json
import os
import pathlib
import subprocess
import sys
import time

PROJECT = pathlib.Path(
    "/Users/Ori/Documents/Projects/BunkerGame"
)

DIRECTOR = PROJECT / ".director"
RUNTIME = DIRECTOR / "bin" / "runtime.py"
DETACHED = DIRECTOR / "detached"

DETACHED.mkdir(
    parents=True,
    exist_ok=True,
)


def safe_id(value):
    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    if not value:
        raise ValueError("EMPTY_ID")

    if any(ch not in allowed for ch in value):
        raise ValueError(
            f"INVALID_ID={value}"
        )

    return value


def record_path(job_id):
    return DETACHED / f"{job_id}.json"


def log_path(job_id):
    return DETACHED / f"{job_id}.log"


def process_alive(pid):
    try:
        completed = subprocess.run(
            [
                "ps",
                "-o",
                "stat=",
                "-p",
                str(pid),
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        completed = None

    if completed is not None:
        state = completed.stdout.strip()

        if not state:
            return False

        if state.startswith("Z"):
            return False

        return True

    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def write_record(path, value):
    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    tmp.replace(path)


def launch(mode, task_ids):
    stamp = time.strftime(
        "%Y%m%d_%H%M%S"
    )

    joined = "-".join(
        task_ids[:2]
    )[:80]

    job_id = safe_id(
        f"{mode}-{joined}-{stamp}"
    )

    record = record_path(job_id)
    log = log_path(job_id)

    if mode == "run":
        command = [
            sys.executable,
            str(RUNTIME),
            "run",
            task_ids[0],
        ]
    elif mode == "parallel":
        command = [
            sys.executable,
            str(RUNTIME),
            "parallel",
            *task_ids,
        ]
    else:
        raise ValueError(
            f"INVALID_MODE={mode}"
        )

    handle = open(
        log,
        "ab",
        buffering=0,
    )

    proc = subprocess.Popen(
        command,
        cwd=str(PROJECT),
        stdin=subprocess.DEVNULL,
        stdout=handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
    )

    handle.close()

    data = {
        "job_id": job_id,
        "mode": mode,
        "task_ids": task_ids,
        "pid": proc.pid,
        "log": str(log),
        "record": str(record),
        "started_at": time.time(),
        "launcher_status": "RUNNING",
    }

    write_record(
        record,
        data,
    )

    print(
        json.dumps(
            data,
            indent=2,
        )
    )


def status(job_id):
    job_id = safe_id(job_id)
    path = record_path(job_id)

    if not path.exists():
        raise RuntimeError(
            f"JOB_NOT_FOUND={job_id}"
        )

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    alive = process_alive(
        int(data["pid"])
    )

    results = {}

    for task_id in data["task_ids"]:
        result = (
            DIRECTOR
            / "results"
            / f"{task_id}.json"
        )

        if result.exists():
            try:
                results[task_id] = json.loads(
                    result.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception as exc:
                results[task_id] = {
                    "status": "INVALID_RESULT",
                    "error": str(exc),
                }

    terminal_states = {
        "PASS",
        "FAILED",
        "BLOCKED",
    }

    all_results_present = (
        len(results)
        == len(data["task_ids"])
    )

    states = [
        value.get("status")
        for value in results.values()
    ]

    all_results_terminal = (
        all_results_present
        and all(
            state in terminal_states
            for state in states
        )
    )

    if all_results_terminal:
        if all(
            state == "PASS"
            for state in states
        ):
            state = "COMPLETE"
        elif any(
            state == "BLOCKED"
            for state in states
        ):
            state = "BLOCKED"
        else:
            state = "FAILED"
    elif alive:
        state = "RUNNING"
    elif all_results_present:
        state = "RESULTS_NOT_TERMINAL"
    else:
        state = "EXITED_WITHOUT_ALL_RESULTS"

    output = {
        **data,
        "process_alive": alive,
        "status": state,
        "results": results,
    }

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
    )


def show_log(job_id, lines):
    job_id = safe_id(job_id)
    path = log_path(job_id)

    if not path.exists():
        raise RuntimeError(
            f"LOG_NOT_FOUND={job_id}"
        )

    content = path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    print(
        "\n".join(
            content[-lines:]
        )
    )


def main():
    if len(sys.argv) < 2:
        raise SystemExit(2)

    command = sys.argv[1]

    if command == "start":
        if len(sys.argv) != 3:
            raise SystemExit(2)

        launch(
            "run",
            [safe_id(sys.argv[2])],
        )

    elif command == "start-parallel":
        if len(sys.argv) < 3:
            raise SystemExit(2)

        launch(
            "parallel",
            [
                safe_id(value)
                for value in sys.argv[2:]
            ],
        )

    elif command == "status":
        if len(sys.argv) != 3:
            raise SystemExit(2)

        status(sys.argv[2])

    elif command == "log":
        if len(sys.argv) not in {
            3,
            4,
        }:
            raise SystemExit(2)

        lines = (
            int(sys.argv[3])
            if len(sys.argv) == 4
            else 80
        )

        show_log(
            sys.argv[2],
            lines,
        )

    else:
        raise SystemExit(
            f"UNKNOWN_COMMAND={command}"
        )


if __name__ == "__main__":
    main()
