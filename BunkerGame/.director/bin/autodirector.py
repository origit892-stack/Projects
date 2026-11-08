#!/usr/bin/env python3

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import uuid

PROJECT = (
    pathlib.Path.home()
    / "Documents/Projects/BunkerGame"
)

ROOT = PROJECT / ".director"
CN = pathlib.Path(
    "/Users/Ori/.npm-global/bin/cn"
)
CONFIG = (
    pathlib.Path.home()
    / ".continue/config.yaml"
)

DIRECTOR_ROOT = ROOT / "director"
DECISIONS = DIRECTOR_ROOT / "decisions"
CYCLES = DIRECTOR_ROOT / "cycles"
OBJECTIVES = DIRECTOR_ROOT / "objectives"
HANDOFFS = DIRECTOR_ROOT / "handoffs"

TASKS = ROOT / "tasks"
RESULTS = ROOT / "results"
PROMPTS = ROOT / "prompts"

RUNTIME = ROOT / "bin/director"

MAX_PARALLEL = 4
MAX_CYCLES_DEFAULT = 50
DIRECTOR_TIMEOUT = 600
DIRECTOR_BOOTSTRAP_LIMIT = 800

ACTIVE_COMPLETED_TASKS_MAX = 8
ACTIVE_FAILED_TASKS_MAX = 8
ACTIVE_BLOCKED_TASKS_MAX = 8
RECENT_HANDOFFS_MAX = 6
DIRECTOR_INPUT_MAX = 49152

HISTORY = DIRECTOR_ROOT / "history"
CHECKPOINTS = DIRECTOR_ROOT / "checkpoints"

for p in (
    DIRECTOR_ROOT,
    DECISIONS,
    CYCLES,
    OBJECTIVES,
    HANDOFFS,
    HISTORY,
    CHECKPOINTS,
):
    p.mkdir(
        parents=True,
        exist_ok=True,
    )

def utcnow():
    return datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()

def write_json(path, value):
    path = pathlib.Path(path)

    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    os.replace(
        tmp,
        path,
    )

def read_json(path):
    return json.loads(
        pathlib.Path(path).read_text(
            encoding="utf-8"
        )
    )

def safe_id(value):
    value = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "-",
        str(value).strip(),
    )

    value = value.strip(".-")

    if not value:
        raise ValueError(
            "EMPTY_ID"
        )

    return value[:96]

def normalize_scope(scope):
    scope = str(
        scope
    ).strip()

    if not scope:
        return ()

    scope = scope.replace(
        "\\",
        "/",
    )

    while scope.startswith("./"):
        scope = scope[2:]

    parts = []

    for part in scope.split("/"):
        if not part:
            continue

        if (
            part in {"*", "**"}
            or any(
                c in part
                for c in "*?["
            )
        ):
            break

        parts.append(part)

    return tuple(parts)

def scopes_overlap(a, b):
    pa = normalize_scope(a)
    pb = normalize_scope(b)

    if not pa or not pb:
        return True

    n = min(
        len(pa),
        len(pb),
    )

    return (
        pa[:n] == pb[:n]
    )

def tasks_overlap(a, b):
    wa = (
        a.get("write_scopes")
        or []
    )

    wb = (
        b.get("write_scopes")
        or []
    )

    if not wa or not wb:
        return False

    return any(
        scopes_overlap(x, y)
        for x in wa
        for y in wb
    )

def validate_parallel(tasks):
    for task in tasks:
        validate_worker_role(task)

    if len(tasks) > MAX_PARALLEL:
        raise RuntimeError(
            "DIRECTOR_MAX_PARALLEL_EXCEEDED"
        )

    for i, a in enumerate(tasks):
        for b in tasks[i + 1:]:
            if tasks_overlap(a, b):
                raise RuntimeError(
                    "DIRECTOR_OVERLAPPING_WRITE_SCOPES:"
                    f"{a['task_id']}:"
                    f"{b['task_id']}"
                )

