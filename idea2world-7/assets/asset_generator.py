"""Procedural asset recipes and the AI-mesh plan.

Two paths exist for every asset:

1. `generate_mesh` (Roblox Studio MCP) with a written prompt — preferred for organic subjects
   (trees, rocks, animals, statues) where hand-placed primitives cannot express the silhouette.
2. A layered *recipe* of shaped parts (balls, cylinders, wedges, corner wedges) that the Luau
   builder assembles when no mesh generator is available.

A flat stack of Blocks is never an acceptable recipe: `asset_validator` rejects recipes whose
silhouette is only boxes, which is what turned 5.0 maps into "piles of squares".
"""
from __future__ import annotations

from typing import Callable

from research.reference_library import PLAYER_HEIGHT_STUDS

P = PLAYER_HEIGHT_STUDS


def _part(name: str, shape: str, size, offset, color: str, material: str, rot=None,
          transparency: float = 0.0, collide: bool = True, reflectance: float = 0.0,
          emissive: bool = False) -> dict:
    return {"name": name, "shape": shape, "size": [round(v, 2) for v in size],
            "offset": [round(v, 2) for v in offset], "rot": list(rot or (0, 0, 0)),
            "color": color, "material": material, "transparency": transparency,
            "collide": collide, "reflectance": reflectance, "emissive": emissive}


def _box(n, size, off, color, mat, **kw):
    return _part(n, "Block", size, off, color, mat, **kw)


def _cyl(n, size, off, color, mat, **kw):
    return _part(n, "Cylinder", size, off, color, mat, **kw)


def _ball(n, size, off, color, mat, **kw):
    return _part(n, "Ball", size, off, color, mat, **kw)


def _wedge(n, size, off, color, mat, **kw):
    return _part(n, "Wedge", size, off, color, mat, **kw)


def _corner(n, size, off, color, mat, **kw):
    return _part(n, "CornerWedge", size, off, color, mat, **kw)


# Palette roles resolve at build time: "role:field", "role:structure", "role:accent", ...
def C(role: str) -> str:
    return f"role:{role}"


# ---------------------------------------------------------------------------------------------
# POI builders. Each returns (height, parts). Sizes are in studs, tuned against a 5-stud player.
# ---------------------------------------------------------------------------------------------

def _house(width: float, depth: float, height: float, wall: str = C("structure"),
           roof: str = C("structure_alt"), accent: str = C("accent")) -> list[dict]:
    parts = [
        _box("Walls", (width, height, depth), (0, height / 2, 0), wall, "WoodPlanks"),
        _box("Foundation", (width + 2.4, 2.2, depth + 2.4), (0, 1.1, 0), C("structure_alt"), "Slate"),
        # Gable roof: two wedges meet at the ridge, so the silhouette is not a box.
        _wedge("Roof_A", (width + 2.6, height * 0.62, depth / 2 + 1.2),
               (0, height + height * 0.31, depth / 4 + 0.4), roof, "WoodPlanks"),
        _wedge("Roof_B", (width + 2.6, height * 0.62, depth / 2 + 1.2),
               (0, height + height * 0.31, -depth / 4 - 0.4), roof, "WoodPlanks",
               rot=(0, 180, 0)),
        _box("Door", (width * 0.20, height * 0.52, 0.6), (0, height * 0.26, depth / 2 + 0.1),
             C("structure_alt"), "Wood"),
        _box("DoorFrame", (width * 0.26, height * 0.58, 0.4), (0, height * 0.29, depth / 2 + 0.05),
             C("highlight"), "Slate"),
    ]
    for i, sx in enumerate((-0.32, 0.32)):
        parts.append(_box(f"Window_{i}", (width * 0.16, height * 0.22, 0.5),
                          (width * sx, height * 0.62, depth / 2 + 0.12), accent, "Glass",
                          transparency=0.35, emissive=True, collide=False))
    parts.append(_cyl("Chimney", (2.2, height * 0.45, 2.2), (width * 0.30, height * 1.05, -depth * 0.18),
                      C("structure_alt"), "Brick"))
    parts.append(_box("Step", (width * 0.34, 0.8, 2.6), (0, 0.4, depth / 2 + 1.6), C("highlight"), "Slate"))
    return parts


def _tower(height: float) -> tuple[float, list[dict]]:
    w = 9.0
    parts = [
        _cyl("Shaft", (w, height, w), (0, height / 2, 0), C("structure"), "Slate"),
        _cyl("Base", (w * 1.5, 4.0, w * 1.5), (0, 2.0, 0), C("structure_alt"), "Slate"),
        _cyl("Balcony", (w * 1.9, 2.0, w * 1.9), (0, height * 0.72, 0), C("highlight"), "Slate"),
        _cyl("Crown", (w * 1.25, height * 0.10, w * 1.25), (0, height * 1.02, 0), C("accent"), "Metal"),
    ]
    parts.append(_part("Spire", "Wedge", (w * 0.9, height * 0.22, w * 0.9),
                       (0, height * 1.16, 0), C("accent"), "Metal"))
    for i in range(6):
        import math
        a = i * math.pi / 3
        parts.append(_box(f"ArrowSlit_{i}", (0.8, height * 0.05, 0.8),
                          (math.cos(a) * w * 0.51, height * 0.82, math.sin(a) * w * 0.51),
                          C("accent"), "Neon", emissive=True, collide=False))
    parts.append(_box("Door", (3.0, 6.0, 1.0), (0, 3.0, w * 0.42), C("structure_alt"), "Wood"))
    return height * 1.3, parts


def _monument(height: float) -> tuple[float, list[dict]]:
    parts = [
        _cyl("Plinth", (14.0, 3.0, 14.0), (0, 1.5, 0), C("structure_alt"), "Slate"),
        _cyl("PlinthTop", (10.0, 1.6, 10.0), (0, 3.8, 0), C("highlight"), "Slate"),
        _part("Obelisk", "Wedge", (7.0, height, 7.0), (0, 4.6 + height / 2, 0), C("structure"), "Slate"),
        _cyl("Collar", (8.2, 1.2, 8.2), (0, 4.6 + height * 0.55, 0), C("highlight"), "Metal"),
        _ball("Keystone", (3.4, 3.4, 3.4), (0, 5.4 + height, 0), C("accent"), "Neon",
              emissive=True, collide=False),
    ]
    for i in range(4):
        import math
        a = i * math.pi / 2 + math.pi / 4
        parts.append(_cyl(f"Column_{i}", (1.8, 7.0, 1.8),
                          (math.cos(a) * 5.2, 7.5, math.sin(a) * 5.2), C("highlight"), "Slate"))
    return 5.4 + height + 4, parts


