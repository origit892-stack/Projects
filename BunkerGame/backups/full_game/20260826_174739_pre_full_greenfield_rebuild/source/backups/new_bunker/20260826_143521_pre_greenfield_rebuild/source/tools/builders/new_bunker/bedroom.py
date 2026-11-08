"""Starting-bedroom dressing and first-person wake composition.

This module owns only the contents of ``NewBunker/Bedroom``.  The structural
shell and localized light sources are assembled by the architecture and
lighting modules respectively.
"""

from __future__ import annotations

from .kit import (
    AGED_WHITE,
    CONCRETE_DARK,
    CONCRETE_WORN,
    FABRIC,
    FLOOR_Y,
    GREEN,
    RED,
    RUST,
    STEEL,
    STEEL_LIGHT,
    UTILITY_BLUE,
    WOOD,
    crate,
    model,
    part,
    pipe,
    shelf,
)


# Runtime spawn is deliberately separate from the cinematic camera.  This
# point sits in the open floor pocket southeast of the cot: its nearest cot
# collision is more than four studs away, leaving a full character-radius
# buffer while retaining a direct diagonal route to the east-wall exit.
WAKE_MARKER_POSITION = (-83.8, FLOOR_Y + 0.1, 82.4)

# QA route anchors.  Navigate into the room via the inner doorway target, then
# to WAKE_MARKER_POSITION; test outbound from the marker through the portal to
# the west residential corridor target.
WAKE_ROUTE_INBOUND_TARGET = (-79.8, FLOOR_Y + 0.1, 76.0)
WAKE_ROUTE_OUTBOUND_TARGET = (-76.2, FLOOR_Y + 0.1, 76.0)

# Director-review camera: pillow-height at the head of the cot.  The mattress,
# blanket and foot rail extend toward the lower foreground before the view
# opens diagonally onto the east-wall exit at X=-78, Z=76.
WAKE_CAMERA_POSITION = (-92.55, 57.15, 87.45)
WAKE_LOOK_TARGET = (-77.35, 57.85, 75.85)


def _cot() -> dict:
    """A low, battered military cot that fills the wake-view foreground."""
    return model(
        "AbandonedMilitaryCot",
        [
            part("NorthSideRail", (7.2, 0.28, 0.28), (-90.45, 55.35, 89.05), material="Metal", color=STEEL),
            part("SouthSideRail", (7.2, 0.28, 0.28), (-90.45, 55.35, 85.95), material="Metal", color=STEEL),
            part("HeadCrossRail", (0.3, 2.9, 3.45), (-94.0, 56.4, 87.5), material="Metal", color=STEEL),
            part("FootCrossRail", (0.3, 2.15, 3.45), (-86.9, 56.0, 87.5), material="Metal", color=STEEL_LIGHT),
            part("HeadTopBar", (0.35, 0.35, 3.65), (-94.0, 57.85, 87.5), material="Metal", color=STEEL_LIGHT),
            part("NorthHeadFoot", (0.3, 1.35, 0.3), (-93.8, 54.68, 88.8), material="Metal", color=STEEL),
            part("SouthHeadFoot", (0.3, 1.35, 0.3), (-93.8, 54.68, 86.2), material="Metal", color=STEEL),
            part("NorthFootLeg", (0.3, 1.35, 0.3), (-87.1, 54.68, 88.8), material="Metal", color=STEEL),
            part("SouthFootLeg", (0.3, 1.35, 0.3), (-87.1, 54.68, 86.2), material="Metal", color=STEEL),
            part("SaggingMattress", (6.75, 0.62, 2.85), (-90.45, 55.82, 87.5), material="Fabric", color=FABRIC, rot=(0, 0, -1.5)),
            part("MattressSeamNorth", (6.35, 0.08, 0.08), (-90.45, 56.12, 88.87), material="Fabric", color=AGED_WHITE, collide=False),
            part("MattressSeamSouth", (6.35, 0.08, 0.08), (-90.45, 56.12, 86.13), material="Fabric", color=AGED_WHITE, collide=False),
            part("FoldedBlanketLower", (3.3, 0.16, 2.94), (-88.45, 56.18, 87.5), material="Fabric", color=GREEN, collide=False, rot=(0, 0, -3)),
            part("BlanketFold", (0.42, 0.24, 2.88), (-89.95, 56.29, 87.5), material="Fabric", color=[0.15, 0.22, 0.18], collide=False, rot=(0, 0, -3)),
            part("WornPillow", (1.45, 0.36, 2.2), (-92.65, 56.36, 87.45), material="Fabric", color=AGED_WHITE, collide=False, rot=(0, 0, 5)),
            part("CotRepairStrap", (0.22, 0.12, 3.2), (-87.75, 56.32, 87.5), material="Fabric", color=[0.22, 0.15, 0.10], collide=False),
            part("NorthRailRustCuff", (0.62, 0.34, 0.34), (-87.65, 55.35, 89.05), material="CorrodedMetal", color=RUST, collide=False),
            part("SouthRailRustCuff", (0.5, 0.34, 0.34), (-92.8, 55.35, 85.95), material="CorrodedMetal", color=RUST, collide=False),
            part("FootRailRustPatch", (0.34, 0.55, 0.6), (-86.88, 55.25, 88.6), material="CorrodedMetal", color=RUST, collide=False),
        ],
    )


