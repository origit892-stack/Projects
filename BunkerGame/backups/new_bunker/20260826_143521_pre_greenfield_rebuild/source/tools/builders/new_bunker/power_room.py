"""Power-room machinery, electrical infrastructure, and reserved systems bays.

This module owns only ``NewBunker/PowerRoom`` and its composition markers.
It does not copy or migrate the protected legacy Processor, BatteryButton, or
BunkerLights systems.  The room instead reserves clearly separated locations
for a later, dependency-audited migration.

Circulation plan (all coordinates are staging-world coordinates):

* south portal at X=-42.5, Z=60 enters a 6.5-stud opening;
* a 5.2-stud maintenance aisle runs beside the west panel bank at X=-49.7..-44.5;
* the west cross-passage joins that aisle at Z=69;
* the aisle turns east behind the generator set to the north service portal;
* the southeast Processor reserve is outside that route at X=-37.5..-31.5.

Director camera: (-49.0, 60.2, 62.8) -> (-37.5, 59.0, 72.5).  This frames
the layered panel bank on the left, generator silhouettes in depth, and the
blue-lit service route beyond.
"""

from __future__ import annotations

from .kit import (
    AGED_WHITE,
    CONCRETE_DARK,
    CONCRETE_WORN,
    FLOOR_Y,
    GREEN,
    LIGHT_COLD,
    LIGHT_WARM,
    RED,
    RUST,
    STEEL,
    STEEL_LIGHT,
    UTILITY_BLUE,
    YELLOW,
    fluorescent,
    model,
    part,
    pipe,
    point_light,
)


def _panel_bank() -> dict:
    """Layered switchgear with real cabinet depth and readable service rhythm."""

    children: list[dict] = []
    # The Z=66..72 gap is the actual west cross-passage opening.  Both the
    # backing and cabinets stop short of it; no decorative layer seals it.
    for section, z, depth in (("South", 63.2, 5.4), ("North", 76.0, 8.0)):
        children.extend([
            part(f"{section}RaisedConcreteCurb", (1.35, 0.55, depth), (-50.72, FLOOR_Y + 0.275, z), material="Concrete", color=CONCRETE_WORN),
            part(f"{section}PanelBankBack", (0.65, 8.6, depth - 0.25), (-51.02, 58.55, z), material="Metal", color=CONCRETE_DARK),
            part(f"{section}UpperCableGutter", (1.15, 1.0, depth), (-50.68, 63.35, z), material="Metal", color=STEEL),
            part(f"{section}LowerCableGutter", (1.10, 0.75, depth), (-50.70, 54.85, z), material="CorrodedMetal", color=STEEL),
        ])
    for index, (z, door_color) in enumerate(((62.2, GREEN), (64.7, STEEL), (73.3, GREEN), (75.9, STEEL), (78.5, GREEN)), 1):
        children.append(model(f"SwitchgearCabinet{index:02d}", [
            part("CabinetBody", (1.12, 7.55, 2.25), (-50.58, 58.85, z), material="Metal", color=door_color),
            part("DoorInset", (0.12, 6.55, 1.82), (-49.96, 58.85, z), material="Metal", color=[0.19, 0.22, 0.21], collide=False),
            part("DoorFrameTop", (0.12, 0.16, 2.02), (-49.88, 62.18, z), material="Metal", color=STEEL_LIGHT, collide=False),
            part("DoorFrameBottom", (0.12, 0.16, 2.02), (-49.88, 55.52, z), material="Metal", color=STEEL_LIGHT, collide=False),
            part("BreakerRowUpper", (0.10, 0.30, 1.10), (-49.80, 60.15, z), material="SmoothPlastic", color=AGED_WHITE, collide=False),
            part("BreakerRowLower", (0.10, 0.30, 1.10), (-49.80, 59.45, z), material="SmoothPlastic", color=AGED_WHITE, collide=False),
            part("WarningPlate", (0.10, 0.90, 0.90), (-49.79, 61.15, z), material="SmoothPlastic", color=YELLOW, collide=False, rot=(45, 0, 0), cast_shadow=False),
            part("Latch", (0.16, 0.82, 0.16), (-49.74, 57.7, z - 0.62), material="Metal", color=STEEL_LIGHT, collide=False),
            part("BottomVent", (0.10, 1.15, 1.52), (-49.79, 56.45, z), material="Metal", color=CONCRETE_DARK, collide=False),
            part("VentSlatA", (0.08, 0.08, 1.30), (-49.72, 56.75, z), material="Metal", color=STEEL_LIGHT, collide=False),
            part("VentSlatB", (0.08, 0.08, 1.30), (-49.72, 56.42, z), material="Metal", color=STEEL_LIGHT, collide=False),
            part("VentSlatC", (0.08, 0.08, 1.30), (-49.72, 56.09, z), material="Metal", color=STEEL_LIGHT, collide=False),
        ]))
    return model("LayeredElectricalPanelBank", children)


