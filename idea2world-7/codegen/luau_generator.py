"""Generates the modular Luau project from a WorldSpec.

The generated project is data-driven: `MapConfig.lua` holds every number, colour and placement;
the other modules are the build system and are byte-identical between worlds. That makes generated
maps diffable, editable and reviewable instead of a 20k-line one-off script.
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from world.terrain_builder import REGION_GROUND, REGION_HEIGHT

from . import lua_emit

TEMPLATE_DIR = Path(__file__).resolve().parent / "luau_templates"

BUILD_MODULES = [
    "MapConfig.lua",
    "WorldLayout.lua",
    "AssetLibrary.lua",
    "TerrainBuilder.lua",
    "BiomeBuilder.lua",
    "PathBuilder.lua",
    "VegetationBuilder.lua",
    "AssetPlacement.lua",
    "BuildingBuilder.lua",
    "LightingController.lua",
    "AtmosphereController.lua",
    "VFXController.lua",
    "SoundscapeController.lua",
    "SpawnSetup.lua",
    "InteractionSetup.lua",
    "MapValidator.lua",
    "MapBootstrap.lua",
]

ENTRY_FILE = "MapBootstrap.server.lua"

DEFAULT_BUDGET = {"maxInstances": 14000, "maxTriangles": 420000, "maxParticleEmitters": 36,
                  "targetFps": 60, "maxUniqueMeshes": 140}

DEFAULT_SOUNDSCAPE = {
    "slots": [
        {"id": "ambience_day", "soundId": "", "volume": 0.35, "label": "day ambience"},
        {"id": "ambience_landmark", "soundId": "", "volume": 0.25, "label": "landmark proximity"},
    ],
    "note": "Roblox audio must be licensed and uploaded; fill soundId with your approved asset id.",
}


def _part_table(part: dict) -> dict:
    out = {
        "name": part["name"],
        "shape": part["shape"],
        "size": part["size"],
        "offset": part["offset"],
        "color": part["color"],
        "material": part["material"],
    }
    rot = part.get("rot") or [0, 0, 0]
    if any(abs(float(v)) > 1e-9 for v in rot):
        out["rot"] = rot
    if part.get("transparency"):
        out["transparency"] = part["transparency"]
    if part.get("collide") is False:
        out["collide"] = False
    if part.get("reflectance"):
        out["reflectance"] = part["reflectance"]
    if part.get("emissive"):
        out["emissive"] = True
    return out


def _config_sections(spec) -> list[str]:
    data = spec.data
    art = spec.art
    world = spec.world
    budget = {**DEFAULT_BUDGET, **{k: v for k, v in spec.budget.items()
                                  if k in ("max_instances", "max_triangles", "max_particle_emitters",
                                           "target_fps", "max_unique_meshes")}}
    budget_lua = {
        "maxInstances": budget["max_instances"],
        "maxTriangles": budget["max_triangles"],
        "maxParticleEmitters": budget["max_particle_emitters"],
        "targetFps": budget["target_fps"],
        "maxUniqueMeshes": budget["max_unique_meshes"],
    }
    lighting = dict(data.get("lighting") or {})
    lighting_lua = {
        "clockTime": lighting.get("clock_time", 15.2),
        "brightness": lighting.get("brightness", 2.2),
        "ambient": lighting.get("ambient", [96, 104, 120]),
        "exposure": lighting.get("exposure", 0.12),
    }
    atmosphere = dict(data.get("atmosphere") or {})
    atmosphere_lua = {
        "density": atmosphere.get("density", 0.28),
        "haze": atmosphere.get("haze", 1.5),
        "glare": atmosphere.get("glare", 0.15),
        "color": atmosphere.get("color", "role:highlight"),
        "decay": atmosphere.get("decay", "role:field"),
    }
    heightmap = world.get("heightmap") or {}
    rows = heightmap.get("rows") or []
    field = spec.heightfield() if rows else None
    hm = {
        "size": world.get("size", 2000),
        "res": heightmap.get("res", 0),
        "cell": round(float(field.cell), 4) if field else 0,
        "water": world.get("water_level", 6.0),
        "rows": rows,
    }
    regions = []
    for region in spec.regions:
        kind = region.get("kind", "forest")
        intent = dict(REGION_HEIGHT.get(kind, REGION_HEIGHT["forest"]))
        intent.update(region.get("height_profile") or {})
        regions.append({
            "id": region["id"], "name": region.get("name", region["id"]), "kind": kind,
            "center": region.get("center", [0, 0]), "radius": region.get("radius", 100),
            "density": region.get("density", 1.0),
            "ground": REGION_GROUND.get(kind, "Ground"),
            "heightStyle": intent.get("style", "flat"),
            "water": kind in ("lake", "coast", "marsh"),
        })
    paths = [{"id": p["id"], "name": p.get("name", p["id"]), "kind": p.get("kind", "main"),
              "width": p.get("width", 12), "nodes": p.get("nodes", []),
              "connects": p.get("connects", [])} for p in spec.paths]
    pois = [{"id": p["id"], "name": p.get("name", p["id"]), "kind": p["kind"],
             "region": p.get("region"), "x": p.get("x"), "z": p.get("z"),
             "scale": p.get("scale", 1.0), "rotation": p.get("rotation", 0),
             "role": p.get("role", "support"), "interaction": p.get("interaction", "landmark")}
            for p in spec.pois]
    spawns = [{"id": s.get("id", "spawn_main"), "name": s.get("name", "Main spawn"),
               "x": s.get("x", 0), "z": s.get("z", 0), "facing": s.get("facing_deg", 0),
               "radius": s.get("radius", 12)} for s in spec.spawns]
    biomes = []
    for zone in data.get("biomes") or []:
        biomes.append({
            "region": zone["region"], "kind": zone["kind"], "material": zone["material"],
            "color": zone["color"], "tint": zone["tint"], "tint_mix": zone["tint_mix"],
            "snow_cap": zone.get("snow_cap", False),
            "water": zone.get("water") is not None,
            "patches": [{"x": p["x"], "z": p["z"], "y": p["y"], "size": p["size"],
                         "rot": p["rot"], "alpha": p["alpha"]} for p in zone.get("patches", [])],
        })
    assets = []
    for asset in spec.asset_manifest.get("assets", []):
        assets.append({
            "id": asset["id"], "kind": asset["kind"], "name": asset.get("name", asset["kind"]),
            "category": asset.get("category", "prop"), "height": asset.get("height", 8),
            "footprint": asset.get("footprint", 4), "method": asset.get("method", "procedural"),
            "parts": [_part_table(p) for p in asset.get("recipe") or []],
        })
    placements: dict[str, list] = {}
    for entry in spec.placements:
        placements.setdefault(entry["region"], []).append(
            [entry["asset"], entry["x"], entry["z"], entry["rot"], entry["scale"], entry.get("color", "")])
    poi_decor = [[d["asset"], d["poi"], d["x"], d["z"], d["rot"], d["scale"], d.get("color", "")]
                 for d in data.get("poi_decor") or []]
    ambient = [{"id": v["id"], "x": v["x"], "y": v["y"], "z": v["z"],
                "rate": v["rate"], "radius": v.get("radius", 80), "color": v["color"]}
               for v in data.get("ambient_vfx") or []]

    sections = [
        f"-- {spec.title}\n-- Idea: {spec.idea}\n-- Generated by Idea2World 6.0. This file is data only:\n"
        f"-- edit numbers, colours and placements here; the builder modules stay unchanged.\n",
        f"local Config = {{}}\n",
        lua_emit.table("Config.Title", spec.title),
        lua_emit.table("Config.Slug", spec.slug),
        lua_emit.table("Config.Idea", spec.idea),
        lua_emit.table("Config.Genre", data.get("genre", "general_adventure")),
        lua_emit.table("Config.Style", art.get("style", "stylized_low_poly")),
        lua_emit.table("Config.StyleLabel", art.get("style_label", "Stylized")),
        lua_emit.table("Config.Theme", art.get("theme", "natural")),
        lua_emit.table("Config.Seed", int(world.get("seed", 42))),
        lua_emit.table("Config.Size", world.get("size", 2000)),
        lua_emit.table("Config.TerrainCells", int(world.get("terrain_cells", 100)),
                       "Terrain fill resolution. Raise for sharper cliffs, lower for faster builds."),
        lua_emit.table("Config.PlacementCount", len(spec.placements)),
        lua_emit.table("Config.Palette", art.get("palette") or {}),
        lua_emit.table("Config.Lighting", lighting_lua),
        lua_emit.table("Config.Atmosphere", atmosphere_lua),
        lua_emit.table("Config.Budget", budget_lua),
        lua_emit.table("Config.Soundscape", data.get("soundscape") or DEFAULT_SOUNDSCAPE),
        lua_emit.table("Config.Heightmap", hm,
                       "Baked by the planner; WorldLayout samples this with the same bilinear filter"),
        lua_emit.table("Config.Regions", regions),
        lua_emit.table("Config.Paths", paths),
        lua_emit.table("Config.Pois", pois),
        lua_emit.table("Config.Spawns", spawns),
        lua_emit.table("Config.Biomes", biomes),
        lua_emit.table("Config.Assets", assets),
        "-- Placements[region] = { {assetId, x, z, rotationDeg, scale, tint}, ... }\n"
        + lua_emit.table("Config.Placements", placements),
        "-- PoiDecor = { {assetId, poiId, x, z, rotationDeg, scale, tint}, ... }\n"
        + lua_emit.table("Config.PoiDecor", poi_decor),
        "-- AmbientVfx entries: { id, x, y, z, rate (particles/s), radius, color }\n"
        + lua_emit.table("Config.AmbientVfx", ambient),
        "return Config\n",
    ]
    return sections


def config_source(spec) -> str:
    return "\n".join(_config_sections(spec))


def project_sources(spec) -> dict[str, str]:
    sources: dict[str, str] = {}
    for name in BUILD_MODULES:
        if name == "MapConfig.lua":
            sources[name] = config_source(spec)
            continue
        path = TEMPLATE_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"missing Luau template: {name}")
        sources[name] = path.read_text(encoding="utf-8")
    entry = TEMPLATE_DIR / ENTRY_FILE
    if entry.exists():
        sources[ENTRY_FILE] = entry.read_text(encoding="utf-8")
    return sources


def install_readme(spec) -> str:
    return f"""# {spec.title} — generated by Idea2World 6.0

