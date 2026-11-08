"""Central common hub geometry and composition.

The hub occupies X=-70..-46 and Z=30..58.  Props deliberately stay outside
the four circulation lanes so the room reads as a junction from player height:

* entrance lane: X=-64..-56, Z=30..38 (8 studs clear)
* west/east cross-axis: Z=38..46, X=-70..-46 (8 studs clear)
* storage lane: X=-66..-58, Z=46..58 (8 studs clear)

Director-review cameras (position -> target):

* wide: (-68, 61.5, 34) -> (-54, 58.5, 49)
* player eye: (-60, 59.4, 33) -> (-55, 59.0, 49)
* route check: (-48, 59.4, 42) -> (-69, 58.6, 42)

The compact utilities landmark is offset into the northeast pocket instead of
blocking the route crossing.  Its light and overhead frame provide the visual
anchor while circulation remains legible through negative space.
"""

from __future__ import annotations

from .kit import (
    AGED_WHITE,
    CONCRETE,
    CONCRETE_DARK,
    CONCRETE_WORN,
    FLOOR_Y,
    GREEN,
    RUST,
    STEEL,
    STEEL_LIGHT,
    UTILITY_BLUE,
    WOOD,
    YELLOW,
    crate,
    model,
    part,
    pipe,
)


def _portal_identity() -> dict:
    """High, non-obstructing route cues integrated with the architecture."""

    return model("CommonRouteIdentity", [
        model("EntranceRouteHeader", [
            part("ServiceLintel", (8.2, 0.55, 0.8), (-60, 64.9, 31.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("FadedDirectionPlate", (3.8, 0.8, 0.10), (-60, 63.9, 30.53), material="Metal", color=GREEN, collide=False),
            part("DirectionMark", (1.8, 0.16, 0.06), (-60, 63.9, 30.45), material="SmoothPlastic", color=AGED_WHITE, collide=False, cast_shadow=False),
        ]),
        model("ResidentialRouteHeader", [
            part("ServiceLintel", (0.8, 0.55, 8.2), (-69.0, 64.9, 42.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("FadedDirectionPlate", (0.10, 0.8, 3.8), (-69.47, 63.9, 42.0), material="Metal", color=GREEN, collide=False),
            part("DirectionMark", (0.06, 0.16, 1.8), (-69.55, 63.9, 42.0), material="SmoothPlastic", color=AGED_WHITE, collide=False, cast_shadow=False),
        ]),
        model("UtilityRouteHeader", [
            part("ServiceLintel", (0.8, 0.55, 8.2), (-47.0, 64.9, 42.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("FadedDirectionPlate", (0.10, 0.8, 3.8), (-46.53, 63.9, 42.0), material="Metal", color=UTILITY_BLUE, collide=False),
            part("DirectionMark", (0.06, 0.16, 1.8), (-46.45, 63.9, 42.0), material="SmoothPlastic", color=AGED_WHITE, collide=False, cast_shadow=False),
        ]),
        model("StorageRouteHeader", [
            part("ServiceLintel", (8.2, 0.55, 0.8), (-62, 64.9, 57.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("FadedDirectionPlate", (3.8, 0.8, 0.10), (-62, 63.9, 57.47), material="Metal", color=YELLOW, collide=False),
            part("DirectionMark", (1.8, 0.16, 0.06), (-62, 63.9, 57.55), material="SmoothPlastic", color=AGED_WHITE, collide=False, cast_shadow=False),
        ]),
    ])


def _offset_utilities_landmark() -> dict:
    """Compact focal infrastructure in the northeast visual pocket."""

    return model("OffsetCommonUtilitiesLandmark", [
        part("RoundFooting", (0.55, 4.2, 4.2), (-52.3, 54.28, 50.2), material="Concrete", color=CONCRETE_WORN, shape="Cylinder", rot=(0, 0, 90)),
        part("RoundColumn", (7.6, 1.35, 1.35), (-52.3, 58.1, 50.2), material="Metal", color=STEEL, shape="Cylinder", rot=(0, 0, 90)),
        part("LowerCollar", (0.55, 2.2, 2.2), (-52.3, 55.0, 50.2), material="CorrodedMetal", color=RUST, shape="Cylinder", rot=(0, 0, 90)),
        part("UpperCollar", (0.55, 2.05, 2.05), (-52.3, 61.1, 50.2), material="Metal", color=STEEL_LIGHT, shape="Cylinder", rot=(0, 0, 90)),
        part("UtilityCabinet", (2.8, 3.9, 1.25), (-50.9, 57.1, 50.2), material="Metal", color=GREEN),
        part("InsetPanel", (0.10, 2.9, 2.15), (-50.24, 57.2, 50.2), material="CorrodedMetal", color=CONCRETE_DARK, collide=False),
        part("DeadGauge", (0.08, 0.58, 0.58), (-50.17, 57.75, 49.65), material="SmoothPlastic", color=AGED_WHITE, collide=False, shape="Cylinder"),
        part("StatusLamp", (0.12, 0.36, 0.36), (-50.16, 58.15, 50.55), material="Neon", color=UTILITY_BLUE, collide=False, cast_shadow=False),
        part("MaintenanceLabel", (0.08, 0.28, 1.25), (-50.15, 56.25, 50.2), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
        pipe("OverheadFeed", (-52.3, 65.3, 50.2), 7.4, "y", 0.38, UTILITY_BLUE),
        pipe("CeilingBranch", (-55.1, 66.5, 50.2), 5.6, "x", 0.38, UTILITY_BLUE),
        part("HangingCable", (0.14, 3.4, 0.14), (-51.45, 63.2, 50.6), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, -7)),
    ])


def _common_life() -> dict:
    """Human-use clusters leave the crossing empty and frame it from the edges."""

    return model("CommonLifeEvidence", [
        model("SouthwestMessNook", [
            part("TableTop", (5.6, 0.45, 2.8), (-66.8, 56.8, 33.8), material="WoodPlanks", color=WOOD),
            part("TableLegWest", (0.45, 2.7, 2.2), (-68.9, 55.4, 33.8), material="Metal", color=STEEL),
            part("TableLegEast", (0.45, 2.7, 2.2), (-64.7, 55.4, 33.8), material="Metal", color=STEEL),
            part("OldRadioBody", (1.8, 1.05, 1.0), (-67.6, 57.55, 33.8), material="Metal", color=GREEN, collide=False),
            part("RadioDial", (0.16, 0.38, 0.38), (-66.65, 57.55, 33.5), material="SmoothPlastic", color=YELLOW, collide=False, shape="Cylinder"),
            part("TinMug", (0.6, 0.65, 0.6), (-65.3, 57.35, 33.6), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("FoldedMap", (1.5, 0.05, 1.0), (-66.2, 57.05, 34.2), material="SmoothPlastic", color=AGED_WHITE, collide=False, rot=(0, -12, 0), cast_shadow=False),
        ]),
        model("SoutheastRestNook", [
            part("BenchSeat", (5.8, 0.48, 2.0), (-49.6, 56.0, 34.0), material="WoodPlanks", color=WOOD),
            part("BenchBack", (5.8, 2.4, 0.35), (-49.6, 57.3, 32.95), material="WoodPlanks", color=WOOD),
            part("BenchLeftLeg", (0.42, 2.0, 1.5), (-51.8, 55.0, 34.0), material="Metal", color=STEEL),
            part("BenchRightLeg", (0.42, 2.0, 1.5), (-47.4, 55.0, 34.0), material="Metal", color=STEEL),
            part("DiscardedCloth", (2.0, 0.18, 1.5), (-50.5, 56.3, 34.0), material="Fabric", color=GREEN, collide=False, rot=(0, 8, 3)),
        ]),
        model("NorthwestWaitingNook", [
            part("BenchSeat", (2.0, 0.48, 6.2), (-67.8, 56.0, 51.8), material="WoodPlanks", color=WOOD),
            part("BenchBack", (0.35, 2.4, 6.2), (-68.85, 57.3, 51.8), material="WoodPlanks", color=WOOD),
            part("BenchNearLeg", (1.5, 2.0, 0.42), (-67.8, 55.0, 49.5), material="Metal", color=STEEL),
            part("BenchFarLeg", (1.5, 2.0, 0.42), (-67.8, 55.0, 54.1), material="Metal", color=STEEL),
            part("DroppedBottle", (0.34, 1.1, 0.34), (-66.5, 54.25, 54.8), material="Glass", color=[0.18, 0.28, 0.23], collide=False, shape="Cylinder", rot=(0, 0, 78)),
        ]),
        crate("CommonEmergencyCrate", (-48.4, 55.0, 54.8), (2.5, 2.0, 2.2)),
        part("MaintenanceBucket", (1.2, 1.4, 1.2), (-48.7, 54.7, 52.8), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 0, 90)),
    ])


def _architectural_rhythm() -> dict:
    """Perimeter buttresses and a suspended canopy give the hub its silhouette."""

    return model("CommonArchitecturalRhythm", [
        model("SouthwestButtress", [
            part("ConcretePier", (1.25, 9.2, 1.7), (-68.5, 58.6, 32.2), material="Concrete", color=CONCRETE_WORN),
            part("SteelFoot", (1.65, 0.7, 2.1), (-68.5, 54.35, 32.2), material="Metal", color=STEEL_LIGHT),
        ]),
        model("SoutheastButtress", [
            part("ConcretePier", (1.25, 9.2, 1.7), (-47.5, 58.6, 32.2), material="Concrete", color=CONCRETE_WORN),
            part("SteelFoot", (1.65, 0.7, 2.1), (-47.5, 54.35, 32.2), material="Metal", color=STEEL_LIGHT),
        ]),
        model("NorthwestButtress", [
            part("ConcretePier", (1.25, 9.2, 1.7), (-68.5, 58.6, 55.8), material="Concrete", color=CONCRETE_WORN),
            part("SteelFoot", (1.65, 0.7, 2.1), (-68.5, 54.35, 55.8), material="Metal", color=STEEL_LIGHT),
        ]),
        model("NortheastButtress", [
            part("ConcretePier", (1.25, 9.2, 1.7), (-47.5, 58.6, 55.8), material="Concrete", color=CONCRETE_WORN),
            part("SteelFoot", (1.65, 0.7, 2.1), (-47.5, 54.35, 55.8), material="Metal", color=STEEL_LIGHT),
        ]),
        model("SuspendedCanopy", [
            part("WestRail", (0.55, 0.6, 12.5), (-63.8, 66.0, 44.5), material="Metal", color=STEEL_LIGHT, collide=False),
            part("EastRail", (0.55, 0.6, 12.5), (-52.2, 66.0, 44.5), material="Metal", color=STEEL_LIGHT, collide=False),
            part("SouthRail", (12.1, 0.6, 0.55), (-58.0, 66.0, 38.5), material="Metal", color=STEEL_LIGHT, collide=False),
            part("NorthRail", (12.1, 0.6, 0.55), (-58.0, 66.0, 50.5), material="Metal", color=STEEL_LIGHT, collide=False),
            part("InsetCeilingPanelWest", (4.8, 0.22, 9.5), (-61.0, 66.15, 44.5), material="Metal", color=CONCRETE_DARK, collide=False),
            part("InsetCeilingPanelEast", (4.8, 0.22, 9.5), (-55.0, 66.15, 44.5), material="Metal", color=CONCRETE_DARK, collide=False),
            part("ColdLightDiffuser", (4.8, 0.16, 0.75), (-58.0, 65.72, 44.5), material="Neon", color=[0.62, 0.76, 0.80], collide=False, cast_shadow=False),
        ]),
        model("NorthWallRepair", [
            part("RepairPlate", (4.0, 3.5, 0.14), (-50.2, 59.2, 57.43), material="CorrodedMetal", color=RUST, collide=False),
            part("RepairBraceLeft", (0.22, 4.0, 0.18), (-51.7, 59.2, 57.32), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, 8)),
            part("RepairBraceRight", (0.22, 4.0, 0.18), (-48.7, 59.2, 57.32), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -8)),
        ]),
    ])


def _overhead_infrastructure() -> dict:
    return model("CommonOverheadInfrastructure", [
        pipe("MainWaterFeed", (-58.0, 66.75, 34.0), 17.0, "x", 0.42, UTILITY_BLUE),
        pipe("OldReturnFeed", (-58.0, 66.1, 34.0), 17.0, "x", 0.28, RUST),
        part("NorthCableTray", (13.5, 0.35, 0.9), (-53.3, 66.5, 54.2), material="Metal", color=STEEL_LIGHT, collide=False),
        part("CableRunDark", (12.8, 0.12, 0.16), (-53.3, 66.25, 54.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False),
        part("CableRunBlue", (12.8, 0.12, 0.16), (-53.3, 66.25, 54.35), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
    ])


def _common_ventilation_drop() -> dict:
    """Asymmetric overhead ventilation focal point kept above circulation."""

    return model("CommonVentilationDrop", [
        pipe("MainDuctBarrel", (-64.8, 65.15, 52.8), 6.6, "x", 1.45, STEEL_LIGHT),
        part("WestMountCollar", (0.42, 1.78, 1.78), (-67.7, 65.15, 52.8), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("EastMountCollar", (0.42, 1.72, 1.72), (-61.9, 65.15, 52.8), material="Metal", color=STEEL, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        pipe("OffsetDrop", (-67.7, 63.7, 52.8), 2.8, "y", 0.72, STEEL),
        part("IntakeBell", (0.70, 2.35, 2.35), (-67.7, 62.25, 52.8), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("IntakeShadow", (0.12, 1.72, 1.72), (-67.28, 62.25, 52.8), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("HangerWest", (0.18, 1.8, 0.18), (-66.4, 66.15, 52.8), material="Metal", color=STEEL, collide=False, rot=(0, 0, 7)),
        part("HangerEast", (0.18, 1.5, 0.18), (-63.2, 66.0, 52.8), material="Metal", color=STEEL, collide=False, rot=(0, 0, -6)),
    ])


def build_common_area() -> list[dict]:
    """Return the common-area models without changing Studio or other regions."""

    return [
        _portal_identity(),
        _offset_utilities_landmark(),
        _common_life(),
        _architectural_rhythm(),
        _overhead_infrastructure(),
        _common_ventilation_drop(),
    ]
