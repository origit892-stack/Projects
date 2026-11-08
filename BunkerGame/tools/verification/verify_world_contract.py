#!/usr/bin/env python3
"""verify_world_contract.py

Verification script for BunkerGame world contract (objective steps 5b + 5d).

Checks (each reported PASS/FAIL with details):
  1. src/Workspace/GameWorld.model.json top-level children are exactly:
     Foundation, Bunker, Exterior, Farm, Resources, EnemySpawns, Objectives, Presentation
  2. GameWorld.Bunker contains sections:
     Architecture, Bedroom, Commons, Entrance, Workshop, Upgrades, Shop,
     Storage, Power, ServiceRoute, Spawns, Stations, PoweredLights, SpawnSafeZone
  3. SpawnLocations container has exactly 6 descendants
     (container resolved by name "SpawnLocations", falling back to "Spawns")
  4. GameWorld.Bunker.PoweredLights exists
  5. GameWorld.Presentation.AudioAnchors exists and contains Sound instances
     BlastDoorOpenCueSound and BlastDoorCloseCueSound, each with a non-empty
     SoundId and Looped == false
  6. src/Workspace/Runtime.model.json is a Folder with no children
  7. All 5 generated asset files exist non-empty in
     src/ServerStorage/GeneratedAssets/
  8. Every generated .model.json file (GameWorld, Runtime, the 5 Lighting
     model files, the 5 asset files) parses as valid JSON

Read-only: this script never modifies any project file.
Exit code: 0 if all checks PASS, 1 otherwise.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GAMEWORLD_PATH = PROJECT_ROOT / "src" / "Workspace" / "GameWorld.model.json"
RUNTIME_PATH = PROJECT_ROOT / "src" / "Workspace" / "Runtime.model.json"
LIGHTING_DIR = PROJECT_ROOT / "src" / "Lighting"
ASSET_DIR = PROJECT_ROOT / "src" / "ServerStorage" / "GeneratedAssets"

EXPECTED_TOP_LEVEL = [
    "Foundation",
    "Bunker",
    "Exterior",
    "Farm",
    "Resources",
    "EnemySpawns",
    "Objectives",
    "Presentation",
]

EXPECTED_BUNKER_SECTIONS = [
    "Architecture",
    "Bedroom",
    "Commons",
    "Entrance",
    "Workshop",
    "Upgrades",
    "Shop",
    "Storage",
    "Power",
    "ServiceRoute",
    "Spawns",
    "Stations",
    "PoweredLights",
    "SpawnSafeZone",
]

EXPECTED_SPAWN_COUNT = 6

EXPECTED_SOUND_NAMES = ["BlastDoorOpenCueSound", "BlastDoorCloseCueSound"]

ASSET_BASENAMES = [
    "bunker_electrical_junction_box_01",
    "bunker_valve_assembly_01",
    "bunker_vent_grille_01",
    "old_military_ammo_crate_01",
    "pipeline_pipe_retry_02",
]

LIGHTING_BASENAMES = [
    "Atmosphere",
    "Bloom",
    "ColorGrade",
    "DepthOfField",
    "SunRays",
]


def find_node(node, name):
    """Depth-first search for a child node by Name."""
    for child in node.get("Children", []):
        if child.get("Name") == name:
            return child
        found = find_node(child, name)
        if found is not None:
            return found
    return None


def count_descendants(node):
    total = 0
    for child in node.get("Children", []):
        total += 1 + count_descendants(child)
    return total


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    results = []  # list of (check_id, name, passed, details)

    def record(check_id, name, passed, details):
        results.append((check_id, name, passed, details))

    # ---- Check 8 (parse first; other checks depend on parsed data) ----
    model_files = {
        "GameWorld": GAMEWORLD_PATH,
        "Runtime": RUNTIME_PATH,
    }
    for base in LIGHTING_BASENAMES:
        model_files["Lighting/" + base] = LIGHTING_DIR / (base + ".model.json")
    for base in ASSET_BASENAMES:
        model_files["Asset/" + base] = ASSET_DIR / (base + ".model.json")

    parsed = {}
    parse_errors = []
    for label, path in model_files.items():
        if not path.is_file():
            parse_errors.append("%s: file missing (%s)" % (label, path))
            continue
        try:
            parsed[label] = load_json(path)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            parse_errors.append("%s: %s" % (label, exc))

    record(
        8,
        "All generated .model.json files parse as valid JSON",
        not parse_errors,
        "checked %d files (%s); errors: %s"
        % (len(model_files), ", ".join(model_files), "; ".join(parse_errors) if parse_errors else "none"),
    )

    gameworld = parsed.get("GameWorld")
    runtime = parsed.get("Runtime")

    # ---- Check 1: GameWorld top-level children exactly ----
    if gameworld is None:
        record(1, "GameWorld top-level children exact", False,
               "GameWorld.model.json did not parse; cannot verify")
    else:
        actual = [c.get("Name") for c in gameworld.get("Children", [])]
        missing = [n for n in EXPECTED_TOP_LEVEL if n not in actual]
        extra = [n for n in actual if n not in EXPECTED_TOP_LEVEL]
        order_ok = actual == EXPECTED_TOP_LEVEL
        passed = not missing and not extra
        details = "actual=%s" % actual
        if missing:
            details += "; missing=%s" % missing
        if extra:
            details += "; unexpected=%s" % extra
        if not order_ok and passed:
            details += "; note: set matches but order differs from expected list"
        record(1, "GameWorld top-level children exact", passed, details)

    # ---- Check 2: Bunker contains required sections ----
    bunker = find_node(gameworld, "Bunker") if gameworld is not None else None
    if bunker is None:
        record(2, "Bunker contains required sections", False,
               "Bunker node not found in GameWorld")
    else:
        actual = [c.get("Name") for c in bunker.get("Children", [])]
        missing = [n for n in EXPECTED_BUNKER_SECTIONS if n not in actual]
        extra = [n for n in actual if n not in EXPECTED_BUNKER_SECTIONS]
        record(
            2,
            "Bunker contains required sections",
            not missing,
            "actual=%s; missing=%s; additional (allowed)=%s"
            % (actual, missing, extra),
        )

    # ---- Check 3: SpawnLocations descendants == 6 ----
    if gameworld is None:
        record(3, "SpawnLocations has exactly 6 descendants", False,
               "GameWorld.model.json did not parse; cannot verify")
    else:
        container = find_node(gameworld, "SpawnLocations")
        container_name = "SpawnLocations"
        if container is None:
            container = find_node(gameworld, "Spawns")
            container_name = "Spawns (fallback: 'SpawnLocations' not present)"
        if container is None:
            record(3, "SpawnLocations has exactly 6 descendants", False,
                   "neither 'SpawnLocations' nor 'Spawns' container found")
        else:
            count = count_descendants(container)
            children = [
                "%s:%s" % (c.get("ClassName"), c.get("Name"))
                for c in container.get("Children", [])
            ]
            record(
                3,
                "SpawnLocations has exactly 6 descendants",
                count == EXPECTED_SPAWN_COUNT,
                "container=%s; descendant_count=%d (expected %d); direct_children=%s"
                % (container_name, count, EXPECTED_SPAWN_COUNT, children),
            )

    # ---- Check 4: Bunker.PoweredLights exists ----
    powered = find_node(bunker, "PoweredLights") if bunker is not None else None
    record(
        4,
        "GameWorld.Bunker.PoweredLights exists",
        powered is not None,
        "found=%s (ClassName=%s)"
        % (powered is not None, powered.get("ClassName") if powered else None),
    )

    # ---- Check 5: Presentation.AudioAnchors sounds ----
    presentation = find_node(gameworld, "Presentation") if gameworld is not None else None
    anchors = find_node(presentation, "AudioAnchors") if presentation is not None else None
    if anchors is None:
        record(5, "AudioAnchors contains required Sound instances", False,
               "GameWorld.Presentation.AudioAnchors not found")
    else:
        problems = []
        for sound_name in EXPECTED_SOUND_NAMES:
            sound = find_node(anchors, sound_name)
            if sound is None:
                problems.append("%s: not found under AudioAnchors" % sound_name)
                continue
            if sound.get("ClassName") != "Sound":
                problems.append("%s: ClassName=%s (expected Sound)"
                                % (sound_name, sound.get("ClassName")))
            props = sound.get("Properties", {})
            sound_id = props.get("SoundId")
            if not sound_id:
                problems.append("%s: SoundId is empty/missing" % sound_name)
            looped = props.get("Looped")
            if looped is not False:
                problems.append("%s: Looped=%r (expected False)" % (sound_name, looped))
        record(
            5,
            "AudioAnchors contains required Sound instances",
            not problems,
            "sounds checked=%s; problems=%s"
            % (EXPECTED_SOUND_NAMES, problems if problems else "none"),
        )

    # ---- Check 6: Runtime is a Folder with no children ----
    if runtime is None:
        record(6, "Runtime.model.json is a Folder with no children", False,
               "Runtime.model.json did not parse; cannot verify")
    else:
        class_name = runtime.get("ClassName")
        n_children = len(runtime.get("Children", []))
        record(
            6,
            "Runtime.model.json is a Folder with no children",
            class_name == "Folder" and n_children == 0,
            "ClassName=%s; children=%d" % (class_name, n_children),
        )

    # ---- Check 7: 5 asset files exist non-empty ----
    asset_problems = []
    for base in ASSET_BASENAMES:
        path = ASSET_DIR / (base + ".model.json")
        if not path.is_file():
            asset_problems.append("%s: missing" % base)
        elif path.stat().st_size == 0:
            asset_problems.append("%s: empty (0 bytes)" % base)
    record(
        7,
        "All 5 generated asset files exist non-empty",
        not asset_problems,
        "dir=%s; problems=%s"
        % (ASSET_DIR, asset_problems if asset_problems else "none"),
    )

    # ---- Report ----
    print("BunkerGame world contract verification")
    print("project root: %s" % PROJECT_ROOT)
    print("-" * 72)
    failures = 0
    for check_id, name, passed, details in sorted(results, key=lambda r: r[0]):
        status = "PASS" if passed else "FAIL"
        if not passed:
            failures += 1
        print("[%s] check %d: %s" % (status, check_id, name))
        print("       %s" % details)
    print("-" * 72)
    total = len(results)
    print("summary: %d/%d checks passed" % (total - failures, total))
    if failures:
        print("RESULT: FAIL (%d check(s) failed)" % failures)
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
