"""Medium-scale, causal deterioration for the approved NewBunker foundation.

These details are deliberately thin, anchored, and non-colliding.  They sit on
room perimeter planes or beneath existing infrastructure so decay enriches the
environment without changing architecture, traversal, or interaction affordance.
"""

from __future__ import annotations

from .kit import (
    CONCRETE_DARK,
    CONCRETE_WORN,
    RUST,
    STEEL,
    STEEL_LIGHT,
    YELLOW,
    model,
    part,
)
from .site import FLOOR_Y


MOISTURE = [0.075, 0.105, 0.095]
MINERAL = [0.39, 0.405, 0.35]
SOOT = [0.055, 0.06, 0.06]
OIL = [0.045, 0.055, 0.055]
DIRT = [0.12, 0.105, 0.085]
PATCH_CONCRETE = [0.285, 0.29, 0.275]


def _floor_layer(
    name: str,
    size: tuple[float, float],
    pos: tuple[float, float],
    color: list[float],
    *,
    transparency: float = 0.18,
    rot_y: float = 0.0,
) -> dict:
    """Return a visual-only film above the floor with no traversal lip."""

    return part(
        name,
        (size[0], 0.035, size[1]),
        (pos[0], FLOOR_Y + 0.045, pos[1]),
        material="SmoothPlastic",
        color=color,
        collide=False,
        transparency=transparency,
        rot=(0, rot_y, 0) if rot_y else None,
        cast_shadow=False,
    )


def _bedroom_decay() -> dict:
    """Oldest room: plumbing moisture, failed ceiling lining, and crude repair."""

    return model("BedroomStructuralDecay", [
        part("NorthWallMoistureBloom", (7.4, 3.7, 0.055), (-89.2, 56.2, 95.47), material="Concrete", color=MOISTURE, collide=False, transparency=0.20, cast_shadow=False),
        part("NorthWallMineralRun", (1.15, 5.1, 0.04), (-93.1, 58.0, 95.43), material="SmoothPlastic", color=MINERAL, collide=False, transparency=0.30, rot=(0, 0, -4), cast_shadow=False),
        part("WestWallDampRise", (0.055, 2.6, 6.1), (-95.47, 55.4, 88.2), material="Concrete", color=MOISTURE, collide=False, transparency=0.24, cast_shadow=False),
        _floor_layer("PipeLeakFloorStain", (5.8, 3.2), (-90.2, 93.6), MOISTURE, transparency=0.16, rot_y=-7),
        _floor_layer("CotFootTrafficWear", (5.9, 1.15), (-85.2, 84.5), DIRT, transparency=0.24, rot_y=-12),
        part("NorthWestSpalledCorner", (1.35, 1.0, 0.22), (-95.22, 55.0, 95.30), material="Concrete", color=CONCRETE_WORN, collide=False, rot=(8, -18, 14), class_name="WedgePart"),
        part("FailedCeilingPanel", (4.4, 0.10, 2.0), (-86.8, 65.93, 91.8), material="CorrodedMetal", color=STEEL, collide=False, rot=(0, 5, 0)),
        part("CeilingMaintenanceVoid", (3.4, 0.06, 1.25), (-86.5, 65.86, 91.8), material="SmoothPlastic", color=SOOT, collide=False, cast_shadow=False),
        part("CrudeWestWallPatch", (0.10, 3.4, 3.0), (-95.40, 58.2, 78.0), material="Concrete", color=PATCH_CONCRETE, collide=False, rot=(0, 0, 2)),
    ])


def _corridor_decay() -> dict:
    """Repeated utility damage creates suspense beats without narrowing lanes."""

    return model("CorridorStructuralDecay", [
        part("ResidentialEastMoistureRun", (0.055, 3.1, 6.8), (-70.48, 55.8, 52.2), material="Concrete", color=MOISTURE, collide=False, transparency=0.20, cast_shadow=False),
        part("ResidentialRepairSkin", (0.08, 4.6, 4.4), (-77.48, 58.2, 66.3), material="CorrodedMetal", color=STEEL, collide=False, rot=(0, 0, -1.5)),
        part("RepairSkinRustEdge", (0.055, 4.2, 0.26), (-77.42, 58.0, 64.25), material="CorrodedMetal", color=RUST, collide=False),
        _floor_layer("ResidentialWallDirt", (1.1, 8.4), (-77.05, 56.0), DIRT, transparency=0.20),
        part("EastUtilityCeilingOpening", (2.6, 0.055, 4.2), (-42.4, 64.93, 50.0), material="SmoothPlastic", color=SOOT, collide=False, cast_shadow=False),
        part("EastUtilityHangingLead", (0.12, 3.3, 0.12), (-44.3, 62.9, 50.7), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, 9)),
        _floor_layer("EastUtilityCondensationTrack", (1.0, 7.2), (-45.25, 55.2), MOISTURE, transparency=0.16, rot_y=1),
    ])


