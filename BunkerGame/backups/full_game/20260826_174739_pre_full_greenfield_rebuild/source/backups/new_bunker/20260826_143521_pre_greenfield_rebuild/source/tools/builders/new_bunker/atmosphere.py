"""Causal aging overlays for the NewBunker environment prototype.

This module owns one noninteractive ``AtmospherePass`` model.  It does not
replace room geometry, introduce lights or scripts, or change global state.
Every part is non-colliding, non-touching, and non-queryable through the shared
``part`` helper so approved player routes remain unchanged.
"""

from __future__ import annotations

from .kit import CONCRETE_DARK, STEEL, model, part
from .site import FLOOR_Y


WET_GRIME = [0.055, 0.075, 0.070]
SOOT = [0.030, 0.037, 0.038]
DRY_DUST = [0.255, 0.250, 0.225]
MINERAL_SALT = [0.340, 0.350, 0.320]
DARK_OXIDATION = [0.190, 0.085, 0.040]
AGED_GREEN = [0.120, 0.170, 0.145]
AGED_WARNING = [0.300, 0.205, 0.055]
OIL = [0.025, 0.032, 0.030]


ATMOSPHERE_REVIEW_CAMERAS = {
    "bedroom_wake": ((-89.0, 58.25, 87.25), (-77.4, 58.1, 75.8)),
    "common_wide": ((-68.0, 61.5, 34.0), (-54.0, 58.5, 49.0)),
    "west_corridor": ((-74.0, 59.3, 79.0), (-74.0, 58.8, 36.0)),
    "workshop": ((-80.5, 59.5, 38.0), (-92.0, 58.5, 36.0)),
    "upgrade": ((-80.5, 59.5, 56.0), (-91.0, 58.5, 57.0)),
    "storage": ((-56.5, 59.5, 60.5), (-64.0, 58.0, 73.0)),
    "power": ((-49.0, 60.2, 62.5), (-37.0, 59.0, 74.0)),
    "shop": ((-38.1, 59.1, 42.0), (-31.4, 58.1, 42.0)),
    "entrance_interior": ((-60.0, 59.5, 18.0), (-60.0, 58.5, 7.0)),
    "service": ((-39.0, 59.3, 84.0), (-39.0, 58.8, 104.0)),
}


def _wear(
    name: str,
    size: tuple[float, float, float],
    pos: tuple[float, float, float],
    *,
    material: str = "Concrete",
    color: list[float] = WET_GRIME,
    transparency: float = 0.5,
    rot: tuple[float, float, float] | None = None,
) -> dict:
    """Create a thin, visual-only aging layer."""

    return part(
        name,
        size,
        pos,
        material=material,
        color=color,
        collide=False,
        transparency=transparency,
        rot=rot,
        cast_shadow=False,
    )


def _bedroom_aging() -> dict:
    return model("BedroomAging", [
        _wear("NorthWallTideLine", (8.0, 1.0, 0.035), (-88.2, 54.75, 95.47), transparency=0.44, rot=(0, 0, -2)),
        _wear("WestCornerDampRise", (0.035, 4.6, 2.2), (-95.47, 56.4, 92.7), transparency=0.48, rot=(3, 0, 0)),
        _wear("CeilingJointLeak", (0.055, 1.5, 4.8), (-95.44, 63.6, 88.8), transparency=0.57, rot=(-4, 0, 0)),
        _wear("MattressSleepDiscoloration", (2.7, 0.025, 1.65), (-91.2, 56.145, 87.45), material="Fabric", color=[0.115, 0.135, 0.125], transparency=0.34, rot=(0, -4, 0)),
        _wear("PillowDampEdge", (0.75, 0.025, 1.5), (-92.7, 56.56, 87.45), material="Fabric", color=[0.20, 0.21, 0.19], transparency=0.42, rot=(0, 4, 0)),
        _wear("CotDustExclusion", (6.1, 0.022, 3.0), (-90.4, FLOOR_Y + 0.018, 87.5), color=DRY_DUST, transparency=0.74, rot=(0, 1, 0)),
        _wear("ExitLowerHandWear", (0.05, 2.0, 0.42), (-78.54, 57.6, 72.65), material="Metal", color=DARK_OXIDATION, transparency=0.32),
    ])


