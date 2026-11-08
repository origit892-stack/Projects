"""Native-Part construction kit shared by NewBunker room builders."""

from __future__ import annotations

import math

from .site import FLOOR_Y


# Restrained structural palette.  Room builders may introduce functional
# accents, but these values keep bunker structure materially coherent.
CONCRETE = [0.24, 0.255, 0.265]
CONCRETE_DARK = [0.145, 0.155, 0.165]
CONCRETE_WORN = [0.31, 0.315, 0.30]
FLOOR = [0.105, 0.12, 0.13]
STEEL = [0.16, 0.18, 0.19]
STEEL_LIGHT = [0.30, 0.325, 0.33]
AGED_WHITE = [0.49, 0.50, 0.46]
GREEN = [0.19, 0.27, 0.22]
RUST = [0.285, 0.145, 0.075]
YELLOW = [0.46, 0.31, 0.07]
RED = [0.43, 0.065, 0.045]
UTILITY_BLUE = [0.12, 0.25, 0.30]
FABRIC = [0.22, 0.26, 0.245]
WOOD = [0.27, 0.19, 0.13]
LIGHT_COLD = [0.72, 0.83, 0.88]
LIGHT_WARM = [0.88, 0.48, 0.24]


def model(name: str, children: list | None = None, class_name: str = "Model") -> dict:
    return {"Name": name, "ClassName": class_name, "Children": children or []}


def matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def rotation_matrix(rx: float, ry: float, rz: float) -> list[list[float]]:
    x, y, z = map(math.radians, (rx, ry, rz))
    cx, sx = math.cos(x), math.sin(x)
    cy, sy = math.cos(y), math.sin(y)
    cz, sz = math.cos(z), math.sin(z)
    mx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    my = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    mz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return matmul(mz, matmul(my, mx))


def cframe(pos: tuple[float, float, float], rot: tuple[float, float, float]) -> list[float]:
    rotation = rotation_matrix(*rot)
    return [pos[0], pos[1], pos[2], *rotation[0], *rotation[1], *rotation[2]]


def part(
    name: str,
    size: tuple[float, float, float],
    pos: tuple[float, float, float],
    *,
    material: str = "Metal",
    color: list[float] = STEEL,
    collide: bool = True,
    transparency: float = 0.0,
    shape: str | None = None,
    rot: tuple[float, float, float] | None = None,
    class_name: str = "Part",
    children: list | None = None,
    cast_shadow: bool = True,
) -> dict:
    props: dict = {
        "Size": list(size),
        "Anchored": True,
        "CanCollide": collide,
        "CanTouch": collide,
        "CanQuery": collide,
        "Material": material,
        "Color": color,
        "Transparency": transparency,
        "CastShadow": cast_shadow,
    }
    if rot:
        props["CFrame"] = cframe(pos, rot)
    else:
        props["Position"] = list(pos)
    if shape:
        props["Shape"] = shape
    result = {"Name": name, "ClassName": class_name, "Properties": props}
    if children:
        result["Children"] = children
    return result


def point_light(name: str, color: list[float], brightness: float, light_range: float, shadows: bool = True) -> dict:
    return {
        "Name": name,
        "ClassName": "PointLight",
        "Properties": {
            "Enabled": True,
            "Color": color,
            "Brightness": brightness,
            "Range": light_range,
            "Shadows": shadows,
        },
    }


def pipe(name: str, pos: tuple[float, float, float], length: float, axis: str, diameter: float, color: list[float] = STEEL_LIGHT) -> dict:
    rot = None if axis == "x" else ((0, 90, 0) if axis == "z" else (0, 0, 90))
    return part(name, (length, diameter, diameter), pos, material="Metal", color=color, collide=False, shape="Cylinder", rot=rot)


def crate(name: str, pos: tuple[float, float, float], size: tuple[float, float, float] = (3.0, 2.2, 2.5)) -> dict:
    x, y, z = pos
    sx, sy, sz = size
    return model(name, [
        part("CrateBody", size, pos, material="WoodPlanks", color=WOOD),
        part("TopBand", (sx + 0.15, 0.22, sz + 0.15), (x, y + sy / 2 - 0.2, z), material="Metal", color=STEEL, collide=False),
        part("FrontBand", (sx + 0.12, sy + 0.08, 0.18), (x, y, z - sz / 2 - 0.02), material="Metal", color=STEEL, collide=False),
        part("SideBand", (0.18, sy + 0.08, sz + 0.12), (x - sx / 2 - 0.02, y, z), material="Metal", color=STEEL, collide=False),
    ])


