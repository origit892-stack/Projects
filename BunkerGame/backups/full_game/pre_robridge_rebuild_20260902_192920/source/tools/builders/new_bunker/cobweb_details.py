"""Selective cobwebs and small abandonment traces for ``NewBunker``.

This module intentionally stays cheap: six four-strand cobweb assemblies and
eleven small story-detail parts (35 visual-only BaseParts total).  The webs use
thin native cylinders aligned between explicit endpoints, avoiding textures,
external assets, and large transparent sheets while remaining legible at
player height.  All output is non-colliding, non-touching, non-queryable, and
casts no shadow.
"""

from __future__ import annotations

import math

from .kit import AGED_WHITE, CONCRETE_DARK, RUST, STEEL_LIGHT, model, part


WEB = [0.76, 0.77, 0.71]
PAPER = [0.47, 0.45, 0.37]


def _strand(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    *,
    width: float = 0.060,
    color: list[float] = WEB,
    transparency: float = 0.14,
) -> dict:
    """Return a thin cylinder whose local X axis joins ``start`` to ``end``."""

    dx, dy, dz = (end[index] - start[index] for index in range(3))
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0:
        raise ValueError(f"strand {name!r} requires distinct endpoints")

    horizontal = math.sqrt(dx * dx + dy * dy)
    ry = math.degrees(math.atan2(-dz, horizontal))
    rz = math.degrees(math.atan2(dy, dx))
    midpoint = tuple((start[index] + end[index]) / 2 for index in range(3))
    return part(
        name,
        (length, width, width),
        midpoint,
        material="SmoothPlastic",
        color=color,
        collide=False,
        transparency=transparency,
        shape="Cylinder",
        rot=(0, ry, rz),
        cast_shadow=False,
    )


def _corner_web(
    name: str,
    anchor: tuple[float, float, float],
    lower: tuple[float, float, float],
    outer: tuple[float, float, float],
) -> dict:
    """Build one triangular corner web with a single interior radial strand."""

    midpoint = tuple((lower[index] + outer[index]) / 2 for index in range(3))
    return model(name, [
        _strand("AnchorToLower", anchor, lower),
        _strand("AnchorToOuter", anchor, outer),
        _strand("OuterArc", lower, outer, transparency=0.20),
        _strand("InnerRadial", anchor, midpoint, width=0.045, transparency=0.24),
    ])


def _build_cobwebs() -> list[dict]:
    """Place webs only in high, low-traffic corners and service recesses."""

    return [
        # Bedroom carries the heaviest neglect.  This first web bridges the
        # west wall pipe/shelf corner and is composed for the bedroom detail
        # review camera from the central floor pocket.
        _corner_web(
            "BedroomPipeShelfCobweb",
            (-95.18, 65.15, 94.05),
            (-95.18, 62.85, 94.05),
            (-95.18, 65.15, 90.80),
        ),
        # A second bedroom web frames the unused upper corner above the locker
        # bank without intruding into the exit sightline.
        _corner_web(
            "BedroomLockerCornerCobweb",
            (-95.18, 65.00, 68.62),
            (-95.18, 62.95, 68.62),
            (-92.35, 65.00, 68.62),
        ),
        _corner_web(
            "StorageNorthRackCobweb",
            (-69.38, 64.25, 77.38),
            (-69.38, 61.95, 77.38),
            (-65.95, 64.25, 77.38),
        ),
        _corner_web(
            "ResidentialMaintenanceCobweb",
            (-77.38, 64.25, 59.00),
            (-77.38, 62.15, 59.00),
            (-77.38, 64.25, 62.15),
        ),
        _corner_web(
            "PowerUnusedMachineryCobweb",
            (-50.65, 66.15, 81.38),
            (-50.65, 63.55, 81.38),
            (-47.05, 66.15, 81.38),
        ),
        _corner_web(
            "ServiceRecessCobweb",
            (-41.75, 63.15, 93.38),
            (-41.75, 61.15, 93.38),
            (-38.70, 63.15, 93.38),
        ),
        _corner_web(
            "WorkshopUpperRackCobweb",
            (-95.12, 64.85, 43.70),
            (-95.12, 62.95, 43.70),
            (-92.25, 64.85, 43.70),
        ),
        _corner_web(
            "CommonServiceNookCobweb",
            (-69.18, 66.10, 56.60),
            (-69.18, 64.20, 56.60),
            (-66.35, 66.10, 56.60),
        ),
    ]