def _common_decay() -> dict:
    """Controlled central wear implies heavy historic circulation, not ruin."""

    return model("CommonHubStructuralDecay", [
        _floor_layer("HistoricCrossingWear", (13.5, 2.0), (-58.5, 42.0), DIRT, transparency=0.27, rot_y=-2),
        _floor_layer("OldTableOilShadow", (4.3, 3.4), (-52.9, 51.8), OIL, transparency=0.20, rot_y=7),
        part("WestColumnImpactScar", (0.12, 2.1, 1.2), (-65.54, 56.0, 48.4), material="Concrete", color=CONCRETE_WORN, collide=False, rot=(0, 0, 6)),
        part("WestColumnRepairPlate", (0.14, 2.8, 1.65), (-65.46, 58.7, 48.4), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
        part("RepairPlateOxidation", (0.055, 1.8, 0.34), (-65.37, 58.2, 49.0), material="CorrodedMetal", color=RUST, collide=False),
        part("NorthWallMoistureBand", (7.4, 2.1, 0.055), (-50.7, 55.2, 57.47), material="Concrete", color=MOISTURE, collide=False, transparency=0.22, cast_shadow=False),
        part("CeilingLeakHalo", (5.0, 0.055, 3.0), (-54.0, 68.92, 51.3), material="SmoothPlastic", color=MOISTURE, collide=False, transparency=0.20, cast_shadow=False),
    ])


def _workshop_decay() -> dict:
    """Grease, heat, and improvised patching follow the active work surfaces."""

    return model("WorkshopStructuralDecay", [
        _floor_layer("WorkbenchOilSpill", (5.8, 2.2), (-89.0, 35.0), OIL, transparency=0.12, rot_y=4),
        _floor_layer("CylinderRackGrease", (3.0, 2.6), (-93.0, 42.0), OIL, transparency=0.16, rot_y=-8),
        part("BackboardSootPlume", (5.4, 2.7, 0.045), (-89.4, 61.3, 30.40), material="SmoothPlastic", color=SOOT, collide=False, transparency=0.18, cast_shadow=False),
        part("NorthWallReplacementPlate", (4.8, 3.6, 0.08), (-84.8, 59.2, 45.48), material="CorrodedMetal", color=STEEL, collide=False, rot=(0, 0, -2)),
        part("ReplacementPlateRustSeam", (4.2, 0.18, 0.055), (-84.8, 57.6, 45.42), material="CorrodedMetal", color=RUST, collide=False),
        part("HeatChippedConcrete", (1.5, 1.15, 0.20), (-93.0, 55.1, 45.30), material="Concrete", color=CONCRETE_WORN, collide=False, rot=(4, 16, 6), class_name="WedgePart"),
        part("DamagedCeilingAccessPanel", (3.2, 0.10, 2.2), (-92.0, 65.93, 39.5), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, -6, 0)),
    ])


def _upgrade_decay() -> dict:
    """Hydraulic leaks and repeated service access distinguish upgrade work."""

    return model("UpgradeStructuralDecay", [
        _floor_layer("HydraulicFluidStain", (4.6, 3.2), (-91.0, 57.0), OIL, transparency=0.12, rot_y=-5),
        _floor_layer("TechnicianKneelingWear", (3.2, 2.0), (-86.8, 57.0), DIRT, transparency=0.23),
        part("DisconnectWallScorch", (0.045, 4.4, 3.3), (-95.48, 59.5, 62.6), material="SmoothPlastic", color=SOOT, collide=False, transparency=0.16, cast_shadow=False),
        part("NorthWallServicePatch", (5.0, 2.9, 0.08), (-88.0, 60.0, 65.48), material="Metal", color=STEEL, collide=False, rot=(0, 0, 1.5)),
        part("ServicePatchOxidizedBottom", (4.5, 0.20, 0.055), (-88.0, 58.65, 65.42), material="CorrodedMetal", color=RUST, collide=False),
    ])