def shelf(name: str, pos: tuple[float, float, float], width: float, height: float, depth: float) -> dict:
    x, y, z = pos
    children = [
        part("LeftUpright", (0.28, height, depth), (x - width / 2, y, z), material="Metal", color=STEEL_LIGHT),
        part("RightUpright", (0.28, height, depth), (x + width / 2, y, z), material="Metal", color=STEEL_LIGHT),
    ]
    for index, offset in enumerate((-height / 2 + 0.2, 0, height / 2 - 0.2), 1):
        children.append(part(f"ShelfDeck{index:02d}", (width, 0.25, depth), (x, y + offset, z), material="DiamondPlate", color=STEEL))
    return model(name, children)


def bench(name: str, pos: tuple[float, float, float], width: float, rot_y: float = 0) -> dict:
    x, y, z = pos
    return model(name, [
        part("Seat", (width, 0.5, 2.2), (x, y + 2.0, z), material="WoodPlanks", color=WOOD, rot=(0, rot_y, 0)),
        part("Back", (width, 2.5, 0.4), (x, y + 3.3, z + 0.9), material="WoodPlanks", color=WOOD, rot=(0, rot_y, 0)),
        part("LeftLeg", (0.4, 2, 1.6), (x - width / 2 + 0.45, y + 1, z), material="Metal", color=STEEL, rot=(0, rot_y, 0)),
        part("RightLeg", (0.4, 2, 1.6), (x + width / 2 - 0.45, y + 1, z), material="Metal", color=STEEL, rot=(0, rot_y, 0)),
    ])


def fluorescent(name: str, pos: tuple[float, float, float], color: list[float], brightness: float = 1.6, light_range: float = 15) -> dict:
    x, y, z = pos
    return model(name, [
        part("FixtureHousing", (6.2, 0.45, 1.45), (x, y, z), material="Metal", color=STEEL, collide=False),
        part("TubeDiffuser", (5.4, 0.18, 0.75), (x, y - 0.25, z), material="Neon", color=color, collide=False, cast_shadow=False,
             children=[point_light("LocalIllumination", color, brightness, light_range, True)]),
        part("EndCapWest", (0.35, 0.38, 1.0), (x - 2.8, y - 0.12, z), material="CorrodedMetal", color=RUST, collide=False),
        part("EndCapEast", (0.35, 0.38, 1.0), (x + 2.8, y - 0.12, z), material="CorrodedMetal", color=RUST, collide=False),
    ])


def structural_rib(
    name: str,
    x0: float,
    x1: float,
    z: float,
    height: float = 11.5,
    *,
    post_width: float = 0.45,
    depth: float = 0.9,
    accent: list[float] = RUST,
) -> dict:
    """Create a corridor rib while preserving a wide central traversal lane."""

    inset = 0.25
    return model(name, [
        part("WestUpright", (post_width, height, depth), (x0 + inset, FLOOR_Y + height / 2, z), material="Metal", color=STEEL_LIGHT),
        part("EastUpright", (post_width, height, depth), (x1 - inset, FLOOR_Y + height / 2, z), material="Metal", color=STEEL_LIGHT),
        part("CeilingCrossMember", (x1 - x0, 0.6, depth), ((x0 + x1) / 2, FLOOR_Y + height, z), material="Metal", color=STEEL_LIGHT),
        part("LowerGuardWest", (0.18, 0.9, 1.2), (x0 + 0.62, FLOOR_Y + 0.45, z), material="Metal", color=accent, collide=False),
        part("LowerGuardEast", (0.18, 0.9, 1.2), (x1 - 0.62, FLOOR_Y + 0.45, z), material="Metal", color=accent, collide=False),
    ])


# Compatibility for room modules migrated from the monolithic generator.
rib = structural_rib