def _village(height: float) -> tuple[float, list[dict]]:
    parts, offset = [], 0.0
    layout = [(-16, -8, 15, 12, 11), (4, -14, 18, 12, 13), (20, 6, 14, 11, 10), (-6, 16, 16, 12, 12)]
    for i, (ox, oz, w, d, h) in enumerate(layout):
        for p in _house(w, d, h * (height / 26.0)):
            p = dict(p)
            p["offset"] = [p["offset"][0] + ox, p["offset"][1], p["offset"][2] + oz]
            p["name"] = f"House{i + 1}_{p['name']}"
            parts.append(p)
    # Well + lantern posts give the village a centre and readable scale cues.
    parts.append(_cyl("WellRing", (7.0, 2.4, 7.0), (0, 1.2, 2), C("highlight"), "Cobblestone"))
    parts.append(_cyl("WellWater", (6.0, 0.6, 6.0), (0, 2.4, 2), C("field_alt"), "Water", transparency=0.3, collide=False))
    for i, (lx, lz) in enumerate(((-10, 6), (10, 8), (0, -4))):
        parts.append(_cyl(f"LanternPost_{i}", (0.8, 9.0, 0.8), (lx, 4.5, lz), C("structure_alt"), "Wood"))
        parts.append(_ball(f"Lantern_{i}", (2.0, 2.0, 2.0), (lx, 9.4, lz), C("accent"), "Neon",
                           emissive=True, collide=False))
    return 20.0 * (height / 26.0), parts


def _temple(height: float) -> tuple[float, list[dict]]:
    parts = [
        _box("Stylobate", (40, 3, 30), (0, 1.5, 0), C("structure_alt"), "Slate"),
        _box("Stylobate2", (34, 2, 24), (0, 4, 0), C("highlight"), "Slate"),
        _box("Cella", (20, height * 0.55, 14), (0, 5 + height * 0.275, 0), C("structure"), "Slate"),
        _wedge("PedimentA", (24, height * 0.35, 8), (0, 5 + height * 0.55 + height * 0.175, 4.5),
               C("structure_alt"), "Slate"),
        _wedge("PedimentB", (24, height * 0.35, 8), (0, 5 + height * 0.55 + height * 0.175, -4.5),
               C("structure_alt"), "Slate", rot=(0, 180, 0)),
    ]
    for i in range(6):
        x = -15 + i * 6
        parts.append(_cyl(f"Column_{i}", (2.2, height * 0.55, 2.2), (x, 5 + height * 0.275, 11),
                          C("highlight"), "Marble"))
        parts.append(_cyl(f"ColumnB_{i}", (2.2, height * 0.55, 2.2), (x, 5 + height * 0.275, -11),
                          C("highlight"), "Marble"))
    parts.append(_box("Altar", (6, 2.4, 4), (0, 6.2, 0), C("accent"), "Marble", emissive=True, collide=False))
    return 5 + height, parts


def _ruins(height: float) -> tuple[float, list[dict]]:
    parts = []
    import math
    for i in range(7):
        a = i * 1.17
        r = 16 + (i % 3) * 5
        h = height * (0.25 + 0.14 * ((i * 7) % 5))
        x, z = math.cos(a) * r, math.sin(a) * r
        parts.append(_box(f"Wall_{i}", (7.5, h, 2.6), (x, h / 2, z), C("structure"), "Slate", rot=(0, math.degrees(a), 0)))
        parts.append(_corner(f"BrokenTop_{i}", (7.5, 2.4, 2.6), (x, h + 1.2, z), C("structure"), "Slate",
                             rot=(0, math.degrees(a), 0)))
    for i in range(3):
        # A real arch: two pillars + a wedge pair instead of a floating rectangle.
        x = -12 + i * 12
        parts.append(_cyl(f"ArchPillarA_{i}", (2.4, height * 0.6, 2.4), (x - 4, height * 0.3, 0), C("highlight"), "Slate"))
        parts.append(_cyl(f"ArchPillarB_{i}", (2.4, height * 0.6, 2.4), (x + 4, height * 0.3, 0), C("highlight"), "Slate"))
        parts.append(_wedge(f"ArchL_{i}", (4.2, 2.6, 2.4), (x - 2, height * 0.6 + 1.3, 0), C("highlight"), "Slate",
                            rot=(0, 0, -28)))
        parts.append(_wedge(f"ArchR_{i}", (4.2, 2.6, 2.4), (x + 2, height * 0.6 + 1.3, 0), C("highlight"), "Slate",
                            rot=(0, 0, 28)))
    return height, parts


def _castle(height: float) -> tuple[float, list[dict]]:
    parts = [_box("Keep", (24, height * 0.85, 20), (0, height * 0.425, 0), C("structure"), "Slate")]
    for i, (sx, sz, w) in enumerate(((-15, -13, 12), (15, -13, 12), (-15, 13, 12), (15, 13, 12))):
        parts.append(_cyl(f"Tower_{i}", (w, height, w), (sx, height / 2, sz), C("structure_alt"), "Slate"))
        parts.append(_part(f"TowerRoof_{i}", "Wedge", (w * 1.15, height * 0.22, w * 1.15),
                           (sx, height + height * 0.11, sz), C("accent"), "Slate"))
    for i, (sx, sz) in enumerate(((-9, 10), (9, 10), (-9, -10), (9, -10))):
        parts.append(_box(f"GateTower_{i}", (7, height * 0.6, 7), (sx, height * 0.3, sz), C("structure_alt"), "Slate"))
    parts.append(_box("Gate", (9, height * 0.45, 2.4), (0, height * 0.225, 10.4), C("structure_alt"), "Wood"))
    parts.append(_wedge("GateArch", (9, 4.0, 2.4), (0, height * 0.45 + 2.0, 10.4), C("accent"), "Slate"))
    for i in range(10):
        parts.append(_box(f"Battlement_{i}", (3.2, 3.0, 3.2), (-11 + i * 2.5, height * 0.85 + 1.5, -9.4),
                          C("structure"), "Slate"))
    parts.append(_cyl("Banner", (0.8, 14, 0.8), (0, height * 1.12, 0), C("accent"), "Metal"))
    parts.append(_box("Flag", (7, 4, 0.4), (3.6, height * 1.18, 0), C("accent"), "Fabric", collide=False))
    return height, parts


def _arena(height: float) -> tuple[float, list[dict]]:
    import math
    parts = [_cyl("Floor", (74, 3, 74), (0, 1.5, 0), C("structure_alt"), "Slate")]
    for i in range(18):
        a = i * (2 * math.pi / 18)
        parts.append(_cyl(f"Pillar_{i}", (3.4, height * 0.55, 3.4),
                          (math.cos(a) * 38, height * 0.275, math.sin(a) * 38), C("structure"), "Slate"))
        parts.append(_box(f"Rail_{i}", (11.5, 2.2, 1.6),
                          (math.cos(a) * 38, height * 0.55 + 1.1, math.sin(a) * 38),
                          C("highlight"), "Metal", rot=(0, math.degrees(a) + 90, 0)))
    parts.append(_cyl("FocalPillar", (6, height * 0.8, 6), (0, height * 0.4, 0), C("accent"), "Metal"))
    parts.append(_ball("ArenaCore", (8, 8, 8), (0, height * 0.9, 0), C("accent"), "Neon", emissive=True, collide=False))
    return height, parts


