"""Workshop, upgrade, and storage set dressing for the NewBunker.

The three rooms share an industrial material family but have deliberately
different silhouettes and functions:

* Workshop: a low, layered repair bench backed by an orderly tool wall.
* Upgrade: a tall enclosed service gantry surrounding a machine cradle.
* Storage: perimeter rack bays and locker banks around an L-shaped aisle.

Player clearance reserved by this module:

* Workshop: doorway-to-bench approach, X=-87..-78 and Z=35.25..40.75
  (5.5 studs clear at the narrowest point).
* Upgrade: doorway-to-rig approach, X=-87.5..-78 and Z=53.25..58.75
  (5.5 studs clear).
* Storage: north/south aisle X=-65..-59 and cross aisle Z=66..72 to the
  east door (at least 6 studs clear).

Recommended director-review cameras (position -> target):

* workshop: (-79.5, 59.4, 38.0) -> (-91.0, 58.3, 32.0)
* upgrade: (-79.4, 59.4, 53.2) -> (-91.0, 58.5, 57.0)
* storage: (-62.0, 59.5, 59.5) -> (-62.0, 58.0, 75.0)
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
    WOOD,
    YELLOW,
    crate,
    model,
    part,
    pipe,
    shelf,
)


def _drawer_stack(name: str, pos: tuple[float, float, float]) -> dict:
    """A weighty shop cabinet with readable drawer layering."""

    x, y, z = pos
    children = [
        part("CabinetCarcass", (2.3, 3.0, 2.7), pos, material="Metal", color=GREEN, collide=True),
        part("KickPlate", (2.0, 0.35, 0.16), (x, y - 1.25, z + 1.42), material="CorrodedMetal", color=RUST, collide=False),
    ]
    for index, y_offset in enumerate((-0.82, -0.24, 0.34, 0.92), 1):
        children.extend([
            part(f"DrawerFace{index:02d}", (1.92, 0.46, 0.12), (x, y + y_offset, z + 1.41), material="Metal", color=STEEL_LIGHT, collide=False),
            part(f"DrawerPull{index:02d}", (0.72, 0.10, 0.10), (x, y + y_offset, z + 1.49), material="Metal", color=AGED_WHITE, collide=False),
        ])
    return model(name, children)


def _industrial_workbench() -> dict:
    """Primary repair focal point: cabinets, layered surface, and task tools."""

    return model("IndustrialRepairBench", [
        _drawer_stack("WestDrawerStack", (-93.0, 55.55, 31.9)),
        _drawer_stack("EastDrawerStack", (-85.0, 55.55, 31.9)),
        part("BenchLowerStretcher", (6.0, 0.4, 0.5), (-89.0, 54.75, 32.0), material="Metal", color=STEEL, collide=True),
        part("ThickWorkSurface", (11.0, 0.58, 3.3), (-89.0, 57.25, 31.9), material="DiamondPlate", color=STEEL_LIGHT, collide=True),
        part("ReplaceableWoodInsert", (4.1, 0.12, 2.25), (-89.4, 57.6, 31.9), material="WoodPlanks", color=WOOD, collide=False),
        part("WornFrontEdge", (10.7, 0.24, 0.18), (-89.0, 57.25, 33.62), material="CorrodedMetal", color=RUST, collide=False),
        part("TaskBackboard", (11.0, 4.3, 0.28), (-89.0, 60.0, 30.2), material="Metal", color=STEEL, collide=True),
        part("BackboardInset", (10.2, 3.55, 0.10), (-89.0, 60.0, 30.37), material="Metal", color=CONCRETE_DARK, collide=False),
        model("BackboardRepairHierarchy", [
            part("BackboardTopCap", (10.7, 0.32, 0.14), (-89.0, 61.82, 30.48), material="Metal", color=STEEL_LIGHT, collide=False),
            part("BackboardWestReturn", (0.28, 3.55, 0.14), (-94.15, 60.0, 30.48), material="CorrodedMetal", color=RUST, collide=False),
            part("BackboardEastReturn", (0.28, 3.55, 0.14), (-83.85, 60.0, 30.48), material="CorrodedMetal", color=RUST, collide=False),
            part("ServiceReferenceStripe", (4.2, 0.22, 0.08), (-89.7, 61.28, 30.50), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
            part("WorkOrderClip", (1.05, 0.72, 0.07), (-86.0, 60.72, 30.51), material="Metal", color=AGED_WHITE, collide=False),
        ]),
        part("UpperTaskShelf", (9.6, 0.28, 1.25), (-89.2, 62.0, 30.9), material="DiamondPlate", color=STEEL, collide=False),
        part("ShelfBraceWest", (0.25, 1.3, 1.1), (-93.3, 61.4, 30.8), material="Metal", color=STEEL_LIGHT, collide=False, rot=(18, 0, 0)),
        part("ShelfBraceEast", (0.25, 1.3, 1.1), (-85.1, 61.4, 30.8), material="Metal", color=STEEL_LIGHT, collide=False, rot=(18, 0, 0)),
        model("BenchVice", [
            part("ViceTurntable", (0.30, 1.45, 1.45), (-85.0, 57.82, 32.1), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("FixedJaw", (0.48, 0.85, 1.45), (-84.65, 58.12, 32.1), material="Metal", color=STEEL_LIGHT, collide=False),
            part("MovingJaw", (0.40, 0.72, 1.35), (-84.08, 58.06, 32.1), material="Metal", color=STEEL_LIGHT, collide=False),
            pipe("ViceScrew", (-83.75, 57.62, 32.1), 1.4, "x", 0.18, AGED_WHITE),
        ]),
        model("BenchTaskObjects", [
            part("DisassembledHousing", (2.5, 0.72, 1.45), (-90.0, 58.0, 31.85), material="Metal", color=GREEN, collide=False, rot=(0, 8, 0)),
            pipe("HousingRotor", (-90.0, 58.5, 31.85), 1.5, "x", 0.55, STEEL_LIGHT),
            part("PartsTray", (2.2, 0.18, 1.3), (-87.4, 57.72, 31.9), material="CorrodedMetal", color=STEEL, collide=False),
            part("OilCanBody", (0.58, 0.9, 0.58), (-92.3, 58.0, 31.8), material="Metal", color=RED, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("OilCanSpout", (0.14, 0.14, 1.0), (-92.3, 58.25, 32.5), material="Metal", color=STEEL_LIGHT, collide=False, rot=(18, 0, 0)),
        ]),
        model("BenchTaskClutter", [
            part("WeldRodBundle", (0.44, 0.38, 1.1), (-85.75, 57.84, 31.08), material="Metal", color=AGED_WHITE, collide=False, rot=(0, 0, -8)),
            part("RepairManual", (1.15, 0.10, 0.82), (-88.55, 57.71, 30.98), material="Fabric", color=GREEN, collide=False, rot=(0, -8, 0)),
            part("GrindingDisc", (0.16, 0.92, 0.92), (-93.05, 57.76, 31.08), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("SpentFastenerCup", (0.52, 0.42, 0.52), (-84.92, 57.81, 31.18), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder"),
        ]),
        model("RepairJobLayering", [
            # Service routing stays on the west/backboard side so the prompt-side
            # work approach remains visually and physically open.
            part("BenchServiceFeed", (0.13, 0.13, 3.05), (-94.12, 61.75, 32.40), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
            part("BenchServiceFeedDrop", (0.13, 2.1, 0.13), (-94.12, 60.72, 33.86), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
            part("FeedClampUpper", (0.24, 0.45, 0.75), (-94.12, 61.75, 31.55), material="Metal", color=STEEL_LIGHT, collide=False),
            part("FeedClampLower", (0.24, 0.45, 0.75), (-94.12, 61.75, 33.25), material="Metal", color=STEEL_LIGHT, collide=False),
            part("BenchPowerLeadDrop", (0.12, 3.6, 0.12), (-92.55, 59.75, 30.55), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, 3)),
            part("LeadStrainRelief", (0.45, 0.24, 0.18), (-92.55, 57.88, 30.61), material="Metal", color=STEEL_LIGHT, collide=False),
            # The open middle bay receives a shallow salvage tray rather than
            # floor clutter, giving the repair job a readable foreground layer.
            part("UnderBenchSalvageTray", (4.8, 0.18, 1.45), (-89.2, 55.14, 31.95), material="CorrodedMetal", color=STEEL, collide=False),
            part("RepairedGearBlank", (0.22, 1.12, 1.12), (-89.8, 55.42, 31.90), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("FoldedWeldingApron", (1.35, 0.12, 0.78), (-87.95, 55.33, 31.92), material="Fabric", color=GREEN, collide=False, rot=(0, -5, 0)),
            part("CalibrationGaugeFace", (0.12, 0.75, 0.75), (-92.85, 57.85, 32.72), material="Metal", color=AGED_WHITE, collide=False, shape="Cylinder", rot=(0, 0, 90)),
            part("GaugeNeedle", (0.07, 0.08, 0.42), (-92.85, 57.85, 32.42), material="Metal", color=RUST, collide=False, rot=(0, 0, 18)),
            part("SocketRail", (2.1, 0.18, 0.24), (-90.1, 57.78, 30.75), material="Metal", color=STEEL_LIGHT, collide=False),
        ]),
    ])


def _tool_wall() -> dict:
    """Purposeful silhouettes grouped by repair task, not decorative scatter."""

    tools = [
        part("LongWrench", (0.20, 2.55, 0.14), (-93.2, 60.25, 30.43), material="Metal", color=AGED_WHITE, collide=False, rot=(0, 0, -10)),
        part("PipeWrenchBody", (0.28, 2.05, 0.14), (-92.2, 60.15, 30.43), material="CorrodedMetal", color=RUST, collide=False, rot=(0, 0, 14)),
        part("SquareHeadHammer", (0.85, 0.38, 0.16), (-91.1, 61.0, 30.43), material="Metal", color=STEEL_LIGHT, collide=False),
        part("HammerHandle", (0.22, 1.75, 0.14), (-91.1, 60.05, 30.43), material="WoodPlanks", color=WOOD, collide=False),
        part("CuttingTool", (0.18, 1.8, 0.14), (-89.7, 60.2, 30.43), material="Metal", color=AGED_WHITE, collide=False, rot=(0, 0, -20)),
        part("MeasuringSquareVertical", (0.16, 1.6, 0.14), (-88.4, 60.25, 30.43), material="Metal", color=YELLOW, collide=False),
        part("MeasuringSquareHorizontal", (1.15, 0.16, 0.14), (-87.9, 59.5, 30.43), material="Metal", color=YELLOW, collide=False),
        pipe("CableCoilOuter", (-86.4, 60.15, 30.43), 1.55, "x", 1.35, UTILITY_BLUE),
        part("LowerToolRail", (9.0, 0.16, 0.16), (-89.0, 58.65, 30.43), material="Metal", color=STEEL_LIGHT, collide=False),
        part("FadedToolLabel", (2.5, 0.28, 0.08), (-89.0, 61.6, 30.43), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
    ]
    return model("OrganizedToolWall", tools)


def _north_parts_rack_frame() -> dict:
    """Keep the entry camera rail clear of a head-height shelf and upright."""

    x, y, z = -82.0, 58.0, 43.7
    return model("RackFrame", [
        part("LeftUpright", (0.28, 7.0, 2.0), (x - 3.0, y, z), material="Metal", color=STEEL_LIGHT),
        # The rear rails preserve the wall-mounted rack read while leaving the
        # doorway-side camera rail fully open.
        part("RearMountRailLower", (6.0, 0.18, 0.18), (x, 54.7, z + 0.9), material="Metal", color=STEEL_LIGHT, collide=False),
        part("RearMountRailMiddle", (6.0, 0.18, 0.18), (x, 58.0, z + 0.9), material="Metal", color=STEEL_LIGHT, collide=False),
        part("ShelfDeck01", (6.0, 0.25, 2.0), (x, 54.7, z), material="DiamondPlate", color=STEEL),
        part("ShelfDeck02", (6.0, 0.25, 2.0), (x, 58.0, z), material="DiamondPlate", color=STEEL),
    ])


def _workshop_support_zones() -> list[dict]:
    return [
        model("NorthPartsRack", [
            _north_parts_rack_frame(),
            part("BearingBin", (1.7, 1.0, 1.45), (-83.7, 56.4, 43.6), material="Metal", color=UTILITY_BLUE, collide=False),
            part("FastenerBin", (1.7, 1.0, 1.45), (-81.7, 56.4, 43.6), material="Metal", color=GREEN, collide=False),
            part("FilterBox", (1.8, 1.1, 1.5), (-80.0, 58.7, 43.6), material="SmoothPlastic", color=AGED_WHITE, collide=False),
            part("RackLabel", (2.2, 0.28, 0.08), (-82.0, 58.25, 42.62), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
            model("LogisticsIdentifiers", [
                part("RackRearServiceBand", (5.6, 0.32, 0.08), (-82.0, 61.45, 45.32), material="Metal", color=STEEL_LIGHT, collide=False),
                part("DispatchStripe", (2.65, 0.20, 0.07), (-82.0, 60.92, 45.38), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
                part("ReservePartsTin", (1.25, 0.72, 1.10), (-84.3, 58.60, 43.48), material="CorrodedMetal", color=RUST, collide=False),
                part("TaggedDispatchBin", (1.08, 0.76, 1.08), (-79.82, 56.28, 43.48), material="Metal", color=UTILITY_BLUE, collide=False),
            ]),
            model("SalvageLogisticsLayers", [
                # The recovered case and inventory tag sit on the middle tier;
                # the open upper frame avoids the doorway camera rail.
                part("RecoveredServiceCase", (1.5, 0.95, 1.25), (-82.35, 58.62, 43.56), material="CorrodedMetal", color=GREEN, collide=False),
                part("ServiceCaseLidSeam", (1.32, 0.06, 0.12), (-82.35, 59.10, 42.89), material="Metal", color=STEEL_LIGHT, collide=False),
                part("ServiceCaseLatch", (0.24, 0.26, 0.08), (-82.35, 58.62, 42.86), material="CorrodedMetal", color=RUST, collide=False),
                part("RackReceivingTag", (2.05, 0.24, 0.06), (-82.35, 59.12, 42.63), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
            ]),
        ]),
        model("WestCylinderServiceRack", [
            part("RackBase", (3.2, 0.35, 4.7), (-94.0, 54.2, 42.4), material="Metal", color=STEEL, collide=True),
            pipe("ShieldingGasCylinder", (-94.0, 56.25, 41.35), 4.0, "y", 0.9, GREEN),
            pipe("SpentCylinder", (-94.0, 56.25, 43.25), 4.0, "y", 0.9, RUST),
            part("BackGuard", (0.35, 4.8, 4.6), (-95.0, 56.35, 42.3), material="Metal", color=STEEL, collide=True),
            part("SafetyChain", (0.16, 0.16, 3.5), (-93.45, 57.25, 42.3), material="Metal", color=YELLOW, collide=False),
            model("ExtractionTieIn", [
                pipe("CylinderManifold", (-94.0, 58.38, 42.3), 2.8, "z", 0.24, UTILITY_BLUE),
                pipe("WestServiceRiser", (-95.32, 61.02, 42.3), 5.5, "y", 0.28, RUST),
                part("RiserClampLower", (0.18, 0.42, 1.05), (-95.32, 59.28, 42.3), material="Metal", color=STEEL_LIGHT, collide=False),
                part("RiserClampUpper", (0.18, 0.42, 1.05), (-95.32, 62.85, 42.3), material="Metal", color=STEEL_LIGHT, collide=False),
                part("IsolationTag", (0.08, 0.68, 1.05), (-95.06, 60.55, 42.3), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
            ]),
            model("CylinderHeadConnections", [
                # The two cylinders visibly route through the existing manifold,
                # valve, vent, and overhead riser instead of reading as props.
                pipe("ShieldingGasHose", (-94.20, 58.62, 41.82), 1.15, "z", 0.16, CONCRETE_DARK),
                pipe("SpentGasHose", (-94.20, 58.62, 42.78), 1.15, "z", 0.16, CONCRETE_DARK),
                part("ShieldingHoseClamp", (0.20, 0.32, 0.48), (-94.20, 58.62, 42.05), material="Metal", color=STEEL_LIGHT, collide=False),
                part("SpentHoseClamp", (0.20, 0.32, 0.48), (-94.20, 58.62, 42.55), material="Metal", color=STEEL_LIGHT, collide=False),
                part("ManifoldRegulator", (0.55, 0.62, 0.55), (-94.0, 58.60, 42.30), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
                pipe("ValveFeedStub", (-94.70, 58.88, 42.30), 1.2, "x", 0.18, UTILITY_BLUE),
                part("ValveFeedClamp", (0.18, 0.42, 0.55), (-95.15, 58.88, 42.30), material="Metal", color=STEEL_LIGHT, collide=False),
                part("VentPlenumBacker", (0.10, 2.80, 3.15), (-95.48, 61.55, 44.0), material="CorrodedMetal", color=STEEL, collide=False),
                part("RiserHeaderSaddle", (0.42, 0.20, 1.10), (-95.23, 63.62, 42.30), material="Metal", color=STEEL_LIGHT, collide=False),
                part("SpineDropClamp", (0.18, 0.50, 1.05), (-95.22, 63.72, 38.75), material="Metal", color=STEEL_LIGHT, collide=False),
            ]),
        ]),
        model("WorkshopFloorIdentity", [
            part("AntiFatigueMat", (7.5, 0.09, 2.7), (-89.0, 54.1, 34.9), material="Rubber", color=CONCRETE_DARK, collide=False),
            part("AisleEdgeWest", (0.16, 0.06, 5.3), (-87.35, 54.12, 38.0), material="SmoothPlastic", color=YELLOW, collide=False),
            part("AisleEdgeEast", (0.16, 0.06, 5.3), (-79.6, 54.12, 38.0), material="SmoothPlastic", color=YELLOW, collide=False),
            part("PortableToolCase", (2.3, 1.0, 1.25), (-91.5, 54.5, 44.0), material="Metal", color=RED, collide=False),
            crate("ConsumablesCrate", (-87.8, 55.0, 43.8), (2.5, 2.0, 2.2)),
        ]),
        model("WorkshopOverheadServices", [
            part("TaskCableTray", (11.0, 0.35, 0.8), (-89.0, 64.8, 31.0), material="Metal", color=STEEL_LIGHT, collide=False),
            pipe("CompressedAirHeader", (-89.0, 64.3, 30.7), 10.5, "x", 0.34, UTILITY_BLUE),
            part("RetractableLead", (0.13, 3.7, 0.13), (-86.0, 62.25, 31.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, -7)),
            model("OrderedServiceSpine", [
                part("SpineNorthSouthTray", (0.72, 0.30, 8.4), (-95.15, 64.62, 38.75), material="Metal", color=STEEL_LIGHT, collide=False),
                pipe("SpineBlueConduit", (-94.92, 64.24, 38.75), 8.0, "z", 0.20, UTILITY_BLUE),
                pipe("SpineDarkConduit", (-95.32, 64.18, 38.75), 7.8, "z", 0.16, CONCRETE_DARK),
                part("ExtractionCrossTie", (5.3, 0.25, 0.64), (-92.40, 64.56, 35.0), material="Metal", color=STEEL, collide=False),
                part("SpineWallHangerNorth", (0.18, 2.15, 0.18), (-95.15, 63.55, 41.85), material="Metal", color=STEEL_LIGHT, collide=False),
                part("SpineWallHangerSouth", (0.18, 2.15, 0.18), (-95.15, 63.55, 35.65), material="Metal", color=STEEL_LIGHT, collide=False),
                part("ServiceRouteMarker", (0.16, 0.10, 1.15), (-94.92, 64.47, 36.10), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
                # These shallow lips and high saddles make the extraction arm's
                # tie-in read as a supported service route above head height.
                part("SpineTrayLipWest", (0.16, 0.20, 8.15), (-95.48, 64.82, 38.75), material="Metal", color=STEEL_LIGHT, collide=False),
                part("SpineTrayLipEast", (0.16, 0.20, 8.15), (-94.82, 64.82, 38.75), material="Metal", color=STEEL_LIGHT, collide=False),
                part("SpineSupportSaddleSouth", (0.85, 0.18, 1.15), (-95.14, 64.42, 36.65), material="Metal", color=STEEL, collide=False),
                part("SpineSupportSaddleNorth", (0.85, 0.18, 1.15), (-95.14, 64.42, 40.85), material="Metal", color=STEEL, collide=False),
                part("ExtractionServiceFeed", (2.35, 0.12, 0.12), (-94.18, 64.16, 35.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False),
                part("ExtractionFeedClamp", (0.20, 0.45, 0.58), (-93.60, 64.16, 35.0), material="CorrodedMetal", color=RUST, collide=False),
            ]),
        ]),
    ]


def _workshop_extraction_arm() -> dict:
    """High, rear-stowed fume extraction silhouette above the repair focal point."""

    return model("WorkshopExtractionArm", [
        part("CeilingPivot", (0.55, 1.8, 1.8), (-93.4, 64.1, 35.0), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        # Keep the hood above the rear-left work surface, outside the doorway-to-bench eye line.
        part("UpperArm", (3.4, 0.52, 0.52), (-92.15, 63.45, 34.35), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -16)),
        part("ElbowJoint", (0.64, 1.10, 1.10), (-90.65, 62.88, 33.7), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("LowerArm", (2.55, 0.42, 0.42), (-89.45, 62.30, 33.1), material="Metal", color=STEEL_LIGHT, collide=False, rot=(0, 0, -24)),
        part("FlexibleNeck", (0.42, 1.35, 0.42), (-89.10, 61.52, 32.75), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, 12)),
        part("ExtractionHood", (1.35, 1.0, 1.35), (-89.0, 60.70, 32.75), material="CorrodedMetal", color=STEEL, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("HoodLip", (0.20, 1.65, 1.65), (-88.75, 60.70, 32.75), material="Metal", color=YELLOW, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("ServiceCable", (0.12, 3.0, 0.12), (-92.70, 62.25, 34.35), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, 9)),
    ])


def _workshop_entry_readability() -> dict:
    """Mark the workshop threshold without adding volume to its clear opening."""

    return model("WorkshopEntryReadability", [
        part("MaintenanceDesignationBacker", (0.10, 2.65, 3.10), (-78.54, 60.08, 43.0), material="Metal", color=CONCRETE_DARK, collide=False),
        part("MaintenanceDesignationBar", (0.07, 0.30, 2.45), (-78.60, 60.82, 43.0), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
        part("MaintenanceDesignationLowerRail", (0.07, 0.12, 2.45), (-78.60, 59.14, 43.0), material="CorrodedMetal", color=RUST, collide=False),
        part("ThresholdSupportPlate", (1.10, 0.05, 5.80), (-80.58, 54.13, 38.0), material="DiamondPlate", color=STEEL, collide=False),
        part("ThresholdRouteLine", (0.16, 0.06, 5.20), (-81.18, 54.16, 38.0), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
        # The zone blades sit beyond the portal edges; the low, translucent
        # aisle inlay is visual-only and keeps the doorway volume unchanged.
        part("BenchBayGuide", (0.07, 0.24, 2.05), (-78.60, 60.02, 32.35), material="SmoothPlastic", color=YELLOW, collide=False, cast_shadow=False),
        part("LogisticsBayGuide", (0.07, 0.24, 1.35), (-78.60, 60.02, 44.05), material="SmoothPlastic", color=UTILITY_BLUE, collide=False, cast_shadow=False),
        part("ClearAisleInlay", (0.82, 0.025, 3.45), (-82.50, 54.145, 38.0), material="SmoothPlastic", color=STEEL_LIGHT, collide=False, transparency=0.30, cast_shadow=False),
    ])


def build_workshop() -> list[dict]:
    """Return workshop-owned models while keeping the central work aisle open."""

    return [
        _industrial_workbench(),
        _tool_wall(),
        *_workshop_support_zones(),
        _workshop_extraction_arm(),
        _workshop_entry_readability(),
    ]


def _upgrade_service_rig() -> dict:
    """Grounded service cradle framed around, rather than across, its sightline."""

    return model("EnclosedUpgradeServiceRig", [
        part("MachinePlinth", (7.2, 0.62, 7.4), (-91.2, 54.32, 57.0), material="DiamondPlate", color=STEEL),
        part("PlinthWarningWest", (0.38, 0.12, 7.1), (-94.6, 54.68, 57.0), material="SmoothPlastic", color=YELLOW, collide=False),
        part("PlinthWarningEast", (0.38, 0.12, 7.1), (-87.8, 54.68, 57.0), material="SmoothPlastic", color=YELLOW, collide=False),
        model("OpenServiceFrame", [
            part("RearNorthPost", (0.62, 8.4, 0.62), (-94.0, 58.9, 54.25), material="Metal", color=STEEL_LIGHT),
            part("RearSouthPost", (0.62, 8.4, 0.62), (-94.0, 58.9, 59.75), material="Metal", color=STEEL_LIGHT),
            part("FrontNorthPost", (0.62, 8.4, 0.62), (-88.4, 58.9, 54.25), material="Metal", color=STEEL_LIGHT),
            part("FrontSouthPost", (0.62, 8.4, 0.62), (-88.4, 58.9, 59.75), material="Metal", color=STEEL_LIGHT),
            part("NorthTopRail", (6.2, 0.62, 0.72), (-91.2, 62.8, 54.25), material="Metal", color=STEEL_LIGHT),
            part("SouthTopRail", (6.2, 0.62, 0.72), (-91.2, 62.8, 59.75), material="Metal", color=STEEL_LIGHT),
            part("RearCrossRail", (0.72, 0.62, 6.1), (-94.0, 62.8, 57.0), material="CorrodedMetal", color=RUST),
            part("NorthLowerBrace", (5.5, 0.34, 0.34), (-91.2, 60.4, 54.25), material="Metal", color=STEEL, collide=False, rot=(0, 0, 10)),
            part("SouthLowerBrace", (5.5, 0.34, 0.34), (-91.2, 60.4, 59.75), material="Metal", color=STEEL, collide=False, rot=(0, 0, -10)),
        ]),
        model("MachineCradle", [
            part("BedSupportNorthWest", (0.5, 2.2, 0.5), (-93.1, 55.75, 55.7), material="Metal", color=STEEL),
            part("BedSupportNorthEast", (0.5, 2.2, 0.5), (-89.0, 55.75, 55.7), material="Metal", color=STEEL),
            part("BedSupportSouthWest", (0.5, 2.2, 0.5), (-93.1, 55.75, 58.3), material="Metal", color=STEEL),
            part("BedSupportSouthEast", (0.5, 2.2, 0.5), (-89.0, 55.75, 58.3), material="Metal", color=STEEL),
            part("ServiceBed", (5.0, 0.48, 3.5), (-91.05, 56.9, 57.0), material="Metal", color=STEEL_LIGHT),
            part("NorthCradleRail", (4.5, 0.48, 0.42), (-91.0, 57.38, 56.05), material="CorrodedMetal", color=RUST, collide=False),
            part("SouthCradleRail", (4.5, 0.48, 0.42), (-91.0, 57.38, 57.95), material="CorrodedMetal", color=RUST, collide=False),
            pipe("ServiceRotor", (-90.7, 58.05, 57.0), 3.2, "x", 1.35, GREEN),
            part("RotorCollarWest", (0.35, 1.65, 1.65), (-92.2, 58.05, 57.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("RotorCollarEast", (0.35, 1.65, 1.65), (-89.2, 58.05, 57.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("NorthClamp", (0.8, 0.85, 0.5), (-90.7, 58.15, 55.75), material="Metal", color=YELLOW, collide=False),
            part("SouthClamp", (0.8, 0.85, 0.5), (-90.7, 58.15, 58.25), material="Metal", color=YELLOW, collide=False),
            part("ServiceStep", (0.8, 0.28, 3.0), (-87.95, 54.75, 57.0), material="DiamondPlate", color=STEEL_LIGHT),
        ]),
        model("WestSideActuator", [
            part("ActuatorFoot", (1.7, 0.42, 2.5), (-93.3, 54.82, 57.0), material="DiamondPlate", color=STEEL),
            part("ActuatorMast", (1.25, 5.7, 2.0), (-93.3, 57.8, 57.0), material="Metal", color=GREEN),
            part("MastAccessPanel", (0.10, 3.6, 1.35), (-92.62, 57.7, 57.0), material="Metal", color=CONCRETE_DARK, collide=False),
            part("PressureGauge", (0.10, 0.72, 0.72), (-92.54, 58.7, 56.5), material="SmoothPlastic", color=AGED_WHITE, collide=False, shape="Cylinder"),
            part("ActuatorHousing", (2.2, 1.8, 1.75), (-92.25, 60.0, 57.0), material="CorrodedMetal", color=RUST),
            pipe("HorizontalRam", (-90.35, 60.0, 57.0), 3.0, "x", 0.62, STEEL_LIGHT),
            part("PressHead", (0.65, 1.45, 1.45), (-88.85, 60.0, 57.0), material="Metal", color=YELLOW, collide=False),
            part("ReturnHose", (0.18, 4.0, 0.18), (-93.65, 58.8, 58.0), material="SmoothPlastic", color=UTILITY_BLUE, collide=False, rot=(0, 0, 8)),
        ]),
        part("MachineIdentityPlate", (0.10, 0.5, 2.3), (-87.73, 55.8, 57.0), material="SmoothPlastic", color=UTILITY_BLUE, collide=False, cast_shadow=False),
    ])


def _upgrade_support_zones() -> list[dict]:
    return [
        model("DiagnosticOperatorStation", [
            part("ConsolePlinth", (3.4, 0.55, 3.0), (-93.6, 54.28, 50.2), material="Concrete", color=CONCRETE_WORN),
            part("ConsoleHousing", (3.2, 3.2, 1.45), (-93.6, 56.0, 50.25), material="Metal", color=STEEL),
            part("SlopedControlFace", (2.7, 1.55, 0.14), (-93.6, 57.45, 51.0), material="Metal", color=GREEN, collide=False, rot=(18, 0, 0)),
            part("DiagnosticScreen", (1.45, 0.72, 0.08), (-94.15, 57.65, 51.13), material="Neon", color=UTILITY_BLUE, collide=False, cast_shadow=False),
            part("StatusLamp", (0.28, 0.28, 0.08), (-92.9, 57.55, 51.13), material="Neon", color=RED, collide=False, cast_shadow=False),
            part("ControlLever", (0.18, 0.95, 0.18), (-92.65, 58.2, 50.9), material="Metal", color=YELLOW, collide=False, rot=(0, 0, -20)),
        ]),
        model("NorthCalibrationRack", [
            shelf("RackFrame", (-82.3, 58.0, 64.0), 5.2, 7.0, 1.8),
            part("CalibrationCaseA", (1.8, 0.9, 1.3), (-83.5, 56.4, 64.0), material="Metal", color=UTILITY_BLUE, collide=False),
            part("CalibrationCaseB", (1.8, 0.9, 1.3), (-81.2, 59.9, 64.0), material="Metal", color=GREEN, collide=False),
            part("CoiledLead", (0.25, 1.4, 1.4), (-83.6, 59.7, 63.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        ]),
        model("UpgradeFloorLanguage", [
            part("ApproachRailNorth", (8.6, 0.08, 0.18), (-82.8, 54.12, 53.25), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
            part("ApproachRailSouth", (8.6, 0.08, 0.18), (-82.8, 54.12, 58.75), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
            part("MaintenanceKneelingMat", (2.5, 0.09, 4.0), (-87.0, 54.1, 57.0), material="Rubber", color=CONCRETE_DARK, collide=False),
            crate("ActuatorSpares", (-81.0, 55.0, 50.2), (2.5, 2.0, 2.1)),
        ]),
        model("UpgradeWallInfrastructure", [
            part("PowerDisconnect", (1.0, 3.1, 2.1), (-95.0, 59.0, 62.7), material="Metal", color=GREEN),
            part("DisconnectFace", (0.10, 2.3, 1.55), (-94.44, 59.0, 62.7), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
            part("EmergencyHandle", (0.18, 1.35, 0.18), (-94.32, 59.0, 62.7), material="Metal", color=RED, collide=False, rot=(0, 0, 20)),
            pipe("OverheadHydraulicFeed", (-90.0, 65.6, 64.7), 9.0, "x", 0.38, UTILITY_BLUE),
            part("DroppedInspectionCover", (2.0, 0.12, 1.4), (-84.8, 54.14, 63.6), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, 17, 0)),
        ]),
    ]


def _upgrade_hydraulic_accumulator_bank() -> dict:
    """Add a rounded pressure-bank silhouette without entering the approach lane."""
    return model("HydraulicAccumulatorBank", [
        part("WallRailUpper", (0.22, 0.28, 6.2), (-95.28, 61.25, 56.8), material="Metal", color=STEEL_LIGHT, collide=False),
        part("WallRailLower", (0.22, 0.28, 6.2), (-95.28, 56.05, 56.8), material="CorrodedMetal", color=RUST, collide=False),
        pipe("AccumulatorNorth", (-94.95, 58.65, 55.15), 4.8, "y", 0.82, GREEN),
        pipe("AccumulatorCenter", (-94.95, 58.65, 57.0), 4.8, "y", 0.82, STEEL_LIGHT),
        pipe("AccumulatorSouth", (-94.95, 58.65, 58.85), 4.8, "y", 0.82, GREEN),
        part("NorthGauge", (0.18, 0.78, 0.78), (-94.52, 60.35, 55.15), material="SmoothPlastic", color=AGED_WHITE, collide=False, shape="Cylinder"),
        part("SouthGauge", (0.18, 0.78, 0.78), (-94.52, 60.35, 58.85), material="SmoothPlastic", color=AGED_WHITE, collide=False, shape="Cylinder"),
        pipe("PressureManifold", (-94.62, 61.05, 57.0), 4.3, "z", 0.22, UTILITY_BLUE),
        part("ServiceHoseDrop", (0.16, 3.8, 0.16), (-94.45, 58.5, 60.15), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, 11)),
        part("FadedPressureTag", (0.08, 0.42, 1.45), (-94.42, 61.0, 57.0), material="SmoothPlastic", color=YELLOW, collide=False, rot=(0, 0, -3), cast_shadow=False),
    ])


def build_upgrade_area() -> list[dict]:
    """Return an intentional service-machine composition and support spaces."""

    return [_upgrade_service_rig(), *_upgrade_support_zones(), _upgrade_hydraulic_accumulator_bank()]


def _storage_rack_z(name: str, x: float, z: float, length: float) -> dict:
    """Shelf bay running along Z for the storage room's west perimeter."""

    height, depth = 7.0, 2.0
    children = [
        part("NearUpright", (depth, height, 0.28), (x, 58.0, z - length / 2), material="Metal", color=STEEL_LIGHT),
        part("FarUpright", (depth, height, 0.28), (x, 58.0, z + length / 2), material="Metal", color=STEEL_LIGHT),
    ]
    for index, y in enumerate((54.7, 58.0, 61.3), 1):
        children.append(part(f"ShelfDeck{index:02d}", (depth, 0.25, length), (x, y, z), material="DiamondPlate", color=STEEL))
    return model(name, children)


