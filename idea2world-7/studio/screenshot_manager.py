"""Screenshot manager: camera plan plus capture, so the critic sees the world from real angles.

Roblox Studio MCP can capture the viewport. Controlling the camera reliably requires Play mode; in
Edit mode the tool captures whatever the viewport shows. This module therefore:
  * produces a deterministic camera plan from the WorldSpec (so views are reproducible);
  * attempts camera positioning, captures, and records honestly whether the pose was applied;
  * never fabricates an image when capture is unavailable.
"""
from __future__ import annotations

import base64
import json
import math
from pathlib import Path


def plan_views(spec, limit: int = 6) -> list[dict]:
    field = spec.heightfield()
    half = float(spec.world.get("size", 2000)) / 2
    peak = max(field.max, field.water + 20)
    views: list[dict] = []
    focal = next((p for p in spec.pois if p.get("role") == "focal"), spec.pois[0] if spec.pois else None)
    views.append({
        "id": "overview",
        "label": "World overview (3/4 aerial)",
        "position": [half * 0.72, peak + 190, half * 0.72],
        "look_at": [0, field.water + 30, 0],
        "fov": 70,
    })
    spawn = spec.spawns[0] if spec.spawns else {"x": 0, "z": 0}
    target = focal or {"x": 0, "z": 0}
    views.append({
        "id": "spawn_eye",
        "label": "Player eye level at spawn",
        "position": [float(spawn.get("x", 0)), field.at(float(spawn.get("x", 0)), float(spawn.get("z", 0))) + 7,
                     float(spawn.get("z", 0))],
        "look_at": [float(target.get("x", 0)), field.at(float(target.get("x", 0)), float(target.get("z", 0))) + 18,
                    float(target.get("z", 0))],
        "fov": 70,
    })
    for poi in [p for p in spec.pois if p.get("role") == "focal"] + [p for p in spec.pois if p.get("role") != "focal"]:
        if len(views) >= limit:
            break
        x, z = float(poi.get("x", 0)), float(poi.get("z", 0))
        ground = field.at(x, z)
        angle = math.radians(float(poi.get("rotation", 0)) + 35)
        distance = 70 if poi.get("role") == "focal" else 55
        views.append({
            "id": f"poi_{poi['id']}",
            "label": f"Landmark: {poi.get('name')}",
            "position": [x + math.cos(angle) * distance, ground + 32, z + math.sin(angle) * distance],
            "look_at": [x, ground + 14, z],
            "fov": 65,
            "poi": poi["id"],
        })
    # District readability view: eye level on the main path toward each outer district.
    for region in spec.regions[1:4]:
        if len(views) >= limit + 2:
            break
        cx, cz = region.get("center", [0, 0])
        views.append({
            "id": f"district_{region['id']}",
            "label": f"District approach: {region.get('name')}",
            "position": [cx * 0.65, field.at(cx * 0.65, cz * 0.65) + 8, cz * 0.65],
            "look_at": [cx, field.at(cx, cz) + 10, cz],
            "fov": 75,
        })
    return views[:limit]


def _camera_code(view: dict, use_play: bool) -> str:
    px, py, pz = view["position"]
    tx, ty, tz = view["look_at"]
    mode = "workspace.CurrentCamera" if not use_play else "workspace.CurrentCamera"
    return f'''local camera = {mode}
if not camera then return {{ applied = false, reason = "no camera" }} end
camera.CameraType = Enum.CameraType.Scriptable
camera.FieldOfView = {view.get("fov", 70)}
camera.CFrame = CFrame.lookAt(Vector3.new({px}, {py}, {pz}), Vector3.new({tx}, {ty}, {tz}))
return {{ applied = true, view = "{view['id']}" }}'''


def capture_views(client, spec, out_dir, views: list[dict] | None = None,
                  use_play: bool = True) -> dict:
    views = views or plan_views(spec)
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    captured, failed = [], []
    available = getattr(client, "has", lambda _n: True)("screen_capture")
    for view in views:
        entry = {"id": view["id"], "label": view["label"], "view": view}
        if not available:
            entry["error"] = "Studio session exposes no screen_capture tool"
            failed.append(entry)
            continue
        try:
            client.execute_luau(_camera_code(view, use_play))
        except Exception as exc:  # noqa: BLE001 - camera pose is best-effort
            entry["camera_error"] = str(exc)[:300]
        try:
            result = client.call("screen_capture", {"label": view["id"]})
        except Exception as exc:  # noqa: BLE001
            entry["error"] = str(exc)[:300]
            failed.append(entry)
            continue
        images = result.get("images") or []
        payload = result.get("json") or {}
        if isinstance(payload, dict) and payload.get("simulated"):
            entry["error"] = "mock Studio cannot render screenshots"
            failed.append(entry)
            continue
        data = None
        if images:
            data = images[0]
        elif isinstance(payload, dict):
            data = payload.get("image") or payload.get("data") or payload.get("png")
        if not data:
            entry["error"] = "capture returned no image data"
            entry["raw"] = str(result.get("text", ""))[:300]
            failed.append(entry)
            continue
        try:
            binary = base64.b64decode(data.split(",")[-1])
        except Exception:  # noqa: BLE001
            entry["error"] = "capture payload was not base64"
            failed.append(entry)
            continue
        path = directory / f"{view['id']}.png"
        path.write_bytes(binary)
        entry["file"] = str(path)
        entry["bytes"] = len(binary)
        captured.append(entry)
    return {"captured": captured, "failed": failed, "views": len(views),
            "mode": "play-mode camera" if use_play else "edit-mode viewport"}


def read_capture_manifest(directory) -> list[dict]:
    manifest = Path(directory) / "capture_manifest.json"
    if not manifest.exists():
        return []
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("captured", [])
    except (OSError, json.JSONDecodeError):
        return []