WORKER_ROLES = {
    "researcher",
    "implementer",
    "verifier",
}


def validate_worker_role(task):
    role = task.get("role")

    if role not in WORKER_ROLES:
        raise ValueError(
            "INVALID_WORKER_ROLE:"
            f"{role!r}; expected one of "
            f"{sorted(WORKER_ROLES)}"
        )

    write_scopes = (
        task.get("write_scopes")
        or []
    )

    if role in {
        "researcher",
        "verifier",
    } and write_scopes:
        raise ValueError(
            f"{role.upper()}_MUST_BE_READ_ONLY:"
            f"{task.get('task_id')}"
        )

    return role


def validate_decision(value):
    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            "DIRECTOR_DECISION_NOT_OBJECT"
        )

    status = value.get(
        "project_status"
    )

    if status not in {
        "CONTINUE",
        "COMPLETE",
        "BLOCKED",
    }:
        raise RuntimeError(
            f"INVALID_PROJECT_STATUS={status}"
        )

    tasks = value.get(
        "tasks"
    )

    if not isinstance(
        tasks,
        list,
    ):
        raise RuntimeError(
            "DIRECTOR_TASKS_NOT_LIST"
        )

    if (
        status == "CONTINUE"
        and not tasks
    ):
        raise RuntimeError(
            "CONTINUE_WITHOUT_TASKS"
        )

    if (
        status in {
            "COMPLETE",
            "BLOCKED",
        }
        and tasks
    ):
        raise RuntimeError(
            "TERMINAL_STATUS_WITH_TASKS"
        )

    seen = set()

    for task in tasks:
        if not isinstance(
            task,
            dict,
        ):
            raise RuntimeError(
                "TASK_NOT_OBJECT"
            )

        required = {
            "task_id",
            "objective",
            "write_scopes",
            "read_scopes",
            "acceptance_criteria",
        }

        missing = (
            required
            - set(task)
        )

        if missing:
            raise RuntimeError(
                f"TASK_MISSING_FIELDS={sorted(missing)}"
            )

        task["task_id"] = safe_id(
            task["task_id"]
        )

        if task["task_id"] in seen:
            raise RuntimeError(
                "DUPLICATE_TASK_ID="
                + task["task_id"]
            )

        seen.add(
            task["task_id"]
        )

        if not isinstance(
            task["write_scopes"],
            list,
        ):
            raise RuntimeError(
                "WRITE_SCOPES_NOT_LIST"
            )

        if not isinstance(
            task["read_scopes"],
            list,
        ):
            raise RuntimeError(
                "READ_SCOPES_NOT_LIST"
            )

        timeout = int(
            task.get(
                "timeout_seconds",
                7200,
            )
        )

        if timeout < 1:
            raise RuntimeError(
                "INVALID_TASK_TIMEOUT"
            )

        task[
            "timeout_seconds"
        ] = timeout

    validate_parallel(tasks)

    return value

def parse_json_response(raw):
    raw = raw.strip()

    if not raw:
        raise RuntimeError(
            "EMPTY_DIRECTOR_RESPONSE"
        )

    try:
        outer = json.loads(raw)
    except json.JSONDecodeError:
        outer = None

    if isinstance(
        outer,
        dict,
    ):
        for key in (
            "response",
            "reply",
            "result",
        ):
            value = outer.get(key)

            if isinstance(
                value,
                str,
            ):
                candidate = (
                    value.strip()
                )

                try:
                    return json.loads(
                        candidate
                    )
                except json.JSONDecodeError:
                    pass

        if (
            "project_status"
            in outer
        ):
            return outer

    start = raw.find("{")
    end = raw.rfind("}")

    if (
        start >= 0
        and end > start
    ):
        candidate = raw[
            start:end + 1
        ]

        try:
            return json.loads(
                candidate
            )
        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        "DIRECTOR_RESPONSE_NOT_JSON"
    )

