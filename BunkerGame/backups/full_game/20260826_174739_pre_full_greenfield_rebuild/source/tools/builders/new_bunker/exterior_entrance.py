"""Reinforced entrances, buried exterior silhouette, and site approach.

This module owns only the generated ``Entrance``, ``ServiceExit``, and
exterior/earthwork models.  Coordinates are the verified staging coordinates;
``FINAL_OFFSET`` is intentionally not applied.

Traversal envelopes:

* main approach: X=-64..-56, Z=0..20, clear to at least Y=62;
* service approach: Z=100..108, X=-48..-18, clear to at least Y=62;
* all shutter leaves are visibly parked outside those envelopes.

Approximate module bounds are X=-112..-11, Y=52.8..70.2, Z=-11.5..128.
Ground wedges intentionally meet/partly embed Grassblox and bunker outer wall
faces.  They stay far from the protected legacy shell (which is around X=0,
Z=14..72.5); the closest eastern construction is the service apron at Z=104.

Director cameras (position -> target):

* entrance exterior: (-60, 62, -9) -> (-60, 59, 10)
* exterior overview: (-61, 94, -28) -> (-59, 57, 57)
* service exterior: (-17, 62, 104) -> (-33, 58.5, 104)
"""

from __future__ import annotations

from .kit import (
    AGED_WHITE,
    CONCRETE_DARK,
    CONCRETE_WORN,
    GREEN,
    RED,
    RUST,
    STEEL,
    STEEL_LIGHT,
    UTILITY_BLUE,
    YELLOW,
    model,
    part,
    pipe,
)
from .site import FLOOR_Y


EARTH_DARK = [0.135, 0.165, 0.115]
EARTH_MOSS = [0.17, 0.205, 0.135]
EARTH_DRY = [0.215, 0.205, 0.155]


def _hazard_band(name: str, x: float, z: float, width: float) -> dict:
    """A restrained threshold marking that never adds a collision lip."""

    stripe_width = width / 5
    return model(name, [
        part(
            f"Stripe{index:02d}",
            (stripe_width - 0.10, 0.06, 1.25),
            (x - width / 2 + stripe_width * (index - 0.5), FLOOR_Y + 0.035, z),
            material="SmoothPlastic",
            color=YELLOW if index % 2 else CONCRETE_DARK,
            collide=False,
            cast_shadow=False,
        )
        for index in range(1, 6)
    ])


