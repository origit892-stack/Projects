#!/usr/bin/env python3
"""Validate the source-owned FG-GREENFIELD-001 candidate or canonical tree.

This assertion intentionally checks only source facts that Rojo can map. Studio
hierarchy and runtime behavior are verified separately after synchronization.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATE = PROJECT_ROOT / "artifacts" / "full_game_candidate"

EXPECTED_REMOTES = {
    "GetSnapshot": "RemoteFunction",
    "StateDelta": "RemoteEvent",
    "ActionResult": "RemoteEvent",
    "InteractionOpened": "RemoteEvent",
    "ToolIntent": "RemoteEvent",
    "InteractionIntent": "RemoteEvent",
    "InteractionCloseIntent": "RemoteEvent",
    "UseItemIntent": "RemoteEvent",
}
EXPECTED_STATIONS = {
    "power_console",
    "shop_terminal",
    "personal_storage",
    "scrap_exchange",
    "harvest_upgrade",
    "weapon_upgrade",
    "storage_upgrade",
    "food_processor",
}
EXPECTED_SPAWNS = {f"bedroom_{index:02d}" for index in range(1, 7)}
EXPECTED_PLOTS = {f"plot_{index:02d}" for index in range(1, 13)}
EXPECTED_TREES = {f"tree_{index:03d}" for index in range(1, 19)}
EXPECTED_SCRAP = {f"scrap_{index:02d}" for index in range(1, 7)}
EXPECTED_ZOMBIE_SPAWNS = {f"zombie_spawn_{index:02d}" for index in range(1, 8)}
LEGACY_SOURCE_TOKENS = (
    "GlobalManager",
    "FarmingSystem",
    "HarvestController",
    "HarvestVisualController",
    "UIBootstrap",
    "BunkerInteractionService",
    "BunkerPowerService",
    "LegacyBunkerGameplayService",
    "ForestResourceSpawner",
    "ResourceNodeService",
)
TEXT_SUFFIXES = {".json", ".lua", ".luau"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def walk(node: dict[str, Any]) -> Iterator[dict[str, Any]]:
    yield node
    for child in node.get("Children", []):
        if isinstance(child, dict):
            yield from walk(child)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def expect_path(errors: list[str], path: Path) -> None:
    if not path.exists():
        fail(errors, f"missing required path: {path}")


def check_project(root: Path, errors: list[str]) -> None:
    project = load_json(root / "default.project.json")
    tree = project.get("tree")
    if not isinstance(tree, dict) or tree.get("$className") != "DataModel":
        fail(errors, "default.project.json must define a DataModel tree")
        return

    expected_roots = {
        "Players",
        "Lighting",
        "ReplicatedStorage",
        "ServerScriptService",
        "ServerStorage",
        "StarterGui",
        "StarterPlayer",
        "Workspace",
    }
    actual_roots = {key for key in tree if not key.startswith("$")}
    if actual_roots != expected_roots:
        fail(errors, f"project roots differ: {sorted(actual_roots)}")
    if tree.get("Players", {}).get("$properties", {}).get("CharacterAutoLoads") is not False:
        fail(errors, "Players.CharacterAutoLoads must be false")
    if tree.get("Workspace", {}).get("$properties", {}).get("StreamingEnabled") is not False:
        fail(errors, "Workspace.StreamingEnabled must be false")
    if tree.get("Workspace", {}).get("$properties", {}).get("SignalBehavior") != "Deferred":
        fail(errors, "Workspace.SignalBehavior must be Deferred")

    expected_paths = {
        "Lighting": "src/Lighting",
        "ReplicatedStorage": "src/ReplicatedStorage",
        "ServerScriptService": "src/ServerScriptService",
        "ServerStorage": "src/ServerStorage",
        "StarterGui": "src/StarterGui",
        "Workspace": "src/Workspace",
    }
    for service, expected_path in expected_paths.items():
        if tree.get(service, {}).get("$path") != expected_path:
            fail(errors, f"{service} must map only {expected_path}")

    starter_player = tree.get("StarterPlayer", {})
    scripts = starter_player.get("StarterPlayerScripts", {})
    if scripts.get("$path") != "src/StarterPlayer/StarterPlayerScripts":
        fail(errors, "StarterPlayerScripts mapping is invalid")
    if "StarterCharacterScripts" in starter_player:
        fail(errors, "legacy StarterCharacterScripts mapping must be absent")


def check_source(root: Path, errors: list[str]) -> None:
    source = root / "src"
    expect_path(errors, source / "ServerScriptService/Game/ServerBootstrap.server.luau")
    expect_path(errors, source / "StarterPlayer/StarterPlayerScripts/GameClient/ClientBootstrap.client.luau")
    expect_path(errors, source / "ReplicatedStorage/Game/NetTypes.luau")
    expect_path(errors, source / "ReplicatedStorage/GeneratedAssets/AssetRegistry.luau")
    if (source / "ReplicatedStorage/GeneratedAssets/AssetRegistry.json").exists():
        fail(errors, "duplicate AssetRegistry.json mapping must be absent")
    if (source / "server").exists():
        fail(errors, "legacy src/server mapping must be absent")

    server_scripts = sorted(source.rglob("*.server.luau"))
    client_scripts = sorted(source.rglob("*.client.luau"))
    expected_server = source / "ServerScriptService/Game/ServerBootstrap.server.luau"
    expected_client = source / "StarterPlayer/StarterPlayerScripts/GameClient/ClientBootstrap.client.luau"
    if server_scripts != [expected_server]:
        fail(errors, f"expected one ServerBootstrap Script, found {[path.relative_to(source).as_posix() for path in server_scripts]}")
    if client_scripts != [expected_client]:
        fail(errors, f"expected one ClientBootstrap LocalScript, found {[path.relative_to(source).as_posix() for path in client_scripts]}")
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        if path.suffix.lower() in {".rbxm", ".rbxmx"}:
            fail(errors, f"binary game asset remains active: {relative}")
        if any(token in relative for token in LEGACY_SOURCE_TOKENS):
            fail(errors, f"legacy competing source remains active: {relative}")


def check_text_hygiene(root: Path, errors: list[str]) -> int:
    paths = [root / "default.project.json"]
    paths.extend(path for path in sorted((root / "src").rglob("*")) if path.suffix in TEXT_SUFFIXES)
    for path in paths:
        content = path.read_bytes()
        relative = path.relative_to(root).as_posix()
        if b"\r" in content:
            fail(errors, f"text file must use LF line endings: {relative}")
        if content and not content.endswith(b"\n"):
            fail(errors, f"text file must end with a newline: {relative}")
        for line_number, line in enumerate(content.splitlines(), start=1):
            if line.endswith((b" ", b"\t")):
                fail(errors, f"trailing whitespace: {relative}:{line_number}")
    return len(paths)


def check_remotes(root: Path, errors: list[str]) -> None:
    remote_root = load_json(root / "src/ReplicatedStorage/Remotes.model.json")
    if remote_root.get("ClassName") != "Folder":
        fail(errors, "Remotes must be a Folder")
        return
    actual = {
        child.get("Name"): child.get("ClassName")
        for child in remote_root.get("Children", [])
        if isinstance(child, dict)
    }
    if actual != EXPECTED_REMOTES:
        fail(errors, f"remote contract differs: {actual}")


def attribute_ids(nodes: list[dict[str, Any]], attribute: str, class_name: str | None = None) -> set[str]:
    values: set[str] = set()
    for node in nodes:
        if class_name is not None and node.get("ClassName") != class_name:
            continue
        value = node.get("attributes", {}).get(attribute)
        if isinstance(value, str):
            values.add(value)
    return values


def check_world(root: Path, errors: list[str]) -> dict[str, int]:
    world = load_json(root / "src/Workspace/GameWorld.model.json")
    runtime = load_json(root / "src/Workspace/Runtime.model.json")
    if world.get("ClassName") != "Model" or world.get("Name") not in {None, "GameWorld"}:
        fail(errors, "GameWorld source must be a Model")
    if runtime != {"ClassName": "Folder", "Children": []}:
        fail(errors, "Runtime source must be an empty Folder")

    nodes = list(walk(world))
    scripts = [node for node in nodes if node.get("ClassName") in {"Script", "LocalScript", "ModuleScript"}]
    if scripts:
        fail(errors, "GameWorld must not contain executable scripts")
    prompts = [node for node in nodes if node.get("ClassName") == "ProximityPrompt"]
    if len(prompts) != 26:
        fail(errors, f"expected 26 interaction prompts, found {len(prompts)}")
    for prompt in prompts:
        properties = prompt.get("Properties", {})
        if properties.get("Style") != "Custom" or properties.get("Enabled") is not True:
            fail(errors, f"prompt {prompt.get('Name')} is not enabled Custom presentation")

    actual_spawns = attribute_ids(nodes, "SpawnId", "SpawnLocation")
    actual_stations = attribute_ids(nodes, "InteractionId", "Model")
    actual_plots = attribute_ids(nodes, "PlotId", "Model")
    actual_trees = {
        node.get("attributes", {}).get("ResourceNodeId")
        for node in nodes
        if node.get("ClassName") == "Model" and node.get("attributes", {}).get("ResourceDefinitionId") == "tree"
    }
    actual_scrap = {
        node.get("attributes", {}).get("ResourceNodeId")
        for node in nodes
        if node.get("ClassName") == "Model" and node.get("attributes", {}).get("ResourceDefinitionId") == "scrap_cache"
    }
    actual_zombie_spawns = {
        node.get("attributes", {}).get("SpawnId")
        for node in nodes
        if node.get("ClassName") == "Part" and node.get("attributes", {}).get("SpawnGroupId") == "night_perimeter"
    }
    if actual_spawns != EXPECTED_SPAWNS:
        fail(errors, f"spawn IDs differ: {sorted(actual_spawns)}")
    if actual_stations != EXPECTED_STATIONS:
        fail(errors, f"station IDs differ: {sorted(actual_stations)}")
    if actual_plots != EXPECTED_PLOTS:
        fail(errors, f"plot IDs differ: {sorted(actual_plots)}")
    if actual_trees != EXPECTED_TREES:
        fail(errors, f"tree IDs differ: {sorted(actual_trees)}")
    if actual_scrap != EXPECTED_SCRAP:
        fail(errors, f"scrap IDs differ: {sorted(actual_scrap)}")
    if actual_zombie_spawns != EXPECTED_ZOMBIE_SPAWNS:
        fail(errors, f"zombie spawn IDs differ: {sorted(actual_zombie_spawns)}")

    base_parts = sum(node.get("ClassName") in {"Part", "MeshPart", "SpawnLocation", "WedgePart", "CornerWedgePart"} for node in nodes)
    if base_parts > 2500 or len(nodes) - 1 > 3600:
        fail(errors, f"world budget exceeded: {base_parts} BaseParts / {len(nodes) - 1} descendants")
    return {
        "baseParts": base_parts,
        "descendants": len(nodes) - 1,
        "prompts": len(prompts),
        "spawns": len(actual_spawns),
        "stations": len(actual_stations),
        "plots": len(actual_plots),
        "trees": len(actual_trees),
        "scrapCaches": len(actual_scrap),
        "zombieMarkers": len(actual_zombie_spawns),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_CANDIDATE, help="candidate or canonical project root")
    arguments = parser.parse_args()
    root = arguments.root.expanduser().resolve()
    errors: list[str] = []
    expect_path(errors, root / "default.project.json")
    expect_path(errors, root / "src")
    if not errors:
        check_project(root, errors)
        check_source(root, errors)
        text_file_count = check_text_hygiene(root, errors)
        check_remotes(root, errors)
        counts = check_world(root, errors)
        counts["textFiles"] = text_file_count
    else:
        counts = {}

    if errors:
        print("FULL_GAME_INTEGRATION_ASSERTIONS=FAIL")
        for error in errors:
            print(f"ERROR={error}")
        return 1
    print("FULL_GAME_INTEGRATION_ASSERTIONS=PASS")
    print(json.dumps({"root": str(root), "counts": counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
