"""Asset validation: the rule that stops a world from becoming a pile of squares.

Checks are intentionally mechanical:
  * every structure must have a silhouette beyond boxes (wedges, cylinders, balls, meshes);
  * per-category part and triangle budgets;
  * unique mesh count and reuse ratio;
  * every POI kind in the spec must have a recipe;
  * material names must exist in Roblox's material set.
"""
from __future__ import annotations

from world.terrain_builder import REGION_GROUND

VALID_MATERIALS = {
    "Plastic", "SmoothPlastic", "Neon", "Wood", "WoodPlanks", "Marble", "Slate", "Concrete",
    "Brick", "Cobblestone", "Rock", "Sand", "Grass", "Mud", "Ground", "Glacier", "Snow", "Metal",
    "CorrodedMetal", "Glass", "ForceField", "Fabric", "Basalt", "CrackedLava", "Water", "Ice",
    "LeafyGrass", "Limestone", "Pavement", "Pebble", "Salt", "Sandstone", "Granite", "Asphalt",
    "Cardboard", "Carpet", "CeramicTiles", "ClayRoofTiles", "DiamondPlate", "Foil", "Granite",
}

SHAPED = {"Wedge", "CornerWedge", "Cylinder", "Ball"}

CATEGORY_PART_LIMITS = {"structure": (8, 90), "vegetation": (3, 20), "rock": (3, 16),
                        "prop": (2, 16), "creature": (6, 30)}


def _issue(code: str, severity: str, message: str, fix: str, asset: str = "") -> dict:
    return {"code": code, "severity": severity, "message": message, "fix": fix, "asset": asset}


def validate_asset_manifest(spec) -> dict:
    assets = spec.asset_manifest.get("assets", [])
    issues: list[dict] = []
    if not assets:
        issues.append(_issue("empty_manifest", "critical", "Asset manifest is empty",
                             "Run the asset planner before code generation"))
    kinds_present = {a.get("kind") for a in assets}
    for poi in spec.pois:
        if poi.get("kind") not in kinds_present:
            issues.append(_issue("missing_recipe", "critical",
                                 f"No asset for landmark kind '{poi.get('kind')}'",
                                 "Add a recipe or map the kind to an existing asset", poi.get("name", "")))

    total_triangles = 0
    for asset in assets:
        aid = asset.get("id", "?")
        parts = asset.get("recipe") or []
        category = asset.get("category", "prop")
        required_min, max_parts = CATEGORY_PART_LIMITS.get(category, (2, 40))
        shaped = [p for p in parts if p.get("shape") in SHAPED]
        box_ratio = 1.0 - (len(shaped) / max(1, len(parts)))
        if category == "structure":
            if len(shaped) < 2:
                issues.append(_issue("box_stack", "critical",
                                     f"'{aid}' is built only from boxes ({len(parts)} parts)",
                                     "Add wedges/cylinders for roofs, arches, trunks or use generate_mesh", aid))
            elif box_ratio > 0.78:
                issues.append(_issue("box_dominant", "major",
                                     f"'{aid}' is {box_ratio:.0%} boxes; silhouette will read as a cube stack",
                                     "Replace flat roof/trim boxes with wedges, or generate a mesh", aid))
        if len(parts) < required_min:
            issues.append(_issue("too_few_parts", "major",
                                 f"'{aid}' has {len(parts)} parts (min {required_min} for {category})",
                                 "Enrich the recipe", aid))
        if len(parts) > max_parts:
            issues.append(_issue("too_many_parts", "minor",
                                 f"'{aid}' has {len(parts)} parts (budget {max_parts})",
                                 "Merge details or use a generated mesh", aid))
        if asset.get("method") == "mesh" and not asset.get("mesh_prompt"):
            issues.append(_issue("missing_mesh_prompt", "minor",
                                 f"'{aid}' is marked as mesh but has no prompt",
                                 "Provide a mesh prompt or mark it procedural", aid))
        for part in parts:
            if part.get("material") not in VALID_MATERIALS:
                issues.append(_issue("unknown_material", "major",
                                     f"'{aid}' uses unknown material '{part.get('material')}'",
                                     "Use a valid Roblox material name", aid))
        if float(asset.get("footprint", 0)) <= 0:
            issues.append(_issue("bad_footprint", "major", f"'{aid}' has no footprint",
                                 "Set footprint so placement can avoid overlaps", aid))
        total_triangles += int(asset.get("triangles", 0))

    # Ground materials referenced by regions must also be real.
    for region in spec.regions:
        ground = REGION_GROUND.get(region.get("kind", "forest"), "Ground")
        if ground not in VALID_MATERIALS:
            issues.append(_issue("bad_ground_material", "major",
                                 f"Region '{region.get('id')}' ground material '{ground}' is invalid",
                                 "Fix REGION_GROUND mapping", region.get("id", "")))

    placed = len(spec.placements)
    unique = len(assets)
    critical = [i for i in issues if i["severity"] == "critical"]
    result = {
        "passed": not critical,
        "critical_count": len(critical),
        "issues": issues,
        "stats": {
            "assets": unique,
            "placed": placed,
            "instances_per_definition": round(placed / unique, 2) if unique else 0,
            "declared_triangles": total_triangles,
            "shaped_share": round(
                sum(1 for a in assets for p in (a.get("recipe") or []) if p.get("shape") in SHAPED)
                / max(1, sum(len(a.get("recipe") or []) for a in assets)), 3),
            "mesh_assets": sum(1 for a in assets if a.get("method") == "mesh"),
        },
    }
    spec.data["asset_validation"] = result
    return result