def _portal(height: float) -> tuple[float, list[dict]]:
    import math
    parts = [_cyl("Base", (22, 2.4, 22), (0, 1.2, 0), C("structure_alt"), "Slate")]
    for i in range(10):
        a = i * (2 * math.pi / 10)
        h = height * (0.8 + 0.25 * math.sin(i * 1.7))
        parts.append(_cyl(f"Ring_{i}", (2.4, h, 2.4), (math.cos(a) * 11, h / 2, math.sin(a) * 11),
                          C("structure"), "Slate"))
    parts.append(_part("Lintel", "Cylinder", (5.2, 23, 5.2), (0, height * 0.95, 0), C("highlight"), "Metal",
                       rot=(0, 0, 90)))
    parts.append(_ball("PortalCore", (16, 18, 4), (0, height * 0.55, 0), C("accent"), "ForceField",
                       transparency=0.35, emissive=True, collide=False))
    parts.append(_ball("Orb", (4.2, 4.2, 4.2), (0, height * 1.2, 0), C("accent"), "Neon",
                       emissive=True, collide=False))
    return height * 1.3, parts


def _observatory(height: float) -> tuple[float, list[dict]]:
    parts = [
        _cyl("Base", (34, height * 0.34, 34), (0, height * 0.17, 0), C("structure"), "Concrete"),
        _ball("Dome", (26, 24, 26), (0, height * 0.34 + 6, 0), C("structure_alt"), "Metal"),
        _cyl("DomeRing", (28, 2.4, 28), (0, height * 0.34 + 4, 0), C("highlight"), "Metal"),
        _cyl("ScopeBarrel", (5.0, 22, 5.0), (0, height * 0.34 + 18, 4), C("accent"), "Metal", rot=(-18, 0, 0)),
        _box("Door", (6, 9, 1.4), (0, 4.5, 17), C("accent"), "Glass", transparency=0.4, emissive=True),
    ]
    for i in range(8):
        import math
        a = i * math.pi / 4
        parts.append(_cyl(f"Buttress_{i}", (2.2, height * 0.3, 2.2),
                          (math.cos(a) * 17, height * 0.15, math.sin(a) * 17), C("highlight"), "Concrete"))
    return height * 0.34 + 34, parts


def _factory(height: float) -> tuple[float, list[dict]]:
    parts = [
        _box("Hall", (46, height * 0.5, 30), (0, height * 0.25, 0), C("structure"), "Concrete"),
        _part("SawRoof_A", "Wedge", (47, 9, 15), (0, height * 0.5 + 4.5, 7.5), C("structure_alt"), "Metal"),
        _part("SawRoof_B", "Wedge", (47, 9, 15), (0, height * 0.5 + 4.5, -7.5), C("structure_alt"), "Metal",
              rot=(0, 180, 0)),
        _cyl("Chimney_A", (7, height * 0.9, 7), (-14, height * 0.45, -10), C("structure_alt"), "Brick"),
        _cyl("Chimney_B", (5, height * 1.15, 5), (12, height * 0.575, -12), C("structure_alt"), "Brick"),
        _cyl("StackCap_A", (7.6, 1.6, 7.6), (-14, height * 0.92, -10), C("accent"), "Metal"),
        _box("LoadingBay", (14, 8, 1.6), (0, 4, 15.2), C("accent"), "Metal"),
        _cyl("Boiler", (10, 16, 10), (20, 8, 10), C("highlight"), "Metal"),
    ]
    for i in range(5):
        parts.append(_box(f"Window_{i}", (5.4, 4.2, 0.8), (-16 + i * 8, height * 0.35, 15.1),
                          C("accent"), "Glass", transparency=0.35, emissive=True, collide=False))
    return height * 0.6, parts


def _dock(height: float) -> tuple[float, list[dict]]:
    parts = [
        _box("Deck", (18, 1.6, 48), (0, 2.4, 24), C("structure_alt"), "WoodPlanks"),
        _box("DeckEnd", (26, 1.6, 12), (0, 2.4, 48), C("structure_alt"), "WoodPlanks"),
    ]
    for i in range(6):
        for side in (-1, 1):
            parts.append(_cyl(f"Pile_{i}_{side}", (2.0, 14, 2.0), (side * 8, -4, i * 8 + 2), C("structure"), "Wood"))
    parts.append(_box("Hut", (10, 9, 9), (0, 7.5, 6), C("structure"), "WoodPlanks"))
    parts.append(_wedge("HutRoof", (12, 4, 10), (0, 12 + 2, 6), C("structure_alt"), "WoodPlanks"))
    parts.append(_cyl("Lamp", (0.7, 8, 0.7), (11, 6, 46), C("highlight"), "Metal"))
    parts.append(_ball("LampGlow", (2.2, 2.2, 2.2), (11, 10.4, 46), C("accent"), "Neon", emissive=True, collide=False))
    return 14, parts


def _lighthouse(height: float) -> tuple[float, list[dict]]:
    parts = [
        _cyl("Base", (16, 3, 16), (0, 1.5, 0), C("structure_alt"), "Rock"),
        _cyl("TowerLow", (9, height * 0.55, 9), (0, 3 + height * 0.275, 0), C("structure"), "Concrete"),
        _cyl("TowerHigh", (6.4, height * 0.45, 6.4), (0, 3 + height * 0.55 + height * 0.225, 0), C("structure_alt"), "Concrete"),
        _cyl("Gallery", (9.4, 1.8, 9.4), (0, 3 + height, 0), C("highlight"), "Metal"),
        _cyl("LampRoom", (5.6, 7, 5.6), (0, 3 + height + 4.4, 0), C("accent"), "Glass",
             transparency=0.3, emissive=True),
        _ball("Lamp", (4.4, 4.4, 4.4), (0, 3 + height + 4.4, 0), C("accent"), "Neon", emissive=True, collide=False),
        _part("Cap", "Wedge", (6.6, 5, 6.6), (0, 3 + height + 10.5, 0), C("structure"), "Metal"),
    ]
    for i in range(6):
        import math
        a = i * math.pi / 3
        parts.append(_box(f"Stripe_{i}", (9.2, height * 0.06, 9.2),
                          (0, 3 + height * 0.18, 0), C("accent"), "Concrete",
                          rot=(math.degrees(a) % 360, 0, 0), collide=False))
    return 3 + height + 14, parts


