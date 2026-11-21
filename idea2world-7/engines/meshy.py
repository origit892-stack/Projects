"""Meshy engine -- text-to-3D hero assets (the user's 3D model tool).

Real two-step API (docs.meshy.ai): ``POST /openapi/v2/text-to-3d`` with ``mode="preview"``
(mesh only) -> poll ``GET /openapi/v2/text-to-3d/{id}`` -> ``mode="refine"`` with the
preview's id (textured model). The result carries model file URLs (GLB/OBJ) that the import
pipeline can download and validate before going into Roblox.

Without ``MESHY_API_KEY`` the engine is honest (``skipped``) and the asset factory keeps
using its layered part recipes. Meshy is a paid service -- we never assume a key.
"""
from __future__ import annotations

import os
import time
from typing import Any

from .base import BaseEngine, EngineResult, HttpClient

API_BASE = "https://api.meshy.ai/openapi/v2"


class MeshyEngine(BaseEngine):
    name = "meshy"
    label = "Meshy"
    purpose = "Text -> 3D model (preview mesh -> refined textured GLB)"

    def __init__(self, api_key: str = "", client: HttpClient | None = None,
                 poll_interval: float = 3.0, timeout_s: float = 600.0):
        self.api_key = api_key or os.environ.get("MESHY_API_KEY", "").strip()
        self.client = client or HttpClient(base_url=API_BASE)
        self.poll_interval = poll_interval
        self.timeout_s = timeout_s

    def available(self) -> dict:
        if self.api_key:
            return {"engine": self.name, "live": True, "reason": "MESHY_API_KEY configured"}
        return {"engine": self.name, "live": False,
                "reason": "No MESHY_API_KEY. Layered part recipes will be used for assets "
                          "instead of generated meshes."}

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    # -- steps -----------------------------------------------------------------------
    def create_preview(self, prompt: str, ai_model: str | None = None) -> dict:
        body: dict[str, Any] = {"mode": "preview", "prompt": prompt}
        if ai_model:
            body["ai_model"] = ai_model
        _, data = self.client.post_json("/text-to-3d", body, headers=self._headers())
        return data if isinstance(data, dict) else {}

    def get_task(self, task_id: str) -> dict:
        _, data = self.client.get_json(f"/text-to-3d/{task_id}", headers=self._headers())
        return data if isinstance(data, dict) else {}

    def wait_for_task(self, task_id: str) -> dict:
        deadline = time.time() + self.timeout_s
        last: dict = {}
        while time.time() < deadline:
            last = self.get_task(task_id)
            state = str(last.get("status", ""))
            if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
                return last
            time.sleep(self.poll_interval)
        return {**last, "status": "TIMEOUT"}

    def create_refine(self, preview_task_id: str, texture_model: str | None = None) -> dict:
        body: dict[str, Any] = {"mode": "refine", "preview_task_id": preview_task_id}
        if texture_model:
            body["texture_model"] = texture_model
        _, data = self.client.post_json("/text-to-3d", body, headers=self._headers())
        return data if isinstance(data, dict) else {}

    # -- build entry point ------------------------------------------------------------
    def build(self, prompt: str, textured: bool = True, ai_model: str | None = None,
              texture_model: str | None = None, **_) -> EngineResult:
        started = time.time()
        status = self.available()
        if not status["live"]:
            return EngineResult(self.name, "skipped", notes=[status["reason"]], seconds=time.time() - started)
        notes: list[str] = []
        try:
            preview = self.create_preview(prompt, ai_model=ai_model)
            preview_id = preview.get("result") or preview.get("id")
            if not preview_id:
                return EngineResult(self.name, "error",
                                    error=f"preview create failed: {str(preview)[:300]}",
                                    seconds=time.time() - started)
            notes.append(f"preview task {preview_id}")
            preview_result = self.wait_for_task(preview_id)
            if preview_result.get("status") != "SUCCEEDED":
                return EngineResult(self.name, "error",
                                    error=f"preview task {preview_result.get('status')}",
                                    payload={"preview": preview_result}, notes=notes,
                                    seconds=time.time() - started)
            payload = {"preview_task_id": preview_id, "preview": preview_result, "models": _model_urls(preview_result)}
            if not textured:
                return EngineResult(self.name, "ok", payload=payload, notes=notes, seconds=time.time() - started)
            refine = self.create_refine(preview_id, texture_model=texture_model)
            refine_id = refine.get("result") or refine.get("id")
            if not refine_id:
                return EngineResult(self.name, "error",
                                    error=f"refine create failed: {str(refine)[:300]}",
                                    payload=payload, notes=notes, seconds=time.time() - started)
            notes.append(f"refine task {refine_id}")
            refine_result = self.wait_for_task(refine_id)
            if refine_result.get("status") != "SUCCEEDED":
                return EngineResult(self.name, "error",
                                    error=f"refine task {refine_result.get('status')}",
                                    payload=payload, notes=notes, seconds=time.time() - started)
            payload["refine_task_id"] = refine_id
            payload["refine"] = refine_result
            payload["models"] = _model_urls(refine_result)
            return EngineResult(self.name, "ok", payload=payload, notes=notes, seconds=time.time() - started)
        except Exception as exc:  # noqa: BLE001
            return EngineResult(self.name, "error", error=str(exc)[:400], notes=notes, seconds=time.time() - started)


def _model_urls(task: dict) -> list[str]:
    urls: list[str] = []
    for key in ("models", "result", "outputs"):
        value = task.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for url_key in ("url", "preview_url", "download_url", "model_url"):
                        if item.get(url_key):
                            urls.append(str(item[url_key]))
                elif isinstance(item, str):
                    urls.append(item)
        elif isinstance(value, dict):
            for url_key in ("url", "preview_url", "download_url"):
                if value.get(url_key):
                    urls.append(str(value[url_key]))
    return urls
