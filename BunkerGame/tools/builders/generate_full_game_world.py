#!/usr/bin/env python3
"""Generate the deterministic FG-GREENFIELD-001 source world.

The builder is intentionally self-contained. It does not import any legacy
bunker or overworld builder. Accepted generated assets are read only as JSON,
copied byte-for-byte into source, and selectively instanced as visual
dressing; the scale-hazard pipe asset is registry-only and is never placed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import shutil
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "src/Workspace/GameWorld.model.json"
ACTIVE_GENERATED_ASSETS = ROOT / "src/ServerStorage/GeneratedAssets"
WORLD_SEED = 260826
GROUND_TOP_Y = 54.0

ACCEPTED_ASSET_FILES = (
    "bunker_electrical_junction_box_01.model.json",
    "bunker_valve_assembly_01.model.json",
    "bunker_vent_grille_01.model.json",
    "old_military_ammo_crate_01.model.json",
    "pipeline_pipe_retry_02.model.json",
)

BASE_PART_CLASSES = {
    "Part",
    "MeshPart",
    "SpawnLocation",
    "WedgePart",
    "CornerWedgePart",
    "TrussPart",
    "Seat",
    "VehicleSeat",
}
LIGHT_CLASSES = {"PointLight", "SpotLight", "SurfaceLight"}
SCRIPT_CLASSES = {"Script", "LocalScript", "ModuleScript"}
ALLOWED_SOUND_IDS = {"rbxassetid://157167203", "rbxassetid://157167205"}

CONCRETE = [0.22, 0.235, 0.23]
CONCRETE_DARK = [0.105, 0.12, 0.12]
CONCRETE_WORN = [0.31, 0.315, 0.285]
STEEL = [0.13, 0.15, 0.15]
STEEL_LIGHT = [0.31, 0.335, 0.32]
RUST = [0.34, 0.17, 0.075]
DEEP_RUST = [0.22, 0.085, 0.035]
HAZARD = [0.72, 0.43, 0.055]
EMERGENCY_RED = [0.55, 0.055, 0.035]
UTILITY_BLUE = [0.10, 0.30, 0.35]
UTILITY_GREEN = [0.14, 0.31, 0.22]
OFF_WHITE = [0.72, 0.75, 0.69]
LIGHT_COOL = [0.62, 0.78, 0.76]
LIGHT_WARM = [0.94, 0.53, 0.24]
EARTH = [0.18, 0.18, 0.13]
EARTH_DARK = [0.105, 0.11, 0.08]
MUD = [0.125, 0.105, 0.07]
SAGE = [0.22, 0.285, 0.19]
SAGE_DARK = [0.105, 0.17, 0.11]
DEAD_GRASS = [0.32, 0.30, 0.18]
WOOD = [0.255, 0.17, 0.085]
WOOD_DARK = [0.14, 0.085, 0.045]
ROCK = [0.25, 0.27, 0.255]
ROCK_DARK = [0.14, 0.16, 0.155]


Vec3 = tuple[float, float, float]


SPAWNS: tuple[tuple[str, int, Vec3], ...] = (
    ("bedroom_01", 1, (-49.0, 54.5, 72.0)),
    ("bedroom_02", 2, (-41.0, 54.5, 72.0)),
    ("bedroom_03", 3, (-33.0, 54.5, 72.0)),
    ("bedroom_04", 4, (-49.0, 54.5, 62.0)),
    ("bedroom_05", 5, (-41.0, 54.5, 62.0)),
    ("bedroom_06", 6, (-33.0, 54.5, 62.0)),
)

STATIONS: tuple[tuple[str, str, Vec3], ...] = (
    ("power_console", "power", (34.0, 56.5, 71.0)),
    ("shop_terminal", "shop", (17.0, 56.5, 108.0)),
    ("personal_storage", "storage", (-48.0, 56.5, 126.0)),
    ("scrap_exchange", "scrap_exchange", (10.0, 56.5, 138.0)),
    ("harvest_upgrade", "upgrade", (-8.0, 56.5, 104.0)),
    ("weapon_upgrade", "upgrade", (-48.0, 56.5, 96.0)),
    ("storage_upgrade", "upgrade", (-48.0, 56.5, 132.0)),
    ("food_processor", "food_processor", (121.0, 55.5, 210.0)),
)

TREE_POSITIONS: tuple[Vec3, ...] = (
    (-110.0, 54.0, -40.0),
    (-128.0, 54.0, -20.0),
    (-145.0, 54.0, 10.0),
    (-160.0, 54.0, 40.0),
    (-118.0, 54.0, 55.0),
    (-178.0, 54.0, 75.0),
    (-95.0, 54.0, 95.0),
    (-140.0, 54.0, 120.0),
    (-195.0, 54.0, 140.0),
    (160.0, 54.0, -30.0),
    (190.0, 54.0, 0.0),
    (220.0, 54.0, 30.0),
    (170.0, 54.0, 70.0),
    (210.0, 54.0, 100.0),
    (245.0, 54.0, 130.0),
    (165.0, 54.0, 160.0),
    (205.0, 54.0, 190.0),
    (250.0, 54.0, 215.0),
)

SCRAP_POSITIONS: tuple[Vec3, ...] = (
    (-55.0, 54.0, -90.0),
    (0.0, 54.0, -120.0),
    (55.0, 54.0, -95.0),
    (-90.0, 54.0, -150.0),
    (15.0, 54.0, -175.0),
    (85.0, 54.0, -155.0),
)

ZOMBIE_POSITIONS: tuple[tuple[float, float], ...] = (
    (-215.0, -70.0),
    (-165.0, -145.0),
    (-85.0, -205.0),
    (0.0, -225.0),
    (85.0, -205.0),
    (165.0, -145.0),
    (215.0, -70.0),
)

OBJECTIVES: tuple[tuple[str, Vec3], ...] = (
    ("bunker_entrance", (0.0, 54.1, 20.0)),
    ("farm_gate", (52.0, 54.1, 155.0)),
    ("zombie_fallback", (0.0, 54.1, 15.0)),
)


def _clean(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == -0.0 else rounded


def _matrix_multiply(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [
        [sum(left[row][index] * right[index][column] for index in range(3)) for column in range(3)]
        for row in range(3)
    ]


def rotation_matrix(rotation: Vec3) -> list[list[float]]:
    x, y, z = (math.radians(value) for value in rotation)
    cx, sx = math.cos(x), math.sin(x)
    cy, sy = math.cos(y), math.sin(y)
    cz, sz = math.cos(z), math.sin(z)
    matrix_x = [[1.0, 0.0, 0.0], [0.0, cx, -sx], [0.0, sx, cx]]
    matrix_y = [[cy, 0.0, sy], [0.0, 1.0, 0.0], [-sy, 0.0, cy]]
    matrix_z = [[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]]
    return _matrix_multiply(matrix_z, _matrix_multiply(matrix_y, matrix_x))


def cframe(position: Vec3, rotation: Vec3 = (0.0, 0.0, 0.0)) -> list[float]:
    matrix = rotation_matrix(rotation)
    return [
        *(_clean(value) for value in position),
        *(_clean(value) for value in matrix[0]),
        *(_clean(value) for value in matrix[1]),
        *(_clean(value) for value in matrix[2]),
    ]


def pivot_property(position: Vec3) -> dict[str, Any]:
    return {
        "WorldPivotData": {
            "OptionalCFrame": {
                "position": list(position),
                "orientation": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            }
        }
    }


def model(
    name: str,
    children: Iterable[dict[str, Any]] = (),
    *,
    attributes: dict[str, Any] | None = None,
    pivot: Vec3 | None = None,
) -> dict[str, Any]:
    node: dict[str, Any] = {"Name": name, "ClassName": "Model", "Children": list(children)}
    if attributes:
        node["attributes"] = attributes
    if pivot is not None:
        node["Properties"] = pivot_property(pivot)
    return node


def part(
    name: str,
    size: Vec3,
    position: Vec3,
    *,
    material: str = "SmoothPlastic",
    color: Sequence[float] = CONCRETE,
    collide: bool = False,
    query: bool | None = None,
    touch: bool = False,
    transparency: float = 0.0,
    cast_shadow: bool = True,
    rotation: Vec3 | None = None,
    shape: str | None = None,
    class_name: str = "Part",
    children: Iterable[dict[str, Any]] = (),
    attributes: dict[str, Any] | None = None,
    extra_properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "Size": list(size),
        "Anchored": True,
        "CanCollide": collide,
        "CanTouch": touch,
        "CanQuery": collide if query is None else query,
        "Material": material,
        "Color": list(color),
        "Transparency": transparency,
        "CastShadow": cast_shadow,
    }
    if rotation is None:
        properties["Position"] = list(position)
    else:
        properties["CFrame"] = cframe(position, rotation)
    if shape:
        properties["Shape"] = shape
    if extra_properties:
        properties.update(extra_properties)
    node: dict[str, Any] = {"Name": name, "ClassName": class_name, "Properties": properties}
    child_list = list(children)
    if child_list:
        node["Children"] = child_list
    if attributes:
        node["attributes"] = attributes
    return node


def cylinder_between(
    name: str,
    start: Vec3,
    end: Vec3,
    diameter: float,
    *,
    material: str = "Metal",
    color: Sequence[float] = STEEL_LIGHT,
    collide: bool = False,
    query: bool | None = None,
    cast_shadow: bool = True,
) -> dict[str, Any]:
    direction = tuple(end[index] - start[index] for index in range(3))
    length = math.sqrt(sum(value * value for value in direction))
    if length <= 0.0:
        raise ValueError(f"zero-length cylinder {name}")
    x_axis = tuple(value / length for value in direction)
    reference = (0.0, 1.0, 0.0) if abs(x_axis[1]) < 0.92 else (0.0, 0.0, 1.0)
    z_axis = (
        x_axis[1] * reference[2] - x_axis[2] * reference[1],
        x_axis[2] * reference[0] - x_axis[0] * reference[2],
        x_axis[0] * reference[1] - x_axis[1] * reference[0],
    )
    z_length = math.sqrt(sum(value * value for value in z_axis))
    z_axis = tuple(value / z_length for value in z_axis)
    y_axis = (
        z_axis[1] * x_axis[2] - z_axis[2] * x_axis[1],
        z_axis[2] * x_axis[0] - z_axis[0] * x_axis[2],
        z_axis[0] * x_axis[1] - z_axis[1] * x_axis[0],
    )
    midpoint = tuple((start[index] + end[index]) / 2.0 for index in range(3))
    matrix = [
        [x_axis[0], y_axis[0], z_axis[0]],
        [x_axis[1], y_axis[1], z_axis[1]],
        [x_axis[2], y_axis[2], z_axis[2]],
    ]
    node = part(
        name,
        (length, diameter, diameter),
        midpoint,
        material=material,
        color=color,
        collide=collide,
        query=query,
        cast_shadow=cast_shadow,
        shape="Cylinder",
    )
    node["Properties"].pop("Position")
    node["Properties"]["CFrame"] = [
        *(_clean(value) for value in midpoint),
        *(_clean(value) for value in matrix[0]),
        *(_clean(value) for value in matrix[1]),
        *(_clean(value) for value in matrix[2]),
    ]
    return node


def point_light(
    name: str,
    color: Sequence[float],
    brightness: float,
    light_range: float,
    *,
    shadows: bool = False,
) -> dict[str, Any]:
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


def prompt(name: str, action: str, object_text: str, *, hold: float = 0.2, distance: float = 9.0) -> dict[str, Any]:
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
            # InteractionService performs the authoritative character-to-target
            # line-of-sight validation. The invisible anchor is nested within
            # the target model, so engine-side prompt line-of-sight can reject
            # valid close-range interactions behind the model's own geometry.
            "RequiresLineOfSight": False,
            "ClickablePrompt": True,
            "Enabled": True,
        },
    }


def interaction_anchor(position: Vec3, prompt_node: dict[str, Any]) -> dict[str, Any]:
    return part(
        "InteractionAnchor",
        (0.4, 0.4, 0.4),
        position,
        material="SmoothPlastic",
        color=CONCRETE_DARK,
        transparency=1.0,
        cast_shadow=False,
        children=[prompt_node],
    )


def surface_label(text: str, text_color: Sequence[float] = OFF_WHITE) -> dict[str, Any]:
    return {
        "Name": "LabelSurface",
        "ClassName": "SurfaceGui",
        "Properties": {
            "Face": "Front",
            "AlwaysOnTop": False,
            "LightInfluence": 0.2,
            "CanvasSize": [480.0, 120.0],
        },
        "Children": [
            {
                "Name": "Label",
                "ClassName": "TextLabel",
                "Properties": {
                    "BackgroundTransparency": 1.0,
                    "Size": {"UDim2": [[1.0, 0], [1.0, 0]]},
                    "Text": text,
                    "TextColor3": list(text_color),
                    "TextScaled": True,
                    "TextWrapped": True,
                    "Font": "GothamBold",
                    "TextStrokeColor3": [0.02, 0.025, 0.025],
                    "TextStrokeTransparency": 0.35,
                },
            }
        ],
    }


def sign(
    name: str,
    text: str,
    position: Vec3,
    *,
    size: Vec3 = (5.5, 1.5, 0.18),
    color: Sequence[float] = STEEL,
    text_color: Sequence[float] = OFF_WHITE,
    rotation: Vec3 = (0.0, 0.0, 0.0),
) -> dict[str, Any]:
    return part(
        name,
        size,
        position,
        material="Metal",
        color=color,
        rotation=rotation,
        children=[surface_label(text, text_color)],
    )


def fixture(
    name: str,
    position: Vec3,
    color: Sequence[float],
    brightness: float,
    light_range: float,
    *,
    shadows: bool = False,
    rotation: Vec3 = (0.0, 0.0, 0.0),
    circuit: str = "main",
) -> dict[str, Any]:
    x, y, z = position
    return model(
        name,
        [
            part("Housing", (6.3, 0.42, 1.35), position, material="Metal", color=STEEL, rotation=rotation),
            part(
                "Tube",
                (5.5, 0.14, 0.68),
                (x, y - 0.25, z),
                material="Neon",
                color=color,
                cast_shadow=False,
                rotation=rotation,
                attributes={"PowerIndicator": True},
                children=[point_light("LocalPool", color, brightness, light_range, shadows=shadows)],
            ),
            part("WestCap", (0.38, 0.34, 0.92), (x - 2.85, y - 0.08, z), material="CorrodedMetal", color=RUST),
            part("EastCap", (0.38, 0.34, 0.92), (x + 2.85, y - 0.08, z), material="CorrodedMetal", color=RUST),
        ],
        attributes={"PowerCircuit": circuit},
    )


def emergency_lamp(name: str, position: Vec3, color: Sequence[float] = LIGHT_WARM) -> dict[str, Any]:
    return model(
        name,
        [
            part("Cage", (1.2, 1.65, 0.7), position, material="CorrodedMetal", color=STEEL),
            part(
                "Glow",
                (0.68, 1.12, 0.3),
                (position[0], position[1], position[2] - 0.24),
                material="Neon",
                color=color,
                cast_shadow=False,
                children=[point_light("BackupPool", color, 2.4, 24.0, shadows=False)],
            ),
        ],
        attributes={"PowerCircuit": "backup"},
    )


def number_range(minimum: float, maximum: float) -> dict[str, list[float]]:
    return {"NumberRange": [minimum, maximum]}


def number_sequence(points: Sequence[tuple[float, float]]) -> dict[str, Any]:
    return {
        "NumberSequence": {
            "keypoints": [
                {"time": time, "value": value, "envelope": 0.0} for time, value in points
            ]
        }
    }


def color_sequence(start: Sequence[float], finish: Sequence[float]) -> dict[str, Any]:
    return {
        "ColorSequence": {
            "keypoints": [
                {"time": 0.0, "color": list(start)},
                {"time": 1.0, "color": list(finish)},
            ]
        }
    }


def particle_anchor(
    name: str,
    position: Vec3,
    *,
    texture: str,
    rate: float,
    lifetime: tuple[float, float],
    speed: tuple[float, float],
    size: Sequence[tuple[float, float]],
    transparency: Sequence[tuple[float, float]],
    color: tuple[Sequence[float], Sequence[float]],
    acceleration: Vec3 = (0.0, 0.15, 0.0),
    spread: tuple[float, float] = (12.0, 12.0),
) -> dict[str, Any]:
    emitter = {
        "Name": f"{name}Emitter",
        "ClassName": "ParticleEmitter",
        "Properties": {
            "Enabled": True,
            "Texture": texture,
            "Rate": rate,
            "Lifetime": number_range(*lifetime),
            "Speed": number_range(*speed),
            "Acceleration": list(acceleration),
            "Drag": 0.8,
            "SpreadAngle": list(spread),
            "Rotation": number_range(0.0, 360.0),
            "RotSpeed": number_range(-5.0, 5.0),
            "Size": number_sequence(size),
            "Transparency": number_sequence(transparency),
            "Color": color_sequence(*color),
            "LightInfluence": 0.86,
            "Orientation": "FacingCamera",
            "LockedToPart": False,
        },
    }
    return part(
        name,
        (0.3, 0.3, 0.3),
        position,
        transparency=1.0,
        cast_shadow=False,
        children=[{"Name": "EmitterAttachment", "ClassName": "Attachment", "Children": [emitter]}],
    )


def audio_anchor(name: str, position: Vec3, sound_id: str, volume: float) -> dict[str, Any]:
    return part(
        name,
        (0.3, 0.3, 0.3),
        position,
        transparency=1.0,
        cast_shadow=False,
        children=[
            {
                "Name": f"{name}Sound",
                "ClassName": "Sound",
                "Properties": {
                    "SoundId": sound_id,
                    "Volume": volume,
                    "PlaybackSpeed": 1.0,
                    "RollOffMinDistance": 4.0,
                    "RollOffMaxDistance": 28.0,
                    "RollOffMode": "InverseTapered",
                    "Looped": False,
                    "Playing": False,
                },
            }
        ],
    )


def placed_asset(
    instance_name: str,
    filename: str,
    position: Vec3,
    target_size: Vec3,
    *,
    rotation: Vec3 = (0.0, 0.0, 0.0),
    collide: bool = False,
) -> dict[str, Any]:
    if filename == "pipeline_pipe_retry_02.model.json":
        raise ValueError("the scale-hazard pipe asset is registry-only")
    source = ACTIVE_GENERATED_ASSETS / filename
    raw = json.loads(source.read_text(encoding="utf-8"))
    placed = copy.deepcopy(raw)
    placed["Name"] = instance_name
    mesh_parts = [child for child in placed.get("Children", []) if child.get("ClassName") == "MeshPart"]
    if len(mesh_parts) != 1:
        raise ValueError(f"accepted asset {filename} must contain exactly one MeshPart")
    properties = mesh_parts[0].setdefault("Properties", {})
    properties["Size"] = list(target_size)
    properties["CFrame"] = cframe(position, rotation)
    properties.pop("Position", None)
    properties["Anchored"] = True
    properties["CanCollide"] = collide
    properties["CanTouch"] = False
    properties["CanQuery"] = collide
    properties["CastShadow"] = True
    placed.setdefault("attributes", {})["WorldPlacement"] = True
    return placed


def wall_x(name: str, x: float, z1: float, z2: float, *, color: Sequence[float] = CONCRETE) -> dict[str, Any]:
    return part(
        name,
        (1.15, 13.0, abs(z2 - z1)),
        (x, 60.65, (z1 + z2) / 2.0),
        material="Concrete",
        color=color,
        collide=True,
    )


def wall_z(name: str, z: float, x1: float, x2: float, *, color: Sequence[float] = CONCRETE) -> dict[str, Any]:
    return part(
        name,
        (abs(x2 - x1), 13.0, 1.15),
        ((x1 + x2) / 2.0, 60.65, z),
        material="Concrete",
        color=color,
        collide=True,
    )


def door_frame(name: str, position: Vec3, width: float, *, wall_axis: str) -> dict[str, Any]:
    x, _, z = position
    if wall_axis == "x":
        posts = [
            part("SouthPost", (1.0, 11.2, 1.4), (x, 59.9, z - width / 2.0), material="Metal", color=STEEL_LIGHT, collide=True),
            part("NorthPost", (1.0, 11.2, 1.4), (x, 59.9, z + width / 2.0), material="Metal", color=STEEL_LIGHT, collide=True),
            part("Header", (1.0, 1.4, width + 1.4), (x, 65.9, z), material="CorrodedMetal", color=RUST, collide=True),
        ]
    elif wall_axis == "z":
        posts = [
            part("WestPost", (1.4, 11.2, 1.0), (x - width / 2.0, 59.9, z), material="Metal", color=STEEL_LIGHT, collide=True),
            part("EastPost", (1.4, 11.2, 1.0), (x + width / 2.0, 59.9, z), material="Metal", color=STEEL_LIGHT, collide=True),
            part("Header", (width + 1.4, 1.4, 1.0), (x, 65.9, z), material="CorrodedMetal", color=RUST, collide=True),
        ]
    else:
        raise ValueError(f"invalid wall axis {wall_axis}")
    return model(name, posts)


def corridor_rib(name: str, z: float) -> dict[str, Any]:
    return model(
        name,
        [
            part("WestRib", (0.42, 12.4, 0.72), (-8.9, 60.7, z), material="Metal", color=STEEL_LIGHT),
            part("EastRib", (0.42, 12.4, 0.72), (8.9, 60.7, z), material="Metal", color=STEEL_LIGHT),
            part("Crown", (18.2, 0.42, 0.72), (0.0, 66.65, z), material="Metal", color=STEEL_LIGHT),
        ],
    )


def build_foundation() -> dict[str, Any]:
    barriers = [
        part("WestBoundary", (2.0, 22.0, 640.0), (-321.0, 64.0, 80.0), collide=True, query=False, transparency=1.0, cast_shadow=False),
        part("EastBoundary", (2.0, 22.0, 640.0), (321.0, 64.0, 80.0), collide=True, query=False, transparency=1.0, cast_shadow=False),
        part("SouthBoundary", (640.0, 22.0, 2.0), (0.0, 64.0, -241.0), collide=True, query=False, transparency=1.0, cast_shadow=False),
        part("NorthBoundary", (640.0, 22.0, 2.0), (0.0, 64.0, 401.0), collide=True, query=False, transparency=1.0, cast_shadow=False),
    ]
    return model(
        "Foundation",
        [
            part(
                "StableGround",
                (640.0, 3.0, 640.0),
                (0.0, 52.5, 80.0),
                material="Ground",
                color=[0.16, 0.19, 0.13],
                collide=True,
                query=True,
                attributes={"SurfaceDatumY": 54.0, "PersistentSubstrate": True},
            ),
            model("PlayableBoundary", barriers, attributes={"InvisibleSafetyBoundary": True}),
        ],
    )


def build_architecture() -> list[dict[str, Any]]:
    floor_specs = (
        ("EntranceFloor", (20.0, 0.36, 36.0), (0.0, 54.18, 32.0)),
        ("WakeCorridorFloor", (37.0, 0.36, 12.0), (-28.5, 54.18, 44.0)),
        ("BedroomFloor", (36.0, 0.36, 34.0), (-44.0, 54.18, 67.0)),
        ("CommonsFloor", (48.0, 0.36, 44.0), (-2.0, 54.18, 72.0)),
        ("PowerFloor", (36.0, 0.36, 42.0), (40.0, 54.18, 71.0)),
        ("WorkshopFloor", (34.0, 0.36, 36.0), (-45.0, 54.18, 102.0)),
        ("UpgradeFloor", (36.0, 0.36, 30.0), (-10.0, 54.18, 109.0)),
        ("ShopFloor", (30.0, 0.36, 30.0), (23.0, 54.18, 109.0)),
        ("StorageFloor", (32.0, 0.36, 32.0), (-46.0, 54.18, 136.0)),
        ("ServiceFloor", (88.0, 0.36, 28.0), (14.0, 54.18, 138.0)),
        ("PowerLinkFloor", (20.0, 0.36, 32.0), (40.0, 54.18, 108.0)),
    )
    floors = [
        part(name, size, position, material="Concrete", color=CONCRETE_DARK, collide=True)
        for name, size, position in floor_specs
    ]
    floors.extend(
        [
            part("EntranceWear", (8.0, 0.05, 29.0), (0.0, 54.39, 32.0), material="DiamondPlate", color=STEEL_LIGHT),
            part("CommonsRouteStripe", (2.0, 0.04, 38.0), (0.0, 54.39, 72.0), material="SmoothPlastic", color=HAZARD, transparency=0.25),
            part("ServiceDrain", (52.0, 0.08, 1.25), (12.0, 54.42, 145.0), material="DiamondPlate", color=STEEL_LIGHT),
        ]
    )

    ceilings = [
        part(
            name.replace("Floor", "Ceiling"),
            (size[0], 0.8, size[2]),
            (position[0], 67.4, position[2]),
            material="Concrete",
            color=CONCRETE_DARK,
            collide=True,
        )
        for name, size, position in floor_specs
    ]

    walls: list[dict[str, Any]] = [
        wall_x("EntranceWestWall", -10.0, 14.0, 38.0),
        wall_x("EntranceEastWall", 10.0, 14.0, 50.0),
        wall_z("EntranceSouthWest", 14.0, -10.0, -5.0),
        wall_z("EntranceSouthEast", 14.0, 5.0, 10.0),
        wall_z("WakeCorridorSouthWall", 38.0, -47.0, -10.0),
        wall_z("WakeCorridorNorthWall", 50.0, -35.0, -26.0),
        wall_x("WakeCorridorWestWall", -47.0, 38.0, 50.0),
        wall_x("BedroomWestWall", -62.0, 50.0, 84.0),
        wall_z("BedroomSouthWest", 50.0, -62.0, -47.0),
        wall_z("BedroomSouthEast", 50.0, -35.0, -26.0),
        wall_z("BedroomNorthWest", 84.0, -62.0, -51.0),
        wall_z("BedroomNorthEast", 84.0, -39.0, -26.0),
        wall_x("BedroomEastSouth", -26.0, 50.0, 59.0),
        wall_x("BedroomEastNorth", -26.0, 76.0, 84.0),
        wall_z("CommonsSouthWest", 50.0, -26.0, -7.0),
        wall_z("CommonsSouthEast", 50.0, 7.0, 22.0),
        wall_x("CommonsEastSouth", 22.0, 50.0, 64.0),
        wall_x("CommonsEastNorth", 22.0, 79.0, 94.0),
        wall_z("CommonsNorthWest", 94.0, -28.0, -6.0),
        wall_z("CommonsNorthEast", 94.0, 6.0, 22.0),
        wall_z("PowerSouthWall", 50.0, 22.0, 58.0),
        wall_x("PowerEastWall", 58.0, 50.0, 92.0),
        wall_z("PowerNorthWest", 92.0, 22.0, 33.0),
        wall_z("PowerNorthEast", 92.0, 47.0, 58.0),
        wall_x("WorkshopWestWall", -62.0, 84.0, 120.0),
        wall_z("WorkshopSouthWest", 84.0, -62.0, -51.0),
        wall_z("WorkshopSouthEast", 84.0, -39.0, -28.0),
        wall_x("WorkshopEastSouth", -28.0, 84.0, 98.0),
        wall_x("WorkshopEastNorth", -28.0, 112.0, 120.0),
        wall_x("UpgradeEastSouth", 8.0, 94.0, 102.0),
        wall_x("UpgradeEastNorth", 8.0, 116.0, 124.0),
        wall_z("UpgradeNorthWest", 124.0, -28.0, -12.0),
        wall_z("UpgradeNorthEast", 124.0, 0.0, 8.0),
        wall_x("ShopEastSouth", 38.0, 94.0, 101.0),
        wall_x("ShopEastNorth", 38.0, 116.0, 124.0),
        wall_z("ShopNorthWest", 124.0, 8.0, 14.0),
        wall_z("ShopNorthEast", 124.0, 24.0, 38.0),
        wall_x("StorageWestWall", -62.0, 120.0, 152.0),
        wall_z("StorageSouthWest", 120.0, -62.0, -52.0),
        wall_z("StorageSouthEast", 120.0, -40.0, -30.0),
        wall_z("StorageNorthWall", 152.0, -62.0, -30.0),
        wall_x("StorageEastSouth", -30.0, 120.0, 128.0),
        wall_x("StorageEastNorth", -30.0, 142.0, 152.0),
        wall_x("ServiceEastWall", 58.0, 124.0, 152.0),
        wall_z("ServiceNorthWest", 152.0, -30.0, 43.0),
        wall_z("ServiceNorthEast", 152.0, 53.0, 58.0),
        wall_x("PowerLinkWestWall", 30.0, 94.0, 124.0),
        wall_x("PowerLinkEastWall", 50.0, 92.0, 124.0),
    ]

    frames = [
        door_frame("ExteriorBlastPortal", (0.0, 54.0, 14.0), 10.0, wall_axis="z"),
        door_frame("EntranceCommonsPortal", (0.0, 54.0, 50.0), 14.0, wall_axis="z"),
        door_frame("BedroomWakePortal", (-41.0, 54.0, 50.0), 12.0, wall_axis="z"),
        door_frame("WakeEntrancePortal", (-10.0, 54.0, 44.0), 12.0, wall_axis="x"),
        door_frame("BedroomCommonsPortal", (-26.0, 54.0, 67.5), 17.0, wall_axis="x"),
        door_frame("BedroomWorkshopPortal", (-45.0, 54.0, 84.0), 12.0, wall_axis="z"),
        door_frame("CommonsPowerPortal", (22.0, 54.0, 71.5), 15.0, wall_axis="x"),
        door_frame("CommonsUpgradePortal", (0.0, 54.0, 94.0), 12.0, wall_axis="z"),
        door_frame("WorkshopUpgradePortal", (-28.0, 54.0, 105.0), 14.0, wall_axis="x"),
        door_frame("UpgradeShopPortal", (8.0, 54.0, 109.0), 14.0, wall_axis="x"),
        door_frame("UpgradeServicePortal", (-6.0, 54.0, 124.0), 12.0, wall_axis="z"),
        door_frame("ShopServicePortal", (19.0, 54.0, 124.0), 10.0, wall_axis="z"),
        door_frame("StorageWorkshopPortal", (-46.0, 54.0, 120.0), 12.0, wall_axis="z"),
        door_frame("StorageServicePortal", (-30.0, 54.0, 135.0), 14.0, wall_axis="x"),
        door_frame("PowerLinkSouthPortal", (40.0, 54.0, 92.0), 14.0, wall_axis="z"),
        door_frame("PowerLinkNorthPortal", (40.0, 54.0, 124.0), 12.0, wall_axis="z"),
        door_frame("FarmAccessPortal", (48.0, 54.0, 152.0), 10.0, wall_axis="z"),
    ]

    ribs = [corridor_rib(f"EntranceRib{index}", z) for index, z in enumerate((21.0, 31.0, 41.0), 1)]
    ribs.extend(
        model(
            f"ServiceRib{index}",
            [
                part("SouthPost", (0.6, 12.0, 0.6), (x, 60.4, 125.0), material="Metal", color=STEEL_LIGHT),
                part("NorthPost", (0.6, 12.0, 0.6), (x, 60.4, 151.0), material="Metal", color=STEEL_LIGHT),
                part("Crown", (0.6, 0.6, 26.0), (x, 66.2, 138.0), material="Metal", color=STEEL_LIGHT),
            ],
        )
        for index, x in enumerate((-20.0, 2.0, 25.0, 47.0), 1)
    )

    conduits = [
        cylinder_between("MainBlueConduit", (-8.7, 65.2, 18.0), (-8.7, 65.2, 48.0), 0.38, color=UTILITY_BLUE),
        cylinder_between("MainRedConduit", (8.7, 64.5, 18.0), (8.7, 64.5, 48.0), 0.28, color=EMERGENCY_RED),
        cylinder_between("ServiceWaterMain", (-25.0, 65.1, 149.0), (54.0, 65.1, 149.0), 0.48, color=UTILITY_BLUE),
        cylinder_between("ServiceReturnMain", (-25.0, 64.4, 147.8), (54.0, 64.4, 147.8), 0.34, color=RUST),
        cylinder_between("PowerFeed", (24.0, 65.0, 88.0), (56.0, 65.0, 88.0), 0.42, color=HAZARD),
    ]

    return [
        model("Floors", floors),
        model("Ceilings", ceilings),
        model("Walls", walls),
        model("Thresholds", frames),
        model("StructuralRibs", ribs),
        model("UtilityConduits", conduits),
    ]


def bed(name: str, position: Vec3, *, rotation: Vec3 = (0.0, 0.0, 0.0), collapsed: bool = False) -> dict[str, Any]:
    x, y, z = position
    tilt = (0.0, rotation[1], 7.0) if collapsed else rotation
    return model(
        name,
        [
            part("Frame", (7.4, 0.45, 3.3), (x, y, z), material="CorrodedMetal", color=RUST, collide=True, rotation=tilt),
            part("Mattress", (6.8, 0.65, 2.8), (x, y + 0.52, z), material="Fabric", color=[0.18, 0.25, 0.21], collide=True, rotation=tilt),
            part("Pillow", (1.65, 0.32, 2.35), (x - 2.35, y + 0.92, z), material="Fabric", color=[0.42, 0.42, 0.34], rotation=tilt),
            part("HeadRail", (0.4, 3.6, 3.45), (x - 3.45, y + 1.55, z), material="Metal", color=STEEL_LIGHT, rotation=tilt),
            part("FootRail", (0.4, 2.5, 3.45), (x + 3.45, y + 1.05, z), material="Metal", color=STEEL_LIGHT, rotation=tilt),
        ],
    )


def build_bedroom() -> list[dict[str, Any]]:
    return [
        bed("AwakeningBed", (-56.7, 55.0, 77.8), rotation=(0.0, 90.0, 0.0)),
        bed("CollapsedBunk", (-56.8, 55.0, 55.8), rotation=(0.0, 90.0, 0.0), collapsed=True),
        model(
            "LockerBank",
            [
                part(f"Locker{index}", (2.2, 6.8, 2.4), (-58.8, 57.8, z), material="CorrodedMetal", color=STEEL, collide=True)
                for index, z in enumerate((63.0, 67.0, 71.0), 1)
            ],
        ),
        model(
            "AbandonedShelf",
            [
                part("Back", (7.0, 5.0, 0.3), (-43.5, 57.2, 82.2), material="Metal", color=STEEL, collide=True),
                part("LowerShelf", (7.0, 0.28, 2.0), (-43.5, 55.1, 81.4), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
                part("UpperShelf", (7.0, 0.28, 2.0), (-43.5, 58.4, 81.4), material="DiamondPlate", color=STEEL_LIGHT),
                part("BlanketRoll", (3.6, 0.9, 1.0), (-44.7, 59.0, 81.1), material="Fabric", color=[0.20, 0.25, 0.19]),
            ],
        ),
        part("DampStain", (8.0, 0.025, 5.0), (-53.0, 54.39, 68.5), material="Glass", color=[0.045, 0.07, 0.055], transparency=0.58, cast_shadow=False, rotation=(0.0, 17.0, 0.0)),
        cylinder_between("CeilingPipeA", (-60.0, 65.0, 52.0), (-60.0, 65.0, 82.0), 0.48, color=RUST),
        cylinder_between("CeilingPipeB", (-58.8, 64.3, 52.0), (-58.8, 64.3, 82.0), 0.30, color=UTILITY_BLUE),
        placed_asset("BedroomVent", "bunker_vent_grille_01.model.json", (-61.3, 62.0, 66.0), (3.3, 2.8, 0.55), rotation=(0.0, 90.0, 0.0)),
        placed_asset("BedroomJunction", "bunker_electrical_junction_box_01.model.json", (-61.2, 58.4, 74.5), (2.4, 2.25, 0.9), rotation=(0.0, 90.0, 0.0)),
        sign("BedroomExitSign", "COMMONS  >", (-26.7, 63.4, 67.5), size=(0.18, 1.4, 6.5), rotation=(0.0, 90.0, 0.0), text_color=LIGHT_WARM),
    ]


def build_commons() -> list[dict[str, Any]]:
    return [
        model(
            "MessTable",
            [
                part("Top", (10.0, 0.5, 4.2), (-13.5, 57.0, 76.5), material="WoodPlanks", color=WOOD, collide=True),
                part("WestLeg", (0.7, 2.5, 3.5), (-17.2, 55.7, 76.5), material="Metal", color=STEEL, collide=True),
                part("EastLeg", (0.7, 2.5, 3.5), (-9.8, 55.7, 76.5), material="Metal", color=STEEL, collide=True),
                part("BenchNorth", (9.5, 0.5, 1.4), (-13.5, 55.6, 80.3), material="WoodPlanks", color=WOOD_DARK, collide=True),
                part("BenchSouth", (9.5, 0.5, 1.4), (-13.5, 55.6, 72.7), material="WoodPlanks", color=WOOD_DARK, collide=True),
            ],
        ),
        model(
            "NoticeWall",
            [
                part("Board", (9.0, 5.0, 0.35), (-10.0, 60.0, 93.0), material="WoodPlanks", color=WOOD_DARK),
                part("RouteCardA", (2.0, 1.2, 0.05), (-12.6, 60.8, 92.8), material="SmoothPlastic", color=OFF_WHITE),
                part("RouteCardB", (2.6, 1.5, 0.05), (-9.4, 59.1, 92.8), material="SmoothPlastic", color=DEAD_GRASS, rotation=(0.0, 0.0, -4.0)),
                part("MissingPoster", (2.0, 2.4, 0.05), (-6.6, 60.0, 92.8), material="SmoothPlastic", color=[0.44, 0.38, 0.26], rotation=(0.0, 0.0, 3.0)),
            ],
        ),
        model(
            "RecoveryCorner",
            [
                part("SofaBase", (8.0, 1.4, 3.2), (15.5, 55.1, 84.5), material="Fabric", color=[0.12, 0.22, 0.17], collide=True),
                part("SofaBack", (8.0, 3.4, 0.8), (15.5, 57.0, 85.7), material="Fabric", color=[0.10, 0.18, 0.14], collide=True),
                part("CrateTable", (3.0, 2.1, 2.7), (10.0, 55.2, 87.5), material="WoodPlanks", color=WOOD, collide=True),
            ],
        ),
        placed_asset("CommonsAmmoCrate", "old_military_ammo_crate_01.model.json", (-20.0, 55.2, 88.5), (3.8, 2.7, 2.7), rotation=(0.0, 16.0, 0.0)),
        sign("CommonsWayfinding", "EXIT     POWER     FARM", (5.0, 63.4, 93.2), size=(11.0, 1.6, 0.18), text_color=LIGHT_WARM),
        part("OldUnitMarking", (5.5, 0.025, 5.5), (13.0, 54.4, 57.0), material="SmoothPlastic", color=EMERGENCY_RED, transparency=0.45, cast_shadow=False, rotation=(0.0, 45.0, 0.0)),
    ]


def build_entrance() -> list[dict[str, Any]]:
    return [
        model(
            "OpenBlastDoor",
            [
                part("WestLeaf", (2.0, 10.5, 7.5), (-7.8, 59.6, 17.0), material="DiamondPlate", color=STEEL_LIGHT, collide=True, rotation=(0.0, -15.0, 0.0)),
                part("EastLeaf", (2.0, 10.5, 7.5), (7.8, 59.6, 17.0), material="DiamondPlate", color=STEEL_LIGHT, collide=True, rotation=(0.0, 15.0, 0.0)),
                cylinder_between("WestHinge", (-8.8, 54.8, 17.0), (-8.8, 65.0, 17.0), 0.7, color=RUST),
                cylinder_between("EastHinge", (8.8, 54.8, 17.0), (8.8, 65.0, 17.0), 0.7, color=RUST),
            ],
        ),
        model(
            "DecontaminationArch",
            [
                part("WestColumn", (1.0, 10.5, 1.5), (-7.5, 59.6, 37.0), material="Metal", color=STEEL_LIGHT),
                part("EastColumn", (1.0, 10.5, 1.5), (7.5, 59.6, 37.0), material="Metal", color=STEEL_LIGHT),
                part("Header", (16.0, 1.0, 1.5), (0.0, 65.3, 37.0), material="CorrodedMetal", color=RUST),
                cylinder_between("RecoveredWaterLine", (-7.0, 64.6, 37.0), (7.0, 64.6, 37.0), 0.34, color=UTILITY_BLUE),
            ],
        ),
        model(
            "GuardNook",
            [
                part("Desk", (5.0, 3.0, 2.4), (-6.5, 55.7, 45.0), material="Metal", color=STEEL, collide=True),
                part("WindowFrame", (5.5, 4.0, 0.3), (-6.5, 61.0, 48.8), material="CorrodedMetal", color=RUST),
                part("BrokenGlass", (4.4, 3.1, 0.05), (-6.5, 61.0, 48.6), material="Glass", color=[0.25, 0.36, 0.34], transparency=0.67),
            ],
        ),
        sign("EntranceDirection", "BUNKER 07  /  SHELTER", (0.0, 63.2, 49.2), size=(10.0, 1.5, 0.18), text_color=LIGHT_WARM),
        part("HazardBandWest", (0.5, 0.05, 29.0), (-4.0, 54.42, 32.0), material="SmoothPlastic", color=HAZARD, cast_shadow=False),
        part("HazardBandEast", (0.5, 0.05, 29.0), (4.0, 54.42, 32.0), material="SmoothPlastic", color=HAZARD, cast_shadow=False),
    ]


def build_workshop() -> list[dict[str, Any]]:
    return [
        model(
            "LongWorkbench",
            [
                part("Top", (15.0, 0.65, 4.0), (-47.0, 57.0, 111.0), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
                part("WestCabinet", (4.5, 4.2, 3.4), (-52.0, 55.9, 111.0), material="Metal", color=STEEL, collide=True),
                part("EastCabinet", (4.5, 4.2, 3.4), (-42.0, 55.9, 111.0), material="Metal", color=STEEL, collide=True),
                part("Backboard", (15.0, 5.8, 0.35), (-47.0, 60.2, 113.0), material="CorrodedMetal", color=STEEL),
                part("ToolStripe", (13.5, 0.3, 0.1), (-47.0, 60.5, 112.75), material="Neon", color=HAZARD, cast_shadow=False),
            ],
        ),
        model(
            "OverheadHoist",
            [
                part("Rail", (27.0, 0.65, 0.8), (-45.0, 64.5, 88.5), material="Metal", color=STEEL_LIGHT),
                part("Trolley", (2.4, 1.3, 2.0), (-39.0, 63.5, 88.5), material="CorrodedMetal", color=RUST),
                cylinder_between("Chain", (-39.0, 62.9, 88.5), (-39.0, 57.2, 88.5), 0.18, color=DEEP_RUST),
                part("Hook", (0.8, 1.2, 0.3), (-39.0, 56.6, 88.5), material="Metal", color=RUST, rotation=(0.0, 0.0, 25.0)),
            ],
        ),
        model(
            "ToolRack",
            [
                part("Rack", (0.5, 7.2, 9.0), (-60.5, 58.5, 102.0), material="Metal", color=STEEL),
                cylinder_between("RecoveredBar", (-60.1, 61.0, 99.0), (-60.1, 58.0, 102.0), 0.22, color=STEEL_LIGHT),
                cylinder_between("Crowbar", (-60.0, 62.5, 104.0), (-60.0, 57.5, 105.0), 0.18, color=RUST),
                part("ToolBin", (3.0, 2.5, 5.0), (-58.7, 55.4, 106.0), material="CorrodedMetal", color=STEEL, collide=True),
            ],
        ),
        placed_asset("WorkshopValve", "bunker_valve_assembly_01.model.json", (-60.7, 60.8, 91.5), (2.8, 2.0, 1.7), rotation=(0.0, 90.0, 0.0)),
        placed_asset("WorkshopCrate", "old_military_ammo_crate_01.model.json", (-34.0, 55.3, 115.5), (3.6, 2.6, 2.5), rotation=(0.0, -12.0, 0.0)),
        sign("WorkshopSign", "WORKSHOP", (-45.0, 63.5, 84.7), text_color=HAZARD),
    ]


def build_upgrades() -> list[dict[str, Any]]:
    return [
        model(
            "SalvagedResearchBench",
            [
                part("Bench", (11.0, 3.5, 3.2), (-13.0, 55.9, 117.5), material="Metal", color=STEEL, collide=True),
                part("Top", (11.5, 0.4, 3.6), (-13.0, 57.8, 117.5), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
                part("Blueprint", (3.0, 0.05, 2.0), (-15.0, 58.05, 117.0), material="SmoothPlastic", color=[0.12, 0.30, 0.38], rotation=(0.0, 8.0, 0.0)),
                part("PartsTray", (3.2, 0.5, 2.2), (-10.0, 58.2, 117.4), material="CorrodedMetal", color=RUST),
            ],
        ),
        model(
            "UpgradeCableTree",
            [
                cylinder_between("BlueFeed", (-26.5, 55.5, 114.0), (-26.5, 65.0, 114.0), 0.35, color=UTILITY_BLUE),
                cylinder_between("AmberFeed", (-25.7, 55.5, 114.0), (-25.7, 64.0, 114.0), 0.28, color=HAZARD),
                placed_asset("UpgradeJunction", "bunker_electrical_junction_box_01.model.json", (-26.2, 60.0, 113.6), (2.6, 2.45, 0.95), rotation=(0.0, 90.0, 0.0)),
            ],
        ),
        sign("UpgradeSign", "UPGRADES", (-10.0, 63.5, 123.2), text_color=UTILITY_BLUE),
    ]


def build_shop() -> list[dict[str, Any]]:
    shelf_children: list[dict[str, Any]] = []
    for index, x in enumerate((13.0, 19.0, 25.0, 31.0), 1):
        shelf_children.extend(
            [
                part(f"Post{index}A", (0.4, 7.0, 0.4), (x, 57.7, 119.5), material="Metal", color=STEEL),
                part(f"Shelf{index}Low", (5.4, 0.28, 2.4), (x + 2.5, 56.0, 119.5), material="DiamondPlate", color=STEEL_LIGHT),
                part(f"Shelf{index}High", (5.4, 0.28, 2.4), (x + 2.5, 59.8, 119.5), material="DiamondPlate", color=STEEL_LIGHT),
            ]
        )
    return [
        model(
            "CagedCounter",
            [
                part("Counter", (18.0, 3.4, 3.2), (23.0, 55.9, 112.5), material="CorrodedMetal", color=STEEL, collide=True),
                part("CounterTop", (18.5, 0.4, 3.6), (23.0, 57.8, 112.5), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
                part("SecurityMesh", (18.0, 7.5, 0.2), (23.0, 61.0, 114.2), material="Metal", color=[0.19, 0.21, 0.20]),
                part("PassThrough", (5.0, 2.8, 0.28), (17.0, 58.8, 114.0), material="Glass", color=[0.20, 0.31, 0.29], transparency=0.8),
            ],
        ),
        model("SupplyShelving", shelf_children),
        placed_asset("ShopRationCrate", "old_military_ammo_crate_01.model.json", (31.5, 55.5, 99.0), (4.0, 2.8, 2.8), rotation=(0.0, -8.0, 0.0)),
        sign("ShopSign", "QUARTERMASTER", (23.0, 64.0, 123.1), size=(10.0, 1.6, 0.18), text_color=LIGHT_WARM),
    ]


def build_storage() -> list[dict[str, Any]]:
    rack_children: list[dict[str, Any]] = []
    for index, z in enumerate((124.5, 137.5, 147.0), 1):
        rack_children.extend(
            [
                part(f"Rack{index}Back", (0.5, 7.0, 8.0), (-59.5, 57.8, z), material="Metal", color=STEEL),
                part(f"Rack{index}Lower", (4.0, 0.35, 7.6), (-57.6, 55.4, z), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
                part(f"Rack{index}Upper", (4.0, 0.35, 7.6), (-57.6, 59.2, z), material="DiamondPlate", color=STEEL_LIGHT),
            ]
        )
    return [
        model("WallRacks", rack_children),
        model(
            "SortedSupplies",
            [
                part("WoodBin", (4.2, 3.0, 4.2), (-37.0, 55.7, 146.0), material="WoodPlanks", color=WOOD, collide=True),
                part("MetalBin", (4.2, 3.0, 4.2), (-42.0, 55.7, 146.0), material="CorrodedMetal", color=STEEL, collide=True),
                part("RationBin", (4.2, 3.0, 4.2), (-47.0, 55.7, 146.0), material="Metal", color=UTILITY_GREEN, collide=True),
                part("FloorManifest", (8.0, 0.04, 3.0), (-39.5, 54.4, 122.5), material="SmoothPlastic", color=HAZARD, transparency=0.55, cast_shadow=False),
            ],
        ),
        placed_asset("StorageCrateA", "old_military_ammo_crate_01.model.json", (-34.5, 55.4, 130.0), (3.8, 2.7, 2.7), rotation=(0.0, 10.0, 0.0)),
        placed_asset("StorageVent", "bunker_vent_grille_01.model.json", (-61.2, 62.0, 137.0), (3.2, 2.7, 0.55), rotation=(0.0, 90.0, 0.0)),
        sign("StorageSign", "STORAGE", (-46.0, 63.6, 151.2), text_color=UTILITY_GREEN),
    ]


def build_power() -> list[dict[str, Any]]:
    return [
        model(
            "RecoveredGenerator",
            [
                part("Skid", (14.0, 0.6, 8.0), (47.0, 54.7, 77.5), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
                part("EngineBlock", (9.0, 5.5, 5.5), (47.0, 57.7, 77.5), material="CorrodedMetal", color=STEEL, collide=True),
                cylinder_between("Alternator", (42.0, 58.0, 77.5), (52.0, 58.0, 77.5), 3.6, material="Metal", color=[0.18, 0.24, 0.21]),
                part("InspectionPanel", (4.5, 2.2, 0.25), (47.0, 58.7, 74.7), material="Metal", color=UTILITY_GREEN),
                part("WarningStripe", (8.0, 0.18, 0.08), (47.0, 60.0, 74.55), material="Neon", color=HAZARD, cast_shadow=False),
            ],
        ),
        model(
            "FuelAndCooling",
            [
                cylinder_between("TankA", (54.5, 54.5, 55.5), (54.5, 64.0, 55.5), 3.4, material="CorrodedMetal", color=STEEL),
                cylinder_between("TankB", (49.5, 54.5, 55.5), (49.5, 64.0, 55.5), 3.4, material="CorrodedMetal", color=STEEL),
                cylinder_between("CoolantHeader", (24.0, 63.7, 52.0), (55.0, 63.7, 52.0), 0.48, color=UTILITY_BLUE),
                cylinder_between("Exhaust", (52.0, 61.0, 81.0), (52.0, 68.0, 81.0), 0.7, color=RUST),
            ],
        ),
        model(
            "SwitchgearWall",
            [
                part("CabinetA", (5.0, 8.0, 2.0), (27.0, 58.3, 86.8), material="Metal", color=STEEL, collide=True),
                part("CabinetB", (5.0, 8.0, 2.0), (33.0, 58.3, 86.8), material="Metal", color=STEEL, collide=True),
                part("CabinetC", (5.0, 8.0, 2.0), (39.0, 58.3, 86.8), material="Metal", color=STEEL, collide=True),
                placed_asset("PowerJunction", "bunker_electrical_junction_box_01.model.json", (45.0, 59.2, 86.3), (2.7, 2.55, 0.98)),
                placed_asset("PowerValve", "bunker_valve_assembly_01.model.json", (56.2, 58.5, 68.0), (2.9, 2.0, 1.75), rotation=(0.0, -90.0, 0.0)),
            ],
        ),
        sign("PowerSign", "POWER / GENERATOR", (40.0, 63.6, 91.2), size=(9.0, 1.5, 0.18), text_color=HAZARD),
    ]


def build_service_route() -> list[dict[str, Any]]:
    return [
        model(
            "ServicePipeRack",
            [
                cylinder_between("RecoveredWater", (-27.0, 62.7, 127.0), (55.0, 62.7, 127.0), 0.46, color=UTILITY_BLUE),
                cylinder_between("FuelReturn", (-27.0, 61.6, 128.0), (55.0, 61.6, 128.0), 0.34, color=RUST),
                cylinder_between("ElectricalBus", (-27.0, 64.0, 129.0), (55.0, 64.0, 129.0), 0.28, color=HAZARD),
                placed_asset("ServiceValve", "bunker_valve_assembly_01.model.json", (29.0, 62.0, 127.0), (2.8, 1.95, 1.7), rotation=(0.0, 0.0, 90.0)),
                placed_asset("ServiceJunction", "bunker_electrical_junction_box_01.model.json", (2.0, 59.0, 126.2), (2.5, 2.35, 0.92)),
            ],
        ),
        model(
            "MaintenanceCart",
            [
                part("Deck", (6.0, 0.55, 3.5), (41.0, 55.2, 144.5), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
                part("Crate", (3.5, 2.5, 2.8), (40.0, 56.7, 144.5), material="WoodPlanks", color=WOOD),
                cylinder_between("Handle", (43.5, 55.5, 143.3), (45.0, 59.0, 143.3), 0.25, color=STEEL_LIGHT),
                cylinder_between("WheelA", (38.5, 54.5, 143.1), (38.5, 54.5, 145.9), 0.8, material="Rubber", color=[0.055, 0.06, 0.055]),
                cylinder_between("WheelB", (43.5, 54.5, 143.1), (43.5, 54.5, 145.9), 0.8, material="Rubber", color=[0.055, 0.06, 0.055]),
            ],
        ),
        model(
            "DrainageStory",
            [
                part("WetSheen", (28.0, 0.025, 4.5), (18.0, 54.42, 147.2), material="Glass", color=[0.04, 0.075, 0.065], transparency=0.66, cast_shadow=False),
                part("RustRunoff", (12.0, 0.03, 2.0), (-18.0, 54.42, 146.0), material="Glass", color=DEEP_RUST, transparency=0.5, cast_shadow=False, rotation=(0.0, -8.0, 0.0)),
                part("BrokenGrate", (5.5, 0.18, 1.2), (-24.0, 54.55, 145.0), material="DiamondPlate", color=RUST, rotation=(0.0, 6.0, 0.0)),
            ],
        ),
        sign("FarmAccessSign", "FARM ACCESS  >", (47.8, 63.5, 151.2), size=(8.0, 1.5, 0.18), text_color=UTILITY_GREEN),
    ]


def build_station(
    interaction_id: str,
    kind: str,
    position: Vec3,
    *,
    label: str,
    action: str,
    accent: Sequence[float],
    upgrade_id: str | None = None,
) -> dict[str, Any]:
    x, y, z = position
    attributes: dict[str, Any] = {"InteractionId": interaction_id, "InteractionKind": kind}
    if upgrade_id:
        attributes["UpgradeId"] = upgrade_id
    return model(
        interaction_id,
        [
            interaction_anchor(position, prompt(f"{interaction_id}_prompt", action, label, distance=9.0)),
            part("Foot", (4.6, 0.45, 2.8), (x, 54.45, z + 0.9), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
            part("ConsoleBody", (4.2, 4.5, 1.6), (x, y, z + 0.85), material="CorrodedMetal", color=STEEL, collide=True),
            part("ControlFace", (3.3, 2.0, 0.18), (x, y + 0.25, z - 0.02), material="SmoothPlastic", color=[0.055, 0.075, 0.07]),
            part("StatusBar", (2.7, 0.22, 0.08), (x, y + 1.15, z - 0.13), material="Neon", color=accent, cast_shadow=False, attributes={"PowerIndicator": True}),
            sign("StationLabel", label, (x, y + 2.7, z + 0.02), size=(4.4, 0.9, 0.15), text_color=accent),
        ],
        attributes=attributes,
        pivot=position,
    )


def build_stations() -> list[dict[str, Any]]:
    return [
        build_station("power_console", "power", (34.0, 56.5, 71.0), label="BUNKER POWER", action="RESTORE POWER", accent=HAZARD),
        build_station("shop_terminal", "shop", (17.0, 56.5, 108.0), label="QUARTERMASTER", action="OPEN SHOP", accent=LIGHT_WARM),
        build_station("personal_storage", "storage", (-48.0, 56.5, 126.0), label="PERSONAL STORAGE", action="OPEN STORAGE", accent=UTILITY_GREEN),
        build_station("scrap_exchange", "scrap_exchange", (10.0, 56.5, 138.0), label="SCRAP EXCHANGE", action="EXCHANGE SCRAP", accent=RUST),
        build_station("harvest_upgrade", "upgrade", (-8.0, 56.5, 104.0), label="HARVEST UPGRADE", action="VIEW UPGRADE", accent=UTILITY_GREEN, upgrade_id="harvest"),
        build_station("weapon_upgrade", "upgrade", (-48.0, 56.5, 96.0), label="WEAPON UPGRADE", action="VIEW UPGRADE", accent=EMERGENCY_RED, upgrade_id="weapon"),
        build_station("storage_upgrade", "upgrade", (-48.0, 56.5, 132.0), label="STORAGE UPGRADE", action="VIEW UPGRADE", accent=UTILITY_BLUE, upgrade_id="storage"),
    ]


def build_spawns() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for spawn_id, slot, position in SPAWNS:
        result.append(
            part(
                spawn_id,
                (5.0, 1.0, 5.0),
                position,
                class_name="SpawnLocation",
                material="SmoothPlastic",
                color=UTILITY_GREEN,
                transparency=1.0,
                cast_shadow=False,
                rotation=(0.0, 0.0, 0.0),
                attributes={"SpawnId": spawn_id, "SpawnRole": "bedroom", "SlotIndex": slot},
                extra_properties={
                    "Neutral": True,
                    "AllowTeamChangeOnTouch": False,
                    "Duration": 0.0,
                    "Enabled": True,
                },
            )
        )
    return result


def build_bunker_lights() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    main_specs = (
        ("BedroomMain", (-44.0, 66.75, 67.0), LIGHT_COOL, 1.0, 17.0, True),
        ("CommonsMain", (-3.0, 66.75, 71.0), LIGHT_WARM, 1.05, 18.0, True),
        ("EntranceMain", (0.0, 66.75, 34.0), LIGHT_WARM, 1.15, 17.0, True),
        ("PowerMain", (39.0, 66.75, 71.0), LIGHT_WARM, 0.92, 16.0, False),
        ("WorkshopMain", (-45.0, 66.75, 102.0), LIGHT_COOL, 0.9, 16.0, False),
        ("ServiceWest", (-9.0, 66.75, 138.0), LIGHT_COOL, 0.8, 16.0, True),
    )
    main = [
        fixture(name, position, color, brightness, light_range, shadows=shadows)
        for name, position, color, brightness, light_range, shadows in main_specs
    ]
    emergency = [
        emergency_lamp("BedroomEmergency", (-43.0, 62.0, 67.0)),
        emergency_lamp("EntranceEmergency", (9.3, 62.0, 19.0)),
        emergency_lamp("CommandEmergency", (-4.5, 62.5, 47.0), color=HAZARD),
        emergency_lamp("CommonsEmergency", (-2.0, 63.0, 78.0), color=LIGHT_COOL),
        emergency_lamp("PowerEmergency", (36.0, 62.0, 71.0)),
        emergency_lamp("WorkshopEmergency", (-46.0, 63.0, 102.0), color=HAZARD),
        emergency_lamp("StorageEmergency", (-46.0, 63.0, 138.0), color=UTILITY_GREEN),
        emergency_lamp("FarmExitEmergency", (55.0, 62.0, 151.2), color=LIGHT_WARM),
    ]
    return main, emergency


def build_director_rework() -> list[dict[str, Any]]:
    """Dense, readable environmental storytelling for the Director-approved rework.

    These bays preserve all frozen gameplay anchors while making the existing
    circulation spine read as a three-tier facility: threshold/command,
    habitation/logistics, and underbelly/storage.
    """
    return [
        model("Level1_CommandDecon", [
            # The leaf is visibly jammed open above the exterior threshold; it
            # must never obstruct the frozen 10-stud entrance route.
            cylinder_between("HydraulicWest", (-8.0, 55.2, 21.0), (-8.0, 63.0, 19.0), 0.42, color=STEEL_LIGHT),
            cylinder_between("HydraulicEast", (8.0, 55.2, 21.0), (8.0, 63.0, 19.0), 0.42, color=STEEL_LIGHT),
            part("DeconNozzleRail", (15.0, 0.35, 0.5), (0.0, 65.0, 37.0), material="Metal", color=STEEL_LIGHT),
            *[cylinder_between(f"DeadNozzle{index}", (x, 64.8, 37.0), (x, 63.7, 37.0), 0.18, color=RUST) for index, x in enumerate((-6.0, -2.0, 2.0, 6.0), 1)],
            part("CommandGlass", (8.0, 4.8, 0.25), (-5.5, 61.0, 48.55), material="Glass", color=[0.18, 0.32, 0.32], transparency=0.48),
            *[part(f"CRT{index}", (1.5, 1.2, 0.25), (-8.5 + index * 1.55, 59.5, 45.6), material="Neon", color=UTILITY_BLUE, cast_shadow=False, attributes={"PowerIndicator": True}) for index in range(5)],
            part("LockdownLever", (0.55, 3.4, 0.55), (6.8, 57.2, 45.5), material="Metal", color=EMERGENCY_RED, rotation=(0.0, 0.0, -28.0)),
            sign("Level1Sign", "LEVEL 1 // DECON + COMMAND", (0.0, 65.7, 48.9), size=(12.0, 1.2, 0.15), text_color=HAZARD),
        ]),
        model("Level2_RottingHeart", [
            model("MedicalBay", [
                part("GurneyA", (6.0, 1.1, 2.4), (-20.0, 56.0, 57.0), material="Metal", color=STEEL, collide=True),
                part("GurneyB", (6.0, 1.1, 2.4), (-20.0, 56.0, 63.0), material="Metal", color=RUST, collide=True),
                part("QuarantineGlass", (5.5, 5.2, 0.2), (-20.0, 60.0, 67.0), material="Glass", color=[0.18, 0.30, 0.26], transparency=0.45),
                *[part(f"Scratch{index}", (0.12, 1.4, 0.05), (-21.5 + index * 0.45, 60.0, 66.85), material="Neon", color=EMERGENCY_RED, cast_shadow=False, rotation=(0.0, 0.0, -18.0)) for index in range(6)],
            ]),
            model("Armory", [
                part("VaultLeaf", (8.0, 10.0, 1.0), (-56.0, 60.0, 88.0), material="CorrodedMetal", color=STEEL_LIGHT, collide=True, rotation=(0.0, 18.0, 0.0)),
                part("GunRack", (0.45, 5.5, 8.0), (-60.8, 60.0, 94.0), material="Metal", color=STEEL),
                *[cylinder_between(f"EmptyRack{index}", (-60.45, 62.0 - index * 0.8, 91.0), (-60.45, 62.0 - index * 0.8, 97.0), 0.12, color=STEEL_LIGHT) for index in range(4)],
                part("CasingSpill", (3.0, 0.04, 1.4), (-53.0, 54.43, 91.0), material="Foil", color=HAZARD, cast_shadow=False),
            ]),
            model("MessHall", [
                part("BarricadeTable", (11.0, 0.55, 3.2), (-4.0, 57.6, 82.0), material="Metal", color=STEEL_LIGHT, collide=True, rotation=(0.0, 0.0, 72.0)),
                part("CheckeredSpill", (9.0, 0.03, 6.0), (-8.0, 54.4, 87.0), material="Glass", color=DEEP_RUST, transparency=0.35, cast_shadow=False),
                part("MoldCeiling", (10.0, 0.08, 3.0), (-16.0, 66.9, 89.0), material="Grass", color=SAGE_DARK),
            ]),
            sign("Level2Sign", "LEVEL 2 // QUARTERS + ARMORY", (-3.0, 65.7, 93.1), size=(14.0, 1.2, 0.15), text_color=LIGHT_COOL),
        ]),
        model("Level3_Underbelly", [
            model("WaterSanitation", [
                cylinder_between("FilterTankA", (53.0, 54.6, 108.0), (53.0, 64.5, 108.0), 3.1, material="CorrodedMetal", color=STEEL),
                cylinder_between("FilterTankB", (45.5, 54.6, 108.0), (45.5, 64.5, 108.0), 3.1, material="CorrodedMetal", color=STEEL),
                part("ToxicPuddle", (13.0, 0.035, 8.0), (48.0, 54.42, 115.0), material="Glass", color=UTILITY_GREEN, transparency=0.38, cast_shadow=False),
            ]),
            model("DeepStorage", [
                *[part(f"TallRack{index}", (1.0, 10.5, 6.0), (-57.0 + index * 5.4, 59.5, 145.0), material="Metal", color=STEEL, collide=True) for index in range(4)],
                *[part(f"Tarp{index}", (4.0, 4.5, 0.16), (-56.0 + index * 5.4, 59.5, 148.0), material="Fabric", color=[0.13, 0.20, 0.17]) for index in range(4)],
            ]),
            sign("Level3Sign", "LEVEL 3 // WATER + DEEP STORAGE", (13.0, 65.7, 151.1), size=(16.0, 1.2, 0.15), text_color=UTILITY_GREEN),
        ]),
    ]


def build_bunker() -> dict[str, Any]:
    main_lights, emergency_lights = build_bunker_lights()
    return model(
        "Bunker",
        [
            model("Architecture", build_architecture()),
            model("Bedroom", build_bedroom()),
            model("Commons", build_commons()),
            model("Entrance", build_entrance()),
            model("Workshop", build_workshop()),
            model("Upgrades", build_upgrades()),
            model("Shop", build_shop()),
            model("Storage", build_storage()),
            model("Power", build_power()),
            model("ServiceRoute", build_service_route()),
			model("DirectorRework", build_director_rework()),
            model("Spawns", build_spawns()),
            model("Stations", build_stations()),
            model("PoweredLights", main_lights, attributes={"CircuitKind": "main", "RequiresPower": True}),
            model("EmergencyLights", emergency_lights, attributes={"CircuitKind": "backup"}),
            part(
                "SpawnSafeZone",
                (37.0, 18.0, 32.0),
                (-43.5, 61.0, 66.0),
                transparency=1.0,
                cast_shadow=False,
                attributes={"ZoneKind": "spawn_safe", "ProtectionSeconds": 10},
            ),
        ],
        attributes={"FacilityId": "outskirts_bunker", "FacilityVersion": "FG-GREENFIELD-001"},
    )


def path_segment(name: str, start: tuple[float, float], finish: tuple[float, float], width: float, *, material: str, color: Sequence[float], thickness: float = 0.14) -> dict[str, Any]:
    dx, dz = finish[0] - start[0], finish[1] - start[1]
    length = math.hypot(dx, dz)
    yaw = math.degrees(math.atan2(dx, dz))
    midpoint = ((start[0] + finish[0]) / 2.0, 54.0 + thickness / 2.0, (start[1] + finish[1]) / 2.0)
    return part(name, (width, thickness, length), midpoint, material=material, color=color, rotation=(0.0, yaw, 0.0), cast_shadow=False)


def rock_cluster(name: str, x: float, z: float, scale: float, heading: float) -> dict[str, Any]:
    return model(
        name,
        [
            part("Core", (7.0 * scale, 3.1 * scale, 5.0 * scale), (x, 54.8 + scale, z), material="Slate", color=ROCK, rotation=(0.0, heading, 6.0)),
            part("ShoulderA", (4.5 * scale, 2.2 * scale, 3.7 * scale), (x - 3.4 * scale, 54.5 + 0.6 * scale, z + 1.8 * scale), material="Rock", color=ROCK_DARK, rotation=(0.0, heading + 23.0, -5.0)),
            part("ShoulderB", (3.8 * scale, 1.7 * scale, 4.2 * scale), (x + 3.3 * scale, 54.4 + 0.45 * scale, z - 1.4 * scale), material="Rock", color=[0.22, 0.26, 0.21], rotation=(0.0, heading - 17.0, 4.0)),
        ],
    )


def dead_snag(name: str, x: float, z: float, height: float, heading: float) -> dict[str, Any]:
    lean_x = math.sin(math.radians(heading)) * 1.4
    lean_z = math.cos(math.radians(heading)) * 1.4
    return model(
        name,
        [
            cylinder_between("Trunk", (x, 54.0, z), (x + lean_x, 54.0 + height, z + lean_z), 1.3, material="Wood", color=WOOD_DARK),
            cylinder_between("BrokenBranch", (x + lean_x * 0.55, 54.0 + height * 0.55, z + lean_z * 0.55), (x + lean_x * 0.55 + 3.5, 54.0 + height * 0.72, z + lean_z * 0.55 - 1.5), 0.48, material="Wood", color=WOOD_DARK),
        ],
    )


def build_paths() -> list[dict[str, Any]]:
    return [
        path_segment("SouthApproachA", (0.0, -210.0), (-50.0, -140.0), 14.0, material="Asphalt", color=[0.16, 0.17, 0.16], thickness=0.18),
        path_segment("SouthApproachB", (-50.0, -140.0), (-38.0, -70.0), 13.0, material="Asphalt", color=[0.15, 0.16, 0.15], thickness=0.18),
        path_segment("SouthApproachC", (-38.0, -70.0), (-18.0, -20.0), 13.0, material="Asphalt", color=[0.16, 0.17, 0.16], thickness=0.18),
        path_segment("EntranceApron", (-8.0, -22.0), (0.0, 24.0), 18.0, material="Pebble", color=[0.25, 0.25, 0.21]),
        path_segment("WestForestTrailA", (-4.0, -35.0), (-80.0, -5.0), 10.0, material="Ground", color=MUD),
        path_segment("WestForestTrailB", (-80.0, -5.0), (-155.0, 62.0), 9.0, material="Ground", color=EARTH_DARK),
        path_segment("WestRidgeTrail", (-155.0, 62.0), (-190.0, 132.0), 8.0, material="Ground", color=MUD),
        path_segment("EastForestTrailA", (4.0, -30.0), (105.0, 0.0), 10.0, material="Ground", color=MUD),
        path_segment("EastForestTrailB", (105.0, 0.0), (190.0, 80.0), 9.0, material="Ground", color=EARTH_DARK),
        path_segment("EastRidgeTrail", (190.0, 80.0), (225.0, 190.0), 8.0, material="Ground", color=MUD),
        path_segment("SalvageWestBranch", (0.0, -122.0), (-90.0, -150.0), 9.0, material="Pebble", color=[0.22, 0.21, 0.18]),
        path_segment("SalvageEastBranch", (0.0, -122.0), (85.0, -155.0), 9.0, material="Pebble", color=[0.22, 0.21, 0.18]),
        path_segment("FarmAccessA", (48.0, 152.0), (52.0, 170.0), 12.0, material="Concrete", color=CONCRETE_WORN),
        path_segment("FarmAccessB", (52.0, 170.0), (70.0, 192.0), 12.0, material="Pebble", color=[0.25, 0.25, 0.21]),
        path_segment("FarmServiceLane", (70.0, 192.0), (119.0, 210.0), 10.0, material="Pebble", color=[0.23, 0.235, 0.20]),
        part("RoadWashoutA", (12.0, 0.05, 8.0), (-3.0, 54.12, -74.0), material="Ground", color=MUD, rotation=(0.0, 14.0, 0.0), cast_shadow=False),
        part("RoadWashoutB", (10.0, 0.05, 13.0), (4.0, 54.12, -163.0), material="Ground", color=EARTH_DARK, rotation=(0.0, -11.0, 0.0), cast_shadow=False),
    ]


def build_landmarks() -> list[dict[str, Any]]:
    checkpoint = model(
        "AbandonedCheckpoint",
        [
            part("WestPillar", (3.0, 12.0, 3.0), (-32.0, 60.0, -180.0), material="Concrete", color=CONCRETE_WORN, collide=True),
            part("EastPillar", (3.0, 12.0, 3.0), (-18.0, 60.0, -180.0), material="Concrete", color=CONCRETE_WORN, collide=True),
            part("BrokenHeader", (14.0, 1.2, 2.0), (-25.0, 66.0, -180.0), material="CorrodedMetal", color=RUST, rotation=(0.0, 0.0, -3.0)),
            part("GuardShelter", (8.0, 7.0, 9.0), (-38.0, 57.5, -173.0), material="Concrete", color=CONCRETE, collide=True),
            part("ShelterRoof", (9.0, 0.7, 10.0), (-38.0, 61.4, -173.0), material="CorrodedMetal", color=STEEL_LIGHT, collide=True, rotation=(0.0, 0.0, -5.0)),
            sign("CheckpointSign", "QUARANTINE LINE", (-25.0, 63.0, -178.9), size=(12.0, 1.8, 0.2), text_color=EMERGENCY_RED),
        ],
    )
    water_tower = model(
        "EastWaterTower",
        [
            cylinder_between("Tank", (114.0, 76.0, -55.0), (114.0, 84.0, -55.0), 10.0, material="CorrodedMetal", color=STEEL_LIGHT),
            cylinder_between("LegNW", (109.5, 54.0, -59.5), (111.0, 76.0, -58.0), 0.8, color=RUST),
            cylinder_between("LegNE", (118.5, 54.0, -59.5), (117.0, 76.0, -58.0), 0.8, color=RUST),
            cylinder_between("LegSW", (109.5, 54.0, -50.5), (111.0, 76.0, -52.0), 0.8, color=RUST),
            cylinder_between("LegSE", (118.5, 54.0, -50.5), (117.0, 76.0, -52.0), 0.8, color=RUST),
            cylinder_between("FeedPipe", (114.0, 54.0, -55.0), (114.0, 76.0, -55.0), 0.55, color=UTILITY_BLUE),
            part("TowerMark", (5.0, 2.0, 0.15), (114.0, 80.0, -60.0), material="SmoothPlastic", color=OFF_WHITE),
        ],
    )
    radio_mast = model(
        "WestEmergencyMast",
        [
            cylinder_between("Mast", (-74.0, 54.0, -112.0), (-74.0, 92.0, -112.0), 0.75, color=STEEL_LIGHT),
            cylinder_between("BraceA", (-81.0, 54.0, -119.0), (-74.0, 82.0, -112.0), 0.32, color=RUST),
            cylinder_between("BraceB", (-67.0, 54.0, -119.0), (-74.0, 82.0, -112.0), 0.32, color=RUST),
            cylinder_between("BraceC", (-74.0, 54.0, -102.0), (-74.0, 82.0, -112.0), 0.32, color=RUST),
            part("Array", (12.0, 0.35, 0.35), (-74.0, 87.0, -112.0), material="Metal", color=STEEL_LIGHT, rotation=(0.0, 18.0, 0.0)),
            part("BeaconHousing", (1.4, 1.4, 1.4), (-74.0, 93.0, -112.0), material="CorrodedMetal", color=RUST),
        ],
    )
    west_watch = model(
        "WestFireLookout",
        [
            part("Platform", (13.0, 0.8, 13.0), (-225.0, 75.0, 172.0), material="WoodPlanks", color=WOOD_DARK, collide=True),
            part("Cabin", (9.0, 7.0, 9.0), (-225.0, 78.8, 172.0), material="WoodPlanks", color=WOOD, collide=True),
            part("Roof", (12.0, 0.8, 12.0), (-225.0, 82.8, 172.0), material="CorrodedMetal", color=RUST, rotation=(0.0, 8.0, 0.0)),
            cylinder_between("LegNW", (-230.0, 54.0, 167.0), (-230.0, 74.5, 167.0), 0.8, material="Wood", color=WOOD_DARK),
            cylinder_between("LegNE", (-220.0, 54.0, 167.0), (-220.0, 74.5, 167.0), 0.8, material="Wood", color=WOOD_DARK),
            cylinder_between("LegSW", (-230.0, 54.0, 177.0), (-230.0, 74.5, 177.0), 0.8, material="Wood", color=WOOD_DARK),
            cylinder_between("LegSE", (-220.0, 54.0, 177.0), (-220.0, 74.5, 177.0), 0.8, material="Wood", color=WOOD_DARK),
            cylinder_between("CrossBraceA", (-230.0, 55.0, 167.0), (-220.0, 73.0, 177.0), 0.4, material="Wood", color=WOOD_DARK),
            cylinder_between("CrossBraceB", (-220.0, 55.0, 167.0), (-230.0, 73.0, 177.0), 0.4, material="Wood", color=WOOD_DARK),
        ],
    )
    farm_gate = model(
        "FarmGateLandmark",
        [
            part("WestGatePost", (1.4, 8.0, 1.4), (45.0, 58.0, 155.0), material="CorrodedMetal", color=RUST, collide=True),
            part("EastGatePost", (1.4, 8.0, 1.4), (59.0, 58.0, 155.0), material="CorrodedMetal", color=RUST, collide=True),
            part("GateHeader", (15.4, 0.8, 1.4), (52.0, 62.2, 155.0), material="Metal", color=STEEL_LIGHT),
            sign("FarmGateSign", "RECOVERY FARM", (52.0, 60.8, 154.2), size=(8.0, 1.5, 0.18), text_color=UTILITY_GREEN),
        ],
    )
    entrance_earthworks = model(
        "BunkerEntranceEarthworks",
        [
            part("WestShoulder", (30.0, 8.0, 30.0), (-22.0, 58.0, 35.0), material="Ground", color=EARTH, rotation=(0.0, 8.0, -3.0)),
            part("WestShoulderLow", (25.0, 4.0, 25.0), (-20.0, 56.0, 15.0), material="Ground", color=MUD, rotation=(0.0, 5.0, -2.0)),
            part("EastShoulder", (22.0, 5.0, 22.0), (18.0, 56.5, 32.0), material="Ground", color=EARTH, rotation=(0.0, -6.0, 2.0)),
            part("PortalCrown", (20.0, 3.0, 6.0), (0.0, 65.5, 16.0), material="Concrete", color=CONCRETE_WORN, collide=True),
            part("WestButtress", (4.0, 10.0, 6.0), (-10.0, 59.0, 16.0), material="Concrete", color=CONCRETE_WORN, collide=True, rotation=(0.0, -3.0, 0.0)),
            part("EastButtress", (4.0, 10.0, 6.0), (10.0, 59.0, 16.0), material="Concrete", color=CONCRETE_WORN, collide=True, rotation=(0.0, 3.0, 0.0)),
            sign("EntranceTitle", "OUTPOST 07", (0.0, 64.0, 14.8), size=(12.0, 2.0, 0.2), text_color=LIGHT_WARM),
        ],
    )
    return [checkpoint, water_tower, radio_mast, west_watch, farm_gate, entrance_earthworks]


def build_forest_dressing() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, (x, _, z) in enumerate(TREE_POSITIONS, 1):
        offset_x = ((index * 17) % 13) - 6
        offset_z = ((index * 11) % 15) - 7
        result.append(rock_cluster(f"TreeEdgeRock{index:02d}", x + offset_x, z + offset_z, 0.38 + (index % 3) * 0.08, index * 19.0))
        result.append(
            part(
                f"ForestFloorPatch{index:02d}",
                (15.0 + index % 4 * 2.0, 0.05, 11.0 + index % 3 * 2.0),
                (x - offset_x * 0.4, 54.035, z - offset_z * 0.4),
                material="LeafyGrass",
                color=SAGE_DARK if index % 2 else EARTH,
                rotation=(0.0, index * 23.0, 0.0),
                cast_shadow=False,
            )
        )
        result.append(
            part(
                f"DeadBrush{index:02d}",
                (6.0 + index % 3, 0.35, 4.5 + index % 2),
                (x + offset_x * 0.6, 54.18, z - offset_z * 0.55),
                material="Grass",
                color=DEAD_GRASS,
                rotation=(0.0, index * 31.0, 0.0),
            )
        )
    snag_specs = (
        (-83.0, 28.0, 10.0, 20.0),
        (-205.0, 35.0, 13.0, -22.0),
        (-175.0, -15.0, 9.0, 35.0),
        (-225.0, 105.0, 11.0, -18.0),
        (130.0, 25.0, 12.0, 21.0),
        (265.0, 65.0, 14.0, -29.0),
        (140.0, 125.0, 10.0, 31.0),
        (275.0, 175.0, 13.0, -12.0),
    )
    result.extend(dead_snag(f"DeadSnag{index:02d}", x, z, height, heading) for index, (x, z, height, heading) in enumerate(snag_specs, 1))
    return result


def build_terrain_shelf() -> dict[str, Any]:
    """Coherent bunker hill embedding facility in hillside -- Iteration 05.

    Design principles:
      - Front apron slopes cover the Y54-67 wall volume flanking the entrance.
      - Side skirts cover full bunker side-wall volume Z=25..165.
      - HillCap covers roof. All pieces overlap to eliminate dark seams.
      - All terrain collidable; route corridor and portal gap clear.
      - Read as 'cut entrance in a hill', not 'portal on a black wall'.
    """
    # -- Central hill cap: covers bunker roof, slope faces south --
    # South edge (Z=25): thin -> Y=67 (meets roof). North edge (Z=155): thick -> Y=73.
    hill_cap = part(
        "HillCap", (140.0, 6.0, 130.0), (0.0, 70.0, 90.0),
        material="Ground", color=EARTH, collide=True,
        class_name="WedgePart", rotation=(0.0, 0.0, 0.0),
    )
    # -- West front apron: covers front wall left of entrance --
    # Thin at Z=14 (portal line, Y=54), thick at Z=65 (Y=69). X=-75..-12.
    # Slope faces south (toward player approach). Overlaps HillCap at back.
    west_front_apron = part(
        "WestFrontApron", (63.0, 15.0, 51.0), (-43.5, 61.5, 39.5),
        material="Ground", color=EARTH, collide=True,
        class_name="WedgePart", rotation=(0.0, 0.0, 0.0),
    )
    # -- East front apron: covers front wall right of entrance --
    # Same logic, X=12..75.
    east_front_apron = part(
        "EastFrontApron", (63.0, 15.0, 51.0), (43.5, 61.5, 39.5),
        material="Ground", color=EARTH, collide=True,
        class_name="WedgePart", rotation=(0.0, 0.0, 0.0),
    )
    # -- West side skirt: covers bunker west wall Z=25..165 --
    # Rotation (0, 90, 0): slope faces west, thick edge at east (near bunker wall).
    # Camera-facing outer edge (X=-108) is thin/grounded.
    west_side_skirt = part(
        "WestSideSkirt", (50.0, 18.0, 140.0), (-83.0, 63.0, 95.0),
        material="Ground", color=EARTH_DARK, collide=True,
        class_name="WedgePart", rotation=(0.0, 90.0, 0.0),
    )
    # -- East side skirt: covers bunker east wall Z=25..165 --
    # Rotation (0, 270, 0): slope faces east, thick edge at west (near bunker wall).
    # Camera-facing outer edge (X=108) is thin/grounded.
    east_side_skirt = part(
        "EastSideSkirt", (50.0, 18.0, 140.0), (83.0, 63.0, 95.0),
        material="Ground", color=EARTH_DARK, collide=True,
        class_name="WedgePart", rotation=(0.0, 270.0, 0.0),
    )
    # -- Rear ridge: extends hill north, slope faces south --
    rear_ridge = part(
        "RearRidge", (140.0, 12.0, 60.0), (0.0, 63.0, 160.0),
        material="Ground", color=EARTH_DARK, collide=True,
        class_name="WedgePart", rotation=(0.0, 0.0, 0.0),
    )
    # -- North fill: flat box behind ridge --
    north_fill = part(
        "NorthFill", (140.0, 4.0, 30.0), (0.0, 56.0, 210.0),
        material="Ground", color=EARTH_DARK, collide=True,
    )
    # -- West transition: smooths west shoulder -> hill cap, slope faces west --
    west_transition = part(
        "WestTransition", (15.0, 7.0, 30.0), (-25.0, 57.0, 10.0),
        material="Ground", color=MUD, collide=True,
        class_name="WedgePart", rotation=(0.0, 90.0, 0.0),
    )
    # -- East transition: smooths east shoulder -> hill cap, slope faces east --
    east_transition = part(
        "EastTransition", (15.0, 7.0, 30.0), (25.0, 57.0, 10.0),
        material="Ground", color=MUD, collide=True,
        class_name="WedgePart", rotation=(0.0, 270.0, 0.0),
    )
    return model(
        "TerrainShelf",
        [
            hill_cap,
            west_front_apron,
            east_front_apron,
            west_side_skirt,
            east_side_skirt,
            rear_ridge,
            north_fill,
            west_transition,
            east_transition,
        ],
        attributes={"TerrainBand": "gate1_macro", "ShelfVersion": "iteration-05b"},
    )

def build_exterior() -> dict[str, Any]:
    ground_patches = [
        part("EntranceYardEarth", (110.0, 0.12, 90.0), (0.0, 54.06, -25.0), material="Ground", color=EARTH, rotation=(0.0, -3.0, 0.0), cast_shadow=False),
        part("WestForestUnderstory", (165.0, 0.08, 235.0), (-155.0, 54.04, 40.0), material="LeafyGrass", color=SAGE_DARK, rotation=(0.0, 5.0, 0.0), cast_shadow=False),
        part("EastForestUnderstory", (165.0, 0.08, 285.0), (210.0, 54.04, 85.0), material="LeafyGrass", color=[0.10, 0.16, 0.105], rotation=(0.0, -4.0, 0.0), cast_shadow=False),
        part("SalvageMudField", (210.0, 0.1, 125.0), (0.0, 54.05, -135.0), material="Ground", color=EARTH_DARK, rotation=(0.0, 2.0, 0.0), cast_shadow=False),
        part("FarmTransitionEarth", (115.0, 0.1, 105.0), (61.0, 54.05, 165.0), material="Ground", color=EARTH, rotation=(0.0, -5.0, 0.0), cast_shadow=False),
    ]
    return model(
        "Exterior",
        [
            model("GroundCover", ground_patches),
            model("Paths", build_paths(), attributes={"PrimaryClearWidth": 10.0, "SecondaryClearWidth": 8.0}),
            model("Landmarks", build_landmarks()),
            build_terrain_shelf(),
            model("ForestDressing", build_forest_dressing()),
        ],
        attributes={"NavigationLanguage": "amber_exit_green_farm_blue_utility"},
    )


def build_plot(plot_id: str, position: Vec3) -> dict[str, Any]:
    x, y, z = position
    frame_color = [0.28, 0.20, 0.105]
    plot_prompt = prompt(f"{plot_id}_prompt", "TEND PLOT", "WHEAT PLOT", hold=0.18, distance=9.0)
    return model(
        plot_id,
        [
            part(
                "PlotBase",
                (8.0, 0.5, 8.0),
                position,
                material="Ground",
                color=[0.13, 0.095, 0.055],
                query=True,
                children=[plot_prompt],
            ),
            part("WestFrame", (0.35, 0.7, 8.4), (x - 4.1, y + 0.35, z), material="WoodPlanks", color=frame_color),
            part("EastFrame", (0.35, 0.7, 8.4), (x + 4.1, y + 0.35, z), material="WoodPlanks", color=frame_color),
            part("SouthFrame", (7.8, 0.7, 0.35), (x, y + 0.35, z - 4.1), material="WoodPlanks", color=frame_color),
            part("NorthFrame", (7.8, 0.7, 0.35), (x, y + 0.35, z + 4.1), material="WoodPlanks", color=frame_color),
            part("CropAnchor", (0.4, 0.4, 0.4), (x, 54.55, z), transparency=1.0, cast_shadow=False),
        ],
        attributes={"PlotId": plot_id, "InteractionKind": "farm_plot"},
        pivot=position,
    )


def build_processor() -> dict[str, Any]:
    position = (121.0, 55.5, 210.0)
    return model(
        "FoodProcessor",
        [
            interaction_anchor(position, prompt("food_processor_prompt", "PROCESS FOOD", "FOOD PROCESSOR", hold=0.2, distance=9.0)),
            part("Deck", (15.0, 0.45, 13.0), (121.0, 54.3, 210.0), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
            part("ProcessorBody", (8.0, 7.0, 6.0), (124.0, 57.8, 212.0), material="CorrodedMetal", color=STEEL, collide=True),
            cylinder_between("InputDrum", (118.5, 56.8, 213.0), (123.5, 56.8, 213.0), 3.2, material="Metal", color=STEEL_LIGHT),
            part("FeedHopper", (5.0, 3.0, 4.0), (121.0, 61.0, 213.0), material="Metal", color=UTILITY_GREEN),
            part("OutputConveyor", (8.0, 1.2, 3.0), (117.0, 55.2, 208.0), material="DiamondPlate", color=STEEL_LIGHT, collide=True, rotation=(0.0, -8.0, 0.0)),
            part("ControlCabinet", (4.0, 5.0, 1.7), (121.0, 57.2, 211.0), material="Metal", color=STEEL, collide=True),
            part("ControlScreen", (3.0, 1.7, 0.14), (121.0, 58.0, 210.1), material="Neon", color=UTILITY_GREEN, cast_shadow=False),
            part("EmergencyStop", (0.8, 0.8, 0.25), (122.3, 56.3, 210.0), material="Neon", color=EMERGENCY_RED, cast_shadow=False),
            cylinder_between("RecoveredWaterFeed", (115.0, 61.8, 216.0), (128.0, 61.8, 216.0), 0.45, color=UTILITY_BLUE),
            cylinder_between("WasteReturn", (127.0, 55.0, 207.0), (127.0, 62.0, 207.0), 0.38, color=RUST),
            placed_asset("ProcessorValve", "bunker_valve_assembly_01.model.json", (127.0, 59.0, 207.0), (2.7, 1.9, 1.65), rotation=(0.0, 90.0, 0.0)),
            placed_asset("ProcessorJunction", "bunker_electrical_junction_box_01.model.json", (126.0, 60.2, 215.5), (2.5, 2.35, 0.92)),
            placed_asset("ProcessorVent", "bunker_vent_grille_01.model.json", (128.2, 59.8, 212.0), (3.0, 2.6, 0.55), rotation=(0.0, -90.0, 0.0)),
            sign("ProcessorLabel", "FOOD PROCESSOR", (121.0, 63.0, 209.8), size=(8.0, 1.3, 0.18), text_color=UTILITY_GREEN),
        ],
        attributes={"ProcessorId": "food_processor", "InteractionId": "food_processor", "InteractionKind": "food_processor"},
        pivot=position,
    )


def build_farm_infrastructure() -> list[dict[str, Any]]:
    children: list[dict[str, Any]] = [
        part("FarmEarthPad", (72.0, 0.2, 66.0), (96.0, 54.1, 214.0), material="Ground", color=EARTH_DARK, cast_shadow=False),
        part("ProcessorApron", (24.0, 0.24, 32.0), (118.0, 54.12, 214.0), material="Concrete", color=CONCRETE_WORN, cast_shadow=False),
        part("CenterServiceLane", (10.0, 0.12, 61.0), (115.0, 54.16, 214.0), material="Pebble", color=[0.25, 0.25, 0.21], cast_shadow=False),
        part("SouthDrain", (62.0, 0.12, 1.4), (96.0, 54.24, 193.8), material="DiamondPlate", color=STEEL_LIGHT),
        part("NorthDrain", (62.0, 0.12, 1.4), (96.0, 54.24, 226.2), material="DiamondPlate", color=STEEL_LIGHT),
    ]
    for index, z in enumerate((195.0, 225.0, 244.0), 1):
        children.extend(
            [
                part(f"FenceWest{index}", (0.5, 5.0, 18.0), (62.0, 56.5, z), material="CorrodedMetal", color=STEEL),
                part(f"FenceEast{index}", (0.5, 5.0, 18.0), (130.0, 56.5, z), material="CorrodedMetal", color=STEEL),
            ]
        )
    children.extend(
        [
            cylinder_between("IrrigationHeaderSouth", (69.0, 61.0, 195.0), (111.0, 61.0, 195.0), 0.42, color=UTILITY_BLUE),
            cylinder_between("IrrigationHeaderNorth", (69.0, 61.0, 225.0), (111.0, 61.0, 225.0), 0.42, color=UTILITY_BLUE),
            cylinder_between("IrrigationWestFeed", (69.0, 61.0, 195.0), (69.0, 61.0, 225.0), 0.34, color=UTILITY_BLUE),
            cylinder_between("IrrigationEastFeed", (111.0, 61.0, 195.0), (111.0, 61.0, 225.0), 0.34, color=UTILITY_BLUE),
            cylinder_between("WaterTank", (125.0, 54.5, 234.0), (125.0, 63.0, 234.0), 5.0, material="CorrodedMetal", color=STEEL_LIGHT),
            placed_asset("FarmWaterValve", "bunker_valve_assembly_01.model.json", (119.0, 59.0, 234.0), (2.8, 1.95, 1.7)),
            placed_asset("FarmJunction", "bunker_electrical_junction_box_01.model.json", (128.5, 59.0, 228.0), (2.5, 2.35, 0.92), rotation=(0.0, -90.0, 0.0)),
            model(
                "FieldScarecrow",
                [
                    cylinder_between("Post", (67.0, 54.0, 238.0), (67.0, 64.0, 238.0), 0.5, material="Wood", color=WOOD_DARK),
                    cylinder_between("Arms", (62.0, 61.5, 238.0), (72.0, 61.5, 238.0), 0.42, material="Wood", color=WOOD_DARK),
                    part("Coat", (6.0, 4.5, 0.6), (67.0, 59.5, 238.0), material="Fabric", color=[0.18, 0.24, 0.18]),
                    part("Head", (1.8, 1.8, 1.8), (67.0, 64.0, 238.0), material="Fabric", color=[0.36, 0.30, 0.17], shape="Ball"),
                ],
            ),
        ]
    )
    return children


def build_farm() -> dict[str, Any]:
    plots: list[dict[str, Any]] = []
    plot_index = 1
    for z in (200.0, 210.0, 220.0):
        for x in (75.0, 85.0, 95.0, 105.0):
            plots.append(build_plot(f"plot_{plot_index:02d}", (x, 54.25, z)))
            plot_index += 1
    return model(
        "Farm",
        [
            model("Infrastructure", build_farm_infrastructure()),
            model("Plots", plots),
            build_processor(),
        ],
        attributes={"FarmId": "recovery_farm", "CropDefinitionId": "wheat"},
    )


def build_tree(index: int, position: Vec3) -> dict[str, Any]:
    tree_id = f"tree_{index:03d}"
    x, y, z = position
    lower_height = 7.0 + (index % 3) * 0.45
    upper_height = 6.0 + ((index + 1) % 4) * 0.4
    lean_x = (((index * 7) % 5) - 2) * 0.38
    lean_z = (((index * 11) % 5) - 2) * 0.32
    joint = (x + lean_x, y + lower_height, z + lean_z)
    crown = (x + lean_x * 1.8, y + lower_height + upper_height, z + lean_z * 1.8)
    branch_a = (crown[0] + 4.0 + (index % 2), crown[1] - 2.0, crown[2] - 2.2)
    branch_b = (crown[0] - 3.8, crown[1] - 3.0, crown[2] + 2.8 + (index % 3) * 0.3)
    foliage_a = [0.18 + (index % 3) * 0.02, 0.27 + (index % 2) * 0.025, 0.14]
    children = [
        part("ResourceAnchor", (0.4, 0.4, 0.4), position, transparency=1.0, cast_shadow=False),
        cylinder_between("LowerTrunk", (x, y + 0.15, z), joint, 2.35, material="Wood", color=WOOD_DARK, collide=True, query=True),
        cylinder_between("UpperTrunk", joint, crown, 1.65, material="Wood", color=WOOD, collide=True, query=True),
        cylinder_between("BranchA", (joint[0], joint[1] + 2.2, joint[2]), branch_a, 0.7, material="Wood", color=WOOD_DARK),
        cylinder_between("BranchB", (joint[0], joint[1] + 1.2, joint[2]), branch_b, 0.62, material="Wood", color=WOOD_DARK),
        cylinder_between("RootA", (x, y + 0.25, z), (x + 3.0, y + 0.15, z + 1.4), 0.65, material="Wood", color=WOOD_DARK),
        cylinder_between("RootB", (x, y + 0.25, z), (x - 2.6, y + 0.12, z - 1.7), 0.58, material="Wood", color=WOOD_DARK),
        part("CrownA", (8.0, 6.5, 7.0), (crown[0], crown[1] + 0.5, crown[2]), material="LeafyGrass", color=foliage_a, shape="Ball"),
        part("CrownB", (6.2, 5.0, 5.8), (branch_a[0] - 0.5, branch_a[1] + 0.8, branch_a[2]), material="LeafyGrass", color=SAGE_DARK, shape="Ball"),
        part("CrownC", (6.0, 5.2, 6.0), (branch_b[0] + 0.5, branch_b[1] + 1.0, branch_b[2]), material="LeafyGrass", color=SAGE, shape="Ball"),
    ]
    return model(
        tree_id,
        children,
        attributes={"ResourceNodeId": tree_id, "ResourceDefinitionId": "tree"},
        pivot=position,
    )


def build_scrap_cache(index: int, position: Vec3) -> dict[str, Any]:
    scrap_id = f"scrap_{index:02d}"
    x, y, z = position
    return model(
        scrap_id,
        [
            part("ResourceAnchor", (0.4, 0.4, 0.4), position, transparency=1.0, cast_shadow=False),
            part("CrushedCrate", (4.2, 1.8, 3.2), (x, y + 0.9, z), material="CorrodedMetal", color=STEEL, rotation=(0.0, index * 17.0, 5.0)),
            part("PlateA", (5.0, 0.3, 2.5), (x + 1.2, y + 0.55, z - 1.2), material="CorrodedMetal", color=RUST, rotation=(8.0, index * 29.0, 10.0)),
            part("PlateB", (3.8, 0.35, 3.0), (x - 1.4, y + 0.48, z + 1.0), material="Metal", color=STEEL_LIGHT, rotation=(-6.0, index * 11.0, -8.0)),
            cylinder_between("BentPipe", (x - 2.2, y + 0.5, z - 1.8), (x + 2.3, y + 1.0, z + 1.6), 0.55, color=RUST),
            part("SalvageMark", (1.2, 0.08, 1.2), (x, y + 1.85, z), material="Neon", color=HAZARD, cast_shadow=False),
            interaction_anchor((x, y + 1.3, z), prompt(f"{scrap_id}_prompt", "SCAVENGE", "SCRAP CACHE", hold=0.35, distance=10.0)),
        ],
        attributes={"ResourceNodeId": scrap_id, "ResourceDefinitionId": "scrap_cache"},
        pivot=position,
    )


def build_resources() -> dict[str, Any]:
    trees = [build_tree(index, position) for index, position in enumerate(TREE_POSITIONS, 1)]
    scraps = [build_scrap_cache(index, position) for index, position in enumerate(SCRAP_POSITIONS, 1)]
    return model("Resources", [model("Trees", trees), model("ScrapCaches", scraps)])


def build_enemy_spawns() -> dict[str, Any]:
    markers = []
    for index, (x, z) in enumerate(ZOMBIE_POSITIONS, 1):
        spawn_id = f"zombie_spawn_{index:02d}"
        markers.append(
            part(
                spawn_id,
                (6.0, 0.2, 6.0),
                (x, 53.9, z),
                transparency=1.0,
                cast_shadow=False,
                attributes={"SpawnId": spawn_id, "SpawnGroupId": "night_perimeter"},
            )
        )
    return model("EnemySpawns", markers, attributes={"SelectionMode": "deterministic_cycle"})


def build_objectives() -> dict[str, Any]:
    return model(
        "Objectives",
        [
            part(
                objective_id,
                (4.0, 0.2, 4.0),
                position,
                transparency=1.0,
                cast_shadow=False,
                attributes={"ObjectiveId": objective_id},
            )
            for objective_id, position in OBJECTIVES
        ],
    )


def exterior_lamp(name: str, position: Vec3, color: Sequence[float], *, shadows: bool = False) -> dict[str, Any]:
    x, y, z = position
    return model(
        name,
        [
            part("Post", (0.7, 8.0, 0.7), (x, y - 4.0, z), material="CorrodedMetal", color=RUST),
            part("Arm", (3.5, 0.45, 0.45), (x + 1.4, y - 0.5, z), material="Metal", color=STEEL_LIGHT),
            part(
                "Lamp",
                (1.5, 0.7, 1.5),
                (x + 2.8, y - 0.8, z),
                material="Neon",
                color=color,
                cast_shadow=False,
                children=[point_light("ExteriorPool", color, 0.9, 18.0, shadows=shadows)],
            ),
        ],
    )


def build_presentation() -> dict[str, Any]:
    lights = [
        exterior_lamp("EntranceYardLamp", (-15.0, 66.0, 4.0), LIGHT_WARM, shadows=True),
        exterior_lamp("FarmGateLamp", (44.0, 65.0, 159.0), UTILITY_GREEN),
        exterior_lamp("CheckpointLamp", (-12.0, 66.0, -157.0), LIGHT_WARM),
        exterior_lamp("ProcessorYardLamp", (129.0, 66.0, 202.0), LIGHT_COOL, shadows=True),
        exterior_lamp("WaterTowerLamp", (104.0, 66.0, -52.0), LIGHT_WARM),
    ]
    vfx = [
        particle_anchor(
            "BunkerExhaustHaze",
            (52.0, 69.0, 81.0),
            texture="rbxasset://textures/particles/smoke_main.dds",
            rate=0.65,
            lifetime=(1.6, 2.6),
            speed=(0.25, 0.5),
            size=((0.0, 0.35), (0.6, 0.8), (1.0, 1.1)),
            transparency=((0.0, 0.87), (0.5, 0.84), (1.0, 1.0)),
            color=([0.28, 0.30, 0.28], [0.16, 0.18, 0.17]),
            acceleration=(0.0, 0.42, 0.0),
        ),
        particle_anchor(
            "EntranceDust",
            (0.0, 59.0, 8.0),
            texture="rbxasset://textures/particles/smoke_main.dds",
            rate=0.35,
            lifetime=(3.0, 5.0),
            speed=(0.05, 0.14),
            size=((0.0, 0.5), (1.0, 1.5)),
            transparency=((0.0, 0.94), (0.5, 0.90), (1.0, 1.0)),
            color=([0.35, 0.37, 0.31], [0.20, 0.22, 0.19]),
        ),
        particle_anchor(
            "WestForestMist",
            (-160.0, 55.0, 65.0),
            texture="rbxasset://textures/particles/smoke_main.dds",
            rate=0.28,
            lifetime=(4.0, 6.0),
            speed=(0.08, 0.16),
            size=((0.0, 1.2), (1.0, 3.2)),
            transparency=((0.0, 0.96), (0.5, 0.91), (1.0, 1.0)),
            color=([0.31, 0.38, 0.33], [0.16, 0.21, 0.18]),
            spread=(24.0, 24.0),
        ),
        particle_anchor(
            "EastForestMist",
            (210.0, 55.0, 95.0),
            texture="rbxasset://textures/particles/smoke_main.dds",
            rate=0.28,
            lifetime=(4.0, 6.0),
            speed=(0.08, 0.16),
            size=((0.0, 1.2), (1.0, 3.2)),
            transparency=((0.0, 0.96), (0.5, 0.91), (1.0, 1.0)),
            color=([0.31, 0.38, 0.33], [0.16, 0.21, 0.18]),
            spread=(24.0, 24.0),
        ),
        particle_anchor(
            "FarmIrrigationMist",
            (100.0, 57.0, 224.0),
            texture="rbxasset://textures/particles/smoke_main.dds",
            rate=0.5,
            lifetime=(1.3, 2.2),
            speed=(0.12, 0.25),
            size=((0.0, 0.25), (1.0, 0.7)),
            transparency=((0.0, 0.88), (0.6, 0.92), (1.0, 1.0)),
            color=([0.48, 0.62, 0.58], [0.25, 0.38, 0.34]),
            acceleration=(0.0, -0.08, 0.0),
        ),
        particle_anchor(
            "ServiceDrip",
            (18.0, 65.8, 147.0),
            texture="rbxasset://textures/particles/sparkles_main.dds",
            rate=0.7,
            lifetime=(0.35, 0.55),
            speed=(0.7, 1.0),
            size=((0.0, 0.055), (1.0, 0.0)),
            transparency=((0.0, 0.35), (0.8, 0.55), (1.0, 1.0)),
            color=([0.58, 0.75, 0.77], [0.35, 0.48, 0.50]),
            acceleration=(0.0, -9.0, 0.0),
            spread=(3.0, 3.0),
        ),
    ]
    audio = [
        audio_anchor("BlastDoorOpenCue", (-7.8, 59.5, 17.0), "rbxassetid://157167203", 0.24),
        audio_anchor("BlastDoorCloseCue", (7.8, 59.5, 17.0), "rbxassetid://157167205", 0.22),
    ]
    return model(
        "Presentation",
        [
            model("ExteriorLights", lights),
            model("VFXAnchors", vfx),
            model("AudioAnchors", audio, attributes={"PlaybackOwner": "server_interactions"}),
        ],
        attributes={"PresentationPass": "creepy_restrained", "ReducedMotionCompatible": True},
    )


def build_world() -> dict[str, Any]:
    return {
        "ClassName": "Model",
        "attributes": {
            "WorldVersion": "FG-GREENFIELD-001",
            "WorldSeed": WORLD_SEED,
            "DatumY": GROUND_TOP_Y,
            "RuntimeRandomness": False,
        },
        "Children": [
            build_foundation(),
            build_bunker(),
            build_exterior(),
            build_farm(),
            build_resources(),
            build_enemy_spawns(),
            build_objectives(),
            build_presentation(),
        ],
    }


def walk(node: dict[str, Any], path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], dict[str, Any]]]:
    yield path, node
    for index, child in enumerate(node.get("Children", [])):
        child_name = child.get("Name", f"#{index}")
        yield from walk(child, (*path, child_name))


def direct_child(node: dict[str, Any], name: str) -> dict[str, Any]:
    matches = [child for child in node.get("Children", []) if child.get("Name") == name]
    if len(matches) != 1:
        raise AssertionError(f"expected one direct child {name}, found {len(matches)}")
    return matches[0]


def node_position(node: dict[str, Any]) -> Vec3:
    properties = node.get("Properties", {})
    if "Position" in properties:
        return tuple(float(value) for value in properties["Position"])  # type: ignore[return-value]
    if "CFrame" in properties:
        return tuple(float(value) for value in properties["CFrame"][:3])  # type: ignore[return-value]
    pivot = properties.get("WorldPivotData", {}).get("OptionalCFrame", {}).get("position")
    if pivot:
        return tuple(float(value) for value in pivot)  # type: ignore[return-value]
    raise AssertionError(f"node {node.get('Name')} has no authored position")


def assert_vector(actual: Sequence[float], expected: Sequence[float], label: str) -> None:
    if len(actual) != len(expected) or any(abs(float(left) - float(right)) > 1e-6 for left, right in zip(actual, expected)):
        raise AssertionError(f"{label}: expected {tuple(expected)}, got {tuple(actual)}")


def descendants(node: dict[str, Any]) -> list[dict[str, Any]]:
    return [child for _, child in list(walk(node))[1:]]


def count_classes(node: dict[str, Any], classes: set[str]) -> int:
    return sum(1 for _, child in walk(node) if child.get("ClassName") in classes)


def validate_world(root: dict[str, Any]) -> dict[str, Any]:
    top_names = [child.get("Name") for child in root.get("Children", [])]
    expected_top = ["Foundation", "Bunker", "Exterior", "Farm", "Resources", "EnemySpawns", "Objectives", "Presentation"]
    if top_names != expected_top:
        raise AssertionError(f"top-level hierarchy mismatch: {top_names}")

    foundation = direct_child(root, "Foundation")
    bunker = direct_child(root, "Bunker")
    exterior = direct_child(root, "Exterior")
    farm = direct_child(root, "Farm")
    resources = direct_child(root, "Resources")
    enemy_spawns = direct_child(root, "EnemySpawns")
    objectives = direct_child(root, "Objectives")
    presentation = direct_child(root, "Presentation")

    stable_ground = direct_child(foundation, "StableGround")
    assert_vector(node_position(stable_ground), (0.0, 52.5, 80.0), "StableGround position")
    assert_vector(stable_ground["Properties"]["Size"], (640.0, 3.0, 640.0), "StableGround size")
    if abs(node_position(stable_ground)[1] + stable_ground["Properties"]["Size"][1] / 2.0 - 54.0) > 1e-6:
        raise AssertionError("StableGround top is not Y=54")

    bunker_required = {
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
    }
    bunker_names = {child.get("Name") for child in bunker.get("Children", [])}
    missing_bunker = sorted(bunker_required - bunker_names)
    if missing_bunker:
        raise AssertionError(f"missing bunker sections: {missing_bunker}")
    spawn_safe_zone = direct_child(bunker, "SpawnSafeZone")
    assert_vector(node_position(spawn_safe_zone), (-43.5, 61.0, 66.0), "SpawnSafeZone position")
    assert_vector(spawn_safe_zone["Properties"]["Size"], (37.0, 18.0, 32.0), "SpawnSafeZone size")

    spawn_container = direct_child(bunker, "Spawns")
    spawn_nodes = [child for child in spawn_container.get("Children", []) if child.get("ClassName") == "SpawnLocation"]
    if len(spawn_nodes) != 6:
        raise AssertionError(f"expected six SpawnLocations, found {len(spawn_nodes)}")
    spawn_by_id = {node.get("attributes", {}).get("SpawnId"): node for node in spawn_nodes}
    for spawn_id, slot, expected_position in SPAWNS:
        spawn = spawn_by_id.get(spawn_id)
        if spawn is None:
            raise AssertionError(f"missing spawn {spawn_id}")
        assert_vector(node_position(spawn), expected_position, spawn_id)
        assert_vector(spawn["Properties"]["Size"], (5.0, 1.0, 5.0), f"{spawn_id} size")
        attrs = spawn.get("attributes", {})
        if attrs.get("SpawnRole") != "bedroom" or attrs.get("SlotIndex") != slot:
            raise AssertionError(f"invalid attributes on {spawn_id}: {attrs}")
        if spawn["Properties"].get("CanCollide") or spawn["Properties"].get("Duration") != 0.0 or not spawn["Properties"].get("Neutral"):
            raise AssertionError(f"invalid spawn properties on {spawn_id}")
        matrix = spawn["Properties"].get("CFrame", [])
        look_z = -float(matrix[11]) if len(matrix) == 12 else 0.0
        if look_z > -0.99:
            raise AssertionError(f"{spawn_id} does not face the bedroom exit")

    expected_station_map = {interaction_id: (kind, position) for interaction_id, kind, position in STATIONS}
    station_models = {
        node.get("attributes", {}).get("InteractionId"): node
        for _, node in walk(root)
        if node.get("ClassName") == "Model" and node.get("attributes", {}).get("InteractionId") in expected_station_map
    }
    if set(station_models) != set(expected_station_map):
        raise AssertionError(f"station IDs mismatch: {sorted(station_models)}")
    for station_id, (expected_kind, expected_position) in expected_station_map.items():
        station = station_models[station_id]
        attrs = station.get("attributes", {})
        if attrs.get("InteractionKind") != expected_kind:
            raise AssertionError(f"{station_id} kind mismatch: {attrs.get('InteractionKind')}")
        if station_id == "food_processor" and attrs.get("ProcessorId") != "food_processor":
            raise AssertionError("FoodProcessor is missing ProcessorId")
        assert_vector(node_position(station), expected_position, f"{station_id} model pivot")
        anchor = direct_child(station, "InteractionAnchor")
        assert_vector(node_position(anchor), expected_position, f"{station_id} anchor")
        prompts = [node for node in descendants(station) if node.get("ClassName") == "ProximityPrompt"]
        if len(prompts) != 1:
            raise AssertionError(f"{station_id} must contain exactly one prompt")

    plots_container = direct_child(farm, "Plots")
    plots = plots_container.get("Children", [])
    if len(plots) != 12:
        raise AssertionError(f"expected 12 plots, found {len(plots)}")
    expected_plots: dict[str, Vec3] = {}
    plot_index = 1
    for z in (200.0, 210.0, 220.0):
        for x in (75.0, 85.0, 95.0, 105.0):
            expected_plots[f"plot_{plot_index:02d}"] = (x, 54.25, z)
            plot_index += 1
    for plot in plots:
        plot_id = plot.get("attributes", {}).get("PlotId")
        if plot_id not in expected_plots or plot.get("attributes", {}).get("InteractionKind") != "farm_plot":
            raise AssertionError(f"invalid plot attributes: {plot.get('attributes')}")
        assert_vector(node_position(plot), expected_plots[plot_id], f"{plot_id} model pivot")
        assert_vector(node_position(direct_child(plot, "PlotBase")), expected_plots[plot_id], plot_id)
        direct_child(plot, "CropAnchor")
        plot_prompts = [node for node in descendants(plot) if node.get("ClassName") == "ProximityPrompt"]
        if len(plot_prompts) != 1:
            raise AssertionError(f"{plot_id} must contain exactly one prompt")

    processor = direct_child(farm, "FoodProcessor")
    if processor is not station_models["food_processor"]:
        raise AssertionError("FoodProcessor station is not the canonical Farm.FoodProcessor model")

    trees_container = direct_child(resources, "Trees")
    trees = trees_container.get("Children", [])
    if len(trees) != 18:
        raise AssertionError(f"expected 18 trees, found {len(trees)}")
    expected_trees = {f"tree_{index:03d}": position for index, position in enumerate(TREE_POSITIONS, 1)}
    for tree in trees:
        attrs = tree.get("attributes", {})
        tree_id = attrs.get("ResourceNodeId")
        if tree_id not in expected_trees or attrs.get("ResourceDefinitionId") != "tree":
            raise AssertionError(f"invalid tree attributes: {attrs}")
        assert_vector(node_position(tree), expected_trees[tree_id], f"{tree_id} model pivot")
        assert_vector(node_position(direct_child(tree, "ResourceAnchor")), expected_trees[tree_id], tree_id)

    scrap_container = direct_child(resources, "ScrapCaches")
    scraps = scrap_container.get("Children", [])
    if len(scraps) != 6:
        raise AssertionError(f"expected six scrap caches, found {len(scraps)}")
    expected_scraps = {f"scrap_{index:02d}": position for index, position in enumerate(SCRAP_POSITIONS, 1)}
    for scrap in scraps:
        attrs = scrap.get("attributes", {})
        scrap_id = attrs.get("ResourceNodeId")
        if scrap_id not in expected_scraps or attrs.get("ResourceDefinitionId") != "scrap_cache":
            raise AssertionError(f"invalid scrap attributes: {attrs}")
        assert_vector(node_position(scrap), expected_scraps[scrap_id], f"{scrap_id} model pivot")
        assert_vector(node_position(direct_child(scrap, "ResourceAnchor")), expected_scraps[scrap_id], scrap_id)
        scrap_prompts = [node for node in descendants(scrap) if node.get("ClassName") == "ProximityPrompt"]
        if len(scrap_prompts) != 1:
            raise AssertionError(f"{scrap_id} must contain exactly one prompt")

    zombie_markers = enemy_spawns.get("Children", [])
    if len(zombie_markers) != 7:
        raise AssertionError(f"expected seven zombie markers, found {len(zombie_markers)}")
    for index, (x, z) in enumerate(ZOMBIE_POSITIONS, 1):
        spawn_id = f"zombie_spawn_{index:02d}"
        marker = next((node for node in zombie_markers if node.get("attributes", {}).get("SpawnId") == spawn_id), None)
        if marker is None or marker.get("attributes", {}).get("SpawnGroupId") != "night_perimeter":
            raise AssertionError(f"invalid zombie marker {spawn_id}")
        assert_vector(node_position(marker), (x, 53.9, z), spawn_id)
        for _, _, player_spawn in SPAWNS:
            if math.hypot(x - player_spawn[0], z - player_spawn[2]) <= 200.0:
                raise AssertionError(f"{spawn_id} is not more than 200 studs from every player spawn")

    objective_nodes = objectives.get("Children", [])
    if len(objective_nodes) != 3:
        raise AssertionError(f"expected three objectives, found {len(objective_nodes)}")
    for objective_id, expected_position in OBJECTIVES:
        objective = next((node for node in objective_nodes if node.get("attributes", {}).get("ObjectiveId") == objective_id), None)
        if objective is None:
            raise AssertionError(f"missing objective {objective_id}")
        assert_vector(node_position(objective), expected_position, objective_id)

    all_nodes = [node for _, node in walk(root)]
    scripts = [node for node in all_nodes if node.get("ClassName") in SCRIPT_CLASSES]
    if scripts:
        raise AssertionError("GameWorld contains executable scripts")
    if any(node.get("attributes", {}).get("GeneratedAssetId") == "pipeline_pipe_retry_02" for node in all_nodes):
        raise AssertionError("scale-hazard pipe asset was placed in GameWorld")

    base_parts = count_classes(root, BASE_PART_CLASSES)
    bunker_parts = count_classes(bunker, BASE_PART_CLASSES)
    farm_parts = count_classes(farm, BASE_PART_CLASSES)
    collidable_parts = sum(
        1
        for node in all_nodes
        if node.get("ClassName") in BASE_PART_CLASSES and node.get("Properties", {}).get("CanCollide") is True
    )
    farm_collidable = sum(
        1
        for _, node in walk(farm)
        if node.get("ClassName") in BASE_PART_CLASSES and node.get("Properties", {}).get("CanCollide") is True
    )
    light_nodes = [node for node in all_nodes if node.get("ClassName") in LIGHT_CLASSES]
    shadow_lights = sum(1 for node in light_nodes if node.get("Properties", {}).get("Shadows") is True)
    emitters = [node for node in all_nodes if node.get("ClassName") == "ParticleEmitter"]
    visible_particles = 0.0
    for emitter in emitters:
        lifetime = emitter.get("Properties", {}).get("Lifetime", {}).get("NumberRange", [0.0, 0.0])
        visible_particles += float(emitter.get("Properties", {}).get("Rate", 0.0)) * float(lifetime[1])
    sounds = [node for node in all_nodes if node.get("ClassName") == "Sound"]
    invalid_sound_ids = sorted({node.get("Properties", {}).get("SoundId") for node in sounds} - ALLOWED_SOUND_IDS)
    if invalid_sound_ids:
        raise AssertionError(f"unverified SoundIds: {invalid_sound_ids}")
    active_sounds = sum(1 for node in sounds if node.get("Properties", {}).get("Playing") is True)
    ambient_beds = sum(1 for node in sounds if node.get("Properties", {}).get("Looped") is True)
    prompt_count = sum(1 for node in all_nodes if node.get("ClassName") == "ProximityPrompt")
    if any(
        node.get("Properties", {}).get("Style") != "Custom"
        for node in all_nodes
        if node.get("ClassName") == "ProximityPrompt"
    ):
        raise AssertionError("all candidate interaction prompts must use Custom presentation")
    descendant_count = len(all_nodes) - 1
    bunker_descendants = len(descendants(bunker))

    if base_parts > 2500:
        raise AssertionError(f"GameWorld BasePart budget exceeded: {base_parts}")
    if descendant_count > 3600:
        raise AssertionError(f"GameWorld descendant budget exceeded: {descendant_count}")
    if bunker_parts > 600 or bunker_descendants > 900:
        raise AssertionError(f"bunker budget exceeded: {bunker_parts} parts / {bunker_descendants} descendants")
    if farm_parts > 180 or farm_collidable > 40:
        raise AssertionError(f"farm budget exceeded: {farm_parts} parts / {farm_collidable} collidable")
    if len(light_nodes) > 23 or shadow_lights > 6:
        raise AssertionError(f"light budget exceeded: {len(light_nodes)} / {shadow_lights} shadow")
    if len(emitters) > 12 or visible_particles > 180.0:
        raise AssertionError(f"particle budget exceeded: {len(emitters)} / {visible_particles:.2f} visible")
    if active_sounds > 16 or ambient_beds > 2:
        raise AssertionError(f"audio budget exceeded: {active_sounds} active / {ambient_beds} beds")

    return {
        "seed": WORLD_SEED,
        "exactPositionChecks": 61,
        "groundTopY": 54.0,
        "baseParts": base_parts,
        "descendants": descendant_count,
        "collidableParts": collidable_parts,
        "bunkerBaseParts": bunker_parts,
        "bunkerDescendants": bunker_descendants,
        "farmBaseParts": farm_parts,
        "farmCollidableParts": farm_collidable,
        "lights": len(light_nodes),
        "shadowLights": shadow_lights,
        "particleEmitters": len(emitters),
        "configuredVisibleParticles": round(visible_particles, 2),
        "sounds": len(sounds),
        "activeSounds": active_sounds,
        "ambientBeds": ambient_beds,
        "prompts": prompt_count,
        "stationPrompts": len(station_models),
        "plotPrompts": len(plots),
        "scrapPrompts": len(scraps),
        "spawns": len(spawn_nodes),
        "stations": len(station_models),
        "plots": len(plots),
        "trees": len(trees),
        "scrapCaches": len(scraps),
        "resourceNodes": len(trees) + len(scraps),
        "zombieMarkers": len(zombie_markers),
        "objectives": len(objective_nodes),
        "scripts": len(scripts),
        "exteriorBaseParts": count_classes(exterior, BASE_PART_CLASSES),
        "presentationBaseParts": count_classes(presentation, BASE_PART_CLASSES),
    }


LIGHTING_MODELS: dict[str, dict[str, Any]] = {
    "Atmosphere.model.json": {
        "ClassName": "Atmosphere",
        "Properties": {
            "Color": [0.46, 0.53, 0.49],
            "Decay": [0.22, 0.27, 0.25],
            "Density": 0.37,
            "Glare": 0.06,
            "Haze": 1.65,
            "Offset": 0.08,
        },
    },
    "Bloom.model.json": {
        "ClassName": "BloomEffect",
        "Properties": {"Enabled": True, "Intensity": 0.22, "Threshold": 1.45, "Size": 18.0},
    },
    "ColorGrade.model.json": {
        "ClassName": "ColorCorrectionEffect",
        "Properties": {
            "Enabled": True,
            "Brightness": 0.0,
            "Contrast": 0.08,
            "Saturation": -0.22,
            "TintColor": [0.82, 0.89, 0.82],
        },
    },
    "DepthOfField.model.json": {
        "ClassName": "DepthOfFieldEffect",
        "Properties": {
            "Enabled": True,
            "FarIntensity": 0.08,
            "FocusDistance": 68.0,
            "InFocusRadius": 52.0,
            "NearIntensity": 0.025,
        },
    },
    "SunRays.model.json": {
        "ClassName": "SunRaysEffect",
        "Properties": {"Enabled": True, "Intensity": 0.025, "Spread": 0.46},
    },
}

LIGHTING_META: dict[str, Any] = {
    "className": "Lighting",
    "properties": {
        "Ambient": [0.26, 0.30, 0.28],
        "Brightness": 1.6,
        "ClockTime": 16.8,
        "ColorShift_Bottom": [0.35, 0.40, 0.36],
        "ColorShift_Top": [0.55, 0.58, 0.49],
        "EnvironmentDiffuseScale": 0.72,
        "EnvironmentSpecularScale": 0.38,
        "ExposureCompensation": 0.08,
        "FogColor": [0.32, 0.38, 0.35],
        "FogEnd": 430.0,
        "FogStart": 110.0,
        "GeographicLatitude": 41.0,
        "GlobalShadows": True,
        "OutdoorAmbient": [0.28, 0.32, 0.30],
        "PrioritizeLightingQuality": True,
        "ShadowSoftness": 0.35,
        "Technology": "Future",
    }
}


def json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_candidate(output: Path, world: dict[str, Any]) -> dict[str, str]:
    if output.parent.name != "Workspace":
        raise ValueError("--output must be under a Workspace directory so supporting candidate paths are unambiguous")
    source_root = output.parent.parent
    runtime_output = output.parent / "Runtime.model.json"
    lighting_output = source_root / "Lighting"
    assets_output = source_root / "ServerStorage/GeneratedAssets"

    output.parent.mkdir(parents=True, exist_ok=True)
    lighting_output.mkdir(parents=True, exist_ok=True)
    assets_output.mkdir(parents=True, exist_ok=True)

    generated: dict[str, bytes] = {
        str(output): json_bytes(world),
        str(runtime_output): json_bytes({"ClassName": "Folder", "Children": []}),
        str(lighting_output / "init.meta.json"): json_bytes(LIGHTING_META),
    }
    for filename, lighting_model in LIGHTING_MODELS.items():
        generated[str(lighting_output / filename)] = json_bytes(lighting_model)

    for path_string, content in generated.items():
        Path(path_string).write_bytes(content)

    for filename in ACCEPTED_ASSET_FILES:
        source = ACTIVE_GENERATED_ASSETS / filename
        destination = assets_output / filename
        if source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
        if source.read_bytes() != destination.read_bytes():
            raise AssertionError(f"asset copy mismatch: {filename}")

    hashes = {path: sha256_bytes(content) for path, content in generated.items()}
    for filename in ACCEPTED_ASSET_FILES:
        path = assets_output / filename
        hashes[str(path)] = sha256_bytes(path.read_bytes())
    return hashes


def resolve_output(raw_output: str | None) -> Path:
    if raw_output is None:
        return DEFAULT_OUTPUT
    output = Path(raw_output).expanduser()
    return output if output.is_absolute() else ROOT / output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="GameWorld.model.json output; supporting files are inferred from its source root")
    parser.add_argument("--validate-only", action="store_true", help="Validate an existing --output without writing files")
    arguments = parser.parse_args()
    output = resolve_output(arguments.output)

    if arguments.validate_only:
        existing = json.loads(output.read_text(encoding="utf-8"))
        summary = validate_world(existing)
        print(json.dumps({"output": str(output), "sha256": sha256_bytes(output.read_bytes()), "counts": summary}, sort_keys=True))
        return

    world = build_world()
    summary = validate_world(world)
    hashes = write_candidate(output, world)

    parsed = json.loads(output.read_text(encoding="utf-8"))
    parsed_summary = validate_world(parsed)
    if parsed_summary != summary:
        raise AssertionError("written world validation differs from in-memory validation")

    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": hashes[str(output)],
                "runtime": str(output.parent / "Runtime.model.json"),
                "counts": summary,
                "generatedFiles": len(hashes),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