def _build_small_details() -> list[dict]:
    """Return four restrained story clusters using the remaining 11 Parts."""

    return [
        model("LooseServiceCable", [
            _strand(
                "UpperCableDrop",
                (-36.05, 63.05, 90.40),
                (-36.12, 61.40, 90.48),
                width=0.10,
                color=CONCRETE_DARK,
                transparency=0.03,
            ),
            _strand(
                "SlackCableMiddle",
                (-36.12, 61.40, 90.48),
                (-36.35, 59.75, 90.12),
                width=0.10,
                color=CONCRETE_DARK,
                transparency=0.03,
            ),
            _strand(
                "FrayedCableTail",
                (-36.35, 59.75, 90.12),
                (-36.02, 58.45, 90.32),
                width=0.075,
                color=CONCRETE_DARK,
                transparency=0.08,
            ),
        ]),
        model("DiscardedStorageCans", [
            part(
                "UprightOldCan",
                (0.78, 0.42, 0.42),
                (-68.25, 54.40, 76.15),
                material="CorrodedMetal",
                color=RUST,
                collide=False,
                shape="Cylinder",
                rot=(0, 0, 90),
                cast_shadow=False,
            ),
            part(
                "CrushedOldCan",
                (0.62, 0.38, 0.38),
                (-67.45, 54.30, 76.35),
                material="Metal",
                color=STEEL_LIGHT,
                collide=False,
                shape="Cylinder",
                rot=(10, 14, 18),
                cast_shadow=False,
            ),
        ]),
        model("DamagedResidentialNotice", [
            part(
                "BentNoticePlate",
                (0.06, 1.55, 2.65),
                (-77.43, 59.40, 47.20),
                material="Metal",
                color=AGED_WHITE,
                collide=False,
                rot=(8, 0, 0),
                transparency=0.08,
                cast_shadow=False,
            ),
            part(
                "FadedWarningSlash",
                (0.035, 0.22, 2.15),
                (-77.39, 59.42, 47.20),
                material="SmoothPlastic",
                color=RUST,
                collide=False,
                rot=(24, 0, 0),
                transparency=0.24,
                cast_shadow=False,
            ),
        ]),
        model("AbandonedBedroomPapers", [
            part("FoldedMaintenanceNote", (1.05, 0.018, 0.72), (-93.55, 54.18, 92.35), material="SmoothPlastic", color=PAPER, collide=False, rot=(0, 14, 0), cast_shadow=False),
            part("TornNoticeHalf", (0.82, 0.016, 0.52), (-92.72, 54.17, 92.72), material="SmoothPlastic", color=AGED_WHITE, collide=False, rot=(0, -22, 0), transparency=0.10, cast_shadow=False),
            part("DustyInventorySlip", (0.68, 0.014, 0.46), (-93.12, 54.19, 91.68), material="SmoothPlastic", color=PAPER, collide=False, rot=(0, 31, 0), transparency=0.16, cast_shadow=False),
            part("CrumpledPaperForm", (0.38, 0.18, 0.32), (-92.40, 54.25, 91.95), material="SmoothPlastic", color=AGED_WHITE, collide=False, rot=(12, -9, 18), transparency=0.08, cast_shadow=False),
        ]),
    ]


def build_cobweb_details() -> list[dict]:
    """Return selective, player-legible cobwebs plus restrained abandonment details."""

    return _build_cobwebs() + _build_small_details()
