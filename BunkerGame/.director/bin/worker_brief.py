from pathlib import Path
import json
import sys

PROJECT = Path(
    "/Users/Ori/Documents/Projects/BunkerGame"
)

D = PROJECT / ".director"

MAX_RESULT = 1800
MAX_VERIFICATION = 1800
MAX_BLOCKERS = 800
MAX_FILES = 1000
MAX_ARTIFACTS = 1000


def clip(value, limit):
    if value is None:
        return ""

    if not isinstance(value, str):
        value = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
        )

    if len(value) <= limit:
        return value

    omitted = len(value) - limit

    return (
        value[:limit]
        + f"\n...[TRUNCATED {omitted} CHARS]"
    )


def result_path(task_id):
    return (
        D
        / "results"
        / f"{task_id}.json"
    )


def show(task_id):
    path = result_path(task_id)

    if not path.exists():
        print(f"TASK_ID={task_id}")
        print("STATUS=PENDING")
        return

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    print(
        f"TASK_ID={data.get('task_id', task_id)}"
    )
    print(
        f"ROLE={data.get('role', 'UNKNOWN')}"
    )
    print(
        f"STATUS={data.get('status', 'UNKNOWN')}"
    )

    print("RESULT_BEGIN")
    print(
        clip(
            data.get("result"),
            MAX_RESULT,
        )
    )
    print("RESULT_END")

    print("VERIFICATION_BEGIN")
    print(
        clip(
            data.get("verification"),
            MAX_VERIFICATION,
        )
    )
    print("VERIFICATION_END")

    print("FILES_CHANGED_BEGIN")
    print(
        clip(
            data.get("files_changed"),
            MAX_FILES,
        )
    )
    print("FILES_CHANGED_END")

    print("ARTIFACTS_BEGIN")
    print(
        clip(
            data.get("artifacts"),
            MAX_ARTIFACTS,
        )
    )
    print("ARTIFACTS_END")

    print("BLOCKERS_BEGIN")
    print(
        clip(
            data.get("blockers"),
            MAX_BLOCKERS,
        )
    )
    print("BLOCKERS_END")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: worker_brief.py TASK_ID"
        )

    show(sys.argv[1])


if __name__ == "__main__":
    main()
