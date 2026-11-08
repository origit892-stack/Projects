"""Trader space and restrained human-use storytelling for ``NewBunker``.

The shop occupies X=-39..-30, Z=30..52.  Its west portal is centred at
Z=42, so the customer lane remains entirely clear from X=-38.5 to X=-34.35.
The counter is architectural furniture rather than a loose box: a low,
segmented cabinet line supports a framed service opening and a rolled-up
security shutter.  Storage and the future trader position live behind it.

Director-review camera suggestion: position ``(-38.1, 59.1, 42.0)`` and look
toward ``(-31.4, 58.1, 42.0)``.  The service opening, counter activity, and
back-room storage layer in one player-height composition.
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
    YELLOW,
    crate,
    model,
    part,
)


SHOP_REVIEW_CAMERA = (-38.1, 59.1, 42.0)
SHOP_REVIEW_TARGET = (-31.4, 58.1, 42.0)


def _service_counter() -> dict:
    """Build a human-height counter with a readable, unobstructed opening."""

    cabinet_z = (35.6, 39.35, 44.65, 48.4)
    children = [
        # A continuous battered timber cap unifies the deliberately segmented
        # metal cabinets without reading as a monolithic colored block.
        part(
            "WornTimberCounterCap",
            (1.45, 0.34, 15.8),
            (-33.62, 57.32, 42.0),
            material="WoodPlanks",
            color=WOOD,
        ),
        part(
            "CustomerEdgeBand",
            (0.16, 0.52, 15.25),
            (-34.37, 57.15, 42.0),
            material="CorrodedMetal",
            color=STEEL_LIGHT,
            collide=False,
        ),
        part(
            "CounterToeRail",
            (0.22, 0.38, 14.9),
            (-34.27, 54.38, 42.0),
            material="CorrodedMetal",
            color=RUST,
            collide=False,
        ),
    ]
    for index, z in enumerate(cabinet_z, 1):
        children.extend(
            [
                part(
                    f"LowerCabinet{index:02d}",
                    (1.25, 2.8, 3.25),
                    (-33.6, 55.55, z),
                    material="Metal",
                    color=GREEN if index in (1, 4) else STEEL,
                ),
                part(
                    f"CabinetInset{index:02d}",
                    (0.10, 2.15, 2.55),
                    (-34.24, 55.65, z),
                    material="Metal",
                    color=CONCRETE_DARK,
                    collide=False,
                ),
                part(
                    f"CabinetPull{index:02d}",
                    (0.12, 0.16, 0.72),
                    (-34.31, 56.0, z - 0.65),
                    material="Metal",
                    color=AGED_WHITE,
                    collide=False,
                ),
            ]
        )
    return model("IntegratedTraderCounter", children)


def _service_window() -> dict:
    """Frame the trader as part of the bunker, with the shutter safely open."""

    children = [
        part("SouthJamb", (0.7, 7.6, 0.7), (-33.15, 59.8, 34.35), material="Metal", color=STEEL_LIGHT),
        part("NorthJamb", (0.7, 7.6, 0.7), (-33.15, 59.8, 49.65), material="Metal", color=STEEL_LIGHT),
        part("OverheadHeader", (0.9, 0.75, 16.0), (-33.15, 63.55, 42.0), material="Metal", color=STEEL_LIGHT),
        part("HeaderInnerShadow", (0.14, 0.38, 14.55), (-33.62, 63.38, 42.0), material="Metal", color=CONCRETE_DARK, collide=False),
        part("RolledShutterDrum", (14.25, 0.72, 0.72), (-33.66, 62.78, 42.0), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 90, 0)),
    ]
    # A few tight slats describe the rolled shutter while preserving the full
    # service sightline below Y=62.3.
    for index, y in enumerate((62.28, 62.48, 62.68), 1):
        children.append(
            part(
                f"RolledShutterSlat{index:02d}",
                (0.16, 0.12, 13.7),
                (-34.03, y, 42.0),
                material="CorrodedMetal",
                color=STEEL_LIGHT if index == 2 else RUST,
                collide=False,
            )
        )
    children.extend(
        [
            part("SouthShutterGuide", (0.16, 4.6, 0.28), (-34.04, 59.75, 34.7), material="Metal", color=STEEL, collide=False),
            part("NorthShutterGuide", (0.16, 4.6, 0.28), (-34.04, 59.75, 49.3), material="Metal", color=STEEL, collide=False),
            part("ManualShutterChain", (0.10, 3.1, 0.10), (-34.02, 60.55, 49.05), material="Metal", color=AGED_WHITE, collide=False),
            part("ChainWeight", (0.24, 0.48, 0.24), (-34.02, 58.95, 49.05), material="CorrodedMetal", color=RUST, collide=False),
        ]
    )
    return model("FramedServiceOpening", children)


def _back_counter_storage() -> dict:
    """Dense stock storage kept behind the service line and off circulation."""

    children = [
        part("RackBack", (0.22, 7.2, 8.3), (-30.62, 58.0, 46.4), material="Metal", color=CONCRETE_DARK),
        part("SouthUpright", (0.72, 7.2, 0.28), (-30.95, 58.0, 42.35), material="Metal", color=STEEL_LIGHT),
        part("CenterUpright", (0.72, 7.2, 0.28), (-30.95, 58.0, 46.4), material="CorrodedMetal", color=STEEL_LIGHT),
        part("NorthUpright", (0.72, 7.2, 0.28), (-30.95, 58.0, 50.45), material="Metal", color=STEEL_LIGHT),
    ]
    for index, y in enumerate((54.65, 57.35, 60.05), 1):
        children.append(
            part(
                f"StockShelf{index:02d}",
                (1.15, 0.25, 8.35),
                (-31.08, y, 46.4),
                material="DiamondPlate",
                color=STEEL,
            )
        )
    children.extend(
        [
            part("WrappedFilterBundle", (0.72, 1.1, 2.5), (-31.35, 58.0, 44.2), material="Fabric", color=FABRIC, collide=False),
            part("SpareClothRoll", (2.2, 0.72, 0.72), (-31.32, 60.55, 48.7), material="Fabric", color=GREEN, collide=False, shape="Cylinder", rot=(0, 90, 0)),
            part("SmallPartsTinA", (0.82, 0.64, 0.64), (-31.35, 57.9, 47.1), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("SmallPartsTinB", (0.82, 0.64, 0.64), (-31.35, 57.9, 48.0), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            crate("LowerSalvageCrate", (-31.65, 55.05, 33.1), (1.45, 1.9, 2.8)),
        ]
    )
    return model("BehindCounterStorage", children)


def _human_support_details() -> dict:
    """Show repeated human use without assigning an identity or story event."""

    return model(
        "TraderSupportDetails",
        [
            part("WorkStoolSeat", (1.45, 0.30, 1.45), (-31.65, 56.1, 40.2), material="WoodPlanks", color=WOOD),
            part("WorkStoolStem", (0.34, 2.05, 0.34), (-31.65, 55.05, 40.2), material="Metal", color=STEEL),
            part("WorkStoolFoot", (1.25, 0.18, 1.25), (-31.65, 54.15, 40.2), material="CorrodedMetal", color=RUST),
            part("CounterScaleBase", (1.35, 0.42, 1.25), (-33.55, 57.7, 38.2), material="Metal", color=STEEL_LIGHT, collide=False),
            part("ScaleDial", (0.16, 0.92, 0.92), (-34.30, 58.2, 38.2), material="SmoothPlastic", color=AGED_WHITE, collide=False, shape="Cylinder"),
            part("ScaleNeedle", (0.08, 0.46, 0.10), (-34.40, 58.2, 38.2), material="SmoothPlastic", color=RED, collide=False, rot=(0, 0, -22)),
            part("Ledger", (0.92, 0.12, 1.35), (-33.55, 57.57, 42.2), material="Fabric", color=[0.22, 0.17, 0.12], collide=False, rot=(0, -9, 0)),
            part("ShortPencil", (0.12, 0.12, 0.9), (-34.0, 57.69, 42.55), material="Wood", color=YELLOW, collide=False, rot=(0, 24, 0)),
            part("TinMug", (0.58, 0.68, 0.58), (-33.55, 57.78, 45.0), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("BarterTray", (0.72, 0.18, 2.2), (-34.0, 57.59, 47.1), material="CorrodedMetal", color=STEEL, collide=False),
            part("FoldedRepairCloth", (0.78, 0.28, 1.4), (-33.85, 57.81, 47.2), material="Fabric", color=GREEN, collide=False),
            part("LowUtilityCabinet", (1.25, 3.6, 3.1), (-31.25, 55.8, 36.6), material="Metal", color=STEEL),
            part("UtilityCabinetFace", (0.10, 2.9, 2.45), (-31.92, 55.9, 36.6), material="Metal", color=UTILITY_BLUE, collide=False),
            part("UtilityCabinetLatch", (0.12, 0.52, 0.18), (-31.99, 56.1, 35.85), material="Metal", color=AGED_WHITE, collide=False),
        ],
    )


def _functional_markings() -> dict:
    """Small-scale functional language; no oversized signage or narrative text."""

    return model(
        "ShopFunctionalMarkings",
        [
            part("CounterWearStrip", (0.10, 0.22, 9.8), (-34.46, 56.55, 42.0), material="CorrodedMetal", color=RUST, collide=False, transparency=0.12),
            part("ServiceIndicatorHousing", (0.24, 1.25, 1.45), (-33.25, 61.0, 35.25), material="Metal", color=STEEL, collide=False),
            part("ServiceIndicator", (0.12, 0.42, 0.42), (-33.40, 61.15, 35.25), material="Neon", color=RED, collide=False, cast_shadow=False),
            part("FadedQueueLine", (0.55, 0.035, 8.8), (-36.2, FLOOR_Y + 0.025, 42.0), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.45, cast_shadow=False),
            part("QueueEndCapSouth", (1.4, 0.035, 0.42), (-36.2, FLOOR_Y + 0.027, 37.7), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.48, cast_shadow=False),
            part("QueueEndCapNorth", (1.4, 0.035, 0.42), (-36.2, FLOOR_Y + 0.027, 46.3), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.48, cast_shadow=False),
        ],
    )


def _shop_silhouette_layer() -> dict:
    """Give the trader bay a deeper industrial silhouette without narrowing its customer lane."""

    return model("ShopMechanicalCanopy", [
        part("SouthCantilever", (2.8, 0.42, 0.48), (-32.25, 63.25, 35.0), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -8)),
        part("NorthCantilever", (2.8, 0.42, 0.48), (-32.25, 63.25, 49.0), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, 8)),
        part("CanopySpine", (0.55, 0.48, 13.6), (-31.35, 63.55, 42.0), material="Metal", color=STEEL, collide=False),
        part("SouthHangingUtility", (0.62, 2.7, 0.62), (-31.35, 61.85, 35.7), material="CorrodedMetal", color=RUST, collide=False, rot=(0, 0, 4)),
        part("NorthHangingUtility", (0.48, 2.2, 0.48), (-31.35, 62.05, 48.5), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -5)),
        part("OverheadCableDark", (0.16, 0.16, 11.8), (-31.65, 63.15, 42.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False),
        part("OverheadCableBlue", (0.13, 0.13, 9.8), (-31.88, 62.95, 42.8), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
        part("PatchedCanopySkin", (1.55, 0.12, 4.2), (-32.25, 63.05, 45.6), material="CorrodedMetal", color=RUST, collide=False, rot=(0, 3, -4)),
    ])


def build_shop_area() -> list[dict]:
    """Return shop-owned children for the shared ``ShopArea`` model."""

    return [
        _service_counter(),
        _service_window(),
        _back_counter_storage(),
        _human_support_details(),
        _functional_markings(),
        _shop_silhouette_layer(),
    ]



def _service_exit_evacuation_story() -> dict:
    """Environmental evidence of an interrupted evacuation at the service exit.

    Presentation-only: all authored parts are non-colliding, non-touching, and
    non-queryable through the shared ``part`` helper.
    """
    return model('ServiceExitEvacuationStory', [
        model('AbandonedEvacuationKit', [
            part('EmergencyBagBody', (2.15, 0.62, 1.35), (27.1, 54.38, 121.75), material='Fabric', color=[0.18, 0.2, 0.16], collide=False),
            part('EmergencyBagFlap', (1.75, 0.12, 1.08), (27.0, 54.74, 121.75), material='Fabric', color=[0.12, 0.14, 0.12], collide=False),
            part('EmergencyBagStrap', (0.16, 0.08, 1.55), (27.1, 54.78, 121.75), material='SmoothPlastic', color=[0.08, 0.09, 0.08], collide=False),
            part('DroppedFilterCanister', (0.72, 0.72, 0.72), (25.75, 54.38, 122.15), material='CorrodedMetal', color=[0.2, 0.22, 0.2], collide=False),
            part('DiscardedGlove', (0.78, 0.08, 0.42), (24.9, 54.1, 121.35), material='Fabric', color=[0.16, 0.18, 0.15], collide=False),
        ]),
        model('FailedExitProcedure', [
            part('FadedEmergencyPanel', (0.08, 2.45, 3.8), (29.36, 59.15, 122.25), color=[0.24, 0.23, 0.18], collide=False),
            part('WarningBandUpper', (0.045, 0.18, 3.15), (29.31, 59.72, 122.25), material='SmoothPlastic', color=[0.48, 0.31, 0.06], collide=False, transparency=0.16, cast_shadow=False),
            part('WarningBandLower', (0.045, 0.18, 2.25), (29.3, 58.55, 122.25), material='SmoothPlastic', color=[0.4, 0.12, 0.055], collide=False, transparency=0.22, cast_shadow=False),
            part('DeadIndicator', (0.04, 0.34, 0.34), (29.28, 59.15, 121.15), material='SmoothPlastic', color=[0.12, 0.055, 0.035], collide=False, cast_shadow=False),
            part('ScratchedProcedureStrip', (0.035, 0.12, 1.45), (29.27, 58.95, 122.55), material='SmoothPlastic', color=[0.55, 0.52, 0.4], collide=False, transparency=0.35, cast_shadow=False),
        ]),
        model('DamagedServiceFeed', [
            part('LooseCableUpper', (4.4, 0.13, 0.13), (17.2, 62.25, 121.65), material='SmoothPlastic', color=[0.055, 0.06, 0.055], collide=False),
            part('LooseCableDrop', (0.13, 2.25, 0.13), (15.05, 61.2, 121.65), material='SmoothPlastic', color=[0.055, 0.06, 0.055], collide=False),
            part('CableEndSleeve', (0.34, 0.42, 0.34), (15.05, 60.08, 121.65), material='CorrodedMetal', color=[0.18, 0.16, 0.13], collide=False),
            part('OldJunctionPlate', (0.08, 1.45, 1.65), (14.66, 60.0, 120.0), material='CorrodedMetal', color=[0.17, 0.18, 0.17], collide=False),
        ]),
        model('EvacuationFloorEvidence', [
            part('DraggedMudTraceA', (2.8, 0.018, 0.42), (26.2, 54.025, 118.9), material='SmoothPlastic', color=[0.105, 0.085, 0.06], collide=False, transparency=0.38, cast_shadow=False),
            part('DraggedMudTraceB', (2.1, 0.018, 0.34), (28.1, 54.026, 119.55), material='SmoothPlastic', color=[0.105, 0.085, 0.06], collide=False, transparency=0.46, cast_shadow=False),
            part('WaterDripPool', (1.35, 0.016, 1.8), (16.0, 54.023, 110.3), material='SmoothPlastic', color=[0.08, 0.12, 0.13], collide=False, transparency=0.58, cast_shadow=False),
        ]),
    ])

def build_environment_story() -> list[dict]:
    """Return sparse noncanonical traces, kept clear of player circulation."""

    return [
        model(
            "ShopThresholdHumanTraces",
            [
                # Floor traces are non-colliding and stay outside the direct
                # portal-to-counter line at Z=42.
                part("ScuffedFloorPatch", (1.55, 0.025, 3.1), (-37.65, FLOOR_Y + 0.018, 47.9), material="Concrete", color=CONCRETE_WORN, collide=False, transparency=0.42, rot=(0, -7, 0), cast_shadow=False),
                part("DroppedWorkGlove", (0.75, 0.12, 1.15), (-37.55, FLOOR_Y + 0.09, 49.7), material="Fabric", color=FABRIC, collide=False, rot=(0, 18, 8)),
                part("LooseInventoryTag", (0.48, 0.025, 0.72), (-36.8, FLOOR_Y + 0.03, 49.2), material="SmoothPlastic", color=AGED_WHITE, collide=False, rot=(0, -26, 0), cast_shadow=False),
            ],
        ),
        model(
            "ImprovisedCleaningCorner",
            [
                part("BroomHandle", (0.16, 4.8, 0.16), (-38.18, 56.35, 31.15), material="Wood", color=WOOD, collide=False, rot=(0, 0, -8)),
                part("BroomHead", (0.45, 0.42, 1.65), (-37.85, 54.25, 31.15), material="Fabric", color=[0.24, 0.22, 0.17], collide=False, rot=(0, 0, -8)),
                part("DustPan", (1.0, 0.12, 1.2), (-36.85, FLOOR_Y + 0.08, 31.0), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 12, 0)),
                part("SweptDebrisA", (0.32, 0.24, 0.38), (-35.9, FLOOR_Y + 0.12, 31.1), material="Concrete", color=CONCRETE_WORN, collide=False, rot=(12, 16, 3)),
                part("SweptDebrisB", (0.22, 0.16, 0.28), (-35.55, FLOOR_Y + 0.08, 30.85), material="Concrete", color=CONCRETE_WORN, collide=False, rot=(4, -18, 8)),
            ],
        ),
        model(
            "RepeatedRepairEvidence",
            [
                part("CounterCornerPatch", (0.12, 1.2, 1.05), (-34.45, 56.35, 34.8), material="CorrodedMetal", color=RUST, collide=False),
                part("PatchFastenerUpper", (0.08, 0.18, 0.18), (-34.53, 56.75, 34.5), material="Metal", color=AGED_WHITE, collide=False, shape="Ball"),
                part("PatchFastenerLower", (0.08, 0.18, 0.18), (-34.53, 55.95, 35.1), material="Metal", color=AGED_WHITE, collide=False, shape="Ball"),
            ],
        ),
        _service_exit_evacuation_story(),
    ]