def _common_aging() -> dict:
    return model("CommonAging", [
        _wear("PipeJointCondensation", (0.035, 3.8, 1.3), (-69.48, 58.0, 53.2), transparency=0.50, rot=(4, 0, 0)),
        _wear("OffsetCeilingLeak", (4.4, 0.028, 2.3), (-63.0, 67.985, 48.2), color=WET_GRIME, transparency=0.62, rot=(0, 8, 0)),
        _wear("NorthRepairMineralBloom", (3.0, 2.2, 0.035), (-50.1, 57.0, 57.48), color=MINERAL_SALT, transparency=0.68, rot=(0, 0, -3)),
        _wear("UtilityFootGrime", (2.4, 0.025, 2.0), (-52.3, FLOOR_Y + 0.02, 50.2), material="SmoothPlastic", color=OIL, transparency=0.46, rot=(0, 10, 0)),
        _wear("MessNookChairScuff", (4.2, 0.023, 1.1), (-66.2, FLOOR_Y + 0.02, 36.0), color=DRY_DUST, transparency=0.66, rot=(0, -6, 0)),
        _wear("CrossingBrokenPolish", (1.2, 0.022, 5.5), (-56.2, FLOOR_Y + 0.019, 43.7), material="SmoothPlastic", color=[0.22, 0.23, 0.22], transparency=0.73, rot=(0, 4, 0)),
    ])


def _corridor_aging() -> dict:
    return model("CorridorAging", [
        _wear("SouthArrivalScuff", (0.035, 2.8, 4.6), (-70.48, 56.0, 49.2), color=[0.16, 0.17, 0.16], transparency=0.55, rot=(3, 0, 0)),
        _wear("MaintenanceOilHalo", (2.3, 0.024, 3.1), (-76.2, FLOOR_Y + 0.019, 61.5), material="SmoothPlastic", color=OIL, transparency=0.36, rot=(0, 14, 0)),
        _wear("MaintenanceWipeArc", (0.035, 2.4, 2.8), (-77.47, 58.3, 61.4), material="Metal", color=DRY_DUST, transparency=0.70, rot=(5, 0, 0)),
        _wear("ResidentialDampTrackA", (0.035, 4.2, 1.1), (-70.48, 56.7, 73.0), transparency=0.46, rot=(-4, 0, 0)),
        _wear("ResidentialDampTrackB", (0.035, 2.8, 0.7), (-70.47, 56.0, 75.0), transparency=0.58, rot=(5, 0, 0)),
        _wear("WestFloorJointDirt", (0.15, 0.022, 27.0), (-77.25, FLOOR_Y + 0.018, 51.0), color=WET_GRIME, transparency=0.60),
        _wear("MaintenanceWetSheen", (2.0, 0.018, 1.3), (-73.1, FLOOR_Y + 0.026, 62.6), material="Glass", color=[0.08, 0.12, 0.12], transparency=0.70, rot=(0, -11, 0)),
    ])


def _workshop_aging() -> dict:
    return model("WorkshopAging", [
        _wear("BenchSootBloom", (7.2, 2.7, 0.035), (-89.0, 61.3, 28.49), color=SOOT, transparency=0.46, rot=(0, 0, 2)),
        _wear("BenchGreaseSmear", (5.4, 0.035, 1.1), (-89.3, 57.62, 31.9), material="SmoothPlastic", color=OIL, transparency=0.55, rot=(0, 3, 0)),
        _wear("CabinetSurvivingPaint", (0.035, 1.6, 1.5), (-94.16, 55.8, 31.9), material="Metal", color=AGED_GREEN, transparency=0.25),
        _wear("MatOilShadow", (4.4, 0.018, 1.2), (-88.4, FLOOR_Y + 0.024, 35.0), material="SmoothPlastic", color=OIL, transparency=0.42, rot=(0, -5, 0)),
        _wear("CylinderWallOverspray", (0.035, 2.2, 3.0), (-95.47, 56.2, 42.2), color=SOOT, transparency=0.58, rot=(3, 0, 0)),
        _wear("BenchFootMetalDust", (2.0, 0.02, 0.9), (-85.5, FLOOR_Y + 0.02, 34.0), material="Metal", color=DRY_DUST, transparency=0.72, rot=(0, 16, 0)),
    ])