def _locker_bank() -> dict:
    """Segmented locker construction; avoids a single large colored cuboid."""
    return model(
        "TwoDoorLockerBank",
        [
            part("LockerBack", (0.35, 7.2, 4.6), (-95.1, 57.6, 74.0), material="Metal", color=STEEL),
            part("LockerOuterWest", (1.8, 7.2, 0.22), (-94.2, 57.6, 71.8), material="CorrodedMetal", color=STEEL_LIGHT),
            part("LockerOuterEast", (1.8, 7.2, 0.22), (-94.2, 57.6, 76.2), material="CorrodedMetal", color=STEEL_LIGHT),
            part("LockerTop", (1.8, 0.24, 4.6), (-94.2, 61.2, 74.0), material="Metal", color=STEEL_LIGHT),
            part("LockerBottom", (1.8, 0.24, 4.6), (-94.2, 54.12, 74.0), material="Metal", color=STEEL),
            part("CenterDivider", (1.82, 7.0, 0.16), (-94.18, 57.55, 74.0), material="Metal", color=STEEL),
            part("SouthDoorInset", (0.16, 6.45, 1.72), (-93.27, 57.62, 72.92), material="Metal", color=[0.25, 0.30, 0.27], collide=False),
            part("NorthDoorInset", (0.16, 6.45, 1.72), (-93.27, 57.62, 75.08), material="CorrodedMetal", color=[0.21, 0.25, 0.23], collide=False, rot=(0, 0, -1.2)),
            part("SouthHandle", (0.18, 0.95, 0.18), (-93.12, 58.0, 73.55), material="Metal", color=AGED_WHITE, collide=False),
            part("NorthHandle", (0.18, 0.95, 0.18), (-93.12, 58.0, 74.45), material="Metal", color=AGED_WHITE, collide=False),
            part("SouthVentUpper", (0.12, 0.12, 1.1), (-93.1, 60.0, 72.9), material="Metal", color=CONCRETE_DARK, collide=False),
            part("SouthVentLower", (0.12, 0.12, 1.1), (-93.1, 59.55, 72.9), material="Metal", color=CONCRETE_DARK, collide=False),
            part("NorthVentUpper", (0.12, 0.12, 1.1), (-93.1, 60.0, 75.1), material="Metal", color=CONCRETE_DARK, collide=False),
            part("NorthVentLower", (0.12, 0.12, 1.1), (-93.1, 59.55, 75.1), material="Metal", color=CONCRETE_DARK, collide=False),
            part("LowerEdgeOxidationSouth", (0.12, 0.42, 0.7), (-93.08, 54.62, 72.65), material="CorrodedMetal", color=RUST, collide=False, transparency=0.12),
            part("LowerEdgeOxidationNorth", (0.12, 0.3, 0.5), (-93.08, 54.56, 75.35), material="CorrodedMetal", color=RUST, collide=False, transparency=0.16),
        ],
    )


