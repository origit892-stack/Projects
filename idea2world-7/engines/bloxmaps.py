"""BloxMaps engine -- prompt-to-complete-Roblox-map, the user's primary map tool.

Two real paths (both documented by BloxMaps; neither is faked):

1. **API** (when a ``BLOXMAPS_API_KEY`` is present): ``POST /api/v1/maps`` -> poll
   ``GET /api/v1/maps/{id}`` until done -> optionally ``POST /maps/{id}/export`` (spends
   credits, needs an ``Idempotency-Key``) -> the export ``manifest`` lists model URLs the
   Studio plugin builds from. Export only happens when the caller sets ``confirm_export``
   (credits are real money); by default we stop at a generated map with preview pictures.

2. **Studio plugin** (when the BloxMaps Cloud plugin is signed in and the place is open in
   Studio): a one-line ``_G.BloxMaps:GenerateMap(prompt, {...})`` run through the Studio MCP
   ``execute_luau`` tool. Only in Edit mode. We detect the plugin by probing CoreGui.

If neither is configured the engine returns an honest ``skipped`` result with a note, and the
orchestrator falls back to the local procedural world builder (6.0's engine).
"""
from __future__ import annotations

import time
import uuid
from typing import Any

from .base import BaseEngine, EngineResult, HttpClient

API_BASE = "https://bloxmaps.com/api/v1"

SIZES = ("small", "medium", "large", "huge", "extra_huge", "ultra_huge", "insanely_huge")
# export credit cost per size, per the BloxMaps docs (used for honest pre-export warnings)
EXPORT_COSTS = {"small": 1, "medium": 2, "large": 4, "huge": 8,
                "extra_huge": 12, "ultra_huge": 16, "insanely_huge": 24}