def _storage_decay() -> dict:
    """Low airflow leaves dust, dampness, and an unrepaired ceiling pocket."""

    return model("StorageStructuralDecay", [
        _floor_layer("WestRackDustBank", (1.25, 12.0), (-68.55, 69.0), DIRT, transparency=0.15),
        _floor_layer("NorthRackDustBank", (6.8, 1.3), (-62.0, 76.7), DIRT, transparency=0.15),
        part("WestWallDampShadow", (0.055, 3.6, 7.0), (-69.47, 55.9, 73.2), material="Concrete", color=MOISTURE, collide=False, transparency=0.18, cast_shadow=False),
        part("NorthWallMineralStreak", (1.1, 4.5, 0.045), (-64.8, 58.2, 77.47), material="SmoothPlastic", color=MINERAL, collide=False, transparency=0.32, rot=(0, 0, 5), cast_shadow=False),
        part("UnsealedCeilingOpening", (4.1, 0.055, 3.0), (-57.7, 64.93, 73.0), material="SmoothPlastic", color=SOOT, collide=False, cast_shadow=False),
        part("LooseCeilingCover", (3.8, 0.10, 2.5), (-58.3, 64.80, 72.8), material="CorrodedMetal", color=STEEL, collide=False, rot=(0, 0, -5)),
        part("LockerBaseOxidation", (4.0, 0.38, 0.055), (-56.7, 54.55, 74.86), material="CorrodedMetal", color=RUST, collide=False, transparency=0.10),
    ])


def _power_decay() -> dict:
    """Heat and electrical maintenance create the bunker’s harshest damage."""

    return model("PowerRoomStructuralDecay", [
        _floor_layer("GeneratorOilPool", (5.4, 3.8), (-46.0, 72.8), OIL, transparency=0.10, rot_y=6),
        _floor_layer("PanelServiceWear", (2.0, 8.0), (-32.7, 69.0), DIRT, transparency=0.22),
        part("PanelBankScorchPlume", (0.045, 5.8, 4.8), (-30.48, 59.6, 67.8), material="SmoothPlastic", color=SOOT, collide=False, transparency=0.10, cast_shadow=False),
        part("PanelBankEmergencyPatch", (0.10, 3.2, 2.8), (-30.42, 59.2, 75.3), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -2)),
        part("EmergencyPatchWarningBand", (0.055, 0.35, 2.35), (-30.35, 59.8, 75.3), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.14, cast_shadow=False),
        part("NorthPipeCondensation", (6.2, 3.0, 0.055), (-40.0, 56.0, 81.48), material="Concrete", color=MOISTURE, collide=False, transparency=0.16, cast_shadow=False),
        part("GeneratorSootCeiling", (6.0, 0.055, 4.4), (-45.0, 67.93, 72.0), material="SmoothPlastic", color=SOOT, collide=False, transparency=0.14, cast_shadow=False),
        part("DiscardedBreakerCover", (2.4, 0.12, 1.3), (-34.7, 54.14, 78.8), material="CorrodedMetal", color=STEEL, collide=False, rot=(0, 21, 0)),
    ])


def _shop_and_entrance_decay() -> dict:
    """Human-use wear at the counter transitions to weather-driven entry damage."""

    return model("ShopEntranceAndServiceDecay", [
        _floor_layer("ShopCounterFootWear", (2.2, 7.0), (-35.1, 41.0), DIRT, transparency=0.23),
        part("ShopSouthWallWaterMark", (5.2, 2.6, 0.055), (-34.5, 55.4, 30.48), material="Concrete", color=MOISTURE, collide=False, transparency=0.20, cast_shadow=False),
        part("CounterReplacementKickPlate", (4.8, 0.65, 0.08), (-34.4, 54.5, 39.0), material="CorrodedMetal", color=RUST, collide=False, rot=(0, 0, -1)),
        _floor_layer("EntranceTrackedMud", (5.0, 7.6), (-59.7, 14.0), DIRT, transparency=0.14, rot_y=-3),
        part("BlastPierRunoffWest", (0.055, 4.8, 2.4), (-64.77, 58.7, 7.75), material="Concrete", color=MOISTURE, collide=False, transparency=0.16, cast_shadow=False),
        part("BlastHeaderMineralStreak", (1.3, 5.1, 0.055), (-58.2, 62.0, 5.68), material="SmoothPlastic", color=MINERAL, collide=False, transparency=0.30, rot=(0, 0, -5), cast_shadow=False),
        _floor_layer("ServiceDrainOverflow", (5.8, 2.4), (-42.0, 98.0), MOISTURE, transparency=0.13, rot_y=8),
        part("ServiceDuctRustBloom", (5.0, 0.075, 2.4), (-39.0, 62.67, 102.0), material="CorrodedMetal", color=RUST, collide=False, transparency=0.16, cast_shadow=False),
        part("DeconHousingMineralRun", (0.055, 3.8, 0.65), (-45.36, 57.4, 99.4), material="SmoothPlastic", color=MINERAL, collide=False, transparency=0.28, cast_shadow=False),
    ])


def build_decay_details() -> list[dict]:
    """Return 59 visual-only BaseParts grouped by causal deterioration source."""

    return [
        _bedroom_decay(),
        _corridor_decay(),
        _common_decay(),
        _workshop_decay(),
        _upgrade_decay(),
        _storage_decay(),
        _power_decay(),
        _shop_and_entrance_decay(),
    ]
