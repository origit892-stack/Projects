"""Static validation of generated Luau.

Three layers, cheapest first:
  1. structural checks inside Python (module graph, placeholders, data completeness);
  2. `luau-compile` if the Luau CLI is installed -- a real parser, not a bracket counter;
  3. `luau-analyze` with Roblox globals treated as engine-provided, to catch real type mistakes.

The validator is honest about what it cannot check: it cannot know whether a Part looks good, and
it cannot run Studio. That is what the Studio bridge and visual QA are for.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REQUIRED_MODULES = [
    "MapConfig", "WorldLayout", "AssetLibrary", "TerrainBuilder", "BiomeBuilder", "PathBuilder",
    "VegetationBuilder", "AssetPlacement", "BuildingBuilder", "LightingController",
    "AtmosphereController", "VFXController", "SoundscapeController", "SpawnSetup",
    "InteractionSetup", "MapValidator", "MapBootstrap",
]

ROBLOX_GLOBALS = {
    "script", "workspace", "game", "Instance", "Enum", "CFrame", "Vector3", "Vector2", "Color3",
    "UDim2", "UDim", "NumberRange", "NumberSequence", "NumberSequenceKeypoint", "ColorSequence",
    "ColorSequenceKeypoint", "RaycastParams", "Random", "task", "TweenInfo", "Rect", "BrickColor",
    "DateTime", "os", "type", "typeof", "warn", "tick", "wait", "spawn", "delay", "settings",
    "shared", "_G", "utf8", "buffer", "debug",
}

REQUIRE_RE = re.compile(r'require\(\s*script\.Parent(?:\[[^\]]+\]|\.([A-Za-z_]\w*))')
WAIT_FOR_CHILD_RE = re.compile(r'script\.Parent:WaitForChild\(\s*["\']([A-Za-z_]\w*)["\']\s*\)')

PLACEHOLDER_TOKENS = ("__DATA__", "__SIZE__", "TODO", "FIXME", "PLACEHOLDER", "_error")

CONFIG_REQUIREMENTS = [
    "Config.Title", "Config.Palette", "Config.Heightmap", "Config.Regions", "Config.Paths",
    "Config.Pois", "Config.Spawns", "Config.Biomes", "Config.Assets", "Config.Placements",
    "Config.Budget",
]


def _tool(name: str) -> str | None:
    return shutil.which(name)


def check_structure(sources: dict[str, str]) -> list[dict]:
    issues: list[dict] = []
    names = {name[:-4] if name.endswith(".lua") else name for name in sources}
    for module in REQUIRED_MODULES:
        if module not in names:
            issues.append({"severity": "critical", "file": module + ".lua",
                           "message": f"required module '{module}' is missing from the project"})
    for name, source in sources.items():
        for match in REQUIRE_RE.finditer(source):
            target = match.group(1)
            if target and target not in names:
                issues.append({"severity": "critical", "file": name,
                               "message": f"require of unknown module '{target}'"})
        for match in WAIT_FOR_CHILD_RE.finditer(source):
            target = match.group(1)
            if target not in names:
                issues.append({"severity": "critical", "file": name,
                               "message": f"WaitForChild targets unknown module '{target}'"})
        for token in PLACEHOLDER_TOKENS:
            if token in source:
                issues.append({"severity": "major", "file": name,
                               "message": f"unresolved placeholder token '{token}'"})
    config = sources.get("MapConfig.lua", "")
    for requirement in CONFIG_REQUIREMENTS:
        if requirement not in config:
            issues.append({"severity": "critical", "file": "MapConfig.lua",
                           "message": f"generated config is missing '{requirement}'"})
    # A parsed-but-empty world is a silent failure; check counts explicitly.
    if re.search(r"Config\.Pois = \{\s*\}", config):
        issues.append({"severity": "critical", "file": "MapConfig.lua", "message": "no landmarks in config"})
    if re.search(r"Config\.Placements = \{\s*\}", config):
        issues.append({"severity": "major", "file": "MapConfig.lua", "message": "no placements in config"})
    return issues


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, timeout=90)
        out = (proc.stdout or b"") + (proc.stderr or b"")
        return proc.returncode, out.decode("utf-8", "replace")
    except (OSError, subprocess.SubprocessError) as exc:
        return -1, str(exc)


def check_syntax(sources: dict[str, str]) -> tuple[list[dict], str]:
    """Parse every module with luau-compile when available."""
    issues: list[dict] = []
    compiler = _tool("luau-compile")
    if not compiler:
        return [], "unavailable"
    with tempfile.TemporaryDirectory(prefix="i2w-luau-") as tmp:
        tmp_path = Path(tmp)
        for name, source in sources.items():
            if not name.endswith(".lua"):
                continue
            file_path = tmp_path / name
            file_path.write_text(source, encoding="utf-8")
            code, output = _run([compiler, "--null", str(file_path)], tmp_path)
            if code != 0:
                for line in output.strip().splitlines()[:6]:
                    issues.append({"severity": "critical", "file": name,
                                   "message": line.replace(str(tmp_path) + "/", "")})
    return issues, "luau-compile"


def check_types(sources: dict[str, str]) -> tuple[list[dict], str]:
    analyzer = _tool("luau-analyze")
    if not analyzer:
        return [], "unavailable"
    issues: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="i2w-analyze-") as tmp:
        tmp_path = Path(tmp)
        written = []
        for name, source in sources.items():
            if name.endswith(".lua"):
                (tmp_path / name).write_text(source, encoding="utf-8")
                written.append(name)
        if not written:
            return [], "empty"
        code, output = _run([analyzer, "--mode=nonstrict"] + written, tmp_path)
        for line in output.strip().splitlines():
            if not line.strip() or "SyntaxError" in line:
                continue
            match = re.search(r"Unknown global '([A-Za-z_]\w*)'", line)
            if match and match.group(1) in ROBLOX_GLOBALS:
                continue
            if "Unknown global 'require'" in line:
                continue
            # Roblox API types are not part of the open-source Luau analysis environment; flagging
            # every BasePart/Instance annotation as an error would bury real mistakes.
            if re.search(r"Unknown type '[A-Za-z_][\w.]*'", line):
                continue
            if "TypeError" in line or "Unknown" in line or "error" in line.lower():
                issues.append({"severity": "minor", "file": line.split("(")[0],
                               "message": line})
    return issues[:20], "luau-analyze"


def validate_sources(sources: dict[str, str], deep: bool = True) -> dict:
    issues = check_structure(sources)
    tools = {}
    if deep:
        syntax_issues, syntax_tool = check_syntax(sources)
        tools["syntax"] = syntax_tool
        issues.extend(syntax_issues)
        if not any(i["severity"] == "critical" for i in syntax_issues):
            type_issues, type_tool = check_types(sources)
            tools["types"] = type_tool
            issues.extend(type_issues)
    critical = [i for i in issues if i["severity"] == "critical"]
    return {"passed": not critical, "issues": issues,
            "critical_count": len(critical),
            "tools": tools,
            "checked_files": len([n for n in sources if n.endswith(".lua")])}


def validate_project(directory) -> dict:
    path = Path(directory)
    if not path.exists():
        return {"passed": False, "issues": [{"severity": "critical", "file": str(path),
                                             "message": "project directory does not exist"}],
                "critical_count": 1, "tools": {}, "checked_files": 0}
    sources = {item.name: item.read_text(encoding="utf-8") for item in path.glob("*.lua")}
    return validate_sources(sources)