def _storage_racks_and_bins() -> list[dict]:
    return [
        model("WestMedicalRackBay", [
            _storage_rack_z("RackFrame", -68.2, 63.0, 6.2),
            part("BandageBin", (1.45, 1.05, 1.8), (-68.1, 56.3, 61.8), material="SmoothPlastic", color=AGED_WHITE, collide=False),
            part("MedicalTin", (1.4, 0.85, 1.6), (-68.1, 59.7, 64.0), material="Metal", color=GREEN, collide=False),
            part("MedicalMark", (0.08, 0.34, 0.75), (-67.31, 59.7, 64.0), material="SmoothPlastic", color=RED, collide=False, cast_shadow=False),
            part("RackLabel", (0.08, 0.28, 1.8), (-67.2, 58.1, 63.0), material="SmoothPlastic", color=AGED_WHITE, collide=False),
        ]),
        model("WestMechanicalRackBay", [
            _storage_rack_z("RackFrame", -68.2, 74.2, 5.6),
            part("FilterBin", (1.45, 1.0, 1.8), (-68.1, 56.3, 73.0), material="Metal", color=UTILITY_BLUE, collide=False),
            part("PartsBin", (1.45, 1.0, 1.8), (-68.1, 59.7, 75.0), material="Metal", color=STEEL_LIGHT, collide=False),
            pipe("StoredPipeBundle", (-68.0, 61.7, 74.2), 4.0, "z", 0.32, RUST),
        ]),
        model("NorthLongRackBay", [
            shelf("RackFrame", (-62.0, 58.0, 76.5), 6.0, 7.0, 2.0),
            part("CanvasBundleA", (2.1, 0.75, 1.45), (-63.6, 56.2, 76.4), material="Fabric", color=GREEN, collide=False),
            part("CanvasBundleB", (2.1, 0.65, 1.45), (-60.8, 59.6, 76.4), material="Fabric", color=[0.34, 0.35, 0.31], collide=False),
            part("LongRackLabel", (2.3, 0.28, 0.08), (-62.0, 58.15, 75.42), material="SmoothPlastic", color=YELLOW, collide=False),
        ]),
        model("EastSouthSupplyRack", [
            _storage_rack_z("RackFrame", -55.8, 61.8, 4.6),
            part("WaterCanister", (1.35, 2.0, 1.35), (-55.8, 55.7, 61.0), material="Metal", color=UTILITY_BLUE, collide=False),
            part("DryGoodsBox", (1.45, 1.0, 1.7), (-55.8, 59.7, 62.7), material="WoodPlanks", color=WOOD, collide=False),
        ]),
    ]