def current_state_path(run_id):
    return (
        DIRECTOR_ROOT
        / f"{run_id}.state.json"
    )

def objective_path(run_id):
    return (
        OBJECTIVES
        / f"{run_id}.objective.md"
    )

def _default_history_totals():
    return {
        "completed": 0,
        "failed": 0,
        "blocked": 0,
        "archived": 0,
    }


def _default_archived_summary():
    return {
        "completed_count": 0,
        "failed_count": 0,
        "blocked_count": 0,
        "latest_archived_cycle": 0,
    }


def _normalize_bounded_state(state):
    state = dict(state)

    state.setdefault("completed_tasks", [])
    state.setdefault("failed_tasks", [])
    state.setdefault("blocked_tasks", [])
    state.setdefault("last_handoffs", [])

    totals = _default_history_totals()
    existing_totals = state.get("history_totals")

    if isinstance(existing_totals, dict):
        for key in totals:
            try:
                totals[key] = int(
                    existing_totals.get(
                        key,
                        totals[key],
                    )
                )
            except (TypeError, ValueError):
                pass
    else:
        totals["completed"] = len(
            state["completed_tasks"]
        )
        totals["failed"] = len(
            state["failed_tasks"]
        )
        totals["blocked"] = len(
            state["blocked_tasks"]
        )

    summary = _default_archived_summary()
    existing_summary = state.get(
        "archived_summary"
    )

    if isinstance(existing_summary, dict):
        for key in summary:
            try:
                summary[key] = int(
                    existing_summary.get(
                        key,
                        summary[key],
                    )
                )
            except (TypeError, ValueError):
                pass

    state["history_totals"] = totals
    state["archived_summary"] = summary

    return state


def _archive_history_records(
    run_id,
    cycle,
    category,
    records,
):
    if not records:
        return None

    run_dir = HISTORY / safe_id(run_id)
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        run_dir
        / (
            f"{int(cycle):06d}."
            f"{category}."
            f"{uuid.uuid4().hex}.json"
        )
    )

    write_json(
        path,
        {
            "run_id": run_id,
            "cycle": int(cycle),
            "category": category,
            "count": len(records),
            "archived_at": utcnow(),
            "records": records,
        },
    )

    return path


def _bound_history_list(
    state,
    run_id,
    category,
    state_key,
    limit,
):
    records = list(
        state.get(
            state_key,
            [],
        )
    )

    overflow = max(
        0,
        len(records) - limit,
    )

    if overflow == 0:
        state[state_key] = records
        return 0

    archived = records[:overflow]

    _archive_history_records(
        run_id,
        state.get("cycle", 0),
        category,
        archived,
    )

    state[state_key] = records[overflow:]

    summary = state[
        "archived_summary"
    ]

    summary_key = (
        f"{category}_count"
    )

    summary[summary_key] = (
        int(
            summary.get(
                summary_key,
                0,
            )
        )
        + overflow
    )

    summary[
        "latest_archived_cycle"
    ] = max(
        int(
            summary.get(
                "latest_archived_cycle",
                0,
            )
        ),
        int(
            state.get(
                "cycle",
                0,
            )
        ),
    )

    state[
        "history_totals"
    ]["archived"] = (
        int(
            state[
                "history_totals"
            ].get(
                "archived",
                0,
            )
        )
        + overflow
    )

    return overflow


def bound_durable_state(
    state,
    run_id=None,
):
    state = _normalize_bounded_state(
        state
    )

    if run_id is None:
        run_id = state.get(
            "run_id",
            "unknown-run",
        )

    _bound_history_list(
        state,
        run_id,
        "completed",
        "completed_tasks",
        ACTIVE_COMPLETED_TASKS_MAX,
    )

    _bound_history_list(
        state,
        run_id,
        "failed",
        "failed_tasks",
        ACTIVE_FAILED_TASKS_MAX,
    )

    _bound_history_list(
        state,
        run_id,
        "blocked",
        "blocked_tasks",
        ACTIVE_BLOCKED_TASKS_MAX,
    )

    state["last_handoffs"] = list(
        state.get(
            "last_handoffs",
            [],
        )
    )[-RECENT_HANDOFFS_MAX:]

    return state