def _giant_tree(height: float) -> tuple[float, list[dict]]:
    import math
    parts = [
        _cyl("Trunk", (height * 0.16, height, height * 0.16), (0, height / 2, 0), C("structure_alt"), "Wood"),
        _cyl("RootFlare", (height * 0.30, height * 0.10, height * 0.30), (0, height * 0.05, 0), C("structure_alt"), "Wood"),
    ]
    for i in range(5):
        a = i * (2 * math.pi / 5)
        parts.append(_cyl(f"Branch_{i}", (height * 0.055, height * 0.5, height * 0.055),
                          (math.cos(a) * height * 0.14, height * 0.78, math.sin(a) * height * 0.14),
                          C("structure_alt"), "Wood", rot=(math.degrees(a) * 0.3, 0, 26)))
    for i in range(7):
        a = i * 1.9
        r = height * (0.10 + 0.10 * (i % 3))
        parts.append(_ball(f"Canopy_{i}", (height * 0.55, height * 0.42, height * 0.55),
                           (math.cos(a) * r, height * (0.95 + 0.08 * (i % 4)), math.sin(a) * r),
                           C("field"), "Grass"))
    return height * 1.35, parts


def _garden(height: float) -> tuple[float, list[dict]]:
    parts = [_box("Terrace", (44, 1.6, 34), (0, 0.8, 0), C("structure_alt"), "Ground")]
    for i in range(4):
        for j in range(3):
            x, z = -15 + i * 10, -10 + j * 10
            parts.append(_box(f"Plot_{i}_{j}", (8, 1.2, 8), (x, 1.8, z), C("highlight"), "Ground"))
            parts.append(_cyl(f"Plant_{i}_{j}", (3.2, 4.0 + (i + j) * 0.6, 3.2), (x, 4.0, z),
                              C("field"), "Grass"))
        parts.append(_box(f"Fence_{i}", (0.6, 3.4, 32), (-19 + i * 12.6, 1.7, 0), C("structure_alt"), "Wood"))
    parts.append(_cyl("Trellis", (0.8, 12, 0.8), (0, 6, 17), C("structure_alt"), "Wood"))
    parts.append(_ball("TrellisTop", (5, 5, 5), (0, 12.4, 17), C("field_alt"), "Grass"))
    return 13, parts


def _gate(height: float) -> tuple[float, list[dict]]:
    import math
    parts = [
        _box("Lintel", (24, 4.4, 4.4), (0, height * 0.85, 0), C("structure"), "Slate"),
        _wedge("CapA", (25, 3.4, 4.6), (0, height * 0.85 + 3.8, 0), C("structure_alt"), "Slate"),
    ]
    for side in (-1, 1):
        parts.append(_cyl(f"Pier_{side}", (5.6, height, 5.6), (side * 10, height / 2, 0), C("structure_alt"), "Slate"))
        parts.append(_ball(f"Finial_{side}", (4.4, 4.4, 4.4), (side * 10, height + 2.2, 0), C("accent"), "Neon",
                           emissive=True, collide=False))
    parts.append(_box("Bar", (16, 0.8, 0.8), (0, height * 0.62, 0), C("highlight"), "Metal"))
    return height, parts


def _cave_mouth(height: float) -> tuple[float, list[dict]]:
    import math
    parts = []
    for i in range(9):
        a = i * (2 * math.pi / 9)
        parts.append(_part(f"Boulder_{i}", "Wedge", (9 + (i % 3) * 3, 11 + (i % 4) * 4, 8),
                           (math.cos(a) * 11, 4 + (i % 2) * 3, math.sin(a) * 11),
                           C("structure"), "Rock", rot=(15 * (i % 3), math.degrees(a), 8 * (i % 2))))
    parts.append(_part("Arch", "Cylinder", (16, 8, 16), (0, 2, 0), C("structure_alt"), "Rock", rot=(0, 0, 90)))
    parts.append(_ball("Dark", (14, 12, 10), (0, 5, 0), "#000000", "Slate", collide=False))
    return height, parts


def _volcano(height: float) -> tuple[float, list[dict]]:
    import math
    parts = [_cyl("Cone", (height * 1.5, height, height * 1.5), (0, height / 2, 0), C("structure"), "Basalt")]
    parts.append(_cyl("ConeUpper", (height * 0.7, height * 0.4, height * 0.7), (0, height * 1.2, 0),
                      C("structure"), "Basalt"))
    parts.append(_cyl("Crater", (height * 0.34, 4, height * 0.34), (0, height * 1.38, 0), C("accent"), "Neon",
                      emissive=True, collide=False))
    for i in range(3):
        a = i * 2.1
        parts.append(_box(f"LavaFlow_{i}", (height * 0.10, 2, height * 0.62),
                          (math.cos(a) * height * 0.42, height * 0.55, math.sin(a) * height * 0.42),
                          C("accent"), "Neon", rot=(0, math.degrees(a), 12), emissive=True, collide=False))
    return height * 1.5, parts


def _bridge(height: float) -> tuple[float, list[dict]]:
    parts = [_box("Deck", (14, 1.8, 70), (0, 6, 0), C("structure_alt"), "WoodPlanks")]
    for i in range(5):
        for side in (-1, 1):
            parts.append(_cyl(f"Pylon_{i}_{side}", (3.0, 16, 3.0), (side * 6, 0, -28 + i * 14),
                              C("structure"), "Slate"))
    for i in range(6):
        for side in (-1, 1):
            parts.append(_box(f"Post_{i}_{side}", (0.8, 6, 0.8), (side * 6, 9.6, -30 + i * 12),
                              C("structure_alt"), "Wood"))
    for side in (-1, 1):
        parts.append(_box(f"Railing_{side}", (0.7, 0.7, 70), (side * 6, 12.4, 0), C("highlight"), "Wood"))
    return 16, parts


def _lake(height: float) -> tuple[float, list[dict]]:
    parts = [
        _cyl("Shore", (46, 1.4, 46), (0, 0.4, 0), C("highlight"), "Sand"),
        _cyl("Water", (42, 1.2, 42), (0, 1.0, 0), C("field_alt"), "Water", transparency=0.25, collide=False),
        _box("Jetty", (5, 1.2, 16), (0, 1.6, 24), C("structure_alt"), "WoodPlanks"),
        _cyl("Marker", (1.0, 8, 1.0), (0, 6, 30), C("structure"), "Wood"),
    ]
    return 8, parts


def _waterfall(height: float) -> tuple[float, list[dict]]:
    parts = [
        _part("CliffFace", "Wedge", (40, height, 22), (0, height / 2, -8), C("structure"), "Rock"),
        _box("Fall", (10, height * 0.9, 2.5), (0, height * 0.48, 2.4), C("field_alt"), "Water",
             transparency=0.35, collide=False),
        _cyl("Pool", (30, 2, 26), (0, 1.4, 12), C("field_alt"), "Water", transparency=0.3, collide=False),
    ]
    parts.append(_box("Mist", (16, 3, 8), (0, 3.2, 12), "#dff4ff", "ForceField", transparency=0.75, collide=False))
    return height, parts