def _storage_lockers_and_crates() -> list[dict]:
    locker_children = [part("LockerCarcass", (4.2, 6.8, 1.7), (-56.7, 57.4, 75.9), material="CorrodedMetal", color=GREEN)]
    for index, x in enumerate((-57.95, -56.7, -55.45), 1):
        locker_children.extend([
            part(f"LockerDoor{index:02d}", (1.38, 5.9, 0.12), (x, 57.5, 74.99), material="Metal", color=STEEL_LIGHT, collide=False),
            part(f"LockerVent{index:02d}", (0.72, 0.12, 0.07), (x, 59.8, 74.90), material="SmoothPlastic", color=CONCRETE_DARK, collide=False),
            part(f"LockerHandle{index:02d}", (0.12, 0.7, 0.08), (x + 0.42, 57.4, 74.88), material="Metal", color=AGED_WHITE, collide=False),
        ])
    return [
        model("NorthEastLockerBank", locker_children),
        model("SupplyCratePockets", [
            crate("MedicalSupplyCrate", (-67.2, 55.1, 67.8), (2.3, 2.1, 2.3)),
            crate("MechanicalSupplyCrate", (-56.2, 55.15, 65.0), (2.4, 2.2, 1.6)),
            crate("LowerReserveCrate", (-67.0, 55.95, 76.0), (2.3, 2.2, 2.0)),
            crate("UpperReserveCrate", (-67.0, 58.95, 76.0), (2.0, 1.6, 1.7)),
        ]),
    ]