def _generator_unit(name: str, x: float, accent: list[float], wear: bool = False) -> dict:
    """Create one coherent diesel-generator silhouette within the shared plinth."""

    body_color = [0.20, 0.25, 0.22] if not wear else [0.21, 0.22, 0.19]
    return model(name, [
        part("EngineBlock", (4.15, 3.25, 5.2), (x, 56.7, 72.0), material="Metal", color=body_color),
        part("UpperCylinderHead", (3.55, 1.35, 4.35), (x, 59.0, 72.0), material="CorrodedMetal" if wear else "Metal", color=STEEL_LIGHT),
        part("TopServiceCover", (3.85, 0.28, 4.65), (x, 59.8, 72.0), material="DiamondPlate", color=STEEL),
        part("FrontHousing", (3.25, 2.5, 1.0), (x, 57.15, 69.0), material="Metal", color=STEEL),
        pipe("Flywheel", (x, 57.05, 68.42), 0.7, "z", 2.45, STEEL_LIGHT),
        pipe("FlywheelHub", (x, 57.05, 67.98), 0.92, "z", 0.66, accent),
        part("RearRadiator", (3.65, 3.2, 0.75), (x, 57.1, 74.95), material="Metal", color=CONCRETE_DARK),
        part("RadiatorSlat01", (2.95, 0.16, 0.10), (x, 58.05, 75.36), material="Metal", color=STEEL_LIGHT, collide=False),
        part("RadiatorSlat02", (2.95, 0.16, 0.10), (x, 57.45, 75.36), material="Metal", color=STEEL_LIGHT, collide=False),
        part("RadiatorSlat03", (2.95, 0.16, 0.10), (x, 56.85, 75.36), material="Metal", color=STEEL_LIGHT, collide=False),
        part("RadiatorSlat04", (2.95, 0.16, 0.10), (x, 56.25, 75.36), material="Metal", color=STEEL_LIGHT, collide=False),
        part("ServiceBox", (2.3, 1.65, 0.70), (x, 58.3, 68.72), material="Metal", color=GREEN),
        part("GaugeFace", (0.16, 0.78, 0.78), (x - 0.55, 58.45, 68.31), material="SmoothPlastic", color=AGED_WHITE, collide=False, shape="Cylinder"),
        part("GaugeNeedle", (0.08, 0.42, 0.10), (x - 0.61, 58.45, 68.20), material="SmoothPlastic", color=RED, collide=False, rot=(0, 0, -24), cast_shadow=False),
        part("StatusLamp", (0.12, 0.34, 0.34), (x + 0.58, 58.55, 68.30), material="Neon", color=accent, collide=False, cast_shadow=False),
        pipe("ExhaustStack", (x + 1.25, 62.3, 73.2), 5.3, "y", 0.56, STEEL_LIGHT),
        part("ExhaustCap", (0.95, 0.22, 0.95), (x + 1.25, 64.95, 73.2), material="CorrodedMetal", color=RUST, collide=False),
        part("VibrationFootWest", (0.85, 0.45, 1.4), (x - 1.35, 54.68, 70.2), material="CorrodedMetal", color=STEEL),
        part("VibrationFootEast", (0.85, 0.45, 1.4), (x + 1.35, 54.68, 70.2), material="CorrodedMetal", color=STEEL),
        part("SideInspectionPlate", (2.2, 1.35, 0.12), (x, 56.55, 74.64), material="CorrodedMetal" if wear else "Metal", color=RUST if wear else STEEL_LIGHT, collide=False),
    ])


def _generator_set() -> dict:
    return model("TwinDieselGeneratorSet", [
        # The north edge stops at Z=75.9, preserving 5.6 studs between the
        # plinth and north wall for the turn into the service connector.
        part("GeneratorPlinth", (11.8, 0.72, 8.4), (-38.6, 54.36, 71.7), material="Concrete", color=CONCRETE_WORN),
        part("PlinthSteelEdgeSouth", (11.5, 0.32, 0.28), (-38.6, 54.62, 67.55), material="CorrodedMetal", color=RUST, collide=False),
        part("PlinthSteelEdgeNorth", (11.5, 0.32, 0.28), (-38.6, 54.62, 75.85), material="Metal", color=STEEL_LIGHT, collide=False),
        _generator_unit("GeneratorA", -41.45, UTILITY_BLUE),
        _generator_unit("GeneratorB", -36.15, RED, wear=True),
        model("SharedFuelAndExhaustHeader", [
            pipe("FuelHeader", (-38.8, 63.8, 76.4), 7.8, "x", 0.34, YELLOW),
            pipe("FuelDropA", (-41.45, 61.8, 76.4), 4.0, "y", 0.28, YELLOW),
            pipe("FuelDropB", (-36.15, 61.8, 76.4), 4.0, "y", 0.28, YELLOW),
            part("HeaderIsolationValve", (0.18, 1.25, 1.25), (-38.8, 63.8, 76.4), material="CorrodedMetal", color=RED, collide=False, shape="Cylinder"),
        ]),
    ])


