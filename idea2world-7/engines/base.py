"""Engine plumbing: a tiny stdlib HTTP client, an engine base class and an honest result type.

Design rules (inherited from 6.0):
  * stdlib only (urllib) so the app stays pip-free;
  * an engine reports which tool actually ran, with an honest status (ok / simulated / error /
    skipped) and a note a human can read -- never a silent fake;
  * the transport is injectable so every engine is testable without a network or a real key.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

__all__ = ["EngineResult", "BaseEngine", "EngineTransportError", "HttpError", "HttpClient", "real_transport"]

_RETRYABLE_HTTP = {429, 500, 502, 503, 504}


class EngineTransportError(RuntimeError):
    """Network or transport failure after all retries."""


@dataclass
class HttpError(Exception):
    """A finished HTTP exchange whose status is not 2xx. The body is kept for diagnostics."""

    status: int
    text: str = ""
    url: str = ""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"HTTP {self.status} for {self.url}: {self.text[:300]}"


class HttpClient:
    """JSON-over-HTTP with retry. `transport` is injectable for tests."""

    def __init__(self, transport: Callable | None = None, timeout: float = 45.0, retries: int = 2,
                 sleep: float = 1.0, base_url: str = ""):
        self._transport = transport or real_transport
        self.timeout = timeout
        self.retries = retries
        self._sleep = sleep
        self.base_url = (base_url or "").rstrip("/")

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}" if self.base_url else path

    def request(self, method: str, path: str, body: dict | list | None = None,
                headers: dict | None = None, retries: int | None = None) -> tuple[int, object]:
        url = self._url(path)
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        sent_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        sent_headers.update(headers or {})
        last_error: Exception | None = None
        attempts = self.retries if retries is None else retries
        for attempt in range(attempts + 1):
            try:
                status, raw = self._transport(method.upper(), url, data, sent_headers, self.timeout)
                text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw or "")
                if 200 <= status < 300:
                    try:
                        return status, json.loads(text) if text else {}
                    except json.JSONDecodeError:
                        return status, text
                last_error = HttpError(status, text, url)
                if status not in _RETRYABLE_HTTP or attempt >= attempts:
                    raise last_error
            except HttpError:
                raise
            except (urllib.error.URLError, OSError) as exc:
                last_error = exc
                if attempt >= attempts:
                    break
            time.sleep(self._sleep * (attempt + 1))
        raise EngineTransportError(f"{method.upper()} {url} failed after {attempts + 1} attempts: {last_error}")

    def get_json(self, path: str, headers: dict | None = None) -> tuple[int, object]:
        return self.request("GET", path, headers=headers)

    def post_json(self, path: str, body: dict | list | None = None, headers: dict | None = None) -> tuple[int, object]:
        return self.request("POST", path, body=body, headers=headers)


def real_transport(method: str, url: str, data: bytes | None, headers: dict, timeout: float) -> tuple[int, bytes]:
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        return exc.code, body.encode("utf-8")


@dataclass
class EngineResult:
    """The outcome of one engine run. `status` is one of ok / simulated / error / skipped."""

    engine: str
    status: str
    payload: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    error: str = ""
    seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return self.status in ("ok", "simulated")

    def to_dict(self) -> dict:
        return {"engine": self.engine, "status": self.status, "ok": self.ok,
                "payload": self.payload, "notes": self.notes, "error": self.error,
                "seconds": round(self.seconds, 2)}


class BaseEngine:
    """An engine is a tool wrapper. Subclasses set `name` and implement `build`."""

    name = "base"
    label = ""
    purpose = ""

    def available(self) -> dict:
        return {"engine": self.name, "live": False, "reason": "not configured"}

    def build(self, *args, **kwargs) -> EngineResult:  # pragma: no cover - interface
        raise NotImplementedError
