"""Structural shells, thresholds, and shared-portal ownership."""

from __future__ import annotations

from .kit import (
    CONCRETE,
    CONCRETE_DARK,
    CONCRETE_WORN,
    FLOOR,
    GREEN,
    STEEL_LIGHT,
    UTILITY_BLUE,
    YELLOW,
    model,
    part,
)
from .site import FLOOR_Y, ROOM_BOUNDS, ROOM_HEIGHTS


Opening = tuple[float, float]


def wall_segments(
    prefix: str,
    axis: str,
    fixed: float,
    lo: float,
    hi: float,
    height: float,
    openings: list[Opening],
    *,
    include_lintels: bool = True,
) -> list[dict]:
    """Build a segmented wall, optionally deferring shared lintels to its peer."""

    thickness = 1.0
    pieces: list[dict] = []
    spans = sorted((max(lo, center - width / 2), min(hi, center + width / 2), center) for center, width in openings)
    cursor = lo
    index = 1
    for start, end, center in spans:
        if start - cursor > 0.1:
            midpoint = (cursor + start) / 2
            length = start - cursor
            size = (length, height, thickness) if axis == "x" else (thickness, height, length)
            pos = (midpoint, FLOOR_Y + height / 2, fixed) if axis == "x" else (fixed, FLOOR_Y + height / 2, midpoint)
            pieces.append(part(f"{prefix}WallSegment{index:02d}", size, pos, material="Concrete", color=CONCRETE))
            index += 1
        if include_lintels:
            lintel_height = max(1.0, height - 8.0)
            size = (end - start, lintel_height, thickness) if axis == "x" else (thickness, lintel_height, end - start)
            pos = (center, FLOOR_Y + 8 + lintel_height / 2, fixed) if axis == "x" else (fixed, FLOOR_Y + 8 + lintel_height / 2, center)
            pieces.append(part(f"{prefix}PortalLintel{index:02d}", size, pos, material="Concrete", color=CONCRETE_DARK))
            index += 1
        cursor = max(cursor, end)
    if hi - cursor > 0.1:
        midpoint = (cursor + hi) / 2
        length = hi - cursor
        size = (length, height, thickness) if axis == "x" else (thickness, height, length)
        pos = (midpoint, FLOOR_Y + height / 2, fixed) if axis == "x" else (fixed, FLOOR_Y + height / 2, midpoint)
        pieces.append(part(f"{prefix}WallSegment{index:02d}", size, pos, material="Concrete", color=CONCRETE))
    return pieces


def door_frame(name: str, axis: str, fixed: float, center: float, width: float, height: float = 8.0) -> dict:
    """Build one authoritative frame for a portal shared by adjacent shells."""

    post_width, depth = 0.5, 1.35
    if axis == "x":
        children = [
            part("LeftPost", (post_width, height + 0.5, depth), (center - width / 2, FLOOR_Y + height / 2, fixed), material="Metal", color=STEEL_LIGHT),
            part("RightPost", (post_width, height + 0.5, depth), (center + width / 2, FLOOR_Y + height / 2, fixed), material="Metal", color=STEEL_LIGHT),
            part("Header", (width + post_width, 0.7, depth), (center, FLOOR_Y + height, fixed), material="Metal", color=STEEL_LIGHT),
            part("Threshold", (width, 0.14, 1.5), (center, FLOOR_Y + 0.07, fixed), material="DiamondPlate", color=STEEL_LIGHT),
        ]
    else:
        children = [
            part("NearPost", (depth, height + 0.5, post_width), (fixed, FLOOR_Y + height / 2, center - width / 2), material="Metal", color=STEEL_LIGHT),
            part("FarPost", (depth, height + 0.5, post_width), (fixed, FLOOR_Y + height / 2, center + width / 2), material="Metal", color=STEEL_LIGHT),
            part("Header", (depth, 0.7, width + post_width), (fixed, FLOOR_Y + height, center), material="Metal", color=STEEL_LIGHT),
            part("Threshold", (1.5, 0.14, width), (fixed, FLOOR_Y + 0.07, center), material="DiamondPlate", color=STEEL_LIGHT),
        ]
    return model(name, children)


