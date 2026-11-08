"""Localized lighting and restrained material-break details for NewBunker.

This module owns only the generated ``Lighting`` model and the shared visual-
cohesion details that are appended to ``EnvironmentDetails``.  It intentionally
does not create scripts or touch Roblox's global ``Lighting`` service.

Lighting budget
---------------
The pass creates 24 local PointLights.  Five composition-critical fixtures cast
shadows (the wake/bedroom exit pair, two common-hub anchors, and the entrance
threshold); the remaining 19 are non-shadowed fill/task lights.  Together with
the three existing power-room practicals, NewBunker stays at 27 local lights and
eight shadowed lights.  This preserves depth at the player's first impressions
without paying shadow cost in every corridor bay.

Flicker name contract
---------------------
``BunkerAtmosphereController`` selectively modulates the wake, residential,
storage, workshop-entry, service-connector, and farm-exit fixtures. These
names are a runtime contract: failures are staggered and localized rather than
a synchronized bunker-wide flicker. Keep the fixture names stable unless the
controller contract is updated in the same change.

Palette direction
-----------------
Concrete and steel remain low-chroma blue/green grays.  Muted cold fluorescent
light is the operational baseline, weak green-gray light identifies secondary
routes, and amber/red is restricted to emergency, human-use, and threshold accents.
Rust appears only on repair clips, cage guards, drip edges, and small wear
patches rather than on every fixture.
"""

from __future__ import annotations

from .kit import (
    AGED_WHITE,
    CONCRETE_DARK,
    CONCRETE_WORN,
    FLOOR_Y,
    RUST,
    STEEL,
    STEEL_LIGHT,
    model,
    part,
    point_light,
)


# Darker emitters retain visible tube form instead of clipping to white.  The
# PointLights provide the usable pool, separately and at deliberately short range.
COLD_FOCAL = [0.47, 0.59, 0.62]
COLD_OPERATIONAL = [0.38, 0.49, 0.51]
COLD_AGED = [0.27, 0.35, 0.34]
COLD_UTILITY = [0.27, 0.39, 0.42]
WARM_HUMAN = [0.55, 0.40, 0.22]
WARM_EMERGENCY = [0.50, 0.16, 0.075]
DEAD_WHITE = [0.28, 0.30, 0.28]
ROUTE_GREEN = [0.16, 0.21, 0.18]
ROUTE_BLUE = [0.13, 0.20, 0.22]
ROUTE_WARNING = [0.36, 0.25, 0.085]
ROUTE_EMERGENCY = [0.32, 0.085, 0.055]
GRIME = [0.075, 0.095, 0.09]