def _storage_and_personal_details() -> list[dict]:
    return [
        shelf("BedroomUtilityShelf", (-82.0, 58.0, 92.9), 5.6, 7.0, 1.8),
        crate("PersonalEffectsCrate", (-83.3, 55.05, 92.6), (2.25, 1.9, 1.55)),
        model(
            "ShelfContents",
            [
                part("FoldedWorkShirt", (1.65, 0.32, 1.15), (-83.1, 60.2, 92.55), material="Fabric", color=[0.34, 0.35, 0.31], collide=False),
                part("ClothFold", (1.5, 0.12, 0.18), (-83.1, 60.41, 92.05), material="Fabric", color=AGED_WHITE, collide=False),
                part("TinCup", (0.58, 0.7, 0.58), (-80.45, 57.55, 92.4), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 0, 90)),
                part("SmallMedicalTin", (1.1, 0.55, 0.85), (-81.7, 57.45, 92.5), material="Metal", color=AGED_WHITE, collide=False),
                part("MedicalTinMark", (0.36, 0.08, 0.12), (-81.7, 57.76, 92.05), material="SmoothPlastic", color=RED, collide=False, cast_shadow=False),
                part("RolledCloth", (1.5, 0.58, 0.58), (-81.3, 55.05, 92.4), material="Fabric", color=GREEN, collide=False, shape="Cylinder"),
                part("ShelfInventoryTag", (1.15, 0.26, 0.07), (-82.0, 58.22, 91.92), material="SmoothPlastic", color=AGED_WHITE, collide=False, cast_shadow=False),
            ],
        ),
        model(
            "BedsidePersonalTrace",
            [
                part("LowBedsideBox", (1.6, 1.4, 1.6), (-94.0, 54.7, 90.7), material="WoodPlanks", color=WOOD),
                part("OldBook", (1.1, 0.18, 0.75), (-94.0, 55.5, 90.7), material="Fabric", color=[0.20, 0.16, 0.12], collide=False, rot=(0, 12, 0)),
                part("EmptyBottle", (0.42, 1.05, 0.42), (-93.6, 56.05, 90.8), material="Glass", color=UTILITY_BLUE, collide=False, transparency=0.38, shape="Cylinder", rot=(0, 0, 90), cast_shadow=False),
            ],
        ),
    ]


def _wall_infrastructure() -> list[dict]:
    return [
        model(
            "WestWallUtilityBay",
            [
                part("RecessBack", (0.28, 5.0, 4.4), (-95.43, 59.2, 82.0), material="Metal", color=CONCRETE_DARK),
                part("RecessTop", (0.8, 0.42, 5.0), (-95.12, 61.75, 82.0), material="CorrodedMetal", color=STEEL_LIGHT),
                part("PanelHousing", (0.7, 3.4, 2.6), (-95.0, 59.0, 82.3), material="Metal", color=STEEL),
                part("PanelFace", (0.12, 2.85, 2.12), (-94.58, 59.0, 82.3), material="Metal", color=[0.23, 0.28, 0.25], collide=False),
                part("DeadIndicator", (0.1, 0.36, 0.36), (-94.49, 59.6, 81.7), material="SmoothPlastic", color=RED, collide=False, cast_shadow=False),
                part("FuseRow", (0.1, 0.28, 1.18), (-94.48, 58.7, 82.45), material="Metal", color=AGED_WHITE, collide=False),
                part("PanelWearEdge", (0.1, 2.2, 0.2), (-94.47, 58.9, 83.35), material="CorrodedMetal", color=RUST, collide=False),
            ],
        ),
        model(
            "OverheadPipeRun",
            [
                pipe("ColdWaterLine", (-87.0, 64.75, 94.05), 15.0, "x", 0.5, UTILITY_BLUE),
                pipe("ReturnLine", (-87.0, 64.05, 94.05), 14.8, "x", 0.32, RUST),
                pipe("WestPipeDrop", (-94.25, 61.25, 94.05), 5.6, "y", 0.5, UTILITY_BLUE),
                part("PipeSupportWest", (0.35, 1.4, 1.6), (-92.2, 64.4, 94.3), material="Metal", color=STEEL_LIGHT, collide=False),
                part("PipeSupportEast", (0.35, 1.4, 1.6), (-82.0, 64.4, 94.3), material="Metal", color=STEEL_LIGHT, collide=False),
                part("IsolationValve", (0.2, 1.5, 1.5), (-94.0, 59.4, 94.05), material="CorrodedMetal", color=RED, collide=False, shape="Cylinder"),
            ],
        ),
        model(
            "ExitWallVent",
            [
                part("VentRecess", (4.8, 2.8, 0.35), (-86.6, 61.5, 68.42), material="Metal", color=CONCRETE_DARK),
                part("VentFrameTop", (4.9, 0.24, 0.55), (-86.6, 62.86, 68.26), material="Metal", color=STEEL_LIGHT, collide=False),
                part("VentFrameBottom", (4.9, 0.24, 0.55), (-86.6, 60.14, 68.26), material="Metal", color=STEEL_LIGHT, collide=False),
                part("VentSlat01", (4.1, 0.14, 0.12), (-86.6, 62.25, 68.18), material="Metal", color=STEEL_LIGHT, collide=False),
                part("VentSlat02", (4.1, 0.14, 0.12), (-86.6, 61.65, 68.18), material="Metal", color=STEEL_LIGHT, collide=False),
                part("VentSlat03", (4.1, 0.14, 0.12), (-86.6, 61.05, 68.18), material="Metal", color=STEEL_LIGHT, collide=False),
                part("VentSlat04", (4.1, 0.14, 0.12), (-86.6, 60.45, 68.18), material="Metal", color=STEEL_LIGHT, collide=False),
            ],
        ),
        model(
            "EastWallConduit",
            [
                part("MainConduit", (0.18, 6.0, 0.18), (-78.62, 61.0, 83.2), material="Metal", color=STEEL_LIGHT, collide=False),
                part("ConduitBend", (0.18, 0.18, 6.6), (-78.62, 63.9, 80.0), material="Metal", color=STEEL_LIGHT, collide=False),
                part("JunctionBox", (0.55, 1.25, 1.25), (-78.75, 59.15, 83.2), material="Metal", color=STEEL, collide=False),
                part("JunctionCover", (0.12, 0.88, 0.88), (-78.43, 59.15, 83.2), material="CorrodedMetal", color=[0.24, 0.27, 0.25], collide=False),
            ],
        ),
    ]