def shell(
    name: str,
    openings: dict[str, list[Opening]],
    *,
    portal_owner_sides: frozenset[str] = frozenset({"south", "north", "west", "east"}),
) -> dict:
    """Build a room shell with one-sided ownership at shared connections."""

    x0, x1, z0, z1 = ROOM_BOUNDS[name]
    height = ROOM_HEIGHTS[name]
    children = [
        part("FloorSlab", (x1 - x0, 1, z1 - z0), ((x0 + x1) / 2, FLOOR_Y - 0.5, (z0 + z1) / 2), material="Slate", color=FLOOR),
        part("CeilingSlab", (x1 - x0, 1, z1 - z0), ((x0 + x1) / 2, FLOOR_Y + height + 0.5, (z0 + z1) / 2), material="Concrete", color=CONCRETE_DARK),
    ]
    side_specs = {
        "south": ("x", z0, x0, x1),
        "north": ("x", z1, x0, x1),
        "west": ("z", x0, z0, z1),
        "east": ("z", x1, z0, z1),
    }
    for side, (axis, fixed, lo, hi) in side_specs.items():
        children.extend(wall_segments(
            side.title(), axis, fixed, lo, hi, height, openings.get(side, []),
            include_lintels=side in portal_owner_sides,
        ))
    # Keep generated child ordering deterministic. portal_owner_sides is a
    # frozenset for membership semantics, so iterating it directly makes model
    # output depend on Python hash order between processes.
    for side in ("south", "north", "west", "east"):
        if side not in portal_owner_sides:
            continue
        axis, fixed, _, _ = side_specs[side]
        for index, (center, width) in enumerate(openings.get(side, []), 1):
            children.append(door_frame(f"{side.title()}PortalFrame{index:02d}", axis, fixed, center, width))
    return model(name, children)


def build_architecture() -> list[dict]:
    """Return all structural shells at the safe staging transform."""

    architecture = [
        shell("EntranceDefenseShell", {"south": [(-60, 8)], "north": [(-60, 8)]}),
        shell("SouthConnectorShell", {"south": [(-60, 8)], "north": [(-60, 8)]}, portal_owner_sides=frozenset()),
        shell("CommonHubShell", {"south": [(-60, 8)], "north": [(-62, 8)], "west": [(42, 8)], "east": [(42, 6.5)]}),
        shell("WestResidentialCorridorShell", {"east": [(42, 8)], "west": [(38, 7), (56, 7), (76, 7)]}, portal_owner_sides=frozenset({"west"})),
        shell("WorkshopShell", {"east": [(38, 7)]}, portal_owner_sides=frozenset()),
        shell("UpgradeShell", {"east": [(56, 7)]}, portal_owner_sides=frozenset()),
        shell("BedroomShell", {"east": [(76, 7)]}, portal_owner_sides=frozenset()),
        shell("StorageShell", {"south": [(-62, 8)], "east": [(69, 6)]}, portal_owner_sides=frozenset({"east"})),
        shell("EastUtilityCorridorShell", {"west": [(42, 6.5)], "east": [(42, 6.5)], "north": [(-42.5, 6.5)]}, portal_owner_sides=frozenset({"east", "north"})),
        shell("ShopShell", {"west": [(42, 6.5)]}, portal_owner_sides=frozenset()),
        shell("PowerRoomShell", {"south": [(-42.5, 6.5)], "west": [(69, 6)], "north": [(-39, 6.5)]}, portal_owner_sides=frozenset({"south", "west", "north"})),
        shell("MaintenanceCrossPassageShell", {"west": [(69, 6)], "east": [(69, 6)]}, portal_owner_sides=frozenset()),
        shell("ServiceConnectorShell", {"south": [(-39, 6.5)], "north": [(-39, 6.5)]}, portal_owner_sides=frozenset()),
        shell("FarmServiceShell", {"south": [(-39, 6.5)], "east": [(104, 8)]}),
    ]

    architecture.extend([
        model("CommonFloorBorders", [
            part("SouthBorder", (23, 0.18, 0.7), (-58, 54.1, 31.1), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
            part("NorthBorder", (23, 0.18, 0.7), (-58, 54.1, 56.9), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
            part("WestBorder", (0.7, 0.18, 26), (-68.9, 54.1, 44), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
            part("EastBorder", (0.7, 0.18, 26), (-47.1, 54.1, 44), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
            part("RouteBandEntrance", (0.8, 0.06, 8), (-60, 54.13, 35), material="SmoothPlastic", color=YELLOW, collide=False),
            part("RouteBandResidential", (7, 0.06, 0.55), (-66.5, 54.13, 42), material="SmoothPlastic", color=GREEN, collide=False),
            part("RouteBandUtility", (7, 0.06, 0.55), (-49.5, 54.13, 42), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
        ]),
        model("CommonCeilingStructure", [
            part("WestBeam", (1.1, 1.2, 27), (-65, 67.7, 44), material="Concrete", color=CONCRETE_WORN),
            part("EastBeam", (1.1, 1.2, 27), (-51, 67.7, 44), material="Concrete", color=CONCRETE_WORN),
            part("SouthCrossBeam", (23, 0.9, 1.2), (-58, 67.8, 36), material="Metal", color=STEEL_LIGHT),
            part("NorthCrossBeam", (23, 0.9, 1.2), (-58, 67.8, 52), material="Metal", color=STEEL_LIGHT),
        ]),
    ])
    return architecture