def _market(height: float) -> tuple[float, list[dict]]:
    parts = [_cyl("Plaza", (34, 1.6, 34), (0, 0.8, 0), C("structure_alt"), "Cobblestone")]
    import math
    for i in range(5):
        a = i * (2 * math.pi / 5)
        x, z = math.cos(a) * 12, math.sin(a) * 12
        parts.append(_cyl(f"StallPost_{i}", (0.9, 8, 0.9), (x - 3, 4, z - 3), C("structure"), "Wood"))
        parts.append(_cyl(f"StallPostB_{i}", (0.9, 8, 0.9), (x + 3, 4, z + 3), C("structure"), "Wood"))
        parts.append(_part(f"Awning_{i}", "Wedge", (8.5, 2.6, 8.5), (x, 8.4, z), C("accent"), "Fabric",
                           rot=(0, math.degrees(a), 0)))
        parts.append(_box(f"Counter_{i}", (7, 2.6, 5), (x, 1.6, z), C("highlight"), "WoodPlanks"))
    parts.append(_cyl("Well", (8, 3, 8), (0, 1.5, 0), C("highlight"), "Cobblestone"))
    return 12, parts


POI_BUILDERS: dict[str, Callable[[float], tuple[float, list[dict]]]] = {
    "tower": _tower, "monument": _monument, "village": _village, "temple": _temple,
    "ruins": _ruins, "castle": _castle, "arena": _arena, "portal": _portal,
    "observatory": _observatory, "factory": _factory, "dock": _dock, "lighthouse": _lighthouse,
    "giant_tree": _giant_tree, "garden": _garden, "gate": _gate, "cave": _cave_mouth,
    "volcano": _volcano, "bridge": _bridge, "lake": _lake, "waterfall": _waterfall,
    "market": _market,
}

# Base height used by the builder signature (before scale). POI scale multiplies this.
POI_BASE_HEIGHT: dict[str, float] = {
    "tower": 26, "monument": 26, "village": 26, "temple": 20, "ruins": 18, "castle": 30,
    "arena": 16, "portal": 18, "observatory": 34, "factory": 22, "dock": 12,
    "lighthouse": 30, "giant_tree": 30, "garden": 8, "gate": 16, "cave": 18,
    "volcano": 30, "bridge": 12, "lake": 8, "waterfall": 22, "market": 12,
}

MESH_PROMPTS: dict[str, str] = {
    "tower": "stylized low-poly stone watchtower, tapering cylindrical shaft, stone balcony ring, conical roof, "
             "weathered blocks, readable silhouette, game-ready, no text, neutral material",
    "giant_tree": "stylized low-poly ancient tree, thick tapered trunk with root flare, five branching limbs, "
                  "layered faceted canopy clusters, hand-painted bark, game-ready",
    "monument": "stylized low-poly stone obelisk monument on a round plinth with four small columns, carved bands, "
                "emissive rune at the tip, game-ready, no text",
    "ruins": "stylized low-poly ruined stone arch and broken wall sections, chipped blocks, moss accents, "
             "modular game-ready pieces",
    "volcano": "stylized low-poly volcano, asymmetric cone with basalt striations, glowing crater rim, "
               "lava channels down one flank, game-ready",
    "village": "stylized low-poly medieval cottage cluster, gabled roofs, timber framing, small chimneys, "
               "modular set, game-ready",
    "temple": "stylized low-poly ancient temple, stepped stylobate, six columns per side, pediment, carved frieze, "
              "game-ready",
    "castle": "stylized low-poly castle keep with four corner towers, crenellations, wooden gate, banner, "
              "game-ready, readable silhouette",
    "portal": "stylized low-poly stone portal ring with floating rune stones and emissive energy plane, "
              "game-ready",
    "observatory": "stylized low-poly observatory dome on a circular concrete base with an angled telescope barrel, "
                   "clean sci-fi proportions",
    "factory": "stylized low-poly industrial hall with sawtooth roof, two brick chimneys, loading bay, "
               "game-ready",
    "dock": "stylized low-poly wooden pier with pilings, small harbour hut, lantern post, game-ready",
    "arena": "stylized low-poly circular arena, stone pillars with metal rails, central emissive core, game-ready",
    "lighthouse": "stylized low-poly lighthouse, tapered white tower with red band, gallery railing, glass lamp room",
    "garden": "stylized low-poly garden terrace with wooden fenced plots, trellis and leafy plants, game-ready",
    "market": "stylized low-poly market plaza, five fabric awnings over wooden stalls, central stone well, game-ready",
    "cave": "stylized low-poly cave mouth, layered rock arch with jagged boulders, dark interior, game-ready",
    "bridge": "stylized low-poly wooden bridge with stone pylons and railings, game-ready",
    "lake": "stylized low-poly lake shore set with jetty, marker post and rounded boulders",
    "waterfall": "stylized low-poly cliff waterfall, layered rock face, wide water sheet, mist base, game-ready",
    "gate": "stylized low-poly stone gateway with two piers, carved lintel and glowing finials, game-ready",
}


# ---------------------------------------------------------------------------------------------
# Scatterable assets: vegetation, rocks, props, creatures.
# ---------------------------------------------------------------------------------------------

def _tree_broadleaf(h: float) -> list[dict]:
    return [
        _cyl("Trunk", (h * 0.10, h * 0.55, h * 0.10), (0, h * 0.275, 0), C("structure_alt"), "Wood"),
        _cyl("RootFlare", (h * 0.18, h * 0.08, h * 0.18), (0, h * 0.04, 0), C("structure_alt"), "Wood"),
        _ball("CanopyA", (h * 0.62, h * 0.44, h * 0.62), (0, h * 0.70, 0), C("field"), "Grass"),
        _ball("CanopyB", (h * 0.44, h * 0.34, h * 0.44), (h * 0.18, h * 0.86, h * 0.05), C("field_alt"), "Grass"),
        _ball("CanopyC", (h * 0.40, h * 0.32, h * 0.40), (-h * 0.16, h * 0.80, -h * 0.10), C("field"), "Grass"),
        _cyl("Branch", (h * 0.045, h * 0.30, h * 0.045), (h * 0.14, h * 0.60, 0), C("structure_alt"), "Wood",
             rot=(0, 0, 38)),
    ]


def _tree_pine(h: float) -> list[dict]:
    parts = [
        _cyl("Trunk", (h * 0.08, h * 0.4, h * 0.08), (0, h * 0.2, 0), C("structure_alt"), "Wood"),
        _cyl("RootFlare", (h * 0.14, h * 0.06, h * 0.14), (0, h * 0.03, 0), C("structure_alt"), "Wood"),
    ]
    for i, (y, s) in enumerate(((0.42, 0.62), (0.62, 0.50), (0.80, 0.34))):
        parts.append(_ball(f"Tier_{i}", (h * s, h * 0.26, h * s), (0, h * y, 0), C("field") if i % 2 == 0 else C("field_alt"),
                           "Grass"))
    return parts