def _main_blast_frame() -> dict:
    """Layered defense portal with a deliberately unobstructed eight-stud lane."""

    return model("ReinforcedMainBlastPortal", [
        part("WestConcretePier", (3.2, 13.2, 4.2), (-66.4, 60.6, 7.8), material="Concrete", color=CONCRETE_WORN),
        part("EastConcretePier", (3.2, 13.2, 4.2), (-53.6, 60.6, 7.8), material="Concrete", color=CONCRETE_WORN),
        part("LoadBearingHeader", (16.0, 2.5, 4.2), (-60.0, 65.35, 7.8), material="Concrete", color=CONCRETE_WORN),
        part("WestArmorJamb", (0.75, 9.4, 2.4), (-64.45, 58.7, 8.4), material="DiamondPlate", color=STEEL),
        part("EastArmorJamb", (0.75, 9.4, 2.4), (-55.55, 58.7, 8.4), material="DiamondPlate", color=STEEL),
        part("ArmorLintel", (9.65, 0.85, 2.4), (-60.0, 63.35, 8.4), material="DiamondPlate", color=STEEL),
        part("WestJambWear", (0.12, 5.8, 1.7), (-64.02, 57.7, 8.0), material="CorrodedMetal", color=RUST, collide=False, transparency=0.12),
        part("EastJambWear", (0.12, 5.8, 1.7), (-55.98, 57.7, 8.0), material="CorrodedMetal", color=RUST, collide=False, transparency=0.12),
        # The operating leaf is parked completely west of the X=-64 clear edge.
        model("ParkedBlastDoorLeaf", [
            part("DoorSlab", (0.72, 8.4, 7.1), (-65.55, 58.25, 12.2), material="CorrodedMetal", color=GREEN, collide=False),
            part("UpperBrace", (0.28, 0.55, 6.25), (-65.12, 60.55, 12.2), material="Metal", color=STEEL_LIGHT, collide=False),
            part("LowerBrace", (0.28, 0.55, 6.25), (-65.12, 56.35, 12.2), material="Metal", color=STEEL_LIGHT, collide=False),
            pipe("GuideWheelUpper", (-65.05, 60.6, 9.15), 0.32, "x", 0.78, STEEL_LIGHT),
            pipe("GuideWheelLower", (-65.05, 56.3, 9.15), 0.32, "x", 0.78, STEEL_LIGHT),
        ]),
        model("OverheadDoorDrive", [
            part("DriveHousing", (6.3, 1.25, 1.65), (-67.1, 64.15, 11.8), material="Metal", color=STEEL),
            pipe("DriveShaft", (-63.4, 64.15, 11.8), 1.2, "x", 0.44, STEEL_LIGHT),
            part("AccessCover", (3.5, 0.12, 1.10), (-67.1, 63.48, 11.8), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
        ]),
    ])


def _entrance_defense_silhouette() -> dict:
    """Layer asymmetric defense hardware around the portal while preserving the eight-stud opening."""

    return model("EntranceDefenseSilhouette", [
        part("WestArmorCheek", (1.15, 9.0, 3.1), (-67.75, 59.0, 9.2), material="CorrodedMetal", color=STEEL, collide=False, rot=(0, -5, 0)),
        part("EastArmorCheek", (1.05, 7.2, 2.8), (-52.35, 58.2, 9.4), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 6, 0)),
        part("WestHeaderGusset", (4.8, 0.55, 1.2), (-64.9, 64.45, 8.9), material="DiamondPlate", color=STEEL, collide=False, rot=(0, 0, -12)),
        part("EastHeaderGusset", (4.0, 0.48, 1.0), (-54.8, 64.15, 9.0), material="CorrodedMetal", color=RUST, collide=False, rot=(0, 0, 10)),
        part("WestCableConduit", (0.30, 5.8, 0.30), (-67.0, 61.0, 11.1), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -3)),
        part("EmergencyFeed", (5.0, 0.26, 0.26), (-64.6, 63.65, 11.1), material="Metal", color=UTILITY_BLUE, collide=False),
        part("BrokenArmorPlate", (2.8, 0.16, 1.7), (-68.2, 54.18, 14.2), material="CorrodedMetal", color=RUST, collide=False, rot=(0, 18, 4)),
        part("DrainGuard", (3.6, 0.38, 0.55), (-52.0, 54.28, 5.0), material="DiamondPlate", color=STEEL_LIGHT, collide=False, rot=(0, -8, 0)),
    ])