def director_state_view(state):
    state = _normalize_bounded_state(
        state
    )

    return {
        "run_id": state.get("run_id"),
        "status": state.get("status"),
        "created_at": state.get(
            "created_at"
        ),
        "updated_at": state.get(
            "updated_at"
        ),
        "cycle": state.get(
            "cycle",
            0,
        ),
        "summary": state.get(
            "summary",
            "",
        ),
        "history_totals": state.get(
            "history_totals",
            _default_history_totals(),
        ),
        "archived_summary": state.get(
            "archived_summary",
            _default_archived_summary(),
        ),
        "completed_tasks": list(
            state.get(
                "completed_tasks",
                [],
            )
        )[-ACTIVE_COMPLETED_TASKS_MAX:],
        "failed_tasks": list(
            state.get(
                "failed_tasks",
                [],
            )
        )[-ACTIVE_FAILED_TASKS_MAX:],
        "blocked_tasks": list(
            state.get(
                "blocked_tasks",
                [],
            )
        )[-ACTIVE_BLOCKED_TASKS_MAX:],
        "last_handoffs": list(
            state.get(
                "last_handoffs",
                [],
            )
        )[-RECENT_HANDOFFS_MAX:],
        "final_result": state.get(
            "final_result",
            "",
        ),
    }


def write_history_checkpoint(
    state,
):
    run_id = safe_id(
        state.get(
            "run_id",
            "unknown-run",
        )
    )

    run_dir = CHECKPOINTS / run_id
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        run_dir
        / (
            f"{int(state.get('cycle', 0)):06d}"
            ".checkpoint.json"
        )
    )

    write_json(
        path,
        {
            "run_id": run_id,
            "cycle": int(
                state.get(
                    "cycle",
                    0,
                )
            ),
            "created_at": utcnow(),
            "history_totals": state.get(
                "history_totals",
                {},
            ),
            "archived_summary": state.get(
                "archived_summary",
                {},
            ),
        },
    )

    return path

def initialize_state(
    run_id,
    objective,
):
    path = current_state_path(
        run_id
    )

    if path.exists():
        state = read_json(path)
        state = bound_durable_state(
            state,
            run_id,
        )
        write_json(
            path,
            state,
        )
        return state

    state = {
        "run_id": run_id,
        "status": "RUNNING",
        "objective": objective,
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "cycle": 0,
        "summary": (
            "No worker tasks have "
            "completed yet."
        ),
        "completed_tasks": [],
        "failed_tasks": [],
        "blocked_tasks": [],
        "last_handoffs": [],
        "history_totals":
            _default_history_totals(),
        "archived_summary":
            _default_archived_summary(),
        "final_result": "",
    }

    write_json(
        path,
        state,
    )

    return state


