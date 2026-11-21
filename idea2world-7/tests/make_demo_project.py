"""Creates one demo world in ./projects so the studio app has something to open.

    python3 tests/make_demo_project.py

Uses the simulator for the build stage (no Studio session required). Swap `studio_mode` to "auto" to
build into Roblox Studio instead.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.orchestrator import Pipeline  # noqa: E402

IDEA = ("A floating ember archipelago at dusk: obsidian bridges between volcanic islets, a broken "
        "observatory on the tallest spire, and lantern-lit shrines where players collect star shards")

if __name__ == "__main__":
    pipeline = Pipeline(root=ROOT / "projects",
                        events=lambda event: print("·", event.get("type"), event.get("stage", ""),
                                                   event.get("seconds", "")))
    result = pipeline.run(IDEA, {
        "size": 1800, "seed": 23, "region_count": 6, "detail_budget": 900,
        "terrain_cells": 80, "studio_mode": "simulate", "repair_iterations": 2,
    })
    print("\nproject:", result["project"]["id"])
    print("visual:", result["visual"]["total"], result["visual"]["mode"])
    print("qa:", result["qa"]["verdict"])
    print("approval:", f"{result['approval']['criteria_met']}/{result['approval']['criteria_total']}",
          result["approval"]["blockers"])
    print("export:", result["export"]["zip"])