def _tree_palm(h: float) -> list[dict]:
    import math
    parts = [_cyl("Trunk", (h * 0.07, h * 0.85, h * 0.07), (0, h * 0.42, 0), C("structure_alt"), "Wood",
                  rot=(6, 0, 0))]
    for i in range(6):
        a = i * (2 * math.pi / 6)
        parts.append(_part(f"Frond_{i}", "Wedge", (h * 0.5, h * 0.05, h * 0.16),
                           (math.cos(a) * h * 0.22, h * 0.86, math.sin(a) * h * 0.22),
                           C("field"), "Grass", rot=(0, math.degrees(a), -22)))
    return parts


def _bush(h: float) -> list[dict]:
    return [
        _ball("BushA", (h * 1.1, h * 0.7, h * 1.1), (0, h * 0.34, 0), C("field"), "Grass"),
        _ball("BushB", (h * 0.8, h * 0.55, h * 0.8), (h * 0.35, h * 0.5, h * 0.2), C("field_alt"), "Grass"),
        _ball("BushC", (h * 0.7, h * 0.5, h * 0.7), (-h * 0.3, h * 0.42, -h * 0.25), C("field"), "Grass"),
    ]


def _flower_patch(h: float) -> list[dict]:
    parts = []
    for i in range(5):
        import math
        a = i * 1.26
        x, z = math.cos(a) * h * 0.22, math.sin(a) * h * 0.22
        parts.append(_cyl(f"Stem_{i}", (0.25, h * 0.5, 0.25), (x, h * 0.25, z), C("field_alt"), "Grass"))
        parts.append(_ball(f"Bloom_{i}", (h * 0.22, h * 0.14, h * 0.22), (x, h * 0.52, z), C("accent"), "Grass"))
    return parts


def _grass_tuft(h: float) -> list[dict]:
    parts = []
    for i in range(4):
        import math
        a = i * 1.57
        parts.append(_part(f"Blade_{i}", "Wedge", (h * 0.09, h * 0.55, h * 0.03),
                           (math.cos(a) * h * 0.10, h * 0.27, math.sin(a) * h * 0.10),
                           C("field"), "Grass", rot=(0, math.degrees(a), 12)))
    return parts


def _mushroom_cluster(h: float) -> list[dict]:
    parts = []
    for i, (dx, dz) in enumerate(((0, 0), (h * 0.3, h * 0.15), (-h * 0.25, h * 0.2))):
        parts.append(_cyl(f"Stem_{i}", (h * 0.08, h * 0.4, h * 0.08), (dx, h * 0.2, dz), C("highlight"), "Grass"))
        parts.append(_ball(f"Cap_{i}", (h * 0.26, h * 0.16, h * 0.26), (dx, h * 0.42, dz), C("accent"), "Grass"))
    return parts


def _rock_boulder(h: float) -> list[dict]:
    return [
        _part("Core", "Wedge", (h * 1.25, h * 0.85, h * 1.05), (0, h * 0.36, 0), C("structure"), "Rock",
              rot=(12, 24, 6)),
        _part("Shoulder", "CornerWedge", (h * 0.85, h * 0.62, h * 0.9), (h * 0.35, h * 0.3, -h * 0.1),
              C("structure_alt"), "Rock", rot=(-8, 40, 0)),
        _part("Chip", "Wedge", (h * 0.5, h * 0.34, h * 0.55), (-h * 0.4, h * 0.15, h * 0.25),
              C("structure"), "Rock", rot=(6, -18, 10)),
    ]


def _rock_cluster(h: float) -> list[dict]:
    parts = []
    for i, (dx, dz, s) in enumerate(((0, 0, 1.0), (h * 0.55, h * 0.2, 0.62), (-h * 0.45, h * 0.35, 0.5))):
        parts.append(_part(f"Rock_{i}", "Wedge", (h * s * 1.1, h * s * 0.8, h * s * 0.95),
                           (dx, h * s * 0.34, dz), C("structure") if i % 2 == 0 else C("structure_alt"),
                           "Rock", rot=(i * 11, i * 37, i * 7)))
    return parts


def _cliff_spire(h: float) -> list[dict]:
    parts = []
    for i in range(3):
        parts.append(_part(f"Layer_{i}", "Wedge", (h * (0.5 - i * 0.11), h * 0.42, h * (0.45 - i * 0.1)),
                           (0, h * (0.2 + i * 0.3), 0), C("structure"), "Rock",
                           rot=(0, i * 26, 0)))
    return parts


def _pebble_field(h: float) -> list[dict]:
    parts = []
    for i in range(6):
        import math
        a = i * 1.4
        r = h * (0.2 + 0.12 * (i % 3))
        parts.append(_ball(f"Pebble_{i}", (h * 0.22, h * 0.14, h * 0.2),
                           (math.cos(a) * r, h * 0.07, math.sin(a) * r), C("structure_alt"), "Rock"))
    return parts


def _crystal_cluster(h: float) -> list[dict]:
    parts = []
    for i in range(5):
        import math
        a = i * 1.26
        parts.append(_part(f"Shard_{i}", "Wedge", (h * 0.16, h * (0.6 + 0.15 * (i % 3)), h * 0.16),
                           (math.cos(a) * h * 0.22, h * (0.3 + 0.07 * (i % 3)), math.sin(a) * h * 0.22),
                           C("accent"), "Glass", rot=(10 * (i % 2), math.degrees(a), 8 * (i % 3)),
                           transparency=0.25, emissive=True))
    return parts


def _fence(h: float) -> list[dict]:
    parts = []
    for i in range(3):
        parts.append(_box(f"Post_{i}", (0.5, h, 0.5), (-h * 1.2 + i * h * 1.2, h / 2, 0), C("structure_alt"), "Wood"))
    for i in range(2):
        parts.append(_box(f"Rail_{i}", (h * 2.6, 0.4, 0.3), (0, h * (0.4 + i * 0.35), 0), C("structure_alt"), "Wood"))
    return parts


def _lamppost(h: float) -> list[dict]:
    return [
        _cyl("Post", (0.6, h, 0.6), (0, h / 2, 0), C("structure_alt"), "Metal"),
        _cyl("Base", (1.8, 0.8, 1.8), (0, 0.4, 0), C("structure_alt"), "Metal"),
        _ball("Lamp", (2.0, 2.0, 2.0), (0, h + 0.8, 0), C("accent"), "Neon", emissive=True, collide=False),
        _part("Cap", "Wedge", (2.6, 1.2, 2.6), (0, h + 2.0, 0), C("structure_alt"), "Metal"),
    ]


def _bench(h: float) -> list[dict]:
    return [
        _box("Seat", (7, 0.5, 2.2), (0, h * 0.55, 0), C("structure_alt"), "WoodPlanks"),
        _box("Back", (7, 1.8, 0.4), (0, h * 0.75, -0.9), C("structure_alt"), "WoodPlanks"),
        _box("LegA", (0.5, h * 0.55, 2.0), (-2.8, h * 0.27, 0), C("structure"), "Metal"),
        _box("LegB", (0.5, h * 0.55, 2.0), (2.8, h * 0.27, 0), C("structure"), "Metal"),
    ]