def build_entrance() -> list[dict]:
    """Return the defense-oriented main entrance and interior transition bay."""

    return [
        _main_blast_frame(),
        _entrance_defense_silhouette(),
        model("DefenseVestibule", [
            part("WestReadyShelf", (5.4, 0.55, 2.1), (-68.2, 58.0, 16.4), material="DiamondPlate", color=STEEL_LIGHT),
            part("ShelfBack", (5.4, 3.2, 0.28), (-68.2, 59.45, 17.35), material="Metal", color=STEEL),
            part("ShelfSupportA", (0.42, 3.7, 1.7), (-70.2, 55.9, 16.4), material="Metal", color=STEEL),
            part("ShelfSupportB", (0.42, 3.7, 1.7), (-66.2, 55.9, 16.4), material="Metal", color=STEEL),
            part("SandbagMassA", (3.2, 1.0, 1.25), (-69.0, 54.55, 12.2), material="Fabric", color=[0.235, 0.25, 0.20], collide=False, shape="Ball"),
            part("SandbagMassB", (2.8, 0.9, 1.15), (-67.0, 54.45, 12.6), material="Fabric", color=[0.20, 0.22, 0.18], collide=False, shape="Ball"),
            model("DoorControlStation", [
                part("ControlCabinet", (2.0, 5.0, 1.4), (-50.2, 57.5, 16.0), material="Metal", color=GREEN),
                part("InsetFace", (1.55, 3.7, 0.12), (-50.2, 58.0, 15.24), material="Metal", color=STEEL_LIGHT, collide=False),
                part("EmergencyStop", (0.45, 0.45, 0.16), (-50.2, 58.65, 15.13), material="Neon", color=RED, collide=False, cast_shadow=False),
                part("StatusBar", (0.55, 0.18, 0.15), (-50.2, 59.45, 15.13), material="Neon", color=UTILITY_BLUE, collide=False, cast_shadow=False),
                part("ConduitDrop", (0.36, 3.4, 0.36), (-50.2, 62.1, 16.0), material="Metal", color=STEEL_LIGHT, collide=False),
            ]),
            part("WestBarricadeSocket", (1.0, 4.0, 1.0), (-70.0, 56.0, 11.5), material="CorrodedMetal", color=RUST),
            part("EastBarricadeSocket", (1.0, 4.0, 1.0), (-50.0, 56.0, 11.5), material="CorrodedMetal", color=RUST),
            model("WestDefenseLocker", [
                part("LockerBody", (2.1, 5.8, 1.45), (-69.5, 57.1, 19.0), material="Metal", color=GREEN),
                part("InsetDoor", (1.65, 4.9, 0.10), (-69.5, 57.25, 18.22), material="Metal", color=STEEL, collide=False),
                part("DoorVent", (1.05, 0.55, 0.08), (-69.5, 58.5, 18.14), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
            ]),
            model("EastObservationAndIntercom", [
                part("ArmoredBackplate", (2.6, 3.6, 0.35), (-50.0, 60.2, 11.9), material="DiamondPlate", color=STEEL),
                part("ViewSlit", (1.6, 0.48, 0.10), (-50.0, 60.8, 11.70), material="Glass", color=[0.08, 0.12, 0.12], collide=False, transparency=0.18),
                part("IntercomFace", (0.85, 1.0, 0.10), (-50.0, 59.6, 11.69), material="Metal", color=STEEL_LIGHT, collide=False),
                part("IntercomStatus", (0.18, 0.18, 0.08), (-50.0, 59.85, 11.62), material="Neon", color=RED, collide=False, cast_shadow=False),
            ]),
            _hazard_band("InteriorThresholdMarking", -60.0, 9.55, 8.0),
        ]),
        model("EntranceApproachEngineering", [
            part("ReinforcedApron", (15.8, 0.65, 9.0), (-60.0, 53.675, 3.5), material="Concrete", color=CONCRETE_WORN),
            part("ApronCenterWear", (5.0, 0.05, 8.0), (-60.0, 54.03, 3.5), material="Concrete", color=[0.255, 0.26, 0.24], collide=False, transparency=0.10),
            part("TransverseDrain", (13.2, 0.22, 0.9), (-60.0, 54.02, -0.1), material="DiamondPlate", color=STEEL, collide=False),
            part("DrainChannelWest", (0.55, 0.18, 9.0), (-67.6, 54.0, 3.5), material="Metal", color=CONCRETE_DARK, collide=False),
            part("DrainChannelEast", (0.55, 0.18, 9.0), (-52.4, 54.0, 3.5), material="Metal", color=CONCRETE_DARK, collide=False),
            part("WestBollard", (0.75, 2.6, 0.75), (-68.4, 55.3, 0.4), material="CorrodedMetal", color=YELLOW),
            part("EastBollard", (0.75, 2.6, 0.75), (-51.6, 55.3, 0.4), material="CorrodedMetal", color=YELLOW),
            part("WestCulvertMouth", (2.5, 1.2, 1.2), (-70.0, 53.95, -0.6), material="Concrete", color=CONCRETE_DARK, collide=False),
            part("EastCulvertMouth", (2.5, 1.2, 1.2), (-50.0, 53.95, -0.6), material="Concrete", color=CONCRETE_DARK, collide=False),
            part("WestApproachWing", (1.0, 3.8, 9.5), (-69.5, 55.4, 3.1), material="Concrete", color=CONCRETE_WORN, rot=(0, -8, 0)),
            part("EastApproachWing", (1.0, 3.8, 9.5), (-50.5, 55.4, 3.1), material="Concrete", color=CONCRETE_WORN, rot=(0, 8, 0)),
        ]),
    ]


def _service_portal() -> dict:
    """Readable east-facing airlock; decorative layers stay outside its lane."""

    return model("ReinforcedServicePortal", [
        part("SouthRetainingPier", (3.2, 10.8, 2.8), (-30.2, 59.0, 97.7), material="Concrete", color=CONCRETE_WORN),
        part("NorthRetainingPier", (3.2, 10.8, 2.8), (-30.2, 59.0, 110.3), material="Concrete", color=CONCRETE_WORN),
        part("ServiceHeader", (3.2, 2.0, 15.4), (-30.2, 63.8, 104.0), material="Concrete", color=CONCRETE_WORN),
        part("SouthSteelJamb", (1.45, 8.8, 0.68), (-29.45, 58.4, 99.65), material="DiamondPlate", color=STEEL),
        part("NorthSteelJamb", (1.45, 8.8, 0.68), (-29.45, 58.4, 108.35), material="DiamondPlate", color=STEEL),
        part("SteelHeader", (1.45, 0.70, 9.4), (-29.45, 62.75, 104.0), material="DiamondPlate", color=STEEL),
        # Slatted shutter is stacked above the 8-stud-tall player opening.
        part("RaisedShutterPack", (1.0, 1.75, 7.6), (-28.9, 64.1, 104.0), material="CorrodedMetal", color=GREEN, collide=False),
        part("ShutterBottomEdge", (1.08, 0.24, 7.8), (-28.85, 63.15, 104.0), material="Metal", color=YELLOW, collide=False),
        part("SouthGuideRail", (0.44, 8.8, 0.38), (-28.65, 58.4, 99.8), material="Metal", color=STEEL_LIGHT, collide=False),
        part("NorthGuideRail", (0.44, 8.8, 0.38), (-28.65, 58.4, 108.2), material="Metal", color=STEEL_LIGHT, collide=False),
    ])


def build_service_exit() -> list[dict]:
    """Return service-airlock infrastructure without corridor-owned ribs."""

    return [
        model("DecontaminationAndUtilities", [
            part("DeconHousingSouth", (1.6, 6.4, 2.1), (-46.25, 57.2, 99.0), material="Metal", color=GREEN),
            part("DeconHousingNorth", (1.6, 6.4, 2.1), (-46.25, 57.2, 109.0), material="Metal", color=GREEN),
            part("HousingFaceSouth", (0.12, 4.8, 1.45), (-45.38, 57.6, 99.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("HousingFaceNorth", (0.12, 4.8, 1.45), (-45.38, 57.6, 109.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("OverheadServiceDuct", (14.0, 1.8, 3.2), (-39.0, 63.6, 102.0), material="Metal", color=STEEL),
            part("DuctInspectionCover", (5.5, 0.12, 2.4), (-39.0, 62.65, 102.0), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
            pipe("BlueMain", (-46.2, 61.4, 104.0), 12.0, "z", 0.58, UTILITY_BLUE),
            pipe("CorrodedReturn", (-45.25, 60.65, 104.0), 12.0, "z", 0.38, RUST),
            pipe("VerticalManifold", (-46.2, 58.5, 109.3), 5.8, "y", 0.58, UTILITY_BLUE),
            part("IsolationValve", (0.22, 1.75, 1.75), (-45.72, 59.1, 109.3), material="CorrodedMetal", color=RED, collide=False, shape="Cylinder"),
            part("ServiceFloorDrain", (4.4, 0.10, 1.0), (-42.3, 54.07, 97.0), material="DiamondPlate", color=STEEL_LIGHT, collide=False),
        ]),
        _service_portal(),
        model("ServiceExteriorApproach", [
            part("ServiceApron", (13.0, 0.65, 13.5), (-23.5, 53.675, 104.0), material="Concrete", color=CONCRETE_WORN),
            part("FarmRouteInset", (11.0, 0.05, 1.0), (-23.5, 54.03, 104.0), material="SmoothPlastic", color=GREEN, collide=False, transparency=0.10),
            part("ServiceTrenchDrain", (0.85, 0.18, 9.0), (-19.0, 54.0, 104.0), material="DiamondPlate", color=STEEL, collide=False),
            part("SouthPipeGuard", (4.5, 2.8, 0.75), (-23.5, 55.4, 97.8), material="CorrodedMetal", color=RUST),
            part("NorthPipeGuard", (4.5, 2.8, 0.75), (-23.5, 55.4, 110.2), material="CorrodedMetal", color=RUST),
            part("SouthApronDrain", (10.0, 0.12, 0.55), (-23.5, 54.02, 98.6), material="DiamondPlate", color=STEEL, collide=False),
            part("NorthApronDrain", (10.0, 0.12, 0.55), (-23.5, 54.02, 109.4), material="DiamondPlate", color=STEEL, collide=False),
            part("SouthRetainingWing", (8.5, 3.6, 0.8), (-25.4, 55.3, 96.0), material="Concrete", color=CONCRETE_WORN, rot=(0, 6, 0)),
            part("NorthRetainingWing", (8.5, 3.6, 0.8), (-25.4, 55.3, 112.0), material="Concrete", color=CONCRETE_WORN, rot=(0, -6, 0)),
        ]),
    ]


def _exterior_utility_landmarks() -> dict:
    """Sparse vertical landmarks that break the buried roofline without blocking approaches."""
    return model("ExteriorUtilityLandmarks", [
        model("ServiceVentStack", [
            pipe("MainStack", (-43.0, 71.1, 101.0), 6.2, "y", 1.15, STEEL),
            pipe("StackCollar", (-43.0, 68.45, 101.0), 0.55, "y", 1.55, STEEL_LIGHT),
            part("WeatherHood", (3.4, 0.55, 2.6), (-43.0, 74.05, 101.0), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 8, -6)),
            part("HoodBaffle", (2.8, 0.22, 2.0), (-43.0, 73.55, 101.0), material="Metal", color=CONCRETE_DARK, collide=False, rot=(0, 8, -6)),
            pipe("BraceWest", (-44.15, 70.2, 101.0), 3.4, "y", 0.18, RUST),
            pipe("BraceEast", (-41.85, 70.2, 101.0), 3.4, "y", 0.18, RUST),
        ]),
        model("EntranceSignalMast", [
            pipe("Mast", (-72.8, 59.4, -3.2), 8.8, "y", 0.38, STEEL_LIGHT),
            part("MastFoot", (1.5, 0.45, 1.5), (-72.8, 54.25, -3.2), material="Concrete", color=CONCRETE_WORN),
            part("SignalHead", (1.0, 1.9, 0.9), (-72.8, 63.25, -3.2), material="CorrodedMetal", color=STEEL, collide=False, rot=(0, -12, 3)),
            part("DeadLens", (0.56, 0.56, 0.12), (-72.8, 63.45, -2.72), material="Glass", color=RED, collide=False, transparency=0.28, cast_shadow=False),
            part("BentCrossArm", (4.0, 0.22, 0.22), (-71.45, 62.15, -3.2), material="CorrodedMetal", color=RUST, collide=False, rot=(0, 0, -11)),
        ]),
    ])


def build_exterior() -> list[dict]:
    """Return a stepped, partly buried silhouette and coherent site drainage."""

    earthworks = model("ExteriorEarthworks", [
        # Longitudinal side wedges use local X as world Z.  This creates a
        # real cross-slope toward the west wall instead of a ramp along it.
        # Every WedgePart has an explicit CFrame to prevent stale rotations.
        part("WestWorkshopInnerSlope", (39.0, 9.2, 8.0), (-100.0, 57.6, 47.5), material="Ground", color=EARTH_DARK, class_name="WedgePart", rot=(0, 90, 0)),
        part("WestWorkshopOuterSlope", (39.0, 5.8, 8.0), (-108.0, 55.9, 47.5), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 90, 0)),
        part("WestBedroomInnerSlope", (31.0, 10.0, 8.0), (-100.0, 58.0, 82.0), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 90, 0)),
        part("WestBedroomOuterSlope", (31.0, 6.5, 8.0), (-108.0, 56.25, 82.0), material="Ground", color=EARTH_DRY, class_name="WedgePart", rot=(0, 90, 0)),
        part("WestRearInnerSlope", (18.0, 8.4, 8.0), (-100.0, 57.2, 106.5), material="Ground", color=EARTH_DARK, class_name="WedgePart", rot=(0, 90, 0)),
        part("WestRearOuterSlope", (18.0, 5.2, 8.0), (-108.0, 55.6, 106.5), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 90, 0)),
        # High banks meet the west wall at X=-96 and make the lower two-thirds
        # of the concrete read as buried even from a shallow exterior camera.
        part("WestWorkshopHighBank", (2.6, 8.2, 38.0), (-97.3, 58.1, 47.5), material="Ground", color=EARTH_DARK),
        part("WestBedroomHighBank", (2.6, 9.0, 30.0), (-97.3, 58.5, 82.0), material="Ground", color=EARTH_MOSS),
        part("WestRearHighBank", (2.6, 7.6, 18.0), (-97.3, 57.8, 106.5), material="Ground", color=EARTH_DRY),
        # Starts north of Z=77, beyond the verified legacy maximum Z=72.5.
        # The narrow gap beside the east utility wall remains intentionally
        # free of earthwork while the protected legacy bunker is still live.
        part("EastPowerRearInnerSlope", (17.0, 8.2, 6.5), (-26.75, 57.1, 85.5), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, -90, 0)),
        part("EastPowerRearOuterSlope", (17.0, 4.8, 6.0), (-20.5, 55.4, 85.5), material="Ground", color=EARTH_DRY, class_name="WedgePart", rot=(0, -90, 0)),
        part("NorthRearInnerSlope", (62.0, 9.0, 8.0), (-61.0, 57.5, 116.0), material="Ground", color=EARTH_DARK, class_name="WedgePart", rot=(0, 180, 0)),
        part("NorthRearOuterSlope", (66.0, 5.4, 8.0), (-61.0, 55.7, 124.0), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 180, 0)),
        part("NorthRearHighBank", (60.0, 8.0, 2.0), (-61.0, 58.0, 113.0), material="Ground", color=EARTH_DARK),
        part("EntranceShoulderWestInner", (10.0, 8.8, 12.0), (-70.5, 57.2, 2.0), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 0, 0)),
        part("EntranceShoulderWestOuter", (13.0, 4.8, 9.0), (-71.5, 55.3, -7.0), material="Ground", color=EARTH_DRY, class_name="WedgePart", rot=(0, 0, 0)),
        part("EntranceShoulderEastInner", (10.0, 8.8, 12.0), (-49.5, 57.2, 2.0), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 0, 0)),
        part("EntranceShoulderEastOuter", (13.0, 4.8, 9.0), (-48.5, 55.3, -7.0), material="Ground", color=EARTH_DRY, class_name="WedgePart", rot=(0, 0, 0)),
        part("ServiceShoulderSouthInner", (14.0, 7.2, 6.0), (-24.0, 56.4, 94.5), material="Ground", color=EARTH_DRY, class_name="WedgePart", rot=(0, 0, 0)),
        part("ServiceShoulderSouthOuter", (12.0, 4.2, 6.0), (-17.0, 55.0, 94.5), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 0, 0)),
        part("ServiceShoulderNorthInner", (14.0, 7.2, 6.0), (-24.0, 56.4, 113.5), material="Ground", color=EARTH_DRY, class_name="WedgePart", rot=(0, 180, 0)),
        part("ServiceShoulderNorthOuter", (12.0, 4.2, 6.0), (-17.0, 55.0, 113.5), material="Ground", color=EARTH_MOSS, class_name="WedgePart", rot=(0, 180, 0)),
    ])

    stepped_roof = model("SteppedRoofSilhouette", [
        part("EntranceRoofCap", (25.0, 0.7, 13.0), (-60.0, 67.35, 14.0), material="Concrete", color=CONCRETE_WORN),
        part("EntranceRoofCrown", (13.0, 1.25, 5.8), (-60.0, 68.30, 13.6), material="Concrete", color=CONCRETE_DARK),
        part("CrownArmorBand", (13.5, 0.45, 6.2), (-60.0, 69.08, 13.6), material="DiamondPlate", color=STEEL),
        part("WestParapet", (1.0, 2.2, 13.0), (-71.5, 68.1, 14.0), material="Concrete", color=CONCRETE_WORN),
        part("EastParapet", (1.0, 2.2, 13.0), (-48.5, 68.1, 14.0), material="Concrete", color=CONCRETE_WORN),
        part("RoofSoilWest", (5.0, 0.55, 10.0), (-68.0, 67.8, 15.0), material="Ground", color=EARTH_DARK),
        part("RoofSoilEast", (5.0, 0.55, 10.0), (-52.0, 67.8, 15.0), material="Ground", color=EARTH_DARK),
        # Discontinuous roof cover lets concrete ribs and utility silhouettes
        # remain visible while breaking the single rectangular roof read.
        part("WorkshopRoofEarth", (9.5, 1.4, 15.0), (-91.0, 67.7, 36.5), material="Ground", color=EARTH_DARK, rot=(0, -3, 0)),
        part("UpgradeRoofEarth", (8.0, 1.0, 13.0), (-92.0, 68.5, 57.0), material="Ground", color=EARTH_MOSS, rot=(0, 4, 0)),
        part("BedroomRoofEarthSouth", (9.5, 1.7, 10.0), (-91.0, 67.85, 76.0), material="Ground", color=EARTH_DARK, rot=(0, 3, 0)),
        part("BedroomRoofEarthNorth", (7.5, 1.1, 9.0), (-92.0, 67.55, 90.0), material="Ground", color=EARTH_MOSS, rot=(0, -5, 0)),
        part("CommonRoofEarthWest", (7.0, 1.2, 23.0), (-66.0, 69.6, 44.0), material="Ground", color=EARTH_DARK, rot=(0, 2, 0)),
        part("CommonRoofEarthNorth", (12.0, 0.8, 7.0), (-56.0, 69.4, 53.0), material="Ground", color=EARTH_MOSS, rot=(0, -3, 0)),
        part("StorageRoofEarth", (9.0, 1.0, 15.0), (-65.0, 66.5, 69.0), material="Ground", color=EARTH_DRY, rot=(0, 5, 0)),
        part("PowerRoofEarth", (9.0, 1.2, 15.0), (-47.0, 68.6, 72.0), material="Ground", color=EARTH_DARK, rot=(0, -4, 0)),
        part("ServiceRoofCap", (20.0, 0.65, 19.0), (-39.0, 66.95, 103.0), material="Concrete", color=CONCRETE_WORN),
        part("ServiceRaisedVentDeck", (7.0, 1.0, 6.0), (-39.0, 67.75, 101.0), material="Metal", color=STEEL),
        part("ServiceVentCowling", (5.0, 1.6, 3.8), (-39.0, 69.0, 101.0), material="CorrodedMetal", color=STEEL_LIGHT),
        part("ServiceRoofEarthSouth", (5.0, 1.0, 15.0), (-45.5, 67.7, 103.0), material="Ground", color=EARTH_MOSS),
        part("ServiceRoofEarthNorth", (4.0, 0.7, 15.0), (-32.0, 67.55, 103.0), material="Ground", color=EARTH_DRY),
    ])

    retaining_and_drainage = model("RetainingAndDrainage", [
        part("WestRetainingToe", (1.0, 2.2, 67.0), (-96.8, 55.1, 65.0), material="Concrete", color=CONCRETE_WORN),
        part("EastRetainingToe", (1.0, 2.0, 16.0), (-29.3, 55.0, 86.0), material="Concrete", color=CONCRETE_WORN),
        part("RearRetainingToe", (52.0, 2.0, 1.0), (-62.0, 55.0, 112.8), material="Concrete", color=CONCRETE_WORN),
        part("WestRunoffChannel", (0.7, 0.18, 62.0), (-102.2, 53.52, 65.0), material="Concrete", color=CONCRETE_DARK, collide=False),
        part("EastRunoffChannel", (0.7, 0.18, 38.0), (-23.2, 53.52, 75.0), material="Concrete", color=CONCRETE_DARK, collide=False),
        part("RearRunoffChannel", (54.0, 0.18, 0.7), (-62.0, 53.52, 119.2), material="Concrete", color=CONCRETE_DARK, collide=False),
        part("EntranceRetainingWest", (6.0, 3.0, 0.8), (-69.0, 55.5, -1.4), material="Concrete", color=CONCRETE_WORN),
        part("EntranceRetainingEast", (6.0, 3.0, 0.8), (-51.0, 55.5, -1.4), material="Concrete", color=CONCRETE_WORN),
        part("FadedFacilityPlate", (8.0, 1.6, 0.12), (-60.0, 62.4, 5.63), material="Metal", color=AGED_WHITE, collide=False),
        part("FacilityPlateWarningBar", (6.8, 0.28, 0.08), (-60.0, 61.95, 5.55), material="SmoothPlastic", color=RED, collide=False, cast_shadow=False),
    ])

    return [earthworks, stepped_roof, retaining_and_drainage, _exterior_utility_landmarks()]