def _upgrade_aging() -> dict:
    return model("UpgradeAging", [
        _wear("ActuatorHydraulicRun", (0.035, 2.5, 0.7), (-92.60, 56.7, 58.0), material="SmoothPlastic", color=OIL, transparency=0.38, rot=(-5, 0, 0)),
        _wear("RamGreaseBand", (0.65, 0.035, 0.9), (-89.2, 60.02, 57.0), material="SmoothPlastic", color=OIL, transparency=0.34),
        _wear("ServiceStepPolish", (0.65, 0.035, 2.3), (-87.93, 54.91, 57.0), material="Metal", color=[0.34, 0.35, 0.33], transparency=0.52),
        _wear("PlinthOilCreep", (1.8, 0.02, 2.6), (-91.7, FLOOR_Y + 0.022, 59.0), material="SmoothPlastic", color=OIL, transparency=0.42, rot=(0, -12, 0)),
        _wear("MaintenanceWipeMark", (0.035, 2.1, 2.6), (-95.47, 58.0, 60.5), color=DRY_DUST, transparency=0.68, rot=(6, 0, 0)),
    ])


def _storage_aging() -> dict:
    return model("StorageAging", [
        _wear("WestShelfDustBand", (1.6, 0.025, 4.8), (-68.15, 61.44, 63.0), color=DRY_DUST, transparency=0.58),
        _wear("NorthShelfDustBand", (4.6, 0.025, 1.4), (-62.0, 61.44, 76.0), color=DRY_DUST, transparency=0.63),
        _wear("InventoryCleanFootprint", (1.2, 0.026, 1.0), (-68.1, 61.46, 64.0), color=CONCRETE_DARK, transparency=0.52),
        _wear("NorthWallMineralEdge", (5.8, 0.6, 0.035), (-62.3, 55.0, 77.48), color=MINERAL_SALT, transparency=0.67, rot=(0, 0, 2)),
        _wear("CrateDragScuff", (0.25, 0.022, 5.0), (-56.8, FLOOR_Y + 0.019, 70.0), color=DRY_DUST, transparency=0.61, rot=(0, -3, 0)),
        _wear("CollapsedPackingCloth", (2.1, 0.16, 1.4), (-56.6, 54.12, 75.4), material="Fabric", color=[0.18, 0.19, 0.16], transparency=0.12, rot=(0, 19, 3)),
    ])


def _power_aging() -> dict:
    return model("PowerAging", [
        _wear("ExhaustSootPlumeA", (2.2, 4.2, 0.035), (-41.5, 62.0, 81.48), color=SOOT, transparency=0.42, rot=(0, 0, -4)),
        _wear("ExhaustSootPlumeB", (1.8, 3.4, 0.035), (-36.3, 62.2, 81.47), color=SOOT, transparency=0.50, rot=(0, 0, 5)),
        _wear("GeneratorPlinthOilEdge", (7.0, 0.022, 1.3), (-38.8, FLOOR_Y + 0.025, 77.0), material="SmoothPlastic", color=OIL, transparency=0.34, rot=(0, 2, 0)),
        _wear("CableTrenchGrime", (8.4, 0.018, 0.7), (-42.0, FLOOR_Y + 0.028, 64.2), material="SmoothPlastic", color=OIL, transparency=0.46),
        _wear("PanelBaseOxidation", (0.035, 0.8, 8.0), (-51.48, 54.7, 69.5), material="Metal", color=DARK_OXIDATION, transparency=0.38),
        _wear("PanelCondensationTrail", (0.035, 3.0, 1.1), (-51.47, 58.2, 67.0), color=WET_GRIME, transparency=0.52, rot=(4, 0, 0)),
        _wear("GeneratorHeatDiscoloration", (3.1, 0.035, 2.0), (-36.3, 59.2, 70.25), material="Metal", color=[0.13, 0.10, 0.075], transparency=0.56),
    ])


def _shop_aging() -> dict:
    return model("ShopAging", [
        _wear("CounterDarkPaintRemnant", (0.10, 0.20, 5.2), (-34.45, 57.30, 40.5), material="Metal", color=STEEL, transparency=0.16),
        _wear("CounterHandPolish", (0.035, 0.16, 3.3), (-34.48, 57.38, 45.0), material="Metal", color=[0.38, 0.36, 0.30], transparency=0.54),
        _wear("ShutterGreaseBand", (0.035, 0.55, 5.0), (-34.10, 62.50, 42.0), material="Metal", color=SOOT, transparency=0.32),
        _wear("BackShelfDust", (1.8, 0.025, 5.8), (-30.70, 61.44, 46.4), color=DRY_DUST, transparency=0.62),
        _wear("CounterQueueWear", (3.2, 0.022, 5.0), (-36.2, FLOOR_Y + 0.019, 42.0), color=[0.21, 0.21, 0.19], transparency=0.68, rot=(0, 2, 0)),
        _wear("ToeRailDarkBreak", (0.035, 0.25, 4.4), (-34.40, 54.40, 44.6), material="Metal", color=AGED_GREEN, transparency=0.22),
    ])