def _crate_stack(h: float) -> list[dict]:
    return [
        _box("CrateA", (4, 4, 4), (0, 2, 0), C("structure_alt"), "WoodPlanks"),
        _box("CrateB", (3.4, 3.4, 3.4), (3.6, 1.7, 1.2), C("structure"), "WoodPlanks"),
        _box("CrateC", (3.0, 3.0, 3.0), (0.6, 5.6, -0.4), C("highlight"), "WoodPlanks", rot=(0, 18, 0)),
    ]


def _barrel(h: float) -> list[dict]:
    return [
        _cyl("Body", (2.6, 3.6, 2.6), (0, 1.8, 0), C("structure_alt"), "Wood"),
        _cyl("HoopA", (2.9, 0.4, 2.9), (0, 1.0, 0), C("structure"), "Metal"),
        _cyl("HoopB", (2.9, 0.4, 2.9), (0, 2.6, 0), C("structure"), "Metal"),
    ]


def _campfire(h: float) -> list[dict]:
    import math
    parts = []
    for i in range(5):
        a = i * (2 * math.pi / 5)
        parts.append(_part(f"Log_{i}", "Cylinder", (0.8, 5, 0.8),
                           (math.cos(a) * 1.2, 0.6, math.sin(a) * 1.2), C("structure_alt"), "Wood",
                           rot=(72, math.degrees(a), 0)))
    parts.append(_ball("Flame", (2.6, 3.2, 2.6), (0, 1.8, 0), C("accent"), "Neon", emissive=True, collide=False))
    return parts


def _signpost(h: float) -> list[dict]:
    return [
        _cyl("Post", (0.6, h, 0.6), (0, h / 2, 0), C("structure_alt"), "Wood"),
        _part("Board", "Wedge", (4.5, 2.2, 0.4), (1.6, h * 0.8, 0), C("highlight"), "WoodPlanks", rot=(0, 0, 8)),
    ]


def _creature(h: float) -> list[dict]:
    """Procedural quadruped fallback; a generated mesh is strongly preferred for animals."""
    return [
        _ball("Body", (h * 0.9, h * 0.55, h * 0.45), (0, h * 0.55, 0), C("field_alt"), "SmoothPlastic"),
        _ball("Head", (h * 0.34, h * 0.32, h * 0.32), (h * 0.48, h * 0.72, 0), C("field_alt"), "SmoothPlastic"),
        _part("Snout", "Cylinder", (h * 0.14, h * 0.18, h * 0.14), (h * 0.64, h * 0.66, 0), C("highlight"), "SmoothPlastic",
              rot=(0, 0, 90)),
        _cyl("LegA", (h * 0.10, h * 0.4, h * 0.10), (h * 0.28, h * 0.2, h * 0.16), C("field"), "SmoothPlastic"),
        _cyl("LegB", (h * 0.10, h * 0.4, h * 0.10), (h * 0.28, h * 0.2, -h * 0.16), C("field"), "SmoothPlastic"),
        _cyl("LegC", (h * 0.10, h * 0.4, h * 0.10), (-h * 0.28, h * 0.2, h * 0.16), C("field"), "SmoothPlastic"),
        _cyl("LegD", (h * 0.10, h * 0.4, h * 0.10), (-h * 0.28, h * 0.2, -h * 0.16), C("field"), "SmoothPlastic"),
        _part("Tail", "Cylinder", (h * 0.07, h * 0.3, h * 0.07), (-h * 0.5, h * 0.62, 0), C("field"), "SmoothPlastic",
              rot=(0, 0, 40)),
        _ball("EarA", (h * 0.12, h * 0.14, h * 0.08), (h * 0.46, h * 0.90, h * 0.10), C("field"), "SmoothPlastic"),
        _ball("EarB", (h * 0.12, h * 0.14, h * 0.08), (h * 0.46, h * 0.90, -h * 0.10), C("field"), "SmoothPlastic"),
    ]