def _industrial_fluorescent(
    name: str,
    pos: tuple[float, float, float],
    *,
    length: float = 5.4,
    axis: str = "x",
    color: list[float] = COLD_OPERATIONAL,
    brightness: float = 1.2,
    light_range: float = 12.0,
    shadows: bool = False,
    damaged_tube: bool = False,
    repair_clip: bool = False,
) -> dict:
    """Build a recessed twin-tube practical, not a floating emissive bar."""

    x, y, z = pos
    along_x = axis == "x"

    def dims(along: float, high: float, across: float) -> tuple[float, float, float]:
        return (along, high, across) if along_x else (across, high, along)

    def offset(along: float, high: float, across: float) -> tuple[float, float, float]:
        return (x + along, y + high, z + across) if along_x else (x + across, y + high, z + along)

    children = [
        # Broad ceiling plate and ballast box visually attach the fixture.
        part("CeilingBackplate", dims(length + 1.0, 0.16, 1.65), offset(0, 0.18, 0), material="Metal", color=CONCRETE_DARK, collide=False),
        part("BallastHousing", dims(length + 0.45, 0.42, 1.25), pos, material="Metal", color=STEEL, collide=False),
        part("HousingWestRail", dims(length + 0.2, 0.18, 0.16), offset(0, -0.25, -0.57), material="Metal", color=STEEL_LIGHT, collide=False),
        part("HousingEastRail", dims(length + 0.2, 0.18, 0.16), offset(0, -0.25, 0.57), material="Metal", color=STEEL_LIGHT, collide=False),
        part("TubeA", dims(length - 0.65, 0.13, 0.22), offset(0, -0.30, -0.25), material="Neon", color=color, collide=False, cast_shadow=False,
             children=[point_light("LocalPool", color, brightness, light_range, shadows)]),
        part("TubeB", dims(length - 0.65, 0.13, 0.22), offset(0, -0.30, 0.25), material="Neon", color=DEAD_WHITE if damaged_tube else color, collide=False, cast_shadow=False),
        part("EndCapNear", dims(0.30, 0.34, 1.16), offset(-length / 2, -0.12, 0), material="Metal", color=STEEL_LIGHT, collide=False),
        part("EndCapFar", dims(0.30, 0.34, 1.16), offset(length / 2, -0.12, 0), material="Metal", color=STEEL_LIGHT, collide=False),
        part("MountNear", dims(0.28, 0.32, 1.45), offset(-length * 0.32, 0.22, 0), material="Metal", color=CONCRETE_DARK, collide=False),
        part("MountFar", dims(0.28, 0.32, 1.45), offset(length * 0.32, 0.22, 0), material="Metal", color=CONCRETE_DARK, collide=False),
    ]
    if damaged_tube:
        children.append(part("DeadTubeEnd", dims(0.55, 0.15, 0.25), offset(length * 0.30, -0.31, 0.25), material="Glass", color=AGED_WHITE, collide=False, transparency=0.35, cast_shadow=False))
    if repair_clip:
        children.append(part("OxidizedRepairClip", dims(0.34, 0.48, 1.38), offset(-length * 0.18, -0.02, 0), material="CorrodedMetal", color=RUST, collide=False))
    return model(name, children)


def _caged_wall_light(
    name: str,
    pos: tuple[float, float, float],
    *,
    face_axis: str,
    color: list[float],
    brightness: float,
    light_range: float,
    shadows: bool = False,
) -> dict:
    """Build a wall-backed utility light with a readable protective cage."""

    x, y, z = pos
    on_x_wall = face_axis == "x"
    housing_size = (0.34, 1.9, 1.35) if on_x_wall else (1.35, 1.9, 0.34)
    lens_size = (0.24, 1.18, 0.72) if on_x_wall else (0.72, 1.18, 0.24)
    bar_h_size = (0.18, 0.15, 0.95) if on_x_wall else (0.95, 0.15, 0.18)
    bar_v_size = (0.18, 1.45, 0.15) if on_x_wall else (0.15, 1.45, 0.18)
    outward = (0.24, 0, 0) if on_x_wall else (0, 0, 0.24)

    def shifted(dx: float, dy: float, dz: float) -> tuple[float, float, float]:
        return (x + dx, y + dy, z + dz)

    lens_pos = shifted(*outward)
    cage_color = STEEL_LIGHT
    return model(name, [
        part("RecessBack", housing_size, pos, material="Metal", color=STEEL, collide=False),
        part("UtilityLens", lens_size, lens_pos, material="Neon", color=color, collide=False, cast_shadow=False,
             children=[point_light("LocalPool", color, brightness, light_range, shadows)]),
        part("CageTop", bar_h_size, shifted(outward[0] * 1.45, 0.70, outward[2] * 1.45), material="Metal", color=cage_color, collide=False),
        part("CageBottom", bar_h_size, shifted(outward[0] * 1.45, -0.70, outward[2] * 1.45), material="Metal", color=cage_color, collide=False),
        part("CageRailA", bar_v_size, shifted(outward[0] * 1.45, 0, outward[2] * 1.45 - (0.37 if on_x_wall else 0)), material="Metal", color=cage_color, collide=False),
        part("CageRailB", bar_v_size, shifted(outward[0] * 1.45, 0, outward[2] * 1.45 + (0.37 if on_x_wall else 0)), material="Metal", color=cage_color, collide=False),
    ])