def _exit_composition() -> dict:
    """Layered but intentionally low-profile framing around the room exit."""
    return model(
        "BedroomExitFocalLayer",
        [
            # Cabinet is north of the sightline and works as midground framing,
            # not a mass between the cot and portal.
            part("ExitUtilityPlinth", (1.25, 0.4, 1.8), (-80.15, 54.2, 83.45), material="Concrete", color=CONCRETE_WORN),
            part("ExitUtilityCabinet", (1.3, 3.25, 1.75), (-80.15, 55.82, 83.45), material="Metal", color=STEEL),
            part("CabinetInset", (1.0, 2.55, 0.12), (-80.15, 55.9, 82.52), material="Metal", color=[0.23, 0.28, 0.25], collide=False),
            part("CabinetPull", (0.5, 0.14, 0.14), (-80.15, 56.05, 82.41), material="Metal", color=AGED_WHITE, collide=False),
            part("ExitWarningPlate", (0.12, 2.4, 1.45), (-78.48, 60.1, 72.45), material="Metal", color=AGED_WHITE, collide=False),
            part("ExitWarningStripeUpper", (0.08, 0.3, 1.05), (-78.39, 60.45, 72.45), material="SmoothPlastic", color=RED, collide=False, rot=(22, 0, 0), cast_shadow=False),
            part("ExitWarningStripeLower", (0.08, 0.3, 1.05), (-78.39, 59.75, 72.45), material="SmoothPlastic", color=RED, collide=False, rot=(22, 0, 0), cast_shadow=False),
            part("HangingCable", (0.14, 3.8, 0.14), (-79.0, 61.4, 69.8), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, -7)),
            part("ThresholdWear", (1.1, 0.04, 4.6), (-78.65, 54.16, 76.0), material="CorrodedMetal", color=RUST, collide=False, transparency=0.18, cast_shadow=False),
            # Secondary inner reveal makes the portal read as a layered bunker
            # opening after the architecture module supplies its main frame.
            part("InnerRevealSouth", (0.38, 7.7, 0.42), (-78.78, 57.85, 72.65), material="Metal", color=STEEL_LIGHT, collide=False),
            part("InnerRevealNorth", (0.38, 7.7, 0.42), (-78.78, 57.85, 79.35), material="Metal", color=STEEL_LIGHT, collide=False),
            part("InnerRevealHeader", (0.38, 0.42, 7.1), (-78.78, 61.72, 76.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("ExitPracticalHousing", (1.25, 0.75, 3.3), (-79.0, 62.45, 76.0), material="Metal", color=STEEL, collide=False),
            part("ExitPracticalDiffuser", (0.18, 0.38, 2.55), (-78.88, 62.08, 76.0), material="Glass", color=AGED_WHITE, collide=False, transparency=0.16, cast_shadow=False),
            part("ExitFloorLeadIn", (3.8, 0.05, 0.48), (-80.55, 54.15, 76.0), material="SmoothPlastic", color=[0.34, 0.31, 0.18], collide=False, cast_shadow=False),
        ],
    )


def _abandonment_details() -> dict:
    return model(
        "RestrainedAbandonmentDetails",
        [
            part("FallenPanelCover", (2.25, 0.14, 1.45), (-84.0, 54.16, 72.0), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 24, 0)),
            part("LooseFastenerA", (0.24, 0.24, 0.24), (-85.0, 54.18, 72.7), material="Metal", color=RUST, collide=False, shape="Ball"),
            part("LooseFastenerB", (0.18, 0.18, 0.18), (-83.0, 54.16, 71.4), material="Metal", color=RUST, collide=False, shape="Ball"),
            part("DroppedCan", (0.68, 0.68, 0.68), (-84.0, 54.38, 83.0), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 20, 18)),
            part("PaperScrapA", (1.0, 0.035, 0.65), (-85.5, 54.06, 80.6), material="SmoothPlastic", color=AGED_WHITE, collide=False, rot=(0, 18, 0), cast_shadow=False),
            part("PaperScrapB", (0.72, 0.035, 0.5), (-84.85, 54.065, 81.25), material="SmoothPlastic", color=[0.36, 0.35, 0.30], collide=False, rot=(0, -14, 0), cast_shadow=False),
            part("RubbleChunkLarge", (0.9, 0.48, 0.7), (-80.25, 54.24, 89.3), material="Concrete", color=CONCRETE_WORN, collide=False, rot=(10, 18, 5)),
            part("RubbleChunkSmall", (0.55, 0.3, 0.45), (-80.9, 54.16, 88.75), material="Concrete", color=CONCRETE_WORN, collide=False, rot=(0, -22, 9)),
            part("DampPatch", (4.6, 2.2, 0.06), (-89.2, 56.3, 95.48), material="Concrete", color=[0.11, 0.15, 0.15], collide=False, transparency=0.22, cast_shadow=False),
            part("CobwebThreadA", (0.035, 2.6, 0.035), (-95.1, 63.5, 95.05), material="SmoothPlastic", color=AGED_WHITE, collide=False, transparency=0.52, rot=(0, 0, 36), cast_shadow=False),
            part("CobwebThreadB", (0.035, 2.2, 0.035), (-94.35, 63.55, 95.05), material="SmoothPlastic", color=AGED_WHITE, collide=False, transparency=0.56, rot=(0, 0, -44), cast_shadow=False),
        ],
    )


