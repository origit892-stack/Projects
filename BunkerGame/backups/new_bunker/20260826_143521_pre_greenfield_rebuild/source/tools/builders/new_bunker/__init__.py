"""Composable builders for the NewBunker environment prototype.

The package deliberately emits the currently safe staging coordinates.  The
verified legacy-site transform is documented in :mod:`new_bunker.site`, but it
must not be applied until the protected legacy systems have an approved
migration/cutover plan.
"""

from .architecture import build_architecture
from .corridors import build_corridors
from .site import FINAL_OFFSET, PLACEMENT_STATUS, ROOM_BOUNDS, STAGING_OFFSET

__all__ = [
    "FINAL_OFFSET",
    "PLACEMENT_STATUS",
    "ROOM_BOUNDS",
    "STAGING_OFFSET",
    "build_architecture",
    "build_corridors",
]