def _storage_navigation_language() -> dict:
    return model("StorageNavigationAndWear", [
        part("WestAisleLine", (0.16, 0.06, 15.0), (-65.0, 54.12, 68.5), material="SmoothPlastic", color=YELLOW, collide=False),
        part("EastAisleLine", (0.16, 0.06, 15.0), (-59.0, 54.12, 68.5), material="SmoothPlastic", color=YELLOW, collide=False),
        part("CrossAisleNorthLine", (5.0, 0.06, 0.16), (-56.5, 54.12, 72.0), material="SmoothPlastic", color=YELLOW, collide=False),
        part("CrossAisleSouthLine", (5.0, 0.06, 0.16), (-56.5, 54.12, 66.0), material="SmoothPlastic", color=YELLOW, collide=False),
        part("WornInventoryBoard", (0.16, 3.4, 3.8), (-69.45, 59.2, 69.0), material="Metal", color=CONCRETE_DARK, collide=False),
        part("InventorySheet", (0.08, 2.5, 2.8), (-69.34, 59.3, 69.0), material="SmoothPlastic", color=AGED_WHITE, collide=False, transparency=0.12, cast_shadow=False),
        part("DroppedLid", (1.5, 0.10, 1.0), (-57.0, 54.12, 72.8), material="CorrodedMetal", color=STEEL_LIGHT, collide=False, rot=(0, -16, 0)),
    ])