def build_lighting() -> list[dict]:
    """Return localized practical-light groups for all major bunker routes."""

    return [
        model("BedroomLighting", [
            # The damaged wake fixture leaves the bed side colder and less
            # reliable; the steadier exit pool remains the background draw.
            _industrial_fluorescent("WakeSideFluorescent", (-88.5, 65.72, 86.0), color=COLD_FOCAL, brightness=0.82, light_range=10.5, shadows=True, damaged_tube=True, repair_clip=True),
            _industrial_fluorescent("ExitSightlineFluorescent", (-82.0, 65.70, 76.5), length=4.8, color=COLD_OPERATIONAL, brightness=0.98, light_range=10.0, shadows=True),
            _caged_wall_light("BedroomEmergencyPractical", (-95.47, 60.6, 72.6), face_axis="x", color=WARM_EMERGENCY, brightness=0.26, light_range=5.5),
        ]),
        model("ResidentialCorridorLighting", [
            # Bright / failing / weak creates a readable suspense rhythm rather
            # than an evenly illuminated rectangular tunnel.
            _industrial_fluorescent("SouthOperationalBay", (-74.0, 64.75, 39.0), length=4.6, color=COLD_OPERATIONAL, brightness=0.62, light_range=7.8),
            _industrial_fluorescent("MiddleAgedBay", (-74.0, 64.75, 55.0), length=4.6, color=COLD_AGED, brightness=0.20, light_range=4.9, damaged_tube=True),
            _industrial_fluorescent("BedroomApproachBay", (-74.0, 64.75, 73.0), length=4.6, color=COLD_UTILITY, brightness=0.42, light_range=6.6, repair_clip=True),
        ]),
        model("CommonHubLighting", [
            # Route anchors remain legible, while their smaller pools allow the
            # perimeter and ceiling infrastructure to fall into shadow.
            _industrial_fluorescent("SouthRouteAnchor", (-63.2, 67.75, 39.0), length=6.0, axis="z", color=COLD_FOCAL, brightness=0.96, light_range=12.5, shadows=True),
            _industrial_fluorescent("NorthRouteAnchor", (-52.8, 67.75, 50.0), length=6.0, axis="z", color=COLD_OPERATIONAL, brightness=0.84, light_range=11.8, shadows=True),
            _caged_wall_light("CommonEmergencyReserve", (-69.46, 61.0, 53.5), face_axis="x", color=WARM_EMERGENCY, brightness=0.29, light_range=5.8),
        ]),
        model("WorkAndMaintenanceLighting", [
            # Keep the rear fixture subdued so the repair bench remains the
            # focal point, while the damaged entry unit reaches the threshold.
            _industrial_fluorescent("WorkshopBenchTaskLight", (-89.2, 65.75, 37.0), length=5.6, color=COLD_FOCAL, brightness=0.72, light_range=9.4, repair_clip=True),
            _industrial_fluorescent("WorkshopEntryFill", (-82.0, 65.75, 41.5), length=4.6, color=COLD_AGED, brightness=0.58, light_range=14.0, damaged_tube=True),
            _industrial_fluorescent("UpgradeRigTaskLight", (-90.0, 66.75, 57.0), length=5.6, color=COLD_UTILITY, brightness=0.92, light_range=9.8),
            _caged_wall_light("UpgradeDisconnectLight", (-95.47, 61.2, 62.7), face_axis="x", color=WARM_EMERGENCY, brightness=0.32, light_range=5.8),
            _industrial_fluorescent("StorageAisleLight", (-62.0, 64.75, 68.0), length=5.0, axis="z", color=COLD_AGED, brightness=0.52, light_range=8.5, damaged_tube=True),
        ]),
        model("UtilityWingLighting", [
            _industrial_fluorescent("EastCorridorSouthBay", (-42.5, 64.75, 41.0), length=4.4, color=COLD_UTILITY, brightness=0.44, light_range=6.6),
            _industrial_fluorescent("EastCorridorNorthBay", (-42.5, 64.75, 56.0), length=4.4, color=COLD_AGED, brightness=0.18, light_range=4.7, damaged_tube=True),
            _industrial_fluorescent("ShopCounterPractical", (-35.2, 64.75, 42.0), length=5.0, axis="z", color=WARM_HUMAN, brightness=0.54, light_range=7.6),
            _industrial_fluorescent("PowerThresholdPractical", (-47.5, 66.75, 64.0), length=4.8, axis="z", color=COLD_UTILITY, brightness=0.54, light_range=7.5),
        ]),
        model("EntranceAndServiceLighting", [
            _industrial_fluorescent("EntranceInteriorPractical", (-60.0, 65.75, 15.0), length=6.0, color=COLD_FOCAL, brightness=0.98, light_range=11.5, shadows=True),
            _caged_wall_light("BlastThresholdBeacon", (-65.46, 60.6, 9.4), face_axis="x", color=WARM_EMERGENCY, brightness=0.54, light_range=7.0),
            _industrial_fluorescent("SouthConnectorPractical", (-60.0, 64.75, 25.0), length=4.8, color=COLD_AGED, brightness=0.24, light_range=5.4, damaged_tube=True),
            _industrial_fluorescent("ServiceConnectorPractical", (-39.0, 63.75, 88.0), length=4.2, color=COLD_UTILITY, brightness=0.30, light_range=5.7, damaged_tube=True),
            _industrial_fluorescent("FarmAirlockPractical", (-39.0, 64.75, 102.0), length=5.2, color=COLD_OPERATIONAL, brightness=0.58, light_range=8.0),
            _caged_wall_light("FarmExitEmergencyPractical", (-30.47, 60.4, 108.4), face_axis="x", color=WARM_EMERGENCY, brightness=0.30, light_range=5.5),
        ]),
    ]