Idea: {spec.idea}

## Install in Roblox Studio

1. Open your place, then **File → Save to Roblox** so you have a restore point.
2. In the Explorer, insert a **Folder** inside `ServerScriptService` named `Idea2World_Generated_Map`.
3. Insert the `.lua` files as **ModuleScripts** with the same names (drop the `.lua` suffix), except
   `MapBootstrap.server.lua`, which is a **Script**.
4. Press **Play** (F5). The map builds in stages; the Output window prints a build report.
5. To rebuild in Edit mode instead, run this in the Command Bar:

```lua
local boot = require(game.ServerScriptService.Idea2World_Generated_Map.MapBootstrap)
boot.build({{ verbose = true }})
```

Rebuilding is safe: the previous world is archived to `ServerStorage/Idea2World_Backups`
(three most recent kept) before a new one is created.

## Or with Rojo

`default.project.json` syncs this folder into `ServerScriptService`. Run `rojo serve` and connect
from the Rojo Studio plugin.

## Files

| File | Role |
| --- | --- |
| `MapBootstrap.lua` | staged build entry point (`build`, `validate`, `clear`) |
| `MapConfig.lua` | **all data**: palette, regions, paths, landmarks, assets, placements |
| `WorldLayout.lua` | heightmap sampling, path distance, region lookup |
| `TerrainBuilder.lua` | Roblox Terrain fill + water bodies |
| `BiomeBuilder.lua` | district ground tint, shores, snow caps |
| `PathBuilder.lua` | route ribbons and edge stones |
| `BuildingBuilder.lua` | landmark structures + labels + interaction anchors |
| `VegetationBuilder.lua` | vegetation placement with distance LOD |
| `AssetPlacement.lua` | rocks, props, creatures, landmark dressing |
| `AssetLibrary.lua` | recipe/mesh -> Model assembler |
| `LightingController.lua` / `AtmosphereController.lua` | art-direction lighting rig |
| `VFXController.lua` / `SoundscapeController.lua` | budgeted ambience |
| `SpawnSetup.lua` / `InteractionSetup.lua` | spawn, prompts, district plates |
| `MapValidator.lua` | post-build structural checks |
"""


def command_bar_bundle(sources: dict[str, str]) -> str:
    """A single paste-once script that installs the module tree and builds the world."""
    parts = ["-- Idea2World 6.0 -- one-shot Command Bar installer.",
             "-- Paste into Roblox Studio's Command Bar in Edit mode, then press Enter.",
             "-- Creates ServerScriptService/Idea2World_Generated_Map and builds immediately.",
             "local Sources = {"]
    for name, source in sources.items():
        parts.append(f'\t["{name[:-4]}"] = {lua_emit.long_string(source)},')
    parts.append("}")
    parts.append("")
    parts.append("""local ServerScriptService = game:GetService("ServerScriptService")
