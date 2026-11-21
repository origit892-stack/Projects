"""Integration test: plan a real world, generate the Luau project, execute it in the simulator.

Run directly (`python3 tests/integration/test_generated_project.py`) or with pytest.
This is the test that would have caught 5.0's "beautiful blueprint, unbuildable map" problem: the
generated modules are actually executed.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents import level_architect  # noqa: E402
from assets import asset_registry, asset_validator  # noqa: E402
from codegen import luau_generator, luau_validator  # noqa: E402
from research.reference_library import STYLE_LIBRARY  # noqa: E402
from research.style_analyzer import build_art_direction  # noqa: E402
from studio import mock_studio  # noqa: E402
from world import biome_builder, navigation_validator, placement_engine, terrain_builder  # noqa: E402
from world.world_spec import WorldSpec  # noqa: E402


def build_spec(idea="A cozy forest village around a lake with an old observatory on the ridge", seed=11):
    art = build_art_direction(idea, "stylized_low_poly", "natural", "general_adventure")
    spec = WorldSpec({
        "schema_version": 6, "idea": idea, "title": "Test World", "genre": "general_adventure",
        "core_loop": ["explore", "collect", "upgrade"],
        "art_direction": art,
        "lighting": {"clock_time": 15.2, "brightness": 2.2, "ambient": [96, 104, 120], "exposure": 0.15},
        "atmosphere": {"density": 0.28, "haze": 1.4, "color": art["palette"]["highlight"],
                       "decay": art["palette"]["field"]},
        "soundscape": {"slots": []},
        "world": {"size": 1500, "seed": seed, "relief": 1.0, "detail_budget": 600,
                  "region_count": 5, "terrain_cells": 64},
        "budget": {"max_instances": 14000, "max_triangles": 420000, "max_unique_meshes": 140,
                   "max_particle_emitters": 36},
    })
    level_architect.plan_layout(spec)
    field = terrain_builder.build_heightfield(spec)
    for region in spec.regions:
        region["ground"] = terrain_builder.REGION_GROUND.get(region["kind"], "Ground")
        region["water"] = region["kind"] in ("lake", "coast", "marsh")
    biome_builder.build_biomes(spec, field)
    biome_builder.ambient_particles(spec)
    asset_registry.build_manifest(spec)
    placement_engine.plan_placements(spec)
    placement_engine.place_poi_decor(spec)
    asset_validator.validate_asset_manifest(spec)
    navigation_validator.validate_navigation(spec)
    return spec


def test_spec_is_valid():
    spec = build_spec()
    critical = [issue for issue in spec.validate() if issue["severity"] == "critical"]
    assert not critical, critical
    assert len(spec.regions) >= 4
    assert len(spec.pois) >= 4
    assert spec.placements


def test_navigation_is_walkable():
    spec = build_spec()
    report = spec.data["navigation_report"]
    assert report["critical_count"] == 0, report["issues"][:5]
    assert report["metrics"]["reachable_pois"] == report["metrics"]["poi_count"]
    assert report["metrics"]["walkable_ratio"] > 0.5


def test_assets_are_not_box_stacks():
    spec = build_spec()
    report = spec.data["asset_validation"]
    assert report["passed"], [i for i in report["issues"] if i["severity"] == "critical"]
    assert report["stats"]["shaped_share"] > 0.5


def test_luau_project_parses_and_builds():
    spec = build_spec()
    sources = luau_generator.project_sources(spec)
    validation = luau_validator.validate_sources(sources, deep=True)
    assert validation["passed"], [i for i in validation["issues"] if i["severity"] == "critical"]
    out = ROOT / "projects" / "_test_generated"
    manifest = luau_generator.write_project(spec, out / "luau")
    assert manifest["source_count"] >= 17
    result = mock_studio.run_build(out / "luau", timeout=240)
    assert result["ok"], result.get("error") or result.get("output")
    report = result["report"]
    assert report["passed"], report.get("validation", {}).get("failures")
    assert result["terrainFillCalls"] > 100
    parts = report["stats"]["partsCreated"]
    assert parts > 200, parts
    assert report["stats"]["pois"] == len(spec.pois)


if __name__ == "__main__":
    test_spec_is_valid()
    test_navigation_is_walkable()
    test_assets_are_not_box_stacks()
    test_luau_project_parses_and_builds()
    print("integration checks passed")
