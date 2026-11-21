"""Dependency-aware stage scheduler for the crew pipeline.

Stages declare dependencies, so independent work (references + art direction + game design) runs in
parallel while the build stays strictly ordered. A failure marks the task failed and skips only its
dependents -- the pipeline reports what is missing instead of producing a half-world silently.
"""
from __future__ import annotations

import time
import traceback
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from dataclasses import dataclass, field


@dataclass
class StageTask:
    name: str
    fn: callable
    deps: tuple[str, ...] = ()
    timeout: float | None = None
    weight: float = 1.0
    optional: bool = False
    status: str = "pending"
    result: object = None
    error: str = ""
    seconds: float = 0.0


class TaskScheduler:
    def __init__(self, max_workers: int = 4):
        self.tasks: dict[str, StageTask] = {}
        self.order: list[str] = []
        self.max_workers = max_workers

    def add(self, name: str, fn, deps: tuple[str, ...] = (), timeout: float | None = None,
            weight: float = 1.0, optional: bool = False) -> "TaskScheduler":
        if name in self.tasks:
            raise ValueError(f"duplicate stage '{name}'")
        missing = [d for d in deps if d not in self.tasks]
        if missing:
            raise ValueError(f"stage '{name}' depends on unknown stage(s): {missing}")
        self.tasks[name] = StageTask(name=name, fn=fn, deps=deps, timeout=timeout,
                                     weight=weight, optional=optional)
        self.order.append(name)
        return self

    def run(self, context: dict | None = None, parallel: bool = True, on_event=None) -> dict:
        context = context if context is not None else {}
        started = time.time()
        pending = set(self.tasks)
        running: dict = {}
        start_times: dict = {}
        executor = ThreadPoolExecutor(max_workers=max(1, self.max_workers if parallel else 1))
        state = {"done": 0, "total_weight": sum(t.weight for t in self.tasks.values()) or 1.0}

        def emit(event: dict) -> None:
            if on_event:
                try:
                    on_event(event)
                except Exception:  # noqa: BLE001 - UI callbacks must never break the build
                    pass

        def progress() -> float:
            finished = sum(t.weight for t in self.tasks.values() if t.status in ("done", "failed", "skipped"))
            return round(min(1.0, finished / state["total_weight"]), 3)

        try:
            while pending or running:
                # Dispatch every task whose dependencies succeeded.
                for name in list(pending):
                    task = self.tasks[name]
                    dep_states = [self.tasks[d].status for d in task.deps]
                    if any(s in ("failed", "skipped") for s in dep_states):
                        task.status = "skipped"
                        task.error = "dependency failed"
                        pending.discard(name)
                        emit({"type": "stage_skipped", "stage": name, "progress": progress()})
                        continue
                    if all(s == "done" for s in dep_states):
                        pending.discard(name)
                        entry = {"stage": name}
                        context.setdefault("stage_results", {})[name] = entry

                        def runner(task=task, entry=entry):
                            t0 = time.time()
                            try:
                                result = task.fn(context)
                                entry["result"] = result
                                return ("done", result, time.time() - t0)
                            except Exception as exc:  # noqa: BLE001 - surface, never swallow
                                entry["error"] = str(exc)
                                entry["traceback"] = traceback.format_exc(limit=6)
                                return ("failed", exc, time.time() - t0)

                        future = executor.submit(runner)
                        running[future] = task
                        start_times[future] = time.time()
                        task.status = "running"
                        emit({"type": "stage_start", "stage": name, "progress": progress()})
                if not running:
                    if pending:
                        # Dependency cycle or unsatisfiable graph.
                        for name in pending:
                            self.tasks[name].status = "skipped"
                            self.tasks[name].error = "unresolvable dependency graph"
                        pending.clear()
                    break
                finished, _ = wait(list(running), return_when=FIRST_COMPLETED,
                                    timeout=1.0)
                for future in finished:
                    task = running.pop(future)
                    start_times.pop(future, None)
                    status, payload, seconds = future.result()
                    task.status = status
                    task.seconds = round(seconds, 2)
                    if status == "done":
                        task.result = payload
                        emit({"type": "stage_done", "stage": task.name, "seconds": task.seconds,
                              "progress": progress()})
                    else:
                        task.error = str(payload)
                        emit({"type": "stage_failed", "stage": task.name, "error": task.error,
                              "progress": progress()})
                        if not task.optional:
                            context.setdefault("failures", []).append(task.name)
                # Timeout enforcement for still-running tasks.
                now = time.time()
                for future, task in list(running.items()):
                    began = start_times.get(future, started)
                    if task.timeout and (now - began) > task.timeout:
                        running.pop(future, None)
                        start_times.pop(future, None)
                        task.status = "failed"
                        task.error = f"timed out after {task.timeout}s"
                        task.seconds = round(now - began, 2)
                        emit({"type": "stage_timeout", "stage": task.name, "error": task.error,
                              "progress": progress()})
                        if not task.optional:
                            context.setdefault("failures", []).append(task.name)
        finally:
            executor.shutdown(wait=False)

        summary = {
            "passed": not any(t.status == "failed" for t in self.tasks.values() if not t.optional),
            "seconds": round(time.time() - started, 2),
            "stages": [{"name": t.name, "status": t.status, "seconds": t.seconds,
                        "error": t.error, "optional": t.optional} for t in self.tasks.values()],
            "failed": [t.name for t in self.tasks.values() if t.status == "failed"],
        }
        context["scheduler_report"] = summary
        return summary