local container = ServerScriptService:FindFirstChild("Idea2World_Generated_Map")
if container then
	container:Destroy()
end
container = Instance.new("Folder")
container.Name = "Idea2World_Generated_Map"
container.Parent = ServerScriptService
for name, source in pairs(Sources) do
	local module = Instance.new("ModuleScript")
	module.Name = name
	module.Source = source
	module.Parent = container
end
local bootstrap = require(container:FindFirstChild("MapBootstrap"))
local report = bootstrap.build({ verbose = true })
print(("[Idea2World] build %s"):format(report.passed and "PASSED" or "FAILED"))
return report""")
    return "\n".join(parts)


def write_project(spec, out_dir) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sources = project_sources(spec)
    written = {}
    for name, source in sources.items():
        path = out / name
        path.write_text(source, encoding="utf-8")
        written[name] = {"path": str(path), "bytes": len(source.encode("utf-8")), "lines": source.count("\n") + 1}
    (out / "README_INSTALL.md").write_text(install_readme(spec), encoding="utf-8")
    (out / "default.project.json").write_text(json.dumps({
        "name": spec.slug,
        "tree": {
            "$className": "DataModel",
            "ServerScriptService": {"$path": "."},
        },
    }, indent=2), encoding="utf-8")
    bundle_path = out / "CommandBar_Install.lua"
    bundle_path.write_text(command_bar_bundle(sources), encoding="utf-8")
    total = sum(v["bytes"] for v in written.values())
    return {"directory": str(out), "files": written, "total_bytes": total,
            "bundle": str(bundle_path), "source_count": len(sources)}


def copy_to(spec, source_dir, target_dir) -> None:
    src, dst = Path(source_dir), Path(target_dir)
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.is_file():
            shutil.copy2(item, dst / item.name)
