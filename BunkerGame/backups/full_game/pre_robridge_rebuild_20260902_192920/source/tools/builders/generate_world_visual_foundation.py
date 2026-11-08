#!/usr/bin/env python3
"""Task 1: additive overworld visual foundation only.

Presentation geometry deliberately reserves distinct spatial opportunities for
future resource gathering, scavenging, combat sightlines and exploration.  It
contains no gameplay IDs, prompts, scripts, remotes or reward state.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "src/Workspace/WorldVisualFoundation.model.json"
GROUND_Y = 53.4

EARTH = [0.235, 0.225, 0.19]
EARTH_DARK = [0.17, 0.17, 0.15]
ROCK = [0.29, 0.30, 0.29]
ROCK_DARK = [0.20, 0.215, 0.21]
ROCK_MOSS = [0.255, 0.285, 0.235]
DEAD_GRASS = [0.285, 0.31, 0.22]
WOOD = [0.255, 0.19, 0.125]
RUST = [0.29, 0.16, 0.09]


def model(name, children):
    return {"Name": name, "ClassName": "Model", "Children": children}


def part(name, size, pos, material, color, *, collide=False, rot=None, transparency=0.0):
    props = {
        "Size": list(size), "Anchored": True,
        "CanCollide": collide, "CanTouch": False, "CanQuery": False,
        "Material": material, "Color": color,
        "Transparency": transparency, "CastShadow": True,
    }
    if rot is None:
        props["Position"] = list(pos)
    else:
        # Only Y rotations are required by this packet.
        import math
        a = math.radians(rot)
        c, s = math.cos(a), math.sin(a)
        props["CFrame"] = [pos[0], pos[1], pos[2], c, 0, s, 0, 1, 0, -s, 0, c]
    return {"Name": name, "ClassName": "Part", "Properties": props}


def rock_cluster(name, x, z, scale=1.0, heading=0):
    # Scenic, non-resource rock language. No ResourceNodeId/definition attributes.
    return model(name, [
        part("OutcropCore", (8*scale, 3.4*scale, 6*scale), (x, GROUND_Y+1.0*scale, z), "Slate", ROCK, rot=heading),
        part("OutcropShoulderA", (5.2*scale, 2.5*scale, 4.5*scale), (x-4.1*scale, GROUND_Y+0.7*scale, z+1.8*scale), "Rock", ROCK_DARK, rot=heading+24),
        part("OutcropShoulderB", (4.5*scale, 2.1*scale, 5.0*scale), (x+4.0*scale, GROUND_Y+0.55*scale, z-1.5*scale), "Rock", ROCK_MOSS, rot=heading-18),
    ])


def route_marker(name, x, z, heading=0):
    # Environmental landmark, not an interaction marker.
    return model(name, [
        part("BrokenPost", (0.65, 4.2, 0.65), (x, GROUND_Y+2.1, z), "Wood", WOOD, rot=heading),
        part("BentCrossbar", (4.2, 0.42, 0.5), (x+0.6, GROUND_Y+3.7, z), "CorrodedMetal", RUST, rot=heading+8),
        part("FootingStone", (2.8, 0.7, 2.2), (x, GROUND_Y+0.25, z), "Rock", ROCK_DARK, rot=heading-11),
    ])


def ground_patch(name, x, z, sx, sz, heading=0):
    return part(name, (sx, 0.18, sz), (x, GROUND_Y+0.08, z), "Ground", EARTH, rot=heading)


def build():
    children = []

    # ITERATION 4: authored bunker/farm world envelope. Scenic only; no resource IDs, prompts or gameplay state.
    children.append(model("BunkerFarmWorldArtEnvelope", [
        # Broad overlapping ground masses remove the immediate bright-green plane reading.
        part("BunkerApproachEarth", (112, 0.30, 72), (28, GROUND_Y+0.16, 54), "Ground", EARTH_DARK, rot=-4),
        part("FarmOuterEarth", (74, 0.32, 66), (67, GROUND_Y+0.18, 211), "Ground", [0.19,0.175,0.135], rot=3),
        part("FarmDisturbedSoil", (48, 0.18, 35), (66, GROUND_Y+0.29, 214), "Ground", [0.145,0.13,0.095], rot=-2),
        part("ServiceYardGravel", (30, 0.20, 38), (85, GROUND_Y+0.28, 211), "Pebble", [0.24,0.245,0.225], rot=5),
        part("BunkerFarmRoute", (13, 0.24, 105), (53, GROUND_Y+0.30, 151), "Ground", [0.16,0.145,0.11], rot=-7),
        part("RouteGravelSpine", (5.5, 0.10, 94), (54, GROUND_Y+0.43, 151), "Pebble", [0.27,0.27,0.24], rot=-7),
        # Safe scenic elevation at the perimeter, leaving the central farm/navigation field open.
        rock_cluster("FarmWestBermA", 38, 202, 0.82, 12),
        rock_cluster("FarmWestBermB", 35, 225, 0.65, -18),
        rock_cluster("FarmNorthOutcrop", 70, 244, 0.88, 8),
        rock_cluster("FarmEastOutcrop", 102, 225, 0.72, -24),
        rock_cluster("BunkerApproachOutcrop", 39, 111, 0.68, 17),
        # Foundation burial and drainage language visually seats the bunker in the earth.
        part("FoundationEarthWest", (18, 2.2, 34), (-5, GROUND_Y+0.65, 65), "Ground", EARTH_DARK, rot=-5),
        part("FoundationEarthEast", (18, 1.8, 40), (47, GROUND_Y+0.50, 78), "Ground", EARTH, rot=6),
        part("FoundationRockToeA", (15, 1.1, 5), (2, GROUND_Y+0.45, 28), "Slate", ROCK_DARK, rot=9),
        part("FoundationRockToeB", (13, 0.9, 5), (44, GROUND_Y+0.38, 99), "Rock", ROCK, rot=-11),
        # Disturbed ground and runoff follow movement/service logic rather than decorative patches.
        part("FarmWheelRutsA", (0.65,0.06,31), (88,GROUND_Y+0.48,211), "Ground", [0.10,0.095,0.075], rot=4),
        part("FarmWheelRutsB", (0.65,0.06,31), (91,GROUND_Y+0.48,211), "Ground", [0.10,0.095,0.075], rot=4),
        part("RunoffChannel", (1.4,0.10,43), (45,GROUND_Y+0.44,207), "Pebble", ROCK_DARK, rot=-5),
        # Clustered decayed vegetation: grouped edge masses, not evenly spaced trees.
        model("WestDeadGrowthCluster", [
            part("DeadBrushA", (7,0.35,5), (42,GROUND_Y+0.30,191), "Grass", DEAD_GRASS, rot=18),
            part("DeadBrushB", (5,0.28,7), (37,GROUND_Y+0.28,196), "Grass", [0.22,0.25,0.17], rot=-13),
            part("FallenTrunk", (12,0.85,0.85), (39,GROUND_Y+0.65,187), "Wood", WOOD, rot=28),
            part("BrokenPostA", (0.55,3.2,0.55), (45,GROUND_Y+1.6,194), "Wood", WOOD, rot=7),
        ]),
        model("NorthFarmEdgeCluster", [
            part("DeadBrushC", (10,0.30,5), (58,GROUND_Y+0.30,239), "Grass", DEAD_GRASS, rot=-9),
            part("DeadBrushD", (8,0.26,4), (83,GROUND_Y+0.28,241), "Grass", [0.24,0.265,0.18], rot=14),
            part("DiscardedPipe", (9,0.55,0.55), (91,GROUND_Y+0.55,238), "CorrodedMetal", RUST, rot=-21),
            part("BrokenTimber", (8,0.70,0.70), (48,GROUND_Y+0.52,237), "Wood", WOOD, rot=31),
        ]),
        model("ServiceDebrisCluster", [
            part("ConcreteChunkA", (3.2,1.0,2.5), (96,GROUND_Y+0.55,205), "Concrete", [0.31,0.31,0.285], rot=17),
            part("ConcreteChunkB", (2.4,0.8,2.0), (99,GROUND_Y+0.42,208), "Concrete", [0.25,0.255,0.24], rot=-8),
            part("DiscardedBeam", (7.5,0.45,0.65), (96,GROUND_Y+0.48,213), "Metal", [0.24,0.25,0.235], rot=24),
        ]),
        # Exterior composition pass: irregular edge masses and sightline framing.
        # All pieces remain scenic/non-colliding and stay outside canonical farm plots.
        model("BunkerApproachForegroundFrame", [
            ground_patch("WestMudShoulder", 22, 112, 24, 18, 14),
            ground_patch("EastGravelShoulder", 49, 120, 22, 16, -17),
            rock_cluster("WestApproachRockMass", 20, 120, 0.78, 24),
            rock_cluster("EastApproachRockMass", 52, 126, 0.62, -16),
            part("StormFallenTrunk", (14,1.05,1.05), (18,GROUND_Y+0.70,128), "Wood", WOOD, rot=31),
            part("RoadsideDeadGrowthA", (11,0.28,5), (28,GROUND_Y+0.25,126), "Grass", DEAD_GRASS, rot=-19),
            part("RoadsideDeadGrowthB", (8,0.24,6), (47,GROUND_Y+0.23,132), "Grass", [0.20,0.225,0.15], rot=23),
        ]),
        model("FarmMidgroundContainment", [
            ground_patch("WestFieldShoulder", 31, 215, 20, 46, 7),
            ground_patch("EastFieldShoulder", 105, 217, 19, 45, -9),
            rock_cluster("WestFieldAnchor", 29, 232, 0.92, 18),
            rock_cluster("EastFieldAnchor", 106, 199, 0.86, -28),
            part("WestCollapsedFencePost", (0.62,5.2,0.62), (34,GROUND_Y+2.6,201), "Wood", WOOD, rot=9),
            part("WestCollapsedFenceRail", (11,0.45,0.55), (31,GROUND_Y+1.0,205), "Wood", WOOD, rot=28),
            part("EastBoundaryBeam", (12,0.55,0.72), (104,GROUND_Y+0.55,233), "CorrodedMetal", RUST, rot=-31),
            part("EastDeadGrowth", (12,0.30,6), (101,GROUND_Y+0.26,238), "Grass", DEAD_GRASS, rot=12),
        ]),
        model("FarmBackgroundSilhouette", [
            rock_cluster("NorthWestSilhouette", 31, 255, 1.18, 12),
            rock_cluster("NorthEastSilhouette", 103, 257, 1.32, -17),
            part("NorthDeadwoodA", (0.85,10.5,0.85), (40,GROUND_Y+5.2,258), "Wood", [0.19,0.145,0.095], rot=-7),
            part("NorthDeadwoodB", (0.75,8.2,0.75), (91,GROUND_Y+4.1,260), "Wood", [0.17,0.13,0.085], rot=11),
            part("NorthFallenCrown", (16,0.85,0.85), (82,GROUND_Y+0.70,252), "Wood", WOOD, rot=-22),
            part("NorthBrushMassA", (17,0.38,8), (50,GROUND_Y+0.30,254), "Grass", [0.19,0.215,0.145], rot=17),
            part("NorthBrushMassB", (14,0.34,9), (87,GROUND_Y+0.28,254), "Grass", DEAD_GRASS, rot=-14),
        ]),
        model("RoadWearAndDrainageStory", [
            part("ApproachMudTrackA", (1.1,0.07,42), (49.8,GROUND_Y+0.45,160), "Ground", [0.105,0.095,0.07], rot=-7),
            part("ApproachMudTrackB", (1.0,0.07,38), (56.6,GROUND_Y+0.45,161), "Ground", [0.115,0.10,0.075], rot=-7),
            part("RoadWashoutA", (7,0.10,8), (50,GROUND_Y+0.47,181), "Pebble", ROCK_DARK, rot=18),
            part("RoadWashoutB", (5,0.09,10), (58,GROUND_Y+0.46,139), "Pebble", ROCK, rot=-16),
            part("AbandonedRoadBeam", (9,0.48,0.7), (63,GROUND_Y+0.48,178), "CorrodedMetal", RUST, rot=36),
        ]),
    ]))

    # WEST RIDGE: future mineral/resource opportunity. Kept west of bunker and
    # well north of protected Scrap piles / ZombieSpawns. Broad central gap is
    # intentionally left open for future mining interaction staging.
    children.append(model("WestRidgeFutureResourceOpportunity", [
        ground_patch("WeatheredGround", -145, 78, 78, 58, -8),
        rock_cluster("NorthOutcrop", -168, 92, 1.35, 18),
        rock_cluster("SouthOutcrop", -158, 55, 1.10, -12),
        rock_cluster("FarShoulder", -121, 101, 0.92, 34),
        route_marker("RidgeReturnLandmark", -108, 73, 12),
    ]))

    # NORTH CLEARING: open sightline / encounter space. Edge dressing only;
    # center remains deliberately unobstructed for future combat/scavenging.
    children.append(model("NorthExplorationClearing", [
        ground_patch("ClearingGround", -12, 205, 105, 68, 5),
        rock_cluster("WestEdgeOutcrop", -58, 214, 0.72, 15),
        rock_cluster("EastEdgeOutcrop", 38, 218, 0.70, -22),
        route_marker("ClearingBunkerReturnLandmark", -8, 170, 0),
        part("FallenTimberA", (13, 1.0, 1.0), (-47, GROUND_Y+0.55, 188), "Wood", WOOD, rot=22),
        part("FallenTimberB", (10, 0.85, 0.85), (47, GROUND_Y+0.45, 190), "Wood", WOOD, rot=-31),
    ]))

    # EAST TRANSITION: intentionally stops before protected farm bounds and
    # creates a readable visual corridor back toward bunker/farm circulation.
    children.append(model("EastBunkerReturnTransition", [
        ground_patch("ReturnTrack", 68, 119, 14, 38, -6),
        rock_cluster("TrackEdgeOutcrop", 66, 143, 0.52, 8),
        route_marker("BunkerReturnPost", 69, 101, -6),
        part("TrackEdgeGrassA", (10, 0.14, 4), (67, GROUND_Y+0.10, 132), "Grass", DEAD_GRASS, rot=-8),
        part("TrackEdgeGrassB", (9, 0.14, 4), (69, GROUND_Y+0.10, 111), "Grass", DEAD_GRASS, rot=8),
    ]))

    # SOUTH-WEST SCAVENGE APPROACH: above/north of Scrap/Zombie protected
    # bounds, framing an exploration route without touching their geometry.
    children.append(model("SouthWestScavengeApproach", [
        ground_patch("ScavengeApproachGround", -108, -4, 54, 34, 9),
        rock_cluster("ApproachOutcrop", -132, 2, 0.70, 25),
        route_marker("ScavengeRouteLandmark", -88, 3, 8),
        part("DiscardedBeam", (11, 0.55, 0.8), (-116, GROUND_Y+0.35, -13), "CorrodedMetal", RUST, rot=17),
    ]))

    return {
        "ClassName": "Model",
        "attributes": {
            "FoundationPurpose": "WorldVisualFoundation",
            "GameplayImplemented": False,
            "FutureResourceCompatible": True,
        },
        "Children": children,
    }


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(f"generated {OUTPUT}")


if __name__ == "__main__":
    main()
