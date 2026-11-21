"""WorldSpec: the single contract between planning, code generation, Studio build and QA.

Everything downstream (Luau modules, asset manifest, visual critic, QA report) reads this object.
If a field is not in the spec, the build cannot invent it -- that is the point: it keeps generated
worlds reviewable, diffable and re-buildable.
"""
from __future__ import annotations

import json
import math
from typing import Any

from .heightfield import Heightfield

SCHEMA_VERSION = 6

REQUIRED_SECTIONS = ["idea", "title", "genre", "regions", "paths", "pois", "spawns", "art_direction",
                     "world", "lighting", "budget"]

DEFAULT_BUDGET = {
    "max_instances": 14000,
    "max_triangles": 420000,
    "max_unique_meshes": 140,
    "max_particle_emitters": 36,
    "max_scripts": 24,
    "target_fps": 60,
    "terrain_cells": 110,
}


def _issue(code: str, severity: str, message: str, fix: str, scope: str = "world") -> dict:
    return {"code": code, "severity": severity, "message": message, "fix": fix, "scope": scope}


class WorldSpec:
    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError("WorldSpec data must be a dict")
        self.data = data
        self.data.setdefault("schema_version", SCHEMA_VERSION)
        self.issues: list[dict] = []

    # -- io ---------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict) -> "WorldSpec":
        return cls(json.loads(json.dumps(data)))

    @classmethod
    def load(cls, path) -> "WorldSpec":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> dict:
        return self.data

    def save(self, path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def clone(self) -> "WorldSpec":
        return WorldSpec.from_dict(self.data)

    # -- accessors --------------------------------------------------------------------
    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        self.data[key] = value

    @property
    def idea(self) -> str:
        return str(self.data.get("idea", ""))

    @property
    def title(self) -> str:
        return str(self.data.get("title", "Untitled World"))

    @property
    def slug(self) -> str:
        base = "".join(c if c.isalnum() else "_" for c in self.title.lower()).strip("_")
        while "__" in base:
            base = base.replace("__", "_")
        return base[:48] or "world"

    @property
    def regions(self) -> list[dict]:
        return self.data.setdefault("regions", [])

    @property
    def paths(self) -> list[dict]:
        return self.data.setdefault("paths", [])

    @property
    def pois(self) -> list[dict]:
        return self.data.setdefault("pois", [])

    @property
    def spawns(self) -> list[dict]:
        return self.data.setdefault("spawns", [])

    @property
    def art(self) -> dict:
        return self.data.setdefault("art_direction", {})

    @property
    def world(self) -> dict:
        return self.data.setdefault("world", {})

    @property
    def budget(self) -> dict:
        merged = dict(DEFAULT_BUDGET)
        merged.update(self.data.get("budget") or {})
        return merged

    @property
    def asset_manifest(self) -> dict:
        return self.data.setdefault("asset_manifest", {"assets": []})

    @property
    def placements(self) -> list[dict]:
        return self.data.setdefault("placements", [])

    def region(self, region_id: str) -> dict | None:
        return next((r for r in self.regions if r.get("id") == region_id), None)

    def poi(self, poi_id: str) -> dict | None:
        return next((p for p in self.pois if p.get("id") == poi_id), None)

    def heightfield(self) -> Heightfield:
        baked = self.world.get("heightmap") or {}
        if not baked.get("rows"):
            raise ValueError("WorldSpec has no baked heightmap")
        return Heightfield(self.world.get("size", 2000), baked["res"], baked["rows"],
                           water=baked.get("water", self.world.get("water_level")))

    def set_heightfield(self, field: Heightfield) -> None:
        self.world["heightmap"] = {"res": field.res, "rows": field.rows_int(),
                                   "water": round(field.water, 2)}
        self.world.setdefault("size", field.size)

    def height_at(self, x: float, z: float) -> float:
        return self.heightfield().at(x, z)

    # -- validation -------------------------------------------------------------------
    def validate(self) -> list[dict]:
        issues: list[dict] = []
        for section in REQUIRED_SECTIONS:
            if not self.data.get(section):
                issues.append(_issue(f"missing_{section}", "critical",
                                     f"WorldSpec section '{section}' is missing or empty",
                                     f"Planner must populate '{section}'", section))

        ids: set[str] = set()
        for coll in ("regions", "pois", "paths"):
            for item in self.data.get(coll, []):
                iid = item.get("id")
                if not iid:
                    issues.append(_issue("missing_id", "major", f"An entry in {coll} has no id",
                                         "Assign a stable id", coll))
                elif iid in ids:
                    issues.append(_issue("duplicate_id", "major", f"Duplicate id '{iid}'",
                                         "Make ids unique across regions/pois/paths", coll))
                else:
                    ids.add(iid)

        size = float(self.world.get("size", 0) or 0)
        half = size / 2.0
        if size <= 0:
            issues.append(_issue("bad_world_size", "critical", "World size must be positive",
                                 "Set world.size in studs", "world"))

        for region in self.regions:
            center = region.get("center") or [0, 0]
            if len(center) != 2:
                issues.append(_issue("bad_region_center", "critical",
                                     f"Region '{region.get('id')}' center must be [x,z]",
                                     "Use a two-number center", "regions"))
                continue
            radius = float(region.get("radius", 0))
            if radius <= 0:
                issues.append(_issue("bad_region_radius", "major",
                                     f"Region '{region.get('id')}' radius is not positive",
                                     "Set radius in studs", "regions"))
            if not region.get("kind"):
                issues.append(_issue("region_kind_missing", "minor",
                                     f"Region '{region.get('id')}' has no kind",
                                     "Set a kind (hub/forest/village/...) so builders can dress it",
                                     "regions"))

        if len(self.regions) < 3:
            issues.append(_issue("too_few_regions", "major", "A world needs at least 3 regions",
                                 "Add distinct districts with different biome/height intent", "regions"))

        # Regions should differ in intent, not be 8 copies of the same circle.
        kinds = [r.get("kind") for r in self.regions]
        if len(set(kinds)) < max(2, len(kinds) // 3):
            issues.append(_issue("region_monotony", "major", "Regions repeat the same kind",
                                 "Vary region kinds and height profiles", "regions"))

        region_ids = {r.get("id") for r in self.regions}
        poi_ids = {p.get("id") for p in self.pois}
        for path in self.paths:
            nodes = path.get("nodes") or []
            if len(nodes) < 2:
                issues.append(_issue("path_too_short", "major",
                                     f"Path '{path.get('id')}' has fewer than 2 nodes",
                                     "Give the path a real route", "paths"))
            for node in nodes:
                if not (isinstance(node, (list, tuple)) and len(node) == 2):
                    issues.append(_issue("bad_path_node", "major",
                                         f"Path '{path.get('id')}' has a malformed node", "Use [x,z]", "paths"))
                    break
            for rid in path.get("connects", []):
                if rid not in region_ids and rid not in poi_ids:
                    issues.append(_issue("dangling_path", "critical",
                                         f"Path '{path.get('id')}' connects unknown region '{rid}'",
                                         "Fix the region id or remove the connection", "paths"))

        for poi in self.pois:
            if not (0 <= float(poi.get("x", 0)) <= half and 0 <= float(poi.get("z", 0)) <= half):
                # POIs use centered coordinates internally but tolerate [0,size] authoring.
                if not (-half <= float(poi.get("x", 0)) <= half and -half <= float(poi.get("z", 0)) <= half):
                    issues.append(_issue("poi_out_of_bounds", "critical",
                                         f"POI '{poi.get('id')}' sits outside the world bounds",
                                         "Move it inside world.size/2", "pois"))
            if poi.get("region") and poi["region"] not in region_ids:
                issues.append(_issue("poi_orphan_region", "major",
                                     f"POI '{poi.get('id')}' references unknown region", "Fix region id", "pois"))
            if not poi.get("kind"):
                issues.append(_issue("poi_kind_missing", "major", f"POI '{poi.get('id')}' has no kind",
                                     "Set a POI kind so a builder recipe is selected", "pois"))

        if not self.spawns:
            issues.append(_issue("no_spawn", "critical", "No spawn point defined",
                                 "Add at least one spawn", "spawns"))
        for spawn in self.spawns:
            d = math.hypot(float(spawn.get("x", 0)), float(spawn.get("z", 0)))
            if d > half:
                issues.append(_issue("spawn_out_of_bounds", "critical", "Spawn is outside the world",
                                     "Move the spawn inward", "spawns"))

        art = self.art
        palette = art.get("palette") or {}
        for role in ("field", "structure", "accent", "highlight"):
            if not palette.get(role):
                issues.append(_issue(f"palette_{role}_missing", "major",
                                     f"Art direction is missing the '{role}' palette role",
                                     "Define all palette roles so builders and the critic agree", "art_direction"))

        baked = self.world.get("heightmap") or {}
        if baked and baked.get("rows"):
            rows = baked["rows"]
            if len(rows) != baked.get("res") or any(len(r) != baked.get("res") for r in rows):
                issues.append(_issue("heightmap_shape", "critical", "Baked heightmap is malformed",
                                     "Regenerate the heightfield", "world"))

        # Asset manifest coverage: every POI kind that needs geometry must have a recipe.
        manifest_kinds = {a.get("kind") for a in self.asset_manifest.get("assets", [])}
        for poi in self.pois:
            if poi.get("kind") and poi["kind"] not in manifest_kinds and poi["kind"] not in ("spawn", "viewpoint"):
                issues.append(_issue("poi_asset_missing", "major",
                                     f"No asset recipe for POI kind '{poi['kind']}'",
                                     "Add a recipe to the asset plan or map the kind to an existing one", "assets"))

        self.issues = issues
        return issues

    def critical_issues(self) -> list[dict]:
        return [i for i in self.validate() if i["severity"] == "critical"]

    # -- reporting --------------------------------------------------------------------
    def summary(self) -> dict:
        return {
            "title": self.title,
            "genre": self.data.get("genre"),
            "style": self.art.get("style_label"),
            "theme": self.art.get("theme"),
            "size": self.world.get("size"),
            "regions": len(self.regions),
            "pois": len(self.pois),
            "paths": len(self.paths),
            "placements": len(self.placements),
            "assets": len(self.asset_manifest.get("assets", [])),
            "spawns": len(self.spawns),
            "budget": self.budget,
        }

    def where(self, x: float, z: float) -> dict | None:
        """Nearest region for a world position (used by balance + QA)."""
        best, best_d = None, float("inf")
        for region in self.regions:
            cx, cz = region.get("center", [0, 0])
            d = math.hypot(x - cx, z - cz)
            if d < best_d:
                best, best_d = region, d
        return best