def _overhead_distribution() -> dict:
    """Cable trays terminate visibly at panels, generators, and service exit."""

    children: list[dict] = [
        part("WestMainTray", (1.0, 0.45, 17.0), (-48.6, 65.45, 70.0), material="Metal", color=STEEL_LIGHT, collide=False),
        part("GeneratorBranchTray", (10.0, 0.45, 1.0), (-43.1, 65.45, 75.8), material="Metal", color=STEEL_LIGHT, collide=False),
        part("ServiceExitTray", (1.0, 0.45, 7.0), (-39.0, 65.45, 78.2), material="Metal", color=STEEL_LIGHT, collide=False),
        part("TrayCableDark", (0.18, 0.15, 16.2), (-48.82, 65.52, 70.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False),
        part("TrayCableBlue", (0.18, 0.15, 16.2), (-48.47, 65.52, 70.0), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
        part("TrayCableRed", (9.2, 0.15, 0.18), (-43.1, 65.52, 75.98), material="SmoothPlastic", color=RED, collide=False),
        pipe("PanelTermination", (-49.0, 64.3, 64.7), 2.3, "y", 0.28, UTILITY_BLUE),
        pipe("GeneratorTerminationA", (-41.45, 64.45, 75.8), 2.0, "y", 0.30, RED),
        pipe("GeneratorTerminationB", (-36.15, 64.45, 75.8), 2.0, "y", 0.30, RED),
    ]
    for index, x in enumerate((-47.4, -44.7, -42.0, -39.3), 1):
        children.append(model(f"BusInsulatorSet{index:02d}", [
            part("CeramicBody", (0.45, 0.62, 0.45), (x, 64.75, 61.0), material="SmoothPlastic", color=AGED_WHITE, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("BusBar", (2.2, 0.16, 0.24), (x, 65.1, 61.0), material="Metal", color=YELLOW, collide=False),
        ]))
    return model("OverheadPowerDistribution", children)


def _maintenance_and_reserves() -> dict:
    """Mark safe working envelopes without placing gameplay dependencies."""

    return model("MaintenanceClearancesAndFutureBays", [
        part("WestAisleEdge", (0.16, 0.06, 15.5), (-44.95, 54.10, 70.0), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.18, cast_shadow=False),
        part("GeneratorServiceEdge", (12.0, 0.06, 0.16), (-38.8, 54.10, 66.95), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.18, cast_shadow=False),
        part("ProcessorBayDeck", (6.2, 0.10, 4.6), (-34.6, 54.11, 63.8), material="DiamondPlate", color=STEEL, collide=False),
        part("ProcessorBayWestEdge", (0.18, 0.08, 4.4), (-37.65, 54.18, 63.8), material="SmoothPlastic", color=UTILITY_BLUE, collide=False, cast_shadow=False),
        part("ProcessorBayEastEdge", (0.18, 0.08, 4.4), (-31.55, 54.18, 63.8), material="SmoothPlastic", color=UTILITY_BLUE, collide=False, cast_shadow=False),
        part("ProcessorBayHeader", (6.2, 0.55, 0.55), (-34.6, 63.7, 66.05), material="Metal", color=STEEL_LIGHT, collide=False),
        part("ProcessorReservePlate", (3.8, 0.65, 0.10), (-34.6, 62.75, 66.34), material="Metal", color=UTILITY_BLUE, collide=False),
        part("BatteryControlBackplate", (0.12, 2.8, 2.3), (-30.53, 58.1, 78.0), material="Metal", color=GREEN, collide=False),
        part("BatteryWarningStripe", (0.08, 0.34, 1.8), (-30.45, 58.65, 78.0), material="SmoothPlastic", color=YELLOW, collide=False, rot=(35, 0, 0), cast_shadow=False),
        part("LightsControlBackplate", (0.12, 2.8, 2.3), (-30.53, 58.1, 80.7), material="Metal", color=STEEL, collide=False),
        part("LightsEmergencyStripe", (0.08, 0.34, 1.8), (-30.45, 58.65, 80.7), material="SmoothPlastic", color=RED, collide=False, rot=(-35, 0, 0), cast_shadow=False),
    ])


def _localized_lighting() -> dict:
    """Modeled, local-only task and emergency fixtures; no global Lighting edits."""

    return model("PowerRoomLocalizedLighting", [
        fluorescent("PanelBankTaskLight", (-46.8, 66.4, 68.0), LIGHT_COLD, brightness=1.45, light_range=13),
        fluorescent("GeneratorTaskLight", (-38.8, 66.4, 72.0), [0.58, 0.70, 0.73], brightness=1.2, light_range=12),
        model("NorthEmergencyCageLight", [
            part("WallMount", (0.75, 1.8, 0.65), (-31.0, 61.8, 79.8), material="Metal", color=STEEL),
            part("CageGlow", (0.48, 1.15, 0.48), (-30.62, 61.8, 79.8), material="Neon", color=LIGHT_WARM, collide=False, cast_shadow=False, children=[point_light("EmergencyPool", LIGHT_WARM, 0.85, 9.0, True)]),
            part("CageBarTop", (0.16, 0.16, 0.80), (-30.35, 62.35, 79.8), material="Metal", color=RUST, collide=False),
            part("CageBarBottom", (0.16, 0.16, 0.80), (-30.35, 61.25, 79.8), material="Metal", color=RUST, collide=False),
        ]),
    ])


def _restrained_wear() -> dict:
    return model("PowerRoomWearDetails", [
        part("PanelOxidationEdge", (0.10, 0.55, 7.0), (-49.72, 54.65, 70.0), material="CorrodedMetal", color=RUST, collide=False, transparency=0.16),
        part("OilStain", (4.2, 0.025, 2.2), (-36.2, 54.02, 77.2), material="SmoothPlastic", color=[0.055, 0.065, 0.06], collide=False, transparency=0.25, cast_shadow=False, rot=(0, 11, 0)),
        part("DiscardedAccessGrille", (2.6, 0.12, 1.5), (-47.0, 54.14, 79.0), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, -18, 0)),
        part("LooseCable", (0.15, 0.15, 3.2), (-46.6, 54.18, 78.1), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 22, 0)),
    ])


def _generator_cooling_manifold() -> dict:
    """Layered cooling hardware above the generator mass, outside player lanes."""

    return model("GeneratorCoolingManifold", [
        pipe("CoolingHeader", (-38.8, 64.7, 69.0), 8.6, "x", 0.64, STEEL_LIGHT),
        part("HeaderCollarWest", (0.38, 0.92, 0.92), (-42.5, 64.7, 69.0), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("HeaderCollarEast", (0.38, 0.92, 0.92), (-35.1, 64.7, 69.0), material="Metal", color=STEEL, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        pipe("GeneratorADrop", (-41.45, 62.6, 69.0), 3.8, "y", 0.46, UTILITY_BLUE),
        pipe("GeneratorBDrop", (-36.15, 62.6, 69.0), 3.8, "y", 0.46, RUST),
        part("IsolationWheelA", (0.16, 1.28, 1.28), (-41.45, 63.75, 69.0), material="CorrodedMetal", color=YELLOW, collide=False, shape="Cylinder"),
        part("IsolationWheelB", (0.16, 1.28, 1.28), (-36.15, 63.75, 69.0), material="CorrodedMetal", color=RED, collide=False, shape="Cylinder"),
        part("WestBrace", (0.24, 2.8, 0.24), (-43.0, 65.2, 69.0), material="Metal", color=STEEL, collide=False, rot=(0, 0, -22)),
        part("EastBrace", (0.24, 2.8, 0.24), (-34.6, 65.2, 69.0), material="Metal", color=STEEL, collide=False, rot=(0, 0, 22)),
        part("ServiceTag", (2.1, 0.38, 0.08), (-38.8, 64.0, 68.62), material="SmoothPlastic", color=AGED_WHITE, collide=False, transparency=0.18, cast_shadow=False),
    ])


def build_power_room() -> list[dict]:
    """Return the complete power-room dressing, with all routes kept open."""

    return [
        _panel_bank(),
        _generator_set(),
        _overhead_distribution(),
        _maintenance_and_reserves(),
        _localized_lighting(),
        _restrained_wear(),
        _generator_cooling_manifold(),
    ]


def power_markers() -> list[dict]:
    """Return non-colliding markers for future dependency-audited migrations."""

    return [
        part("FutureProcessorMarker", (6.0, 0.12, 4.4), (-34.6, FLOOR_Y + 0.18, 63.8), material="SmoothPlastic", color=UTILITY_BLUE, collide=False, transparency=1.0, cast_shadow=False),
        part("FutureBatteryButtonMarker", (0.12, 2.0, 2.0), (-30.42, 58.1, 78.0), material="SmoothPlastic", color=YELLOW, collide=False, transparency=1.0, cast_shadow=False),
        part("FutureBunkerLightsControlMarker", (0.12, 2.0, 2.0), (-30.42, 58.1, 80.7), material="SmoothPlastic", color=RED, collide=False, transparency=1.0, cast_shadow=False),
    ]
