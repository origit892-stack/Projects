"""Corridor rhythm and non-blocking utility infrastructure."""

from __future__ import annotations

from .kit import (
    CONCRETE_DARK,
    GREEN,
    RUST,
    STEEL,
    STEEL_LIGHT,
    UTILITY_BLUE,
    YELLOW,
    model,
    part,
    pipe,
    structural_rib,
)
from .site import FLOOR_Y, ROOM_BOUNDS


def _destination_frame(
    name: str,
    x: float,
    z: float,
    width: float,
    accent: list[float],
    clear_height: float = 8.2,
) -> dict:
    """Add a high, non-colliding visual frame without duplicating portals."""

    return model(name, [
        part("WestBlade", (0.14, clear_height, 0.32), (x - width / 2, FLOOR_Y + clear_height / 2, z), material="Metal", color=accent, collide=False),
        part("EastBlade", (0.14, clear_height, 0.32), (x + width / 2, FLOOR_Y + clear_height / 2, z), material="Metal", color=accent, collide=False),
        part("HeaderBlade", (width, 0.18, 0.32), (x, FLOOR_Y + clear_height, z), material="Metal", color=accent, collide=False),
    ])


def _portal_release_rib(name: str, x0: float, x1: float, z: float, height: float) -> dict:
    """Keep overhead rhythm while leaving the shared east portal unobstructed."""

    rib_model = structural_rib(name, x0, x1, z, height, accent=STEEL)
    rib_model["Children"] = [
        child
        for child in rib_model["Children"]
        if child["Name"] not in {"EastUpright", "LowerGuardEast"}
    ]
    return rib_model


