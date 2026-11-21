"""Background jobs for long-running world creation and Studio builds.

The HTTP layer must stay responsive: a build can take minutes in Studio, and the World Plan screen
needs to poll progress. Jobs keep an event log so the UI can show the crew thinking, stage by stage.
"""
from __future__ import annotations

import threading
import time
import traceback
import uuid


class Job:
    def __init__(self, kind: str, meta: dict | None = None):
        self.id = uuid.uuid4().hex[:12]
        self.kind = kind
        self.meta = meta or {}
        self.status = "queued"
        self.progress = 0.0
        self.events: list[dict] = []
        self.result = None
        self.error = ""
        self.created = time.time()
        self.finished = 0.0
        self._cancel = threading.Event()

    def emit(self, event: dict) -> None:
        event = {**event, "job": self.id}
        self.events.append(event)
        if len(self.events) > 600:
            self.events = self.events[-400:]
        if event.get("type") == "stage_start":
            self.progress = min(0.95, self.progress + 0.02)
        elif event.get("type") == "stage_done":
            total = event.get("total_stages") or 12
            self.progress = min(0.97, self.progress + 1.0 / max(1, total))
        elif event.get("type") == "pipeline_start":
            self.status = "running"
            self.progress = 0.02

    @property
    def cancelled(self) -> bool:
        return self._cancel.is_set()

    def cancel(self) -> None:
        self._cancel.set()

    def to_dict(self, include_events: bool = True, event_cursor: int = 0) -> dict:
        payload = {
            "id": self.id, "kind": self.kind, "status": self.status,
            "progress": round(self.progress, 3), "error": self.error,
            "created": self.created, "finished": self.finished,
            "seconds": round((self.finished or time.time()) - self.created, 1),
            "meta": self.meta,
            "event_count": len(self.events),
        }
        if include_events:
            payload["events"] = self.events[event_cursor:]
        if self.result is not None and self.status in ("done", "failed"):
            payload["result"] = self.result
        return payload


class JobManager:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def start(self, kind: str, fn, meta: dict | None = None) -> Job:
        job = Job(kind, meta)
        with self._lock:
            self.jobs[job.id] = job

        def runner() -> None:
            job.status = "running"
            try:
                result = fn(job)
                if job.cancelled:
                    job.status = "cancelled"
                else:
                    job.status = "done"
                    job.result = result
                    job.progress = 1.0
            except Exception as exc:  # noqa: BLE001 - job failures are reported, not raised
                job.status = "failed"
                job.error = f"{exc}"
                job.emit({"type": "job_failed", "error": str(exc),
                          "traceback": traceback.format_exc(limit=8)})
            finally:
                job.finished = time.time()

        thread = threading.Thread(target=runner, name=f"job-{job.id}", daemon=True)
        thread.start()
        return job

    def get(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def list(self, limit: int = 20) -> list[dict]:
        jobs = sorted(self.jobs.values(), key=lambda j: j.created, reverse=True)[:limit]
        return [job.to_dict(include_events=False) for job in jobs]

    def prune(self, keep: int = 40) -> None:
        if len(self.jobs) <= keep:
            return
        ordered = sorted(self.jobs.values(), key=lambda j: j.created)
        for job in ordered[:len(self.jobs) - keep]:
            self.jobs.pop(job.id, None)