def _storage_emergency_supply_nest() -> dict:
    """Use rounded emergency stores to break the rack-and-crate silhouette."""
    return model("EmergencySupplyNest", [
        part("LowContainmentTray", (4.8, 0.22, 2.5), (-58.8, 54.18, 75.4), material="DiamondPlate", color=STEEL, collide=False),
        pipe("WaterDrumA", (-60.15, 55.45, 75.4), 2.35, "y", 1.35, UTILITY_BLUE),
        pipe("WaterDrumB", (-58.55, 55.45, 75.4), 2.35, "y", 1.35, UTILITY_BLUE),
        pipe("ReserveCylinder", (-57.0, 55.65, 75.45), 2.75, "y", 0.72, GREEN),
        part("DrumBandAUpper", (0.16, 1.48, 1.48), (-60.15, 56.05, 75.4), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("DrumBandALower", (0.16, 1.48, 1.48), (-60.15, 54.85, 75.4), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("DrumBandBUpper", (0.16, 1.48, 1.48), (-58.55, 56.05, 75.4), material="Metal", color=STEEL_LIGHT, collide=False, shape="Cylinder", rot=(0, 0, 90)),
        part("RetainingStrap", (4.0, 0.16, 0.16), (-58.8, 55.6, 74.65), material="Fabric", color=[0.20, 0.16, 0.10], collide=False, rot=(0, 0, -4)),
        part("RolledTarp", (0.95, 3.0, 0.95), (-61.1, 55.0, 75.25), material="Fabric", color=GREEN, collide=False, shape="Cylinder", rot=(0, 0, 82)),
        part("LeaningInventorySlate", (1.7, 2.4, 0.12), (-56.65, 55.25, 74.9), material="Metal", color=CONCRETE_DARK, collide=False, rot=(0, 0, -11)),
    ])


def build_storage() -> list[dict]:
    """Return dense perimeter storage while retaining the two-door aisle."""

    return [*_storage_racks_and_bins(), *_storage_lockers_and_crates(), _storage_navigation_language(), _storage_emergency_supply_nest()]