class BloxMapsEngine(BaseEngine):
    name = "bloxmaps"
    label = "BloxMaps"
    purpose = "Prompt -> complete Roblox map (terrain, water, paths, buildings, vegetation, lighting)"

    def __init__(self, api_key: str = "", client: HttpClient | None = None,
                 studio_client: Any = None, poll_interval: float = 2.0, timeout_s: float = 900.0):
        import os
        self.api_key = api_key or os.environ.get("BLOXMAPS_API_KEY", "").strip()
        self.client = client or HttpClient(base_url=API_BASE)
        self.studio_client = studio_client
        self.poll_interval = poll_interval
        self.timeout_s = timeout_s

    # -- status ----------------------------------------------------------------------
    def available(self) -> dict:
        if self.api_key:
            return {"engine": self.name, "live": True, "path": "api",
                    "reason": "BLOXMAPS_API_KEY configured"}
        if self.studio_client is not None and self._plugin_present():
            return {"engine": self.name, "live": True, "path": "studio_plugin",
                    "reason": "BloxMaps Cloud plugin detected in Studio"}
        return {"engine": self.name, "live": False, "path": None,
                "reason": "No BLOXMAPS_API_KEY and no BloxMaps plugin in Studio. "
                          "The local procedural world builder will be used instead."}

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _plugin_present(self) -> bool:
        try:
            result = self.studio_client.execute_luau(
                'local ok, mod = pcall(function() return game:GetService("CoreGui"):FindFirstChild("BloxMaps") end)\n'
                'return { present = ok ~= nil and mod ~= nil }', timeout=30)
            payload = result.get("json") or {}
            return bool(payload.get("present"))
        except Exception:  # noqa: BLE001 - probe failure means "not there"
            return False

    # -- API path --------------------------------------------------------------------
    def start_map(self, prompt: str, size: str = "medium", theme: str | None = None,
                  time_of_day: str | None = None, layout: str | None = None,
                  seed: int | None = None, must_haves: list[str] | None = None) -> dict:
        body: dict[str, Any] = {"prompt": prompt[:300]}
        if size in SIZES:
            body["size"] = size
        if theme:
            body["theme"] = theme
        if time_of_day:
            body["time"] = time_of_day
        if layout:
            body["layout"] = layout
        if seed is not None:
            body["seed"] = int(seed)
        if must_haves:
            body["must_haves"] = list(must_haves[:6])
        status, data = self.client.post_json("/maps", body, headers=self._headers())
        return {"status": status, "map": data if isinstance(data, dict) else {}}

    def get_map(self, map_id: str) -> dict:
        _, data = self.client.get_json(f"/maps/{map_id}", headers=self._headers())
        return data if isinstance(data, dict) else {}

    def wait_for_map(self, map_id: str) -> dict:
        deadline = time.time() + self.timeout_s
        last: dict = {}
        while time.time() < deadline:
            last = self.get_map(map_id)
            state = str(last.get("status", ""))
            if state in ("done", "failed"):
                return last
            time.sleep(self.poll_interval)
        return {**last, "status": "timeout"}

    def export_map(self, map_id: str, max_credits: int = 24) -> dict:
        idempotency = f"i2w-{int(time.time())}-{uuid.uuid4().hex[:10]}"
        _, data = self.client.post_json(
            f"/maps/{map_id}/export", {"max_credits": max_credits},
            headers={**self._headers(), "Idempotency-Key": idempotency})
        return data if isinstance(data, dict) else {}

    def balance(self) -> dict:
        _, data = self.client.get_json("/balance", headers=self._headers())
        return data if isinstance(data, dict) else {}

    # -- Studio plugin path ----------------------------------------------------------
    def studio_generate(self, prompt: str, size: str = "medium", must_haves: list[str] | None = None,
                        theme: str | None = None, time_of_day: str | None = None) -> dict:
        options = [f'size = "{size}"']
        if theme:
            options.append(f'theme = "{theme}"')
        if time_of_day:
            options.append(f'time = "{time_of_day}"')
        if must_haves:
            items = ", ".join(f'"{str(m)[:40]}"' for m in must_haves[:6])
            options.append(f"mustHaves = {{ {items} }}")
        code = (
            'local ok, BloxMaps = pcall(function() return game:GetService("CoreGui"):WaitForChild("BloxMaps", 5) end)\n'
            'if not ok or not BloxMaps then return { ok = false, error = "plugin_missing", '
            'message = "BloxMaps Cloud plugin not signed in" } end\n'
            f'local result = BloxMaps:GenerateMap("{prompt.replace(chr(92), "").replace(chr(34), "")[:280]}", '
            f'{{ {", ".join(options)} }})\n'
            'return { ok = result.ok, error = result.error, message = result.message, '
            'creditsSpent = result.creditsSpent, balance = result.balance, name = result.name }'
        )
        result = self.studio_client.execute_luau(code, timeout=self.timeout_s)
        payload = result.get("json")
        if payload is None:
            payload = _extract(result.get("text", ""))
        return payload or {"ok": False, "error": "no_result", "message": result.get("text", "")[:300]}

    # -- build entry point ------------------------------------------------------------
    def build(self, prompt: str, size: str = "medium", theme: str | None = None,
              time_of_day: str | None = None, seed: int | None = None,
              must_haves: list[str] | None = None, confirm_export: bool = False,
              max_credits: int = 24, **_) -> EngineResult:
        started = time.time()
        status = self.available()
        if not status["live"]:
            return EngineResult(self.name, "skipped", notes=[status["reason"]], seconds=time.time() - started)
        notes: list[str] = []
        try:
            if status["path"] == "api":
                started_map = self.start_map(prompt, size=size, theme=theme,
                                             time_of_day=time_of_day, seed=seed, must_haves=must_haves)
                map_id = (started_map.get("map") or {}).get("id") or (started_map.get("map") or {}).get("map_id")
                if not map_id:
                    return EngineResult(self.name, "error",
                                        error=f"map start returned no id: {str(started_map)[:300]}",
                                        seconds=time.time() - started)
                notes.append(f"map {map_id} started (api)")
                finished = self.wait_for_map(map_id)
                previews = [p for p in (finished.get("previews") or []) if p]
                if finished.get("status") != "done":
                    return EngineResult(self.name, "error", payload={"map_id": map_id, "state": finished},
                                        error=f"map did not finish: {finished.get('status')}",
                                        notes=notes, seconds=time.time() - started)
                payload = {"map_id": map_id, "name": finished.get("name"),
                           "export_size": finished.get("export_size"),
                           "export_cost": finished.get("export_cost"), "previews": previews}
                if confirm_export:
                    notes.append(f"export confirmed (max {max_credits} credits)")
                    export = self.export_map(map_id, max_credits=max_credits)
                    payload["export"] = export
                else:
                    notes.append(f"not exported (would cost {finished.get('export_cost')} credits; "
                                 "pass confirm_export to spend them)")
                return EngineResult(self.name, "ok", payload=payload, notes=notes, seconds=time.time() - started)
            # studio plugin path
            notes.append("using BloxMaps Cloud plugin in Studio")
            result = self.studio_generate(prompt, size=size, must_haves=must_haves,
                                          theme=theme, time_of_day=time_of_day)
            if not result.get("ok"):
                return EngineResult(self.name, "error", payload=result,
                                    error=f"{result.get('error')}: {result.get('message', '')}",
                                    notes=notes, seconds=time.time() - started)
            return EngineResult(self.name, "ok", payload=result, notes=notes, seconds=time.time() - started)
        except Exception as exc:  # noqa: BLE001 - every failure is reported, not swallowed
            return EngineResult(self.name, "error", error=str(exc)[:400], notes=notes, seconds=time.time() - started)


def _extract(text: str) -> dict | None:
    if not text:
        return None
    import json
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None
    return None
