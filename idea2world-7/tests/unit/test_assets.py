"""Asset quality rules: a world may not ship as a pile of squares."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from assets.asset_generator import POI_BUILDERS, build_recipe  # noqa: E402
from assets.asset_registry import build_manifest, reuse_stats  # noqa: E402
from assets.asset_validator import validate_asset_manifest  # noqa: E402
from world.world_spec import WorldSpec  # noqa: E402

SHAPED = {"Wedge", "Cylinder", "Ball", "CornerWedge"}
PALETTE = {"primary": "#3a2f5c", "secondary": "#6b4f9e", "accent": "#ffb347",
           "ground": "#4c6b3c", "highlight": "#d9f2ff", "shadow": "#1d1830"}


def make_spec(kinds=("monument", "observatory", "tower", "market", "gate")):
    pois = [{"id": f"poi_{i}", "name": f"Landmark {i}", "kind": kind, "region": "region_hub",
             "x": i * 40, "z": 0, "role": "focal" if i == 0 else "support",
             "interaction": "viewpoint"} for i, kind in enumerate(kinds)]
    return WorldSpec({
        "schema_version": 6, "idea": "an asset test world", "title": "Asset Test",
        "art_direction": {"palette": PALETTE, "props": ["lantern", "banner"], "style": "stylized_low_poly"},
        "world": {"size": 1400, "seed": 3, "water_level": 4.0, "detail_budget": 200},
        "regions": [{"id": "region_hub", "name": "Hub", "kind": "hub", "center": [0, 0], "radius": 180}],
        "pois": pois, "paths": [], "spawns": [{"id": "spawn", "x": 0, "z": 90}],
        "biomes": [], "placements": [],
    })


def test_every_landmark_recipe_is_shaped():
    for kind in POI_BUILDERS:
        parts = build_recipe({"kind": kind, "scale": 1.0})
        shaped = [p for p in parts if p["shape"] in SHAPED]
        assert len(parts) >= 3, f"{kind} has only {len(parts)} parts"
        assert len(shaped) >= 2, f"{kind} is a box stack: {[p['shape'] for p in parts]}"


def test_manifest_is_complete_and_passes_validation():
    spec = make_spec()
    manifest = build_manifest(spec)
    assert manifest["assets"], "manifest should not be empty"
    for asset in manifest["assets"]:
        assert asset["id"].startswith(("asset_", "theme_")), asset["id"]
        assert asset["recipe"], asset["id"]
        if asset["category"] == "structure":
            assert asset["footprint"] > 0, asset["id"]
            assert asset["mesh_prompt"], asset["id"]
    report = validate_asset_manifest(spec)
    critical = [issue for issue in report["issues"] if issue["severity"] == "critical"]
    assert not critical, critical


def test_box_only_structure_is_a_critical_failure():
    spec = make_spec()
    build_manifest(spec)
    assets = spec.asset_manifest["assets"]
    victim = next(a for a in assets if a["category"] == "structure")
    for part in victim["recipe"]:
        part["shape"] = "Block"
    report = validate_asset_manifest(spec)
    codes = {(issue["code"], issue["severity"]) for issue in report["issues"]}
    assert ("box_stack", "critical") in codes, report["issues"]
    assert report["passed"] is False


def test_reuse_is_measured_not_assumed():
    spec = make_spec()
    build_manifest(spec)
    tree = next((a for a in spec.asset_manifest["assets"] if a["category"] != "structure"), None)
    assert tree, [a["kind"] for a in spec.asset_manifest["assets"]]
    spec.data["placements"] = [{"asset": tree["id"], "kind": tree["kind"], "category": tree["category"],
                                "x": i * 5, "y": 10, "z": 0, "scale": 1.0} for i in range(12)]
    stats = reuse_stats(spec)
    assert stats["placed_instances"] == 12
    assert stats["most_reused"][0] == (tree["id"], 12)
    assert stats["estimated_parts"] > 0


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print("ok", name)
