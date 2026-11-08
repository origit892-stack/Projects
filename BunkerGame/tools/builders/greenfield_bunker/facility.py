"""Build the greenfield bunker without importing the legacy NewBunker builder.

The model deliberately keeps only the small set of named compatibility seams
consumed by existing gameplay services. All shell, room, prop, and exterior
composition is freshly authored here.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


Vec3 = Tuple[float, float, float]
Bounds = Tuple[float, float, float, float]

FLOOR_Y = 54.0
ACTIVE_OFFSET: Vec3 = (0.0, 0.0, 0.0)
STAGING_OFFSET: Vec3 = (-260.0, 0.0, 0.0)

CONCRETE = [0.23, 0.25, 0.26]
CONCRETE_DARK = [0.12, 0.135, 0.145]
CONCRETE_WORN = [0.32, 0.33, 0.31]
FLOOR = [0.10, 0.115, 0.125]
STEEL = [0.15, 0.17, 0.18]
STEEL_LIGHT = [0.31, 0.34, 0.34]
RUST = [0.32, 0.16, 0.075]
HAZARD = [0.72, 0.43, 0.06]
EMERGENCY_RED = [0.58, 0.075, 0.045]
UTILITY_BLUE = [0.11, 0.31, 0.38]
UTILITY_GREEN = [0.13, 0.34, 0.25]
OFFWHITE = [0.76, 0.78, 0.74]
WOOD = [0.25, 0.17, 0.11]
BED_FABRIC = [0.19, 0.27, 0.26]
EARTH = [0.18, 0.20, 0.145]
LIGHT_COOL = [0.67, 0.83, 0.90]
LIGHT_WARM = [0.94, 0.50, 0.20]

# These are inspected, source-controlled production assets already mapped under
# ServerStorage.GeneratedAssets. The greenfield builder uses their verified mesh
# and SurfaceAppearance data directly as small non-colliding dressing accents.
IMPORTED_ASSETS = {
    "junction_box": {
        "MeshId": "rbxassetid://138460865383806",
        "ColorMap": "rbxassetid://139579734340579",
        "NormalMap": "rbxassetid://101009095631637",
        "RoughnessMap": "rbxassetid://73092764580147",
        "MetalnessMap": "rbxassetid://129094780313320",
    },
    "valve_assembly": {
        "MeshId": "rbxassetid://75117650394533",
        "ColorMap": "rbxassetid://136685065521485",
        "NormalMap": "rbxassetid://78946883212753",
        "RoughnessMap": "rbxassetid://81052079342113",
        "MetalnessMap": "rbxassetid://118332949942821",
    },
    "vent_grille": {
        "MeshId": "rbxassetid://129788520191225",
        "ColorMap": "rbxassetid://111071233724492",
        "NormalMap": "rbxassetid://101188069065673",
        "RoughnessMap": "rbxassetid://133041917278365",
        "MetalnessMap": "rbxassetid://127496283006416",
    },
    "ammo_crate": {
        "MeshId": "rbxassetid://140136727798730",
        "ColorMap": "rbxassetid://79418719084559",
        "NormalMap": "rbxassetid://75088026659430",
        "RoughnessMap": "rbxassetid://81827742837440",
        "MetalnessMap": "rbxassetid://72826286691276",
    },
}


def model(name: str, children: Optional[List[dict]] = None, attributes: Optional[Dict] = None) -> dict:
    node = {"Name": name, "ClassName": "Model", "Children": children or []}
    if attributes:
        node["attributes"] = attributes
    return node


def rotation_matrix(rx: float, ry: float, rz: float) -> List[List[float]]:
    x, y, z = map(math.radians, (rx, ry, rz))
    cx, sx = math.cos(x), math.sin(x)
    cy, sy = math.cos(y), math.sin(y)
    cz, sz = math.cos(z), math.sin(z)
    mx = [[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]]
    my = [[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]]
    mz = [[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]]

    def multiply(left: List[List[float]], right: List[List[float]]) -> List[List[float]]:
        return [
            [sum(left[row][index] * right[index][column] for index in range(3)) for column in range(3)]
            for row in range(3)
        ]

    return multiply(mz, multiply(my, mx))


def cframe(position: Vec3, rotation: Tuple[float, float, float]) -> List[float]:
    matrix = rotation_matrix(*rotation)
    return [position[0], position[1], position[2], *matrix[0], *matrix[1], *matrix[2]]


def part(
    name: str,
    size: Vec3,
    position: Vec3,
    *,
    material: str = "Metal",
    color: Sequence[float] = STEEL,
    collide: bool = True,
    transparency: float = 0.0,
    rotation: Optional[Tuple[float, float, float]] = None,
    shape: Optional[str] = None,
    class_name: str = "Part",
    children: Optional[List[dict]] = None,
    attributes: Optional[Dict] = None,
    cast_shadow: bool = True,
    extra_properties: Optional[Dict] = None,
) -> dict:
    properties: Dict = {
        "Size": list(size),
        "Anchored": True,
        "CanCollide": collide,
        "CanTouch": collide,
        "CanQuery": collide,
        "Material": material,
        "Color": list(color),
        "Transparency": transparency,
        "CastShadow": cast_shadow,
    }
    if rotation:
        properties["CFrame"] = cframe(position, rotation)
    else:
        properties["Position"] = list(position)
    if shape:
        properties["Shape"] = shape
    if extra_properties:
        properties.update(extra_properties)
    node = {"Name": name, "ClassName": class_name, "Properties": properties}
    if children:
        node["Children"] = children
    if attributes:
        node["attributes"] = attributes
    return node


def point_light(name: str, color: Sequence[float], brightness: float, light_range: float, shadows: bool = True) -> dict:
    return {
        "Name": name,
        "ClassName": "PointLight",
        "Properties": {
            "Enabled": True,
            "Color": list(color),
            "Brightness": brightness,
            "Range": light_range,
            "Shadows": shadows,
        },
    }


def prompt(name: str, action: str, object_text: str, hold: float, distance: float) -> dict:
    return {
        "Name": name,
        "ClassName": "ProximityPrompt",
        "Properties": {
            "ActionText": action,
            "ObjectText": object_text,
            "Style": "Custom",
            "Exclusivity": "OnePerButton",
            "KeyboardKeyCode": "E",
            "GamepadKeyCode": "ButtonX",
            "HoldDuration": hold,
            "MaxActivationDistance": distance,
            "RequiresLineOfSight": True,
            "ClickablePrompt": True,
        },
    }


def interaction_anchor(position: Vec3, prompt_node: dict) -> dict:
    return part(
        "InteractionAnchor",
        (0.4, 0.4, 0.4),
        position,
        material="SmoothPlastic",
        color=CONCRETE_DARK,
        collide=False,
        transparency=1.0,
        cast_shadow=False,
        children=[prompt_node],
    )


def pipe(name: str, position: Vec3, length: float, axis: str, diameter: float, color: Sequence[float] = STEEL_LIGHT) -> dict:
    rotations = {"x": None, "y": (0.0, 0.0, 90.0), "z": (0.0, 90.0, 0.0)}
    rotation = rotations[axis]
    return part(
        name,
        (length, diameter, diameter),
        position,
        material="Metal",
        color=color,
        collide=False,
        shape="Cylinder",
        rotation=rotation,
    )


def fluorescent_fixture(name: str, position: Vec3, color: Sequence[float], brightness: float, light_range: float) -> dict:
    x, y, z = position
    return model(
        name,
        [
            part("FixtureHousing", (6.4, 0.45, 1.55), position, material="Metal", color=STEEL, collide=False),
            part(
                "TubeA",
                (5.55, 0.17, 0.78),
                (x, y - 0.25, z),
                material="Neon",
                color=color,
                collide=False,
                cast_shadow=False,
                children=[point_light("LocalIllumination", color, brightness, light_range)],
            ),
            part("EndCapWest", (0.34, 0.36, 1.05), (x - 2.9, y - 0.08, z), material="CorrodedMetal", color=RUST, collide=False),
            part("EndCapEast", (0.34, 0.36, 1.05), (x + 2.9, y - 0.08, z), material="CorrodedMetal", color=RUST, collide=False),
        ],
    )


def emergency_wall_lamp(name: str, position: Vec3, color: Sequence[float] = LIGHT_WARM) -> dict:
    """Low-power navigation light kept outside the switchable Lighting subtree."""

    x, y, z = position
    return model(
        name,
        [
            part("Backplate", (1.2, 1.7, 0.14), (x, y, z + 0.05), material="CorrodedMetal", color=STEEL, collide=False),
            part(
                "EmergencyLens",
                (0.68, 0.68, 0.18),
                (x, y + 0.12, z - 0.10),
                material="Neon",
                color=color,
                collide=False,
                cast_shadow=False,
                children=[point_light("EmergencyPool", color, 2.4, 15.0, True)],
            ),
            part("CableDrop", (0.16, 1.6, 0.16), (x + 0.54, y - 0.6, z), material="Metal", color=RUST, collide=False),
        ],
    )


def _wall_segment(name: str, position: Vec3, size: Vec3) -> dict:
    return part(name, size, position, material="Concrete", color=CONCRETE)


def _normalise_openings(openings):
    if not openings:
        return []
    if isinstance(openings, tuple) and len(openings) == 3 and isinstance(openings[0], (float, int)):
        return [openings]
    return sorted(list(openings), key=lambda opening: opening[0])


def _horizontal_wall(
    name: str,
    x0: float,
    x1: float,
    z: float,
    height: float,
    openings,
) -> List[dict]:
    thickness = 0.72
    normalized = _normalise_openings(openings)
    if not normalized:
        return [_wall_segment(name, ((x0 + x1) / 2, FLOOR_Y + height / 2, z), (x1 - x0, height, thickness))]
    children: List[dict] = []
    cursor = x0
    for index, (center, width, door_height) in enumerate(normalized, 1):
        left = max(x0, center - width / 2)
        right = min(x1, center + width / 2)
        if left > cursor:
            children.append(_wall_segment(name + "Segment" + str(index), ((cursor + left) / 2, FLOOR_Y + height / 2, z), (left - cursor, height, thickness)))
        children.append(_wall_segment(name + "Header" + str(index), (center, FLOOR_Y + door_height + (height - door_height) / 2, z), (right - left, height - door_height, thickness)))
        cursor = max(cursor, right)
    if cursor < x1:
        children.append(_wall_segment(name + "SegmentEnd", ((cursor + x1) / 2, FLOOR_Y + height / 2, z), (x1 - cursor, height, thickness)))
    return children


def _vertical_wall(
    name: str,
    x: float,
    z0: float,
    z1: float,
    height: float,
    openings,
) -> List[dict]:
    thickness = 0.72
    normalized = _normalise_openings(openings)
    if not normalized:
        return [_wall_segment(name, (x, FLOOR_Y + height / 2, (z0 + z1) / 2), (thickness, height, z1 - z0))]
    children: List[dict] = []
    cursor = z0
    for index, (center, width, door_height) in enumerate(normalized, 1):
        near = max(z0, center - width / 2)
        far = min(z1, center + width / 2)
        if near > cursor:
            children.append(_wall_segment(name + "Segment" + str(index), (x, FLOOR_Y + height / 2, (cursor + near) / 2), (thickness, height, near - cursor)))
        children.append(_wall_segment(name + "Header" + str(index), (x, FLOOR_Y + door_height + (height - door_height) / 2, center), (thickness, height - door_height, far - near)))
        cursor = max(cursor, far)
    if cursor < z1:
        children.append(_wall_segment(name + "SegmentEnd", (x, FLOOR_Y + height / 2, (cursor + z1) / 2), (thickness, height, z1 - cursor)))
    return children


def room_shell(name: str, bounds: Bounds, height: float, openings: Optional[Dict[str, Tuple[float, float, float]]] = None) -> dict:
    openings = openings or {}
    x0, x1, z0, z1 = bounds
    width, depth = x1 - x0, z1 - z0
    children: List[dict] = [
        part("FloorSlab", (width, 0.5, depth), ((x0 + x1) / 2, FLOOR_Y - 0.25, (z0 + z1) / 2), material="Slate", color=FLOOR),
        part("CeilingSlab", (width, 0.52, depth), ((x0 + x1) / 2, FLOOR_Y + height, (z0 + z1) / 2), material="Concrete", color=CONCRETE_DARK),
    ]
    children.extend(_horizontal_wall("SouthWall", x0, x1, z0, height, openings.get("south")))
    children.extend(_horizontal_wall("NorthWall", x0, x1, z1, height, openings.get("north")))
    children.extend(_vertical_wall("WestWall", x0, z0, z1, height, openings.get("west")))
    children.extend(_vertical_wall("EastWall", x1, z0, z1, height, openings.get("east")))

    def door_clearance(side: str, coordinate: float) -> bool:
        for center, opening_width, _ in _normalise_openings(openings.get(side)):
            if abs(coordinate - center) <= opening_width / 2 + 0.8:
                return True
        return False

    for index, z in enumerate(range(int(z0) + 4, int(z1), 7), 1):
        if not door_clearance("west", z):
            children.append(part(f"Rib{index:02d}West", (0.46, height - 0.8, 0.72), (x0 + 0.8, FLOOR_Y + (height - 0.8) / 2, z), material="Metal", color=STEEL_LIGHT))
        if not door_clearance("east", z):
            children.append(part(f"Rib{index:02d}East", (0.46, height - 0.8, 0.72), (x1 - 0.8, FLOOR_Y + (height - 0.8) / 2, z), material="Metal", color=STEEL_LIGHT))
        children.append(part(f"Rib{index:02d}Header", (width - 1.6, 0.38, 0.72), ((x0 + x1) / 2, FLOOR_Y + height - 0.7, z), material="Metal", color=STEEL_LIGHT, collide=False))
    return model(name, children, {"FacilityRoom": True, "FloorY": FLOOR_Y})


def connector_shell(name: str, bounds: Bounds, height: float, closed_sides: Sequence[str]) -> dict:
    """Build a corridor segment whose adjoining door walls are owned by rooms.

    This prevents coplanar floor/ceiling slabs where a service bridge meets the
    main room grid while retaining walls only on its exposed edges.
    """

    x0, x1, z0, z1 = bounds
    width, depth = x1 - x0, z1 - z0
    children: List[dict] = [
        part("FloorSlab", (width, 0.5, depth), ((x0 + x1) / 2, FLOOR_Y - 0.25, (z0 + z1) / 2), material="Slate", color=FLOOR),
        part("CeilingSlab", (width, 0.52, depth), ((x0 + x1) / 2, FLOOR_Y + height, (z0 + z1) / 2), material="Concrete", color=CONCRETE_DARK),
    ]
    if "south" in closed_sides:
        children.append(_wall_segment("SouthWall", ((x0 + x1) / 2, FLOOR_Y + height / 2, z0), (width, height, 0.72)))
    if "north" in closed_sides:
        children.append(_wall_segment("NorthWall", ((x0 + x1) / 2, FLOOR_Y + height / 2, z1), (width, height, 0.72)))
    if "west" in closed_sides:
        children.append(_wall_segment("WestWall", (x0, FLOOR_Y + height / 2, (z0 + z1) / 2), (0.72, height, depth)))
    if "east" in closed_sides:
        children.append(_wall_segment("EastWall", (x1, FLOOR_Y + height / 2, (z0 + z1) / 2), (0.72, height, depth)))
    return model(name, children, {"FacilityRoom": True, "FloorY": FLOOR_Y})


def aged_floor_marks(prefix: str, center: Vec3, width: float, depth: float, count: int = 4) -> List[dict]:
    x, y, z = center
    marks: List[dict] = []
    for index in range(count):
        offset_x = -width * 0.32 + (index % 3) * width * 0.26
        offset_z = -depth * 0.24 + (index // 3) * depth * 0.45
        marks.append(
            part(
                f"{prefix}Wear{index + 1:02d}",
                (width * (0.12 + 0.02 * (index % 2)), 0.026, depth * 0.07),
                (x + offset_x, y, z + offset_z),
                material="Concrete",
                color=[0.08 + index * 0.006, 0.085 + index * 0.006, 0.082 + index * 0.005],
                collide=False,
                transparency=0.28,
                cast_shadow=False,
                rotation=(0.0, (index - 2) * 8.0, 0.0),
            )
        )
    return marks


def crate(name: str, position: Vec3, size: Vec3 = (3.0, 2.2, 2.5), accent: Sequence[float] = RUST) -> dict:
    x, y, z = position
    sx, sy, sz = size
    return model(
        name,
        [
            part("CrateBody", size, position, material="WoodPlanks", color=WOOD),
            part("TopBand", (sx + 0.14, 0.22, sz + 0.14), (x, y + sy / 2 - 0.18, z), material="CorrodedMetal", color=STEEL, collide=False),
            part("FrontBand", (sx + 0.12, sy + 0.06, 0.18), (x, y, z - sz / 2 - 0.03), material="Metal", color=accent, collide=False),
            part("CornerBand", (0.18, sy + 0.08, sz + 0.1), (x - sx / 2 - 0.02, y, z), material="Metal", color=STEEL_LIGHT, collide=False),
        ],
    )


def production_mesh(
    name: str,
    position: Vec3,
    size: Vec3,
    asset_key: str,
    *,
    rotation: Optional[Tuple[float, float, float]] = None,
) -> dict:
    """Place one verified existing production mesh as non-blocking dressing."""

    asset = IMPORTED_ASSETS[asset_key]
    appearance = {
        "Name": "SurfaceAppearance",
        "ClassName": "SurfaceAppearance",
        "Properties": {
            "ColorMap": asset["ColorMap"],
            "NormalMap": asset["NormalMap"],
            "RoughnessMap": asset["RoughnessMap"],
            "MetalnessMap": asset["MetalnessMap"],
        },
    }
    return part(
        name,
        size,
        position,
        material="Metal",
        color=OFFWHITE,
        collide=False,
        class_name="MeshPart",
        children=[appearance],
        rotation=rotation,
        extra_properties={"MeshId": asset["MeshId"]},
    )


def cable_tray(name: str, position: Vec3, length: float, axis: str, color: Sequence[float] = CONCRETE_DARK) -> dict:
    """A restrained three-line cable tray with a visible carrier rail."""

    x, y, z = position
    if axis == "x":
        offsets = [(0.0, 0.0, -0.32), (0.0, 0.0, 0.32)]
    elif axis == "z":
        offsets = [(-0.32, 0.0, 0.0), (0.32, 0.0, 0.0)]
    else:
        offsets = [(-0.32, 0.0, 0.0), (0.32, 0.0, 0.0)]
    children = [pipe("CarrierRail", position, length, axis, 0.18, STEEL_LIGHT)]
    for index, (offset_x, offset_y, offset_z) in enumerate(offsets, 1):
        children.append(pipe(f"Cable{index}", (x + offset_x, y + offset_y, z + offset_z), length, axis, 0.12, color))
    return model(name, children)


def wall_grille(name: str, position: Vec3, width: float, height: float, accent: Sequence[float] = STEEL_LIGHT) -> dict:
    """Make a shallow steel intake grille for an interior wall surface."""

    x, y, z = position
    children: List[dict] = [
        part("Backplate", (width + 0.32, height + 0.32, 0.14), position, material="CorrodedMetal", color=CONCRETE_DARK, collide=False),
        part("TopFrame", (width + 0.46, 0.18, 0.2), (x, y + height / 2 + 0.06, z - 0.08), material="Metal", color=accent, collide=False),
        part("BottomFrame", (width + 0.46, 0.18, 0.2), (x, y - height / 2 - 0.06, z - 0.08), material="Metal", color=accent, collide=False),
        part("LeftFrame", (0.18, height + 0.36, 0.2), (x - width / 2 - 0.06, y, z - 0.08), material="Metal", color=accent, collide=False),
        part("RightFrame", (0.18, height + 0.36, 0.2), (x + width / 2 + 0.06, y, z - 0.08), material="Metal", color=accent, collide=False),
    ]
    for index in range(5):
        slat_y = y - height * 0.32 + index * height * 0.16
        children.append(part(f"Slat{index + 1}", (width - 0.22, 0.10, 0.16), (x, slat_y, z - 0.13), material="Metal", color=STEEL, collide=False))
    return model(name, children)


def supply_shelf(name: str, position: Vec3, width: float, depth: float, height: float) -> dict:
    x, y, z = position
    children: List[dict] = [
        part("WestUpright", (0.26, height, depth), (x - width / 2, y, z), material="Metal", color=STEEL_LIGHT),
        part("EastUpright", (0.26, height, depth), (x + width / 2, y, z), material="Metal", color=STEEL_LIGHT),
    ]
    for index, level in enumerate((-height * 0.38, 0.0, height * 0.38), 1):
        children.append(part(f"Deck{index}", (width, 0.22, depth), (x, y + level, z), material="DiamondPlate", color=STEEL))
        children.append(crate(f"Supply{index}", (x + (index - 2) * 0.68, y + level + 0.75, z), (1.1, 1.0, depth * 0.62), HAZARD))
    return model(name, children)


def prototype_crate(name: str, position: Vec3, object_text: str, accent: Sequence[float]) -> dict:
    x, y, z = position
    sx, sy, sz = (3.1, 2.3, 2.7)
    return model(
        name,
        [
            part("CrateBody", (sx, sy, sz), position, material="WoodPlanks", color=WOOD),
            part("MovingPart", (sx + 0.18, 0.28, sz + 0.18), (x, y + sy / 2 + 0.13, z), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
            part("OpenPose", (sx + 0.18, 0.28, sz + 0.18), (x, y + sy + 1.15, z + 1.16), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, transparency=1.0, cast_shadow=False, rotation=(-82.0, 0.0, 0.0)),
            part("Latch", (0.62, 0.62, 0.16), (x, y + 0.55, z - sz / 2 - 0.1), material="CorrodedMetal", color=accent, collide=False),
            part("InventoryStripe", (sx * 0.62, 0.17, 0.07), (x, y - 0.32, z - sz / 2 - 0.12), material="SmoothPlastic", color=accent, collide=False, cast_shadow=False),
            interaction_anchor((x, y + 0.18, z - sz / 2 - 0.42), prompt("PrototypeCratePrompt", "OPEN", object_text, 0.42, 7.5)),
        ],
    )


def locker(position: Vec3) -> dict:
    x, y, z = position
    return model(
        "BedroomPersonalUtilityLocker",
        [
            part("LockerBody", (2.2, 6.8, 2.5), position, material="CorrodedMetal", color=STEEL),
            part("MovingPart", (0.18, 6.0, 1.9), (x - 1.18, y, z), material="CorrodedMetal", color=UTILITY_GREEN, collide=False),
            part("OpenPose", (0.18, 6.0, 1.9), (x - 2.1, y, z - 0.9), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, transparency=1.0, cast_shadow=False, rotation=(0.0, 90.0, 0.0)),
            part("NumberPlate", (0.9, 0.44, 0.07), (x - 1.22, y + 0.75, z - 0.78), material="SmoothPlastic", color=OFFWHITE, collide=False, cast_shadow=False),
            part("VentA", (0.82, 0.10, 0.06), (x - 1.22, y + 2.1, z - 0.78), material="Metal", color=CONCRETE_DARK, collide=False),
            part("VentB", (0.82, 0.10, 0.06), (x - 1.22, y + 1.72, z - 0.78), material="Metal", color=CONCRETE_DARK, collide=False),
            interaction_anchor((x - 1.5, y, z - 1.1), prompt("PrototypeLockerPrompt", "OPEN", "PERSONAL LOCKER", 0.42, 7.0)),
        ],
    )


def compatibility_station(
    name: str,
    position: Vec3,
    *,
    target_id: Optional[str],
    prompt_name: str,
    action: str,
    object_text: str,
    accent: Sequence[float],
) -> dict:
    x, y, z = position
    children = [
        part("StationBody", (3.4, 4.8, 2.2), position, material="CorrodedMetal", color=CONCRETE_DARK),
        part("ControlFace", (2.55, 2.18, 0.14), (x, y + 0.52, z - 1.16), material="Metal", color=STEEL, collide=False),
        part("StatusLamp", (0.30, 0.30, 0.12), (x + 0.82, y + 1.12, z - 1.27), material="Neon", color=accent, collide=False, cast_shadow=False, children=[point_light("StationGlow", accent, 0.42, 6.0, False)]),
        part("LabelBar", (1.72, 0.22, 0.08), (x - 0.25, y - 0.25, z - 1.28), material="SmoothPlastic", color=accent, collide=False, cast_shadow=False),
        part("Conduit", (0.35, 4.6, 0.35), (x + 1.82, y, z + 0.45), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rotation=(0.0, 0.0, 90.0)),
        interaction_anchor((x, y + 0.4, z - 1.55), prompt(prompt_name, action, object_text, 0.42, 7.5)),
    ]
    attributes = {"GameplayTargetId": target_id} if target_id else None
    return model(name, children, attributes)


def old_bed(position: Vec3) -> dict:
    x, y, z = position
    return model(
        "WakeBed",
        [
            part("Frame", (7.4, 0.55, 3.6), (x, y, z), material="Metal", color=STEEL),
            part("Mattress", (6.8, 0.58, 3.15), (x, y + 0.55, z), material="Fabric", color=BED_FABRIC),
            part("Blanket", (4.2, 0.18, 3.2), (x + 0.95, y + 0.95, z), material="Fabric", color=[0.13, 0.19, 0.18], collide=False),
            part("Pillow", (1.25, 0.42, 2.6), (x - 2.45, y + 1.0, z), material="Fabric", color=OFFWHITE, collide=False),
            part("FrameWest", (0.22, 1.1, 3.7), (x - 3.48, y + 0.52, z), material="Metal", color=RUST),
            part("FrameEast", (0.22, 1.1, 3.7), (x + 3.48, y + 0.52, z), material="Metal", color=RUST),
        ],
    )


def generator_set() -> dict:
    children: List[dict] = []
    for index, x in enumerate((34.0, 43.0), 1):
        children.append(
            model(
                f"Generator{index}",
                [
                    part("GeneratorBlock", (6.5, 4.3, 3.5), (x, 56.25, 66.0), material="CorrodedMetal", color=STEEL),
                    part("GeneratorTop", (6.8, 0.30, 3.8), (x, 58.55, 66.0), material="Metal", color=STEEL_LIGHT, collide=False),
                    part("ServicePanel", (3.2, 1.6, 0.12), (x, 56.8, 64.18), material="Metal", color=CONCRETE_DARK, collide=False),
                    part("StatusStrip", (1.7, 0.16, 0.08), (x, 57.3, 64.1), material="Neon", color=UTILITY_GREEN, collide=False, cast_shadow=False),
                    pipe("ExhaustPipe", (x, 62.1, 66.8), 7.0, "y", 0.48, STEEL_LIGHT),
                    part("ExhaustCap", (1.15, 0.35, 1.15), (x, 65.7, 66.8), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder"),
                ],
            )
        )
    return model("TwinGeneratorArray", children)


def build_architecture() -> List[dict]:
    rooms = [
        room_shell("BlastVestibule", (-12.0, 12.0, 14.0, 34.0), 12.0, {"south": (0.0, 10.0, 8.0), "north": (0.0, 10.0, 8.0)}),
        room_shell("DecontaminationSpine", (-8.0, 8.0, 34.0, 52.0), 11.0, {"south": (0.0, 10.0, 8.0), "north": (0.0, 10.0, 8.0)}),
        room_shell("CentralCommons", (-24.0, 24.0, 52.0, 80.0), 15.0, {"south": (0.0, 10.0, 8.0), "west": (66.0, 10.0, 8.0), "east": (66.0, 10.0, 8.0), "north": (-4.0, 10.0, 8.0)}),
        room_shell("ResidentialSpine", (-36.0, -24.0, 54.0, 112.0), 11.0, {"east": (66.0, 10.0, 8.0), "west": [(68.0, 10.0, 8.0), (98.0, 10.0, 8.0)]}),
        room_shell("StartingBedroom", (-60.0, -36.0, 56.0, 82.0), 11.0, {"east": (68.0, 10.0, 8.0)}),
        room_shell("WorkshopArmory", (-60.0, -36.0, 86.0, 112.0), 12.0, {"east": (98.0, 10.0, 8.0)}),
        room_shell("UpgradeBay", (-20.0, 4.0, 92.0, 118.0), 12.0, {"south": (-8.0, 10.0, 8.0), "north": (0.0, 10.0, 8.0), "east": (98.0, 10.0, 8.0)}),
        room_shell("UpgradeLink", (-12.0, 4.0, 80.0, 92.0), 11.0, {"south": (-4.0, 10.0, 8.0), "north": (-4.0, 10.0, 8.0)}),
        room_shell("PowerHall", (24.0, 54.0, 52.0, 80.0), 14.0, {"west": (66.0, 10.0, 8.0), "north": (30.0, 12.0, 8.0)}),
        model("PowerServiceBridge", [
            part("FloorSlab", (18.0, 0.5, 6.0), (27.0, FLOOR_Y - 0.25, 83.0), material="Slate", color=FLOOR),
            part("CeilingSlab", (18.0, 0.52, 6.0), (27.0, FLOOR_Y + 11.0, 83.0), material="Concrete", color=CONCRETE_DARK),
            _wall_segment("SouthClosure", (21.0, FLOOR_Y + 5.5, 80.0), (6.0, 11.0, 0.72)),
            _wall_segment("NorthClosure", (31.0, FLOOR_Y + 5.5, 86.0), (10.0, 11.0, 0.72)),
            _wall_segment("WestWall", (18.0, FLOOR_Y + 5.5, 83.0), (0.72, 11.0, 6.0)),
            _wall_segment("EastWall", (36.0, FLOOR_Y + 5.5, 83.0), (0.72, 11.0, 6.0)),
            part("WestServiceRib", (0.42, 10.2, 0.72), (18.8, FLOOR_Y + 5.1, 83.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("EastServiceRib", (0.42, 10.2, 0.72), (35.2, FLOOR_Y + 5.1, 83.0), material="Metal", color=STEEL_LIGHT, collide=False),
        ], {"FacilityRoom": True, "FloorY": FLOOR_Y}),
        room_shell("UtilitySpine", (16.0, 28.0, 86.0, 118.0), 11.0, {"south": (22.0, 8.0, 8.0), "north": (22.0, 8.0, 8.0), "west": (98.0, 10.0, 8.0), "east": (96.0, 10.0, 8.0)}),
        room_shell("UtilitySpineNorth", (16.0, 28.0, 130.0, 148.0), 11.0, {"south": (22.0, 8.0, 8.0), "east": (132.0, 10.0, 8.0)}),
        room_shell("StorageMedicalReserve", (28.0, 54.0, 86.0, 108.0), 11.0, {"west": (96.0, 10.0, 8.0)}),
        room_shell("ScrapExchange", (-4.0, 16.0, 130.0, 154.0), 11.0, {"south": (8.0, 10.0, 8.0)}),
        room_shell("FarmServiceLock", (28.0, 54.0, 116.0, 148.0), 11.0, {"west": [(124.0, 10.0, 8.0), (132.0, 10.0, 8.0)], "north": (40.0, 10.0, 8.0)}),
        room_shell("ServiceCrossPassage", (-4.0, 28.0, 118.0, 130.0), 10.0, {"south": [(0.0, 10.0, 8.0), (22.0, 8.0, 8.0)], "north": [(8.0, 10.0, 8.0), (22.0, 8.0, 8.0)], "east": (124.0, 10.0, 8.0)}),
        connector_shell("UpgradeServiceBridge", (4.0, 16.0, 92.0, 104.0), 11.0, ("south", "north")),
    ]
    return rooms


def build_room_dressing() -> List[dict]:
    bedroom = model(
        "BedroomDressing",
        [
            old_bed((-46.5, 55.0, 66.5)),
            part("BedsideLocker", (1.8, 2.2, 1.8), (-41.2, 55.1, 63.3), material="CorrodedMetal", color=STEEL),
            part("WakeLamp", (0.4, 1.3, 0.4), (-41.2, 56.95, 63.3), material="Metal", color=RUST, collide=False, children=[point_light("WakeLampPool", LIGHT_WARM, 0.65, 8.0, True)]),
            crate("BedroomArchiveCrate", (-51.0, 55.1, 60.8), (2.3, 1.8, 2.0), UTILITY_GREEN),
            *aged_floor_marks("Bedroom", (-44.0, 54.02, 70.0), 17.0, 16.0),
        ],
    )
    commons_children: List[dict] = [
        part("CommonsTable", (9.0, 0.65, 4.2), (0.0, 56.0, 65.0), material="WoodPlanks", color=WOOD),
        part("CommonsTableLegWest", (0.42, 3.2, 0.42), (-3.7, 54.4, 63.4), material="Metal", color=STEEL),
        part("CommonsTableLegEast", (0.42, 3.2, 0.42), (3.7, 54.4, 66.6), material="Metal", color=STEEL),
        supply_shelf("MedicalWallShelf", (-18.3, 58.0, 72.5), 3.4, 1.2, 6.8),
        crate("CommonsRationCrate", (13.5, 55.2, 72.0), (2.7, 2.0, 2.2), HAZARD),
        *aged_floor_marks("Commons", (0.0, 54.02, 65.0), 33.0, 18.0, 6),
    ]
    workshop = model(
        "WorkshopDressing",
        [
            part("WorkbenchSurface", (10.0, 0.48, 2.8), (-47.0, 57.0, 91.0), material="WoodPlanks", color=WOOD),
            part("WorkbenchFrame", (10.2, 2.6, 0.26), (-47.0, 55.6, 92.25), material="Metal", color=STEEL),
            supply_shelf("WorkshopPartsShelf", (-52.2, 58.0, 106.0), 4.4, 1.8, 7.0),
            pipe("WorkshopOverheadLineA", (-43.0, 64.7, 99.0), 17.0, "z", 0.38, RUST),
            pipe("WorkshopOverheadLineB", (-40.9, 64.2, 99.0), 17.0, "z", 0.28, STEEL_LIGHT),
            *aged_floor_marks("Workshop", (-44.0, 54.02, 99.0), 16.0, 17.0, 5),
        ],
    )
    upgrade = model(
        "UpgradeDressing",
        [
            part("HydraulicRigBase", (8.8, 0.6, 6.2), (-8.0, 54.3, 101.0), material="DiamondPlate", color=STEEL),
            pipe("HydraulicRamWest", (-11.5, 58.5, 101.0), 6.7, "y", 0.72, STEEL_LIGHT),
            pipe("HydraulicRamEast", (-4.5, 58.5, 101.0), 6.7, "y", 0.72, STEEL_LIGHT),
            part("UpgradeStatusPanel", (4.2, 2.3, 0.14), (-8.0, 58.4, 108.1), material="Metal", color=CONCRETE_DARK, collide=False),
            part("UpgradeStatusGlow", (2.1, 0.16, 0.08), (-8.0, 58.6, 108.2), material="Neon", color=HAZARD, collide=False, cast_shadow=False),
            *aged_floor_marks("Upgrade", (-8.0, 54.02, 97.0), 15.0, 17.0, 5),
        ],
    )
    storage = model(
        "StorageDressing",
        [
            supply_shelf("StorageShelfNorth", (49.2, 58.0, 90.0), 4.4, 1.8, 7.0),
            supply_shelf("StorageShelfSouth", (49.2, 58.0, 103.0), 4.4, 1.8, 7.0),
            crate("MedicalManifestCrate", (35.0, 55.2, 91.0), (2.8, 2.1, 2.4), EMERGENCY_RED),
            *aged_floor_marks("Storage", (39.0, 54.02, 96.0), 17.0, 16.0, 5),
        ],
    )
    power = model(
        "PowerDressing",
        [
            generator_set(),
            pipe("PowerDistributionA", (29.5, 65.5, 58.0), 20.0, "z", 0.48, STEEL_LIGHT),
            pipe("PowerDistributionB", (51.0, 64.8, 62.0), 18.0, "z", 0.32, RUST),
            part("BreakerBoard", (4.3, 5.0, 0.35), (50.8, 58.0, 54.5), material="Metal", color=CONCRETE_DARK),
            part("BreakerStrip", (2.6, 0.16, 0.10), (50.8, 58.9, 54.26), material="Neon", color=UTILITY_GREEN, collide=False, cast_shadow=False),
            *aged_floor_marks("Power", (40.0, 54.02, 71.0), 18.0, 16.0, 5),
        ],
    )
    exchange = model(
        "ExchangeDressing",
        [
            part("Counter", (6.0, 1.1, 2.6), (12.0, 56.3, 146.0), material="Metal", color=STEEL),
            part("CounterGrille", (4.8, 2.0, 0.18), (12.0, 58.0, 147.35), material="Metal", color=CONCRETE_DARK, collide=False),
            crate("ScrapIntakeBin", (3.4, 55.2, 143.0), (2.4, 2.2, 2.2), RUST),
            pipe("ExchangeVent", (1.4, 63.9, 140.0), 8.5, "z", 0.46, STEEL_LIGHT),
            *aged_floor_marks("Exchange", (8.0, 54.02, 142.0), 14.0, 16.0, 4),
        ],
    )
    farm_lock = model(
        "FarmServiceDressing",
        [
            part("DeconDrain", (7.0, 0.08, 1.2), (40.0, 54.04, 127.0), material="DiamondPlate", color=STEEL, collide=False),
            part("ServiceWindowFrame", (6.6, 4.0, 0.24), (29.1, 59.5, 141.2), material="Metal", color=STEEL_LIGHT, collide=False),
            pipe("FarmWaterLine", (50.0, 60.5, 135.0), 19.0, "z", 0.34, UTILITY_BLUE),
            *aged_floor_marks("FarmService", (40.0, 54.02, 132.0), 17.0, 22.0, 5),
        ],
    )
    return [bedroom, model("CentralCommonsDressing", commons_children), workshop, upgrade, storage, power, exchange, farm_lock]


def build_infrastructure_art() -> dict:
    """Add room-specific infrastructure without consuming circulation clearance."""

    return model(
        "InfrastructureArt",
        [
            model(
                "CommonsInfrastructure",
                [
                    cable_tray("CommonsCableTray", (0.0, 67.2, 57.5), 28.0, "x", RUST),
                    pipe("CommonsAirMain", (0.0, 66.2, 76.0), 34.0, "x", 0.62, STEEL_LIGHT),
                    pipe("CommonsAirDropWest", (-17.5, 62.3, 75.7), 7.4, "y", 0.38, STEEL_LIGHT),
                    wall_grille("CommonsNorthIntake", (16.0, 61.0, 79.52), 3.6, 2.55),
                    production_mesh("CommonsJunctionBox", (-20.6, 59.0, 79.45), (1.7, 1.6, 0.82), "junction_box"),
                ],
            ),
            model(
                "BedroomInfrastructure",
                [
                    cable_tray("BedroomCableTray", (-49.0, 64.6, 59.2), 13.0, "x", CONCRETE_DARK),
                    pipe("BedroomHeatReturn", (-58.0, 58.3, 74.0), 10.0, "z", 0.32, RUST),
                    wall_grille("BedroomAirReturn", (-56.5, 60.4, 81.52), 3.2, 2.35),
                    production_mesh("BedroomJunctionBox", (-58.6, 59.0, 75.8), (1.4, 1.45, 0.72), "junction_box"),
                ],
            ),
            model(
                "WorkshopInfrastructure",
                [
                    cable_tray("WorkshopCableTray", (-49.0, 65.0, 99.0), 17.0, "z", CONCRETE_DARK),
                    wall_grille("WorkshopExtractionGrille", (-56.4, 60.7, 111.5), 3.4, 2.6),
                    production_mesh("WorkshopValveAssembly", (-56.8, 57.2, 93.4), (1.8, 1.35, 1.15), "valve_assembly", rotation=(0.0, 90.0, 0.0)),
                    production_mesh("WorkshopAmmoCrate", (-39.2, 54.74, 108.4), (2.1, 1.48, 1.42), "ammo_crate", rotation=(0.0, -16.0, 0.0)),
                ],
            ),
            model(
                "UpgradeInfrastructure",
                [
                    cable_tray("UpgradeCableTray", (-8.0, 65.1, 114.8), 15.0, "x", RUST),
                    production_mesh("UpgradeJunctionBox", (-17.6, 59.4, 112.5), (1.8, 1.7, 0.84), "junction_box", rotation=(0.0, 90.0, 0.0)),
                    production_mesh("UpgradeHydraulicValve", (-17.2, 57.0, 96.3), (1.72, 1.3, 1.1), "valve_assembly", rotation=(0.0, 90.0, 0.0)),
                ],
            ),
            model(
                "StorageInfrastructure",
                [
                    wall_grille("StorageAirReturn", (33.0, 60.5, 107.52), 3.4, 2.45),
                    production_mesh("StorageMedicalCrate", (37.0, 54.725, 103.4), (2.0, 1.45, 1.36), "ammo_crate", rotation=(0.0, 18.0, 0.0)),
                    production_mesh("StorageDistributionBox", (52.5, 59.6, 91.0), (1.7, 1.6, 0.82), "junction_box", rotation=(0.0, -90.0, 0.0)),
                ],
            ),
            model(
                "PowerInfrastructure",
                [
                    cable_tray("PowerCableTray", (40.0, 66.3, 57.5), 20.0, "x", CONCRETE_DARK),
                    pipe("PowerCoolantReturn", (51.0, 61.0, 73.0), 9.2, "y", 0.44, UTILITY_BLUE),
                    production_mesh("PowerValveAssembly", (52.5, 57.3, 68.5), (1.9, 1.38, 1.2), "valve_assembly", rotation=(0.0, -90.0, 0.0)),
                    production_mesh("PowerNorthVent", (50.2, 61.6, 79.4), (2.2, 1.9, 2.1), "vent_grille", rotation=(0.0, 180.0, 0.0)),
                ],
            ),
            model(
                "ServiceInfrastructure",
                [
                    cable_tray("ServiceCrossCableTray", (24.0, 63.3, 123.5), 16.0, "z", CONCRETE_DARK),
                    production_mesh("ServiceCrossValve", (16.8, 58.1, 115.5), (1.7, 1.3, 1.1), "valve_assembly", rotation=(0.0, 90.0, 0.0)),
                    production_mesh("ExchangeJunctionBox", (-2.8, 59.0, 150.8), (1.75, 1.65, 0.82), "junction_box", rotation=(0.0, 90.0, 0.0)),
                ],
            ),
            model(
                "FarmServiceInfrastructure",
                [
                    wall_grille("FarmServiceExhaust", (40.0, 60.5, 147.52), 3.8, 2.65),
                    production_mesh("FarmWaterValve", (52.5, 57.5, 128.5), (1.78, 1.34, 1.13), "valve_assembly", rotation=(0.0, -90.0, 0.0)),
                    production_mesh("FarmAirVent", (31.5, 60.7, 140.8), (2.15, 1.9, 2.1), "vent_grille", rotation=(0.0, 90.0, 0.0)),
                ],
            ),
        ],
    )


def build_interactions() -> dict:
    return model(
        "InteractiveProps",
        [
            locker((-53.2, 57.4, 75.5)),
            prototype_crate("StorageMedicalSupplyCrate", (35.5, 55.2, 91.0), "MEDICAL SUPPLY CRATE", EMERGENCY_RED),
            prototype_crate("WorkshopConsumablesCrate", (-48.0, 55.2, 105.0), "WORKSHOP SUPPLY CRATE", HAZARD),
            compatibility_station("BatteryPurchaseStation", (31.8, 56.6, 73.5), target_id="legacy_battery_station", prompt_name="OfflineControlPrompt", action="BUY", object_text="BATTERY CELL — 20 CREDITS", accent=UTILITY_GREEN),
            compatibility_station("ScrapExchangeStation", (12.5, 56.6, 137.0), target_id="legacy_scrap_processor", prompt_name="InspectStationPrompt", action="PROCESS", object_text="SCRAP EXCHANGE — 5 CREDITS EACH", accent=HAZARD),
            compatibility_station("HarvestUpgradeConsole", (-8.0, 56.6, 105.0), target_id="legacy_harvest_upgrade", prompt_name="InspectStationPrompt", action="UPGRADE", object_text="HARVEST RIG — 100 CREDITS", accent=HAZARD),
            compatibility_station("WeaponWorkbenchStation", (-42.5, 56.6, 94.0), target_id="legacy_weapon_upgrade", prompt_name="InspectStationPrompt", action="UPGRADE", object_text="WEAPON BENCH — 200 CREDITS", accent=EMERGENCY_RED),
            compatibility_station("EntrySystemsInspectionPoint", (-7.2, 56.6, 28.5), target_id=None, prompt_name="InspectStationPrompt", action="INSPECT", object_text="ENTRY SYSTEMS — NO POWER", accent=EMERGENCY_RED),
        ],
    )


def build_markers() -> dict:
    marker = lambda name, position, attributes=None: part(
        name,
        (0.5, 0.5, 0.5),
        position,
        material="SmoothPlastic",
        color=UTILITY_BLUE,
        collide=False,
        transparency=1.0,
        cast_shadow=False,
        attributes=attributes,
    )
    return model(
        "CompositionMarkers",
        [
            marker("FutureBunkerDoorMarker", (0.0, 54.1, 21.2), {"BunkerEntranceTarget": True, "GreenfieldContract": "EntranceTarget"}),
            marker("FutureBunkerLightsControlMarker", (31.8, 58.1, 72.0), {"GreenfieldContract": "PowerControl"}),
            marker("FutureBatteryButtonMarker", (31.8, 58.1, 73.5), {"GreenfieldContract": "BatteryPurchase"}),
            marker("FutureProcessorMarker", (12.5, 54.1, 137.0), {"GreenfieldContract": "ScrapExchange"}),
            marker("FutureUpgradeTableMarker", (-8.0, 54.1, 105.0), {"GreenfieldContract": "HarvestUpgrade"}),
            marker("FutureWeaponWorkbenchMarker", (-42.5, 54.1, 94.0), {"GreenfieldContract": "WeaponUpgrade"}),
            marker("FarmRouteMarker", (40.0, 54.1, 151.0), {"GreenfieldContract": "FarmRoute"}),
        ],
    )


def build_lighting() -> dict:
    return model(
        "Lighting",
        [
            fluorescent_fixture("WakeSideFluorescent", (-46.0, 64.7, 73.0), LIGHT_WARM, 1.3, 14.0),
            fluorescent_fixture("MiddleAgedBay", (-27.5, 64.1, 70.0), LIGHT_COOL, 1.35, 15.0),
            fluorescent_fixture("StorageAisleLight", (39.0, 64.1, 96.0), LIGHT_COOL, 1.4, 16.0),
            fluorescent_fixture("WorkshopEntryFill", (-39.0, 65.0, 91.0), LIGHT_WARM, 1.45, 16.0),
            fluorescent_fixture("ServiceConnectorPractical", (24.0, 64.0, 124.0), LIGHT_COOL, 1.25, 14.0),
            fluorescent_fixture("FarmExitEmergencyPractical", (40.0, 64.0, 140.0), EMERGENCY_RED, 1.1, 13.0),
            fluorescent_fixture("CommonsHighBayA", (-11.0, 67.9, 60.0), LIGHT_COOL, 1.7, 19.0),
            fluorescent_fixture("CommonsHighBayB", (11.0, 67.9, 72.0), LIGHT_COOL, 1.7, 19.0),
            fluorescent_fixture("PowerGridBay", (40.0, 66.7, 72.0), LIGHT_WARM, 1.55, 18.0),
            fluorescent_fixture("ExchangeCounterBay", (8.0, 64.0, 142.0), LIGHT_WARM, 1.3, 14.0),
        ],
    )


def build_environment_details() -> dict:
    return model(
        "EnvironmentDetails",
        [
            part("WaterDripPool", (3.1, 0.035, 2.2), (40.0, 54.025, 139.5), material="SmoothPlastic", color=[0.10, 0.18, 0.20], collide=False, transparency=0.14, cast_shadow=False),
            part("ServiceWetSheen", (4.8, 0.025, 2.8), (24.0, 54.02, 123.5), material="SmoothPlastic", color=[0.11, 0.17, 0.17], collide=False, transparency=0.22, cast_shadow=False),
            part("PowerSootBand", (11.0, 0.025, 1.2), (40.0, 67.6, 75.5), material="SmoothPlastic", color=[0.055, 0.055, 0.05], collide=False, transparency=0.34, cast_shadow=False),
            part("CommonsLeakHalo", (2.8, 0.024, 2.8), (5.0, 68.72, 60.0), material="SmoothPlastic", color=[0.10, 0.10, 0.085], collide=False, transparency=0.42, cast_shadow=False),
            pipe("ServiceConduitA", (24.6, 63.5, 124.0), 16.0, "z", 0.22, UTILITY_BLUE),
            pipe("ServiceConduitB", (26.3, 63.0, 124.0), 16.0, "z", 0.22, RUST),
            model(
                "EmergencyLighting",
                [
                    emergency_wall_lamp("EntryGuideWest", (-8.6, 59.5, 21.0), LIGHT_WARM),
                    emergency_wall_lamp("EntryGuideEast", (8.6, 59.5, 38.0), LIGHT_WARM),
                    emergency_wall_lamp("CommonsGuideSouth", (-18.8, 61.0, 58.0), LIGHT_COOL),
                    emergency_wall_lamp("CommonsGuideNorth", (18.8, 61.0, 74.0), LIGHT_COOL),
                    emergency_wall_lamp("BedroomGuide", (-53.8, 59.5, 66.0), LIGHT_WARM),
                    emergency_wall_lamp("WorkshopGuide", (-53.8, 60.0, 96.0), LIGHT_WARM),
                    emergency_wall_lamp("UpgradeGuide", (-18.7, 60.0, 97.0), HAZARD),
                    emergency_wall_lamp("PowerGuide", (52.7, 60.0, 71.0), UTILITY_GREEN),
                    emergency_wall_lamp("PowerServiceGuide", (17.4, 59.5, 82.0), UTILITY_BLUE),
                    emergency_wall_lamp("ServiceCrossGuide", (17.4, 59.5, 123.0), LIGHT_COOL),
                    emergency_wall_lamp("StorageGuide", (52.7, 59.5, 96.0), LIGHT_COOL),
                    emergency_wall_lamp("ExchangeGuide", (-2.8, 59.5, 140.0), LIGHT_WARM),
                    emergency_wall_lamp("FarmGuide", (52.7, 59.5, 137.0), EMERGENCY_RED),
                ],
            ),
        ],
    )


def build_exterior() -> dict:
    return model(
        "Exterior",
        [
            part("EntranceApron", (17.0, 0.42, 12.0), (0.0, 53.79, 8.0), material="Concrete", color=CONCRETE_WORN),
            part("WestBerm", (10.0, 3.8, 13.0), (-13.0, 55.4, 15.0), material="Ground", color=EARTH, rotation=(0.0, 0.0, -18.0)),
            part("EastBerm", (10.0, 3.8, 13.0), (13.0, 55.4, 15.0), material="Ground", color=EARTH, rotation=(0.0, 0.0, 18.0)),
            part("BlastDoorFrameWest", (1.0, 8.8, 1.1), (-4.6, 58.2, 14.4), material="Metal", color=STEEL_LIGHT),
            part("BlastDoorFrameEast", (1.0, 8.8, 1.1), (4.6, 58.2, 14.4), material="Metal", color=STEEL_LIGHT),
            part("BlastDoorHeader", (10.2, 1.0, 1.1), (0.0, 62.25, 14.4), material="Metal", color=STEEL_LIGHT),
            part("DoorWarningStripe", (6.0, 0.24, 0.08), (0.0, 60.5, 13.82), material="SmoothPlastic", color=HAZARD, collide=False, cast_shadow=False),
            part("FarmServiceApron", (14.0, 0.4, 13.0), (40.0, 53.8, 154.0), material="Concrete", color=CONCRETE_WORN),
            part("FarmRouteTrackA", (8.0, 0.18, 32.0), (40.0, 53.92, 174.0), material="Concrete", color=CONCRETE_WORN, collide=False, rotation=(0.0, 12.0, 0.0)),
            part("FarmRouteTrackB", (8.0, 0.18, 21.0), (47.0, 53.92, 199.0), material="Concrete", color=CONCRETE_WORN, collide=False, rotation=(0.0, 12.0, 0.0)),
            part("EntrySignBackplate", (5.4, 1.45, 0.12), (0.0, 61.0, 13.78), material="Metal", color=CONCRETE_DARK, collide=False),
            model(
                "EntryHeadworks",
                [
                    part("WestBlastLeaf", (4.3, 8.4, 0.30), (-7.55, 58.4, 13.18), material="CorrodedMetal", color=STEEL, collide=False),
                    part("EastBlastLeaf", (4.3, 8.4, 0.30), (7.55, 58.4, 13.18), material="CorrodedMetal", color=STEEL, collide=False),
                    part("WestLeafBrace", (0.28, 7.4, 0.42), (-8.85, 58.25, 12.92), material="Metal", color=STEEL_LIGHT, collide=False),
                    part("EastLeafBrace", (0.28, 7.4, 0.42), (8.85, 58.25, 12.92), material="Metal", color=STEEL_LIGHT, collide=False),
                    part("ArmoredHeaderBand", (17.2, 1.18, 0.38), (0.0, 64.55, 13.10), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
                    part("DoorTrackRail", (10.2, 0.22, 0.32), (0.0, 61.75, 12.93), material="Metal", color=RUST, collide=False),
                    part("WestDoorStatusLens", (0.42, 0.78, 0.15), (-6.2, 60.2, 12.88), material="Neon", color=HAZARD, collide=False, cast_shadow=False, children=[point_light("WestStatusGlow", HAZARD, 0.5, 7.0, False)]),
                    part("EastDoorStatusLens", (0.42, 0.78, 0.15), (6.2, 60.2, 12.88), material="Neon", color=EMERGENCY_RED, collide=False, cast_shadow=False, children=[point_light("EastStatusGlow", EMERGENCY_RED, 0.45, 7.0, False)]),
                    pipe("WestEntryConduit", (-10.2, 60.7, 13.0), 8.7, "y", 0.26, UTILITY_BLUE),
                    pipe("EastEntryConduit", (10.2, 60.7, 13.0), 8.7, "y", 0.26, RUST),
                    production_mesh("WestEntryVent", (-10.2, 60.0, 13.03), (2.05, 1.82, 1.98), "vent_grille", rotation=(0.0, 180.0, 0.0)),
                    production_mesh("EastEntryJunction", (10.2, 58.4, 13.0), (1.65, 1.55, 0.80), "junction_box", rotation=(0.0, 180.0, 0.0)),
                ],
            ),
            model(
                "SurfaceRevetment",
                [
                    part("WestRetainingTier", (8.0, 1.7, 9.5), (-14.3, 54.9, 8.3), material="Ground", color=[0.23, 0.24, 0.18], collide=False, rotation=(0.0, 0.0, -9.0)),
                    part("EastRetainingTier", (8.0, 1.7, 9.5), (14.3, 54.9, 8.3), material="Ground", color=[0.23, 0.24, 0.18], collide=False, rotation=(0.0, 0.0, 9.0)),
                    part("WestApronCurb", (5.0, 0.46, 1.0), (-7.4, 54.02, 7.6), material="Concrete", color=CONCRETE_WORN, collide=False, rotation=(0.0, -7.0, 0.0)),
                    part("EastApronCurb", (5.0, 0.46, 1.0), (7.4, 54.02, 7.6), material="Concrete", color=CONCRETE_WORN, collide=False, rotation=(0.0, 7.0, 0.0)),
                    pipe("WestSurfaceVentStack", (-13.3, 61.5, 17.3), 9.0, "y", 0.44, STEEL_LIGHT),
                    pipe("EastSurfaceVentStack", (13.3, 61.5, 17.3), 9.0, "y", 0.44, STEEL_LIGHT),
                    part("WestVentCap", (1.05, 0.30, 1.05), (-13.3, 66.15, 17.3), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder"),
                    part("EastVentCap", (1.05, 0.30, 1.05), (13.3, 66.15, 17.3), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder"),
                ],
            ),
        ],
    )


def bedroom_spawn() -> dict:
    return part(
        "BedroomStartSpawn",
        (5.0, 1.0, 5.0),
        (-46.5, 54.5, 72.5),
        material="SmoothPlastic",
        color=UTILITY_GREEN,
        collide=False,
        transparency=1.0,
        class_name="SpawnLocation",
        cast_shadow=False,
        extra_properties={
            "Neutral": True,
            "AllowTeamChangeOnTouch": False,
            "Duration": 0.0,
            "Enabled": True,
        },
        attributes={"GreenfieldSpawn": True},
    )


def _translate_tree(node: dict, offset: Vec3) -> None:
    properties = node.get("Properties")
    if isinstance(properties, dict):
        position = properties.get("Position")
        if isinstance(position, list) and len(position) == 3:
            properties["Position"] = [position[index] + offset[index] for index in range(3)]
        cframe_value = properties.get("CFrame")
        if isinstance(cframe_value, list) and len(cframe_value) >= 3:
            for index in range(3):
                cframe_value[index] += offset[index]
    for child in node.get("Children", []):
        _translate_tree(child, offset)


def build_facility(mode: str) -> dict:
    if mode not in {"staging", "active"}:
        raise ValueError("mode must be 'staging' or 'active'")

    root = {
        "ClassName": "Model",
        "attributes": {
            "FacilityVersion": "BKR-GREENFIELD-001",
            "FacilityMode": mode,
            "GreenfieldFacility": True,
            "FloorElevation": FLOOR_Y,
        },
        "Children": [
            model("Architecture", build_architecture()),
            model("Rooms", build_room_dressing() + [build_infrastructure_art()]),
            build_interactions(),
            build_markers(),
            build_lighting(),
            build_environment_details(),
            build_exterior(),
        ],
    }
    if mode == "active":
        root["Children"].append(model("Spawn", [bedroom_spawn()]))
    _translate_tree(root, STAGING_OFFSET if mode == "staging" else ACTIVE_OFFSET)
    return root