def build_material_details() -> list[dict]:
    """Return sparse wear/material breaks kept off primary collision lanes."""

    return [
        model("ConcreteMoistureAndRepairBreaks", [
            part("BedroomNorthDampBloom", (4.8, 2.2, 0.035), (-88.5, 56.2, 95.48), material="Concrete", color=GRIME, collide=False, transparency=0.36, rot=(0, 0, -3), cast_shadow=False),
            part("BedroomWestSpall", (0.035, 3.2, 2.7), (-95.48, 58.4, 91.2), material="Concrete", color=CONCRETE_WORN, collide=False, transparency=0.28, rot=(5, 0, 0), cast_shadow=False),
            part("CommonSouthWaterMark", (5.4, 2.6, 0.035), (-54.2, 56.5, 30.49), material="Concrete", color=GRIME, collide=False, transparency=0.40, rot=(0, 0, 2), cast_shadow=False),
            part("StorageNorthDampLine", (5.2, 0.8, 0.035), (-60.8, 54.7, 77.49), material="Concrete", color=GRIME, collide=False, transparency=0.43, cast_shadow=False),
            part("ServiceEastWaterTrack", (0.035, 4.8, 2.1), (-35.49, 57.1, 91.0), material="Concrete", color=GRIME, collide=False, transparency=0.38, rot=(4, 0, 0), cast_shadow=False),
            part("BedroomLeakSheen", (3.6, 0.018, 1.35), (-88.2, FLOOR_Y + 0.016, 93.4), material="Glass", color=[0.07, 0.095, 0.09], collide=False, transparency=0.72, rot=(0, -7, 0), cast_shadow=False),
            part("StorageDrainSheen", (4.2, 0.018, 0.82), (-60.8, FLOOR_Y + 0.016, 75.9), material="Glass", color=[0.06, 0.085, 0.08], collide=False, transparency=0.75, rot=(0, 3, 0), cast_shadow=False),
            part("ServiceRunoffSheen", (1.7, 0.018, 4.2), (-39.0, FLOOR_Y + 0.016, 98.9), material="Glass", color=[0.055, 0.08, 0.075], collide=False, transparency=0.70, rot=(0, -4, 0), cast_shadow=False),
        ]),
        model("SelectiveMetalOxidation", [
            part("BedroomThresholdOxidation", (0.14, 0.12, 2.4), (-77.32, FLOOR_Y + 0.13, 73.7), material="CorrodedMetal", color=RUST, collide=False, transparency=0.18, cast_shadow=False),
            part("CommonCanopyDripEdge", (4.6, 0.14, 0.10), (-58.0, 65.63, 44.9), material="CorrodedMetal", color=RUST, collide=False, transparency=0.20, cast_shadow=False),
            part("WorkshopBenchWearEdge", (0.10, 0.22, 4.6), (-94.52, 57.4, 37.0), material="CorrodedMetal", color=RUST, collide=False, transparency=0.15, cast_shadow=False),
            part("ShopCounterHandWear", (0.08, 0.18, 4.0), (-34.48, 57.28, 42.0), material="CorrodedMetal", color=AGED_WHITE, collide=False, transparency=0.28, cast_shadow=False),
            part("EntranceHeaderRunoff", (3.6, 0.16, 0.08), (-60.0, 64.15, 8.47), material="CorrodedMetal", color=RUST, collide=False, transparency=0.20, cast_shadow=False),
        ]),
        model("FloorUseAndMaintenanceTraces", [
            part("WakeFootScuff", (2.1, 0.025, 3.6), (-84.4, FLOOR_Y + 0.02, 84.2), material="Concrete", color=GRIME, collide=False, transparency=0.50, rot=(0, -8, 0), cast_shadow=False),
            part("CommonCrossingWear", (3.1, 0.025, 7.0), (-58.0, FLOOR_Y + 0.02, 44.0), material="Concrete", color=CONCRETE_WORN, collide=False, transparency=0.60, rot=(0, 3, 0), cast_shadow=False),
            part("WorkshopOilShadow", (3.2, 0.025, 1.9), (-90.2, FLOOR_Y + 0.02, 40.7), material="SmoothPlastic", color=[0.045, 0.052, 0.05], collide=False, transparency=0.38, rot=(0, 14, 0), cast_shadow=False),
            part("UpgradeHydraulicStain", (2.5, 0.025, 1.4), (-89.2, FLOOR_Y + 0.02, 60.2), material="SmoothPlastic", color=[0.045, 0.06, 0.058], collide=False, transparency=0.36, rot=(0, -18, 0), cast_shadow=False),
            part("StorageCartWheelTrace", (0.28, 0.022, 8.5), (-62.7, FLOOR_Y + 0.018, 68.0), material="Concrete", color=GRIME, collide=False, transparency=0.58, rot=(0, 2, 0), cast_shadow=False),
            part("ServiceDrainRunoff", (2.2, 0.025, 4.8), (-39.0, FLOOR_Y + 0.02, 98.8), material="Concrete", color=GRIME, collide=False, transparency=0.48, rot=(0, -4, 0), cast_shadow=False),
        ]),
        model("FunctionalColorDiscipline", [
            # Small desaturated backplates tie recurring route colors to
            # function without turning full walls or floors into colored zones.
            part("ResidentialRoutePlate", (0.10, 1.25, 2.2), (-77.47, 60.2, 79.0), material="Metal", color=ROUTE_GREEN, collide=False),
            part("UtilityRoutePlate", (0.10, 1.25, 2.2), (-45.47, 60.2, 57.5), material="Metal", color=ROUTE_BLUE, collide=False),
            part("MaintenanceWarningPlate", (0.10, 0.42, 2.2), (-95.47, 58.0, 61.5), material="SmoothPlastic", color=ROUTE_WARNING, collide=False, transparency=0.18, cast_shadow=False),
            part("EmergencyThresholdPlate", (0.10, 0.42, 2.2), (-65.47, 58.0, 9.4), material="SmoothPlastic", color=ROUTE_EMERGENCY, collide=False, transparency=0.18, cast_shadow=False),
        ]),
    ]