def _theme_prop(kind: str, h: float) -> list[dict]:
    if kind == "floating_obelisk":
        return [_part("Shaft", "Wedge", (3.4, h, 3.4), (0, h / 2, 0), C("structure"), "Slate"),
                _cyl("Ring", (4.6, 0.5, 4.6), (0, h * 0.72, 0), C("accent"), "Neon", emissive=True, collide=False)]
    if kind == "star_orb":
        return [_ball("Orb", (h * 0.5, h * 0.5, h * 0.5), (0, h * 0.5, 0), C("accent"), "Neon", emissive=True, collide=False),
                _cyl("Base", (h * 0.4, 1.2, h * 0.4), (0, 0.6, 0), C("structure"), "Slate")]
    if kind == "crystal_cluster" or kind == "prism_spire":
        return _crystal_cluster(h)
    if kind == "rift_arch":
        return [_part("ArchA", "Wedge", (5, h, 1.4), (-3, h / 2, 0), C("structure"), "Slate", rot=(0, 0, 14)),
                _part("ArchB", "Wedge", (5, h, 1.4), (3, h / 2, 0), C("structure"), "Slate", rot=(0, 0, -14)),
                _ball("Core", (3, 3, 1), (0, h * 0.55, 0), C("accent"), "ForceField", transparency=0.4,
                      emissive=True, collide=False)]
    if kind == "antenna_array":
        return [_cyl("Mast", (0.8, h, 0.8), (0, h / 2, 0), C("structure"), "Metal"),
                _cyl("DishA", (4.4, 0.6, 4.4), (0, h * 0.8, 0), C("highlight"), "Metal", rot=(20, 0, 0)),
                _cyl("Base", (4, 1.2, 4), (0, 0.6, 0), C("structure_alt"), "Concrete"),
                _ball("Beacon", (1.4, 1.4, 1.4), (0, h + 0.6, 0), C("accent"), "Neon", emissive=True, collide=False)]
    if kind == "holo_pylon":
        return [_cyl("Pylon", (2.4, h, 2.4), (0, h / 2, 0), C("structure"), "Metal"),
                _box("Screen", (3.4, h * 0.4, 0.3), (0, h * 0.7, 1.3), C("accent"), "Glass",
                     transparency=0.4, emissive=True, collide=False)]
    if kind == "reactor_core":
        return [_cyl("Housing", (6, h * 0.6, 6), (0, h * 0.3, 0), C("structure"), "Metal"),
                _ball("Core", (4, 4, 4), (0, h * 0.45, 0), C("accent"), "Neon", emissive=True, collide=False),
                _cyl("Ring", (7.2, 0.8, 7.2), (0, h * 0.6, 0), C("highlight"), "Metal")]
    if kind == "drone_dock":
        return [_cyl("Pad", (8, 0.8, 8), (0, 0.4, 0), C("structure_alt"), "Concrete"),
                _cyl("Pillar", (1.4, h * 0.6, 1.4), (4, h * 0.3, 4), C("structure"), "Metal"),
                _ball("Beacon", (1.2, 1.2, 1.2), (4, h * 0.6, 4), C("accent"), "Neon", emissive=True, collide=False)]
    if kind == "rune_stone":
        return [_part("Stone", "Wedge", (3.4, h * 0.8, 2.4), (0, h * 0.4, 0), C("structure"), "Rock", rot=(4, 18, 0)),
                _box("Rune", (1.6, h * 0.3, 0.2), (0, h * 0.45, 1.2), C("accent"), "Neon",
                     emissive=True, collide=False)]
    if kind == "ancient_shrine":
        return [_box("Base", (7, 1.4, 7), (0, 0.7, 0), C("structure_alt"), "Slate"),
                _cyl("Pillar", (2.2, h * 0.7, 2.2), (0, h * 0.35, 0), C("structure"), "Slate"),
                _part("Cap", "Wedge", (5, 2.0, 5), (0, h * 0.72, 0), C("structure"), "Slate"),
                _ball("Glow", (1.8, 1.8, 1.8), (0, h * 0.78, 0), C("accent"), "Neon", emissive=True, collide=False)]
    if kind == "lantern_post":
        return _lamppost(h)
    if kind == "gear_stack":
        return [_cyl("GearA", (h * 0.7, 1.2, h * 0.7), (0, 1.0, 0), C("highlight"), "Metal"),
                _cyl("GearB", (h * 0.5, 1.2, h * 0.5), (h * 0.2, 2.6, 0), C("highlight"), "Metal"),
                _box("Axle", (1.0, h * 0.6, 1.0), (0, h * 0.3, 0), C("structure"), "Metal")]
    if kind == "brass_tower":
        return [_cyl("Column", (3.2, h, 3.2), (0, h / 2, 0), C("structure"), "Metal"),
                _part("Top", "Wedge", (4.4, 3, 4.4), (0, h + 1.4, 0), C("highlight"), "Metal")]
    if kind == "pipe_organ":
        return [_cyl(f"Pipe_{i}", (1.6, h * (0.5 + i * 0.15), 1.6), ((i - 1.5) * 2.6, h * 0.3, 0),
                     C("highlight"), "Metal") for i in range(4)]
    if kind == "airship_mooring":
        return [_cyl("Mast", (1.6, h, 1.6), (0, h / 2, 0), C("structure"), "Metal"),
                _ball("Balloon", (h * 0.7, h * 0.45, h * 0.7), (0, h * 1.1, 0), C("accent"), "Fabric",
                      transparency=0.2, collide=False)]
    if kind == "stone_shrine":
        return _theme_prop("ancient_shrine", h)
    if kind == "fallen_log":
        return [_part("Log", "Cylinder", (2.2, h, 2.2), (0, 1.2, 0), C("structure_alt"), "Wood", rot=(0, 0, 90)),
                _ball("Moss", (h * 0.4, 1.2, 2.4), (0, 2.2, 0), C("field"), "Grass")]
    if kind == "rock_garden":
        return _rock_cluster(h)
    if kind == "watch_post":
        return [_cyl("Post", (1.2, h, 1.2), (0, h / 2, 0), C("structure_alt"), "Wood"),
                _box("Platform", (6, 0.6, 6), (0, h, 0), C("structure"), "WoodPlanks"),
                _part("Roof", "Wedge", (7, 2.2, 7), (0, h + 1.8, 0), C("structure_alt"), "WoodPlanks")]
    return _crystal_cluster(h)


PROP_RECIPES: dict[str, tuple[str, Callable[[float], list[dict]], float, str]] = {
    # id: (category, recipe, default height, mesh prompt)
    "tree_broadleaf": ("vegetation", _tree_broadleaf, 24, "stylized low-poly broadleaf tree, faceted canopy lobes, tapered trunk"),
    "tree_pine": ("vegetation", _tree_pine, 28, "stylized low-poly pine tree, three stacked conical tiers, slim trunk"),
    "tree_palm": ("vegetation", _tree_palm, 22, "stylized low-poly palm tree, curved trunk, six fronds"),
    "bush": ("vegetation", _bush, 6, "stylized low-poly shrub, three clustered lobes"),
    "flower_patch": ("vegetation", _flower_patch, 3, "stylized low-poly wildflower patch, five blooms"),
    "grass_tuft": ("vegetation", _grass_tuft, 2.4, "stylized low-poly grass tuft"),
    "mushroom_cluster": ("vegetation", _mushroom_cluster, 3, "stylized low-poly mushroom cluster"),
    "rock_boulder": ("rock", _rock_boulder, 9, "stylized low-poly boulder, chipped facets"),
    "rock_cluster": ("rock", _rock_cluster, 7, "stylized low-poly rock cluster, three boulders"),
    "cliff_spire": ("rock", _cliff_spire, 26, "stylized low-poly rock spire, stacked strata"),
    "pebble_field": ("rock", _pebble_field, 4, "stylized low-poly pebble field"),
    "crystal_cluster": ("rock", _crystal_cluster, 12, "stylized low-poly crystal cluster, emissive shards"),
    "fence": ("prop", _fence, 4, "stylized low-poly wooden fence segment"),
    "lamppost": ("prop", _lamppost, 12, "stylized low-poly lantern post"),
    "bench": ("prop", _bench, 4, "stylized low-poly wooden bench"),
    "crate_stack": ("prop", _crate_stack, 6, "stylized low-poly crate stack"),
    "barrel": ("prop", _barrel, 4, "stylized low-poly wooden barrel"),
    "campfire": ("prop", _campfire, 4, "stylized low-poly campfire"),
    "signpost": ("prop", _signpost, 7, "stylized low-poly wooden signpost"),
    "creature_quadruped": ("creature", _creature, 3.4, "stylized low-poly friendly quadruped creature, rounded body, short legs, big eyes"),
}


def theme_prop_asset(kind: str, height: float = 8.0) -> tuple[float, list[dict]]:
    return height, _theme_prop(kind, height)


def build_recipe(asset: dict) -> list[dict]:
    """Materialize an asset's parts (POI builder or prop recipe)."""
    kind = asset.get("kind", "")
    scale = float(asset.get("scale", 1.0))
    if kind in POI_BUILDERS:
        base = POI_BASE_HEIGHT.get(kind, 20) * scale
        _, parts = POI_BUILDERS[kind](base)
        return parts
    if kind in PROP_RECIPES:
        _, fn, base_h, _ = PROP_RECIPES[kind]
        return fn(base_h * scale)
    theme = asset.get("theme_prop")
    if theme:
        return theme_prop_asset(theme, 8.0 * scale)[1]
    raise KeyError(f"No recipe for asset kind '{kind}'")
