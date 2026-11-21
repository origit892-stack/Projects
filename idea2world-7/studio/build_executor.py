"""Build executor: installs the generated project into Studio and drives the build.

The build is installed as real ModuleScripts inside `ServerScriptService`, then executed through the
Studio MCP `execute_luau` tool. That means what runs in Studio is the same file set a human can open,
edit and re-run -- not a one-off string of code.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from codegen import lua_emit

FOLDER = "Idea2World_Generated_Map"


@dataclass
class BuildResult:
    ok: bool
    mode: str = "studio"
    report: dict = field(default_factory=dict)
    console: str = ""
    error: str = ""
    seconds: float = 0.0
    instances: int = 0

    def to_dict(self) -> dict:
        return {"ok": self.ok, "mode": self.mode, "error": self.error,
                "seconds": round(self.seconds, 2), "instances": self.instances,
                "report": self.report, "console": self.console[-4000:]}


def _install_code(batch: dict[str, str], first: bool) -> str:
    lines = []
    if first:
        lines.append(f'''local ServerScriptService = game:GetService("ServerScriptService")
local folder = ServerScriptService:FindFirstChild("{FOLDER}")
if folder then folder:Destroy() end
folder = Instance.new("Folder")
folder.Name = "{FOLDER}"
folder.Parent = ServerScriptService
''')
    lines.append(f'local folder = game:GetService("ServerScriptService"):FindFirstChild("{FOLDER}")')
    lines.append('assert(folder, "Idea2World module folder missing")')
    for name, source in batch.items():
        lines.append(f'''do
	local module = folder:FindFirstChild("{name}")
	if not module then
		module = Instance.new("ModuleScript")
		module.Name = "{name}"
		module.Parent = folder
	end
	module.Source = {lua_emit.long_string(source)}
end''')
    lines.append('return "installed:" .. tostring(#folder:GetChildren())')
    return "\n".join(lines)


def install_project(client, sources: dict[str, str], batch_size: int = 4) -> dict:
    modules = {name[:-4]: source for name, source in sources.items() if name.endswith(".lua")
               and not name.endswith(".server.lua")}
    names = sorted(modules)
    installed = 0
    for index in range(0, len(names), batch_size):
        batch = {name: modules[name] for name in names[index:index + batch_size]}
        result = client.execute_luau(_install_code(batch, first=(index == 0)))
        if result.get("isError"):
            return {"ok": False, "error": result.get("text", "install failed"), "installed": installed}
        installed += len(batch)
    return {"ok": True, "installed": installed, "modules": names}


def build(client, verbose: bool = True, timeout: float = 900.0) -> BuildResult:
    started = time.time()
    code = f'''local folder = game:GetService("ServerScriptService"):FindFirstChild("{FOLDER}")
assert(folder, "Idea2World module folder not installed")
local bootstrap = require(folder:FindFirstChild("MapBootstrap"))
local report = bootstrap.build({{ verbose = {str(verbose).lower()} }})
local parts, models, emitters = 0, 0, 0
local root = workspace:FindFirstChild("Idea2World_Generated")
if root then
	for _, descendant in ipairs(root:GetDescendants()) do
		if descendant:IsA("BasePart") then parts += 1
		elseif descendant:IsA("Model") then models += 1
		elseif descendant:IsA("ParticleEmitter") then emitters += 1 end
	end
end
return {{
	passed = report.passed,
	title = report.title,
	seconds = report.stats and report.stats.seconds or 0,
	stages = report.stages,
	validation = report.validation,
	stats = report.stats,
	instanceCounts = {{ parts = parts, models = models, emitters = emitters }},
}}'''
    try:
        result = client.execute_luau(code, timeout=timeout) if _accepts_timeout(client) else client.execute_luau(code)
    except Exception as exc:  # noqa: BLE001 - transport failure is a build failure, reported
        return BuildResult(ok=False, error=str(exc), seconds=time.time() - started)
    payload = result.get("json")
    if payload is None:
        payload = _extract_payload(result.get("text", ""))
    if result.get("isError"):
        return BuildResult(ok=False, error=result.get("text", "execute_luau failed"),
                           console=result.get("text", ""), seconds=time.time() - started)
    if isinstance(payload, dict):
        counts = payload.get("instanceCounts") or {}
        report = payload.get("report") if isinstance(payload.get("report"), dict) else payload
        report.setdefault("mode", payload.get("mode", "studio"))
        stats = report.get("stats") or {}
        instances = int(counts.get("parts", 0)) + int(counts.get("models", 0))
        if not instances:
            instances = int(stats.get("partsCreated", 0)) + int(stats.get("modelsCreated", 0))
        return BuildResult(ok=bool(payload.get("passed", payload.get("ok"))), report=report,
                           mode=str(payload.get("mode", "studio")),
                           console=result.get("text", ""), seconds=time.time() - started,
                           instances=instances)
    return BuildResult(ok=False, error="build returned no structured report",
                       console=result.get("text", ""), seconds=time.time() - started)


def validate(client) -> dict:
    code = f'''local folder = game:GetService("ServerScriptService"):FindFirstChild("{FOLDER}")
assert(folder, "Idea2World module folder not installed")
local bootstrap = require(folder:FindFirstChild("MapBootstrap"))
return bootstrap.validate()'''
    result = client.execute_luau(code)
    return result.get("json") or _extract_payload(result.get("text", "")) or {"passed": False,
                                                                             "error": result.get("text")}


def clear(client) -> dict:
    code = f'''local root = workspace:FindFirstChild("Idea2World_Generated")
if root then root:Destroy() end
return {{ cleared = true }}'''
    result = client.execute_luau(code)
    return result.get("json") or {"cleared": False}


def generate_meshes(client, spec, limit: int = 8) -> dict:
    """Ask Studio's mesh generator for hero assets. Absent tool -> recipes stay in use."""
    if not getattr(client, "has", lambda _name: False)("generate_mesh"):
        return {"attempted": 0, "generated": 0,
                "reason": "Studio MCP session does not expose a mesh generation tool; "
                          "the layered part recipes are used instead."}
    attempts, generated, failures = 0, 0, []
    queue = [a for a in spec.asset_manifest.get("assets", []) if a.get("mesh_prompt")]
    priority = {"structure": 0, "creature": 1, "vegetation": 2, "rock": 3, "prop": 4}
    queue.sort(key=lambda a: priority.get(a.get("category"), 5))
    for asset in queue[:limit]:
        attempts += 1
        try:
            result = client.call("generate_mesh", {
                "prompt": asset["mesh_prompt"],
                "name": asset["id"],
                "targetFolder": f"ReplicatedStorage/Idea2World_Meshes/{asset['id']}",
            })
            if result.get("isError"):
                failures.append({"asset": asset["id"], "error": result.get("text", "")[:300]})
            else:
                generated += 1
        except Exception as exc:  # noqa: BLE001
            failures.append({"asset": asset["id"], "error": str(exc)[:300]})
    return {"attempted": attempts, "generated": generated, "failures": failures}


def _accepts_timeout(client) -> bool:
    import inspect
    try:
        return "timeout" in inspect.signature(client.execute_luau).parameters
    except (TypeError, ValueError):
        return False


def _extract_payload(text: str):
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None
    return None


def run_full_build(client, project_dir, spec, sources: dict[str, str],
                   enable_meshes: bool = False, mesh_limit: int = 8) -> dict:
    started = time.time()
    install = install_project(client, sources)
    if not install.get("ok"):
        return {"ok": False, "install": install, "error": install.get("error", "install failed")}
    mesh_report = generate_meshes(client, spec, mesh_limit) if enable_meshes else {"attempted": 0, "generated": 0}
    result = build(client)
    payload = result.to_dict()
    payload["install"] = install
    payload["meshes"] = mesh_report
    payload["total_seconds"] = round(time.time() - started, 2)
    Path(project_dir).mkdir(parents=True, exist_ok=True)
    (Path(project_dir) / "build_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