def _west_corridor_beats() -> list[dict]:
    """Create three silhouette beats without entering the traversal lane."""

    return [
        model("SouthArrivalBay", [
            # A shallow east-wall skin breaks the blank concrete run at the
            # common/workshop junction.  Every layer is visual-only.
            part("InsetWallPanel", (0.08, 5.8, 6.2), (-70.46, 58.0, 49.5), material="Metal", color=CONCRETE_DARK, collide=False),
            part("PanelFrameSouth", (0.16, 6.4, 0.28), (-70.38, 58.2, 46.5), material="Metal", color=STEEL_LIGHT, collide=False),
            part("PanelFrameNorth", (0.16, 6.4, 0.28), (-70.38, 58.2, 52.5), material="Metal", color=STEEL_LIGHT, collide=False),
            part("PanelServiceBand", (0.12, 0.48, 5.2), (-70.38, 60.0, 49.5), material="CorrodedMetal", color=RUST, collide=False),
            part("FadedBayPlate", (0.10, 1.4, 2.2), (-70.31, 58.2, 49.5), material="Metal", color=STEEL, collide=False),
            part("CeilingDrop", (6.5, 0.32, 3.8), (-74.0, 64.55, 49.5), material="Metal", color=STEEL, collide=False),
            part("CeilingDropRib", (6.8, 0.38, 0.35), (-74.0, 64.30, 51.1), material="Metal", color=STEEL_LIGHT, collide=False),
        ]),
        model("MidMaintenanceBay", [
            # Dark backplate sits in the wall plane; the surround projects
            # only 0.18 studs and is non-colliding, creating perceived depth.
            part("DeepRecessBack", (0.06, 6.0, 6.4), (-77.54, 58.4, 61.5), material="Metal", color=[0.08, 0.10, 0.11], collide=False),
            part("RecessSouthJamb", (0.34, 6.5, 0.34), (-77.34, 58.5, 58.4), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
            part("RecessNorthJamb", (0.34, 6.5, 0.34), (-77.34, 58.5, 64.6), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
            part("RecessHeader", (0.34, 0.42, 6.6), (-77.34, 61.7, 61.5), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
            part("ValvePanel", (0.22, 3.5, 2.5), (-77.20, 58.3, 61.5), material="Metal", color=GREEN, collide=False),
            part("ValvePanelInset", (0.10, 2.8, 1.9), (-77.07, 58.35, 61.5), material="Metal", color=CONCRETE_DARK, collide=False),
            part("IsolationWheel", (0.16, 1.35, 1.35), (-76.95, 58.5, 61.5), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder"),
            part("MaintenanceCanopy", (6.2, 0.42, 4.8), (-73.9, 64.45, 61.5), material="DiamondPlate", color=STEEL, collide=False),
        ]),
        model("NorthResidentialApproach", [
            part("EastWallRepairPlate", (0.08, 6.2, 7.2), (-70.46, 58.2, 74.8), material="CorrodedMetal", color=STEEL, collide=False),
            part("RepairBraceA", (0.10, 6.7, 0.30), (-70.38, 58.3, 71.5), material="Metal", color=STEEL_LIGHT, collide=False, rot=(8, 0, 0)),
            part("RepairBraceB", (0.10, 6.7, 0.30), (-70.38, 58.3, 78.1), material="Metal", color=STEEL_LIGHT, collide=False, rot=(-8, 0, 0)),
            part("ResidentialUtilityStrip", (0.10, 0.42, 5.8), (-70.31, 59.9, 74.8), material="Metal", color=GREEN, collide=False),
            part("OverheadTransitionPanel", (6.0, 0.30, 5.0), (-74.0, 64.62, 75.0), material="Metal", color=CONCRETE_DARK, collide=False),
            part("LooseCableDrop", (0.12, 2.8, 0.12), (-70.70, 62.5, 72.2), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, -7)),
        ]),
    ]


def _service_approach_beats() -> list[dict]:
    """Frame the power-to-service transition and remove the blank-tube read."""

    return [
        model("ServiceSouthJunction", [
            part("WestInsetPanel", (0.08, 5.6, 4.4), (-41.96, 58.1, 84.6), material="Metal", color=CONCRETE_DARK, collide=False),
            part("WestPanelEdgeA", (0.16, 6.0, 0.26), (-41.86, 58.2, 82.6), material="Metal", color=STEEL_LIGHT, collide=False),
            part("WestPanelEdgeB", (0.16, 6.0, 0.26), (-41.86, 58.2, 86.6), material="Metal", color=STEEL_LIGHT, collide=False),
            part("PowerRoutePlate", (0.10, 1.25, 2.1), (-41.77, 59.0, 84.6), material="Metal", color=UTILITY_BLUE, collide=False),
            part("JunctionCeilingDrop", (5.8, 0.34, 3.4), (-39.0, 63.62, 84.5), material="Metal", color=STEEL, collide=False),
        ]),
        model("ServiceInspectionBay", [
            part("EastRecessBack", (0.06, 5.5, 4.6), (-36.04, 58.0, 89.0), material="Metal", color=[0.08, 0.10, 0.11], collide=False),
            part("EastRecessSouthJamb", (0.28, 6.0, 0.28), (-36.18, 58.2, 86.85), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
            part("EastRecessNorthJamb", (0.28, 6.0, 0.28), (-36.18, 58.2, 91.15), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
            part("InspectionHousing", (0.18, 3.2, 2.8), (-36.27, 58.1, 89.0), material="Metal", color=GREEN, collide=False),
            part("InspectionFace", (0.08, 2.5, 2.1), (-36.38, 58.2, 89.0), material="Metal", color=CONCRETE_DARK, collide=False),
            part("StatusBand", (0.06, 0.35, 1.5), (-36.43, 59.0, 89.0), material="Neon", color=UTILITY_BLUE, collide=False, cast_shadow=False),
        ]),
        model("ServiceFarmThreshold", [
            part("WestDestinationBlade", (0.16, 7.8, 0.36), (-41.55, 57.9, 93.25), material="Metal", color=STEEL_LIGHT, collide=False),
            part("EastDestinationBlade", (0.16, 7.8, 0.36), (-36.45, 57.9, 93.25), material="Metal", color=STEEL_LIGHT, collide=False),
            part("HighDestinationHeader", (5.3, 0.22, 0.36), (-39.0, 61.8, 93.25), material="Metal", color=STEEL_LIGHT, collide=False),
            part("FarmRouteInset", (3.4, 0.06, 0.7), (-39.0, FLOOR_Y + 0.04, 93.0), material="SmoothPlastic", color=GREEN, collide=False, transparency=0.15),
        ]),
    ]


def build_corridors() -> list[dict]:
    """Return varied corridor bays with a minimum 5.5-stud practical lane."""

    west_x0, west_x1, _, _ = ROOM_BOUNDS["WestResidentialCorridorShell"]
    east_x0, east_x1, _, _ = ROOM_BOUNDS["EastUtilityCorridorShell"]
    service_x0, service_x1, _, _ = ROOM_BOUNDS["ServiceConnectorShell"]
    corridors: list[dict] = []

    # Irregular spacing avoids the repeated-box-tunnel read while retaining a
    # recognizable structural cadence.  Slim posts keep routes comfortably open.
    for index, (z, height, accent) in enumerate((
        (33, 10.8, RUST), (43, 11.4, STEEL), (51, 10.9, RUST),
        (61, 11.5, STEEL), (69, 10.8, RUST), (81, 11.3, STEEL),
    ), 1):
        name = f"WestCorridorRib{index:02d}"
        if index == 2:
            # Z=43 lies inside the common-hub portal (Z=38..46).  Retain the
            # west support and overhead member, but remove the blocking east post.
            corridors.append(_portal_release_rib(name, west_x0, west_x1, z, height))
        else:
            corridors.append(structural_rib(name, west_x0, west_x1, z, height, accent=accent))
    for index, (z, height) in enumerate(((36, 10.7), (47, 11.4), (53, 10.8), (60, 11.2)), 1):
        corridors.append(structural_rib(f"EastCorridorRib{index:02d}", east_x0, east_x1, z, height, accent=UTILITY_BLUE))

    corridors.extend([
        structural_rib("SouthConnectorRib", -65, -55, 25, 10.5, accent=YELLOW),
        structural_rib("SouthServiceRib", service_x0, service_x1, 86, 9.4, accent=UTILITY_BLUE),
        structural_rib("NorthServiceRib", service_x0, service_x1, 91, 9.8, accent=RUST),
        model("WestCorridorPipeRun", [
            # Short, muted service branches replace the two colored 46-stud
            # vanishing lines that previously dominated the player view.
            pipe("SouthWaterBranch", (-77.05, 64.0, 42.5), 11.0, "z", 0.26, STEEL_LIGHT),
            pipe("NorthReturnBranch", (-77.10, 63.85, 72.5), 13.0, "z", 0.22, STEEL),
            pipe("MaintenanceCrossFeed", (-74.3, 64.05, 61.5), 5.4, "x", 0.24, [0.18, 0.25, 0.25]),
            pipe("RecessVerticalDrop", (-77.10, 60.9, 61.5), 5.8, "y", 0.26, STEEL_LIGHT),
            part("SouthExpansionJoint", (0.42, 0.42, 0.55), (-77.05, 64.0, 47.8), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 90, 0)),
            part("NorthExpansionJoint", (0.36, 0.36, 0.5), (-77.10, 63.85, 66.2), material="CorrodedMetal", color=RUST, collide=False, shape="Cylinder", rot=(0, 90, 0)),
        ]),
        model("EastCorridorConduitRun", [
            part("MainTray", (0.35, 0.48, 27), (-45.65, 62.7, 47), material="Metal", color=STEEL_LIGHT, collide=False),
            part("UtilityCableBlue", (0.13, 0.13, 25), (-45.40, 62.7, 47), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
            part("UtilityCableRed", (0.12, 0.12, 24), (-45.22, 62.5, 47), material="SmoothPlastic", color=RUST, collide=False),
        ]),
        model("ServiceWallRecess", [
            # This housing remains behind the east interior wall plane (X=-36)
            # so the seven-stud connector retains a six-stud clear lane.
            part("RecessBack", (0.22, 4.2, 3.2), (-35.88, 58.1, 88), material="Metal", color=CONCRETE_DARK),
            part("RecessLintel", (0.48, 0.45, 3.6), (-36.05, 60.3, 88), material="Metal", color=STEEL_LIGHT, collide=False),
        ]),
        model("ServiceElectricalContinuity", [
            # Continue the utility-wing electrical language through the service
            # connector without projecting into its verified six-stud lane.
            part("WestServiceTray", (0.34, 0.42, 10.2), (-42.30, 62.85, 88.0), material="Metal", color=STEEL_LIGHT, collide=False),
            part("ServiceCableDark", (0.11, 0.11, 9.5), (-42.08, 62.78, 88.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False),
            part("ServiceCableBlue", (0.11, 0.11, 9.2), (-41.91, 62.78, 88.1), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
            part("SouthJunctionBox", (0.20, 1.25, 1.45), (-42.30, 61.45, 83.5), material="Metal", color=STEEL, collide=False),
            part("SouthJunctionCover", (0.08, 0.90, 1.08), (-42.18, 61.45, 83.5), material="CorrodedMetal", color=RUST, collide=False),
            part("NorthServiceDrop", (0.14, 2.5, 0.14), (-42.08, 61.55, 92.0), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, rot=(0, 0, -4)),
            part("FarmThresholdFeed", (5.0, 0.14, 0.14), (-39.55, 62.78, 92.35), material="SmoothPlastic", color=UTILITY_BLUE, collide=False),
            part("OldCableClamp", (0.12, 0.42, 0.55), (-42.16, 62.78, 89.4), material="CorrodedMetal", color=RUST, collide=False),
        ]),
        _destination_frame("WorkshopDestinationFrame", -74, 38, 5.6, RUST),
        _destination_frame("UpgradeDestinationFrame", -74, 56, 5.6, UTILITY_BLUE),
        _destination_frame("BedroomDestinationFrame", -74, 76, 5.6, GREEN),
        _destination_frame("UtilityDestinationFrame", -42.5, 60.8, 5.6, UTILITY_BLUE),
    ])
    corridors.extend(_west_corridor_beats())
    corridors.extend(_service_approach_beats())
    return corridors
