"""Verified world-space constants for the NewBunker.

The Director authorized legacy-bunker migration on 2026-08-15. Studio evidence
places the legacy bunker door at approximately (0, 59, 21). ``FINAL_OFFSET``
relocates the authored NewBunker from its staging site to the legacy bunker
site while preserving the complete authored hierarchy and room relationships.
"""

from __future__ import annotations

from typing import Final


Vec3 = tuple[float, float, float]
Bounds2D = tuple[float, float, float, float]

FLOOR_Y: Final[float] = 54.0
STAGING_OFFSET: Final[Vec3] = (0.0, 0.0, 0.0)
FINAL_OFFSET: Final[Vec3] = (60.0, 0.0, 12.0)
ACTIVE_OFFSET: Final[Vec3] = FINAL_OFFSET
PLACEMENT_STATUS: Final[str] = (
    "FINAL_SITE_AUTHORIZED: legacy-bunker migration approved by Director; "
    "generation uses FINAL_OFFSET as the permanent Rojo source-of-truth placement."
)

# X0, X1, Z0, Z1.  East/service corridors are seven studs wide so structural
# walls and ribs retain at least 5.5 studs of practical player clearance.
ROOM_BOUNDS: Final[dict[str, Bounds2D]] = {
    "EntranceDefenseShell": (-72.0, -48.0, 8.0, 20.0),
    "SouthConnectorShell": (-65.0, -55.0, 20.0, 30.0),
    "CommonHubShell": (-70.0, -46.0, 30.0, 58.0),
    "WestResidentialCorridorShell": (-78.0, -70.0, 32.0, 82.0),
    "WorkshopShell": (-96.0, -78.0, 28.0, 46.0),
    "UpgradeShell": (-96.0, -78.0, 48.0, 66.0),
    "BedroomShell": (-96.0, -78.0, 68.0, 96.0),
    "StorageShell": (-70.0, -54.0, 58.0, 78.0),
    "EastUtilityCorridorShell": (-46.0, -39.0, 32.0, 62.0),
    "ShopShell": (-39.0, -30.0, 30.0, 52.0),
    "PowerRoomShell": (-52.0, -30.0, 60.0, 82.0),
    "MaintenanceCrossPassageShell": (-54.0, -52.0, 66.0, 72.0),
    "ServiceConnectorShell": (-42.5, -35.5, 82.0, 94.0),
    "FarmServiceShell": (-48.0, -30.0, 94.0, 112.0),
}

ROOM_HEIGHTS: Final[dict[str, float]] = {
    "EntranceDefenseShell": 12.0,
    "SouthConnectorShell": 11.0,
    "CommonHubShell": 14.0,
    "WestResidentialCorridorShell": 11.0,
    "WorkshopShell": 12.0,
    "UpgradeShell": 13.0,
    "BedroomShell": 12.0,
    "StorageShell": 11.0,
    "EastUtilityCorridorShell": 11.0,
    "ShopShell": 11.0,
    "PowerRoomShell": 13.0,
    "MaintenanceCrossPassageShell": 10.0,
    "ServiceConnectorShell": 10.0,
    "FarmServiceShell": 11.0,
}


def translated_point(point: Vec3, offset: Vec3 = ACTIVE_OFFSET) -> Vec3:
    """Return a translated point without mutating the authoritative plan."""

    return tuple(a + b for a, b in zip(point, offset, strict=True))


def translated_bounds(bounds: Bounds2D, offset: Vec3 = ACTIVE_OFFSET) -> Bounds2D:
    """Translate X/Z bounds; Y remains governed by ``FLOOR_Y``."""

    x0, x1, z0, z1 = bounds
    return x0 + offset[0], x1 + offset[0], z0 + offset[2], z1 + offset[2]


def final_room_bounds() -> dict[str, Bounds2D]:
    """Expose the authorized final-site room bounds for audits and validation."""

    return {name: translated_bounds(bounds, FINAL_OFFSET) for name, bounds in ROOM_BOUNDS.items()}