def _bedroom_ventilation_radiator() -> dict:
    """Asymmetric wall-mounted utility mass outside the wake/locker circulation lane."""

    return model("BedroomVentilationRadiator", [
        part("LowerPipe", (4.8, 0.42, 0.42), (-91.2, 56.0, 95.12), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 90, 0)),
        part("UpperPipe", (4.8, 0.34, 0.34), (-91.2, 60.6, 95.12), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 90, 0)),
        part("WestHeader", (0.55, 5.4, 0.55), (-93.45, 58.3, 95.12), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder"),
        part("EastHeader", (0.55, 5.4, 0.55), (-88.95, 58.3, 95.12), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder"),
        part("RadiatorBank", (3.6, 3.5, 0.34), (-91.2, 58.3, 94.92), material="Metal", color=CONCRETE_DARK, collide=False),
        part("RadiatorFinWest", (0.22, 3.0, 0.48), (-92.25, 58.3, 94.70), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 0, 5)),
        part("RadiatorFinCenter", (0.22, 3.0, 0.48), (-91.2, 58.3, 94.70), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -3)),
        part("RadiatorFinEast", (0.22, 3.0, 0.48), (-90.15, 58.3, 94.70), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 0, 4)),
        part("ValveWheel", (0.20, 1.25, 1.25), (-93.45, 60.25, 94.76), material="CorrodedMetal", color=RED, collide=False, shape="Cylinder"),
    ])


def build_bedroom() -> list[dict]:
    """Return bedroom-owned children for the shared ``Bedroom`` model."""
    children = [_cot(), _locker_bank()]
    children.extend(_storage_and_personal_details())
    children.extend(_wall_infrastructure())
    children.extend([_exit_composition(), _abandonment_details(), _bedroom_ventilation_radiator()])
    return children


def bedroom_markers() -> list[dict]:
    """Return composition markers owned by this room for central assembly."""
    return [
        part(
            "PlayerWakeMarker",
            (1.6, 0.12, 1.6),
            WAKE_MARKER_POSITION,
            material="SmoothPlastic",
            color=GREEN,
            collide=False,
            transparency=1.0,
            cast_shadow=False,
        )
    ]