def write_director_input(
    run_id,
    cycle,
    state,
):
    path = (
        CYCLES
        / (
            f"{run_id}."
            f"{cycle:04d}.input.json"
        )
    )

    bounded_state = (
        director_state_view(
            state
        )
    )

    payload = {
        "objective_file":
            str(
                objective_path(
                    run_id
                )
            ),

        "state":
            bounded_state,

        "instruction":
            (
                "Read the objective file. "
                "Use the bounded durable state "
                "and recent worker handoffs in "
                "this input. Decide the next "
                "bounded worker tasks or declare "
                "COMPLETE/BLOCKED. Historical "
                "details are archived on disk "
                "and are not automatically "
                "rehydrated."
            ),
    }

    serialized = (
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")

    size = len(serialized)

    if size > DIRECTOR_INPUT_MAX:
        raise RuntimeError(
            "DIRECTOR_INPUT_TOO_LARGE="
            f"{size}>"
            f"{DIRECTOR_INPUT_MAX}"
        )

    path.write_bytes(
        serialized
    )

    return path


def director_bootstrap(
    input_path,
):
    prompt = (
        "You are the Director. "
        "Read and follow this decision "
        "contract: "
        + str(
            PROMPTS
            / "director.txt"
        )
        + ". Read this current input file: "
        + str(input_path)
        + ". Return only the required JSON "
        "decision object."
    )

    size = len(
        prompt.encode("utf-8")
    )

    if (
        size
        > DIRECTOR_BOOTSTRAP_LIMIT
    ):
        raise RuntimeError(
            f"DIRECTOR_BOOTSTRAP_TOO_LARGE={size}"
        )

    return prompt

def run_director_model(
    run_id,
    cycle,
    input_path,
):
    prompt = director_bootstrap(
        input_path
    )

    output_path = (
        CYCLES
        / (
            f"{run_id}."
            f"{cycle:04d}.director.out"
        )
    )

    cmd = [
        str(CN),
        "-p",
        "--config",
        str(CONFIG),
        "--readonly",
        "--format",
        "json",
        prompt,
    ]

    env = os.environ.copy()
    env.pop(
        "FORCE_NO_TTY",
        None,
    )

    started = time.monotonic()

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as out:
        proc = subprocess.Popen(
            cmd,
            cwd=str(PROJECT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )

        try:
            rc = proc.wait(
                timeout=DIRECTOR_TIMEOUT
            )
        except subprocess.TimeoutExpired:
            try:
                os.killpg(
                    proc.pid,
                    15,
                )
            except ProcessLookupError:
                pass

            try:
                proc.wait(
                    timeout=10
                )
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(
                        proc.pid,
                        9,
                    )
                except ProcessLookupError:
                    pass

                proc.wait()

            raise RuntimeError(
                "DIRECTOR_MODEL_TIMEOUT"
            )

    elapsed = (
        time.monotonic()
        - started
    )

    raw = output_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    if rc != 0:
        raise RuntimeError(
            f"DIRECTOR_MODEL_EXIT={rc}:"
            + raw[-1000:]
        )

    decision = validate_decision(
        parse_json_response(
            raw
        )
    )

    decision[
        "_director_seconds"
    ] = round(
        elapsed,
        3,
    )

    decision[
        "_director_output"
    ] = str(
        output_path
    )

    return decision

def write_worker_task(task):
    task_id = safe_id(
        task["task_id"]
    )

    path = (
        TASKS
        / f"{task_id}.json"
    )

    payload = {
        "task_id":
            task_id,

        "role":
            task["role"],

        "objective":
            task["objective"],

        "write_scopes":
            task.get(
                "write_scopes"
            ) or [],

        "read_scopes":
            task.get(
                "read_scopes"
            ) or ["."],

        "acceptance_criteria":
            task.get(
                "acceptance_criteria"
            )
            or (
                "Verify the assigned "
                "objective."
            ),

        "timeout_seconds":
            int(
                task.get(
                    "timeout_seconds",
                    7200,
                )
            ),

        "created_at":
            utcnow(),
    }

    write_json(
        path,
        payload,
    )

    return path

def execute_worker(task):
    task_id = safe_id(
        task["task_id"]
    )

    write_worker_task(
        task
    )

    proc = subprocess.run(
        [
            str(RUNTIME),
            "run",
            task_id,
        ],
        cwd=str(PROJECT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    result_path = (
        RESULTS
        / f"{task_id}.json"
    )

    if not result_path.exists():
        return {
            "task_id": task_id,
            "status": "FAILED",
            "executed":
                "Worker runtime did not "
                "produce a result file.",
            "result":
                f"RUNTIME_EXIT={proc.returncode}",
            "files_changed": "UNKNOWN",
            "artifacts": "NONE",
            "verification":
                proc.stdout[-2000:],
            "blockers":
                "WORKER_RESULT_MISSING",
            "completed_at":
                utcnow(),
        }

    result = read_json(
        result_path
    )

    return result

def execute_batch(tasks):
    validate_parallel(
        tasks
    )

    if len(tasks) == 1:
        return [
            execute_worker(
                tasks[0]
            )
        ]

    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(tasks)
    ) as pool:

        future_map = {
            pool.submit(
                execute_worker,
                task,
            ): task["task_id"]
            for task in tasks
        }

        for future in (
            concurrent.futures.as_completed(
                future_map
            )
        ):
            results.append(
                future.result()
            )

    return results

def compact_handoff(result):
    allowed = (
        "task_id",
        "role",
        "status",
        "executed",
        "result",
        "files_changed",
        "artifacts",
        "verification",
        "blockers",
        "completed_at",
    )

    return {
        key: result.get(key)
        for key in allowed
    }

def update_state(
    state,
    decision,
    results,
):
    state = _normalize_bounded_state(
        state
    )

    state["cycle"] = (
        int(
            state.get(
                "cycle",
                0,
            )
        )
        + 1
    )

    state["updated_at"] = (
        utcnow()
    )

    state["summary"] = (
        decision.get(
            "summary",
            state.get(
                "summary",
                "",
            ),
        )
    )

    handoffs = [
        compact_handoff(r)
        for r in results
    ]

    state[
        "last_handoffs"
    ] = (
        list(
            state.get(
                "last_handoffs",
                [],
            )
        )
        + handoffs
    )[-RECENT_HANDOFFS_MAX:]

    for result in results:
        status = result.get(
            "status"
        )

        task_id = result.get(
            "task_id"
        )

        record = {
            "task_id":
                task_id,

            "role":
                result.get("role"),

            "status":
                status,

            "result":
                result.get(
                    "result"
                ),

            "verification":
                result.get(
                    "verification"
                ),

            "files_changed":
                result.get(
                    "files_changed"
                ),

            "artifacts":
                result.get(
                    "artifacts"
                ),

            "blockers":
                result.get(
                    "blockers"
                ),
        }

        if status == "PASS":
            state[
                "completed_tasks"
            ].append(record)

            state[
                "history_totals"
            ]["completed"] += 1

        elif status == "BLOCKED":
            state[
                "blocked_tasks"
            ].append(record)

            state[
                "history_totals"
            ]["blocked"] += 1

        else:
            state[
                "failed_tasks"
            ].append(record)

            state[
                "history_totals"
            ]["failed"] += 1

    state = bound_durable_state(
        state,
        state.get(
            "run_id",
            "unknown-run",
        ),
    )

    write_history_checkpoint(
        state
    )

    return state


def archive_handoffs(
    run_id,
    cycle,
    results,
):
    path = (
        HANDOFFS
        / (
            f"{run_id}."
            f"{cycle:04d}.json"
        )
    )

    write_json(
        path,
        [
            compact_handoff(r)
            for r in results
        ],
    )

def run_loop(
    run_id,
    objective,
    max_cycles,
):
    objective_file = (
        objective_path(
            run_id
        )
    )

    if not objective_file.exists():
        objective_file.write_text(
            objective.strip()
            + "\n",
            encoding="utf-8",
        )

    state = initialize_state(
        run_id,
        objective,
    )

    start_cycle = int(
        state.get(
            "cycle",
            0,
        )
    )

    for cycle in range(
        start_cycle + 1,
        max_cycles + 1,
    ):
        print()
        print(
            f"===== DIRECTOR CYCLE "
            f"{cycle} =====",
            flush=True,
        )

        input_path = (
            write_director_input(
                run_id,
                cycle,
                state,
            )
        )

        decision = (
            run_director_model(
                run_id,
                cycle,
                input_path,
            )
        )

        decision_path = (
            DECISIONS
            / (
                f"{run_id}."
                f"{cycle:04d}.json"
            )
        )

        write_json(
            decision_path,
            decision,
        )

        print(
            "PROJECT_STATUS=",
            decision[
                "project_status"
            ],
            flush=True,
        )

        print(
            "SUMMARY=",
            decision.get(
                "summary",
                "",
            ),
            flush=True,
        )

        status = decision[
            "project_status"
        ]

        if status in {
            "COMPLETE",
            "BLOCKED",
        }:
            state[
                "status"
            ] = status

            state[
                "summary"
            ] = decision.get(
                "summary",
                state.get(
                    "summary",
                    "",
                ),
            )

            state[
                "final_result"
            ] = decision.get(
                "final_result",
                "",
            )

            state[
                "updated_at"
            ] = utcnow()

            write_json(
                current_state_path(
                    run_id
                ),
                state,
            )

            print(
                "FINAL_RESULT=",
                state[
                    "final_result"
                ],
                flush=True,
            )

            return (
                0
                if status
                == "COMPLETE"
                else 2
            )

        tasks = decision[
            "tasks"
        ]

        print(
            "TASK_COUNT=",
            len(tasks),
            flush=True,
        )

        for task in tasks:
            print(
                "TASK=",
                task["task_id"],
                flush=True,
            )

        results = execute_batch(
            tasks
        )

        archive_handoffs(
            run_id,
            cycle,
            results,
        )

        for result in results:
            print(
                "HANDOFF=",
                result.get(
                    "task_id"
                ),
                result.get(
                    "status"
                ),
                flush=True,
            )

        state = update_state(
            state,
            decision,
            results,
        )

        write_json(
            current_state_path(
                run_id
            ),
            state,
        )

    state["status"] = (
        "MAX_CYCLES"
    )

    state["updated_at"] = (
        utcnow()
    )

    state["final_result"] = (
        f"Stopped after "
        f"{max_cycles} cycles."
    )

    write_json(
        current_state_path(
            run_id
        ),
        state,
    )

    print(
        "MAX_CYCLES_REACHED=YES"
    )

    return 3

def status_command(args):
    path = current_state_path(
        safe_id(
            args.run_id
        )
    )

    if not path.exists():
        raise RuntimeError(
            "DIRECTOR_RUN_NOT_FOUND"
        )

    print(
        path.read_text()
    )

def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    p = sub.add_parser(
        "run"
    )

    p.add_argument(
        "run_id"
    )

    p.add_argument(
        "objective"
    )

    p.add_argument(
        "--max-cycles",
        type=int,
        default=MAX_CYCLES_DEFAULT,
    )

    p = sub.add_parser(
        "resume"
    )

    p.add_argument(
        "run_id"
    )

    p.add_argument(
        "--max-cycles",
        type=int,
        default=MAX_CYCLES_DEFAULT,
    )

    p = sub.add_parser(
        "status"
    )

    p.add_argument(
        "run_id"
    )

    args = parser.parse_args()

    try:
        if args.command == "run":
            run_id = safe_id(
                args.run_id
            )

            return run_loop(
                run_id,
                args.objective,
                args.max_cycles,
            )

        if args.command == "resume":
            run_id = safe_id(
                args.run_id
            )

            op = objective_path(
                run_id
            )

            if not op.exists():
                raise RuntimeError(
                    "OBJECTIVE_NOT_FOUND"
                )

            objective = op.read_text(
                encoding="utf-8"
            )

            return run_loop(
                run_id,
                objective,
                args.max_cycles,
            )

        if args.command == "status":
            status_command(
                args
            )

            return 0

        raise RuntimeError(
            "UNKNOWN_COMMAND"
        )

    except Exception as exc:
        print(
            f"ERROR={exc}",
            file=sys.stderr,
        )

        return 1

if __name__ == "__main__":
    raise SystemExit(
        main()
    )