def _entrance_aging() -> dict:
    return model("EntranceAging", [
        _wear("InteriorBootMud", (4.0, 0.022, 3.2), (-60.3, FLOOR_Y + 0.02, 11.2), color=[0.12, 0.105, 0.075], transparency=0.48, rot=(0, -7, 0)),
        _wear("ThresholdDragMark", (0.34, 0.023, 6.5), (-58.8, FLOOR_Y + 0.022, 10.5), material="Metal", color=SOOT, transparency=0.50, rot=(0, -4, 0)),
        _wear("WestJambAbrasion", (0.035, 2.7, 1.0), (-64.03, 56.7, 8.0), material="Metal", color=[0.34, 0.31, 0.25], transparency=0.60),
        _wear("EastJambAbrasion", (0.035, 1.9, 0.8), (-55.97, 56.2, 8.1), material="Metal", color=[0.34, 0.31, 0.25], transparency=0.65),
        _wear("HeaderRunoffFan", (4.8, 2.4, 0.035), (-60.0, 61.8, 6.48), color=WET_GRIME, transparency=0.52, rot=(0, 0, -2)),
        _wear("BarricadeSocketDust", (16.0, 0.02, 1.2), (-60.0, FLOOR_Y + 0.019, 12.0), color=DRY_DUST, transparency=0.70),
    ])


def _service_aging() -> dict:
    return model("ServiceAging", [
        _wear("DuctCondensationA", (0.035, 4.4, 1.0), (-47.48, 57.0, 100.2), transparency=0.42, rot=(-5, 0, 0)),
        _wear("DuctCondensationB", (0.035, 3.2, 0.8), (-47.47, 56.5, 103.2), transparency=0.53, rot=(4, 0, 0)),
        _wear("ServiceWallTideLine", (0.035, 0.9, 7.2), (-47.48, 54.8, 104.0), color=WET_GRIME, transparency=0.43),
        _wear("DrainMineralBloom", (4.0, 0.02, 1.7), (-42.3, FLOOR_Y + 0.025, 97.0), color=MINERAL_SALT, transparency=0.66, rot=(0, 4, 0)),
        _wear("ServiceWetSheen", (2.8, 0.018, 5.2), (-39.0, FLOOR_Y + 0.027, 99.5), material="Glass", color=[0.075, 0.115, 0.11], transparency=0.72, rot=(0, -3, 0)),
        _wear("FarmBootTraceA", (0.65, 0.02, 2.2), (-36.8, FLOOR_Y + 0.026, 105.5), color=[0.13, 0.115, 0.08], transparency=0.56, rot=(0, 14, 0)),
        _wear("FarmBootTraceB", (0.60, 0.02, 2.0), (-34.8, FLOOR_Y + 0.027, 106.8), color=[0.13, 0.115, 0.08], transparency=0.62, rot=(0, -8, 0)),
    ])


def _exterior_aging() -> dict:
    return model("ExteriorAging", [
        _wear("EntranceGroundContactSeam", (15.0, 0.18, 0.10), (-60.0, 54.05, -0.45), color=WET_GRIME, transparency=0.30),
        _wear("EntranceDrainRunoffFan", (5.4, 0.025, 3.0), (-60.0, 53.43, -2.2), color=WET_GRIME, transparency=0.54, rot=(0, -2, 0)),
        _wear("ServiceGroundContactSeam", (0.10, 0.22, 10.0), (-29.20, 54.10, 104.0), color=WET_GRIME, transparency=0.34),
        _wear("ServiceApronMudFan", (4.5, 0.024, 5.0), (-20.5, 54.02, 104.8), color=[0.12, 0.105, 0.075], transparency=0.55, rot=(0, 7, 0)),
        _wear("WestRetainingMineralEdge", (0.035, 1.0, 7.0), (-96.29, 55.0, 67.0), color=MINERAL_SALT, transparency=0.70, rot=(2, 0, 0)),
    ])


def build_atmosphere() -> list[dict]:
    """Return the isolated atmosphere hierarchy for ``EnvironmentDetails``."""

    return [model("AtmospherePass", [
        _bedroom_aging(),
        _common_aging(),
        _corridor_aging(),
        _workshop_aging(),
        _upgrade_aging(),
        _storage_aging(),
        _power_aging(),
        _shop_aging(),
        _entrance_aging(),
        _service_aging(),
        _exterior_aging(),
    ])]
