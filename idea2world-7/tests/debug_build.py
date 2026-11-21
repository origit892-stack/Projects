import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests" / "integration"))

from test_generated_project import build_spec  # noqa: E402
from codegen import luau_generator  # noqa: E402
from studio import mock_studio  # noqa: E402

spec = build_spec()
out = ROOT / "projects" / "_debug_generated"
luau_generator.write_project(spec, out / "luau")
extra = """
local root = workspace:FindFirstChild("Idea2World_Generated")
print("ROOT", root and root.Name, root and #root:GetChildren())
local desc = workspace:GetDescendants()
print("DESC_COUNT", #desc)
local spawns = 0
for _, d in ipairs(desc) do
  if d.ClassName == "SpawnLocation" then spawns += 1; print("SPAWN", d.Name, tostring(d:GetAttribute("SpawnId")), tostring(d:IsA("SpawnLocation"))) end
end
print("SPAWN_COUNT", spawns)
local spa = root and root:FindFirstChild("Spawns")
print("SPAWNS_FOLDER", spa and spa.Name, spa and #spa:GetChildren())
"""
result = mock_studio.run_build(out / "luau", timeout=240, keep_harness=str(out / "harness.lua"))
report = result.get("report") or {}
print("PASSED", report.get("passed"), "FAILURES", (report.get("validation") or {}).get("failures"))
print("STAGES", [(s["name"], s["ok"]) for s in report.get("stages", []) if not s["ok"]])
print("OUTPUT", "\n".join(line for line in (result.get("output") or "").splitlines() if line.startswith(("ROOT","DESC","SPAWN","I2W","[Idea2World]"))))
