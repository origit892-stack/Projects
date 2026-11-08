"""Selected interactive and explicitly inactive props for ``NewBunker``.

This module owns only the children later mounted under
``NewBunker/InteractiveProps``.  It deliberately keeps the prompt population
small: two opening crates, one opening locker, one offline power control, and
one inspect-only workshop station.  The first three follow the shared
``BunkerInteractionService`` contract with one ``MovingPart`` and one invisible
``OpenPose`` per functional model.

The two crates sleeve existing static supply-crate massing by a small margin.
That preserves the approved room dressing while adding a readable hinged lid,
latches, state lamp, and centralized interaction anchor without changing the
room modules.  The bedroom locker is freestanding in the southeast wall pocket
and leaves the exit sightline and wake-to-door lane clear.

Director-review cameras (position -> target):

* storage crate: (-63.0, 59.1, 67.8) -> (-67.2, 56.0, 67.8)
* workshop crate: (-83.8, 59.0, 40.8) -> (-87.8, 56.0, 43.8)
* bedroom locker: (-84.2, 59.1, 73.1) -> (-80.0, 57.6, 70.8)
* power control: (-35.1, 59.3, 78.0) -> (-30.4, 58.2, 78.0)
* workbench station: (-84.6, 59.2, 36.8) -> (-89.0, 58.1, 32.8)
"""

from __future__ import annotations

from .kit import (
    AGED_WHITE,
    CONCRETE_DARK,
    GREEN,
    RED,
    RUST,
    STEEL,
    STEEL_LIGHT,
    UTILITY_BLUE,
    WOOD,
    YELLOW,
    model,
    part,
)


def _prompt(
    name: str,
    action_text: str,
    object_text: str,
    *,
    hold_duration: float,
    max_distance: float,
) -> dict:
    """Return one Custom ProximityPrompt matching the centralized UI contract."""

    return {
        "Name": name,
        "ClassName": "ProximityPrompt",
        "Properties": {
            "ActionText": action_text,
            "ObjectText": object_text,
            "Style": "Custom",
            "Exclusivity": "OnePerButton",
            "KeyboardKeyCode": "E",
            "GamepadKeyCode": "ButtonX",
            "HoldDuration": hold_duration,
            "MaxActivationDistance": max_distance,
            "RequiresLineOfSight": True,
            "ClickablePrompt": True,
        },
    }


def _interaction_anchor(
    pos: tuple[float, float, float],
    prompt: dict,
    *,
    size: tuple[float, float, float] = (0.35, 0.35, 0.35),
) -> dict:
    """Give each prop one invisible, non-colliding and non-queryable prompt host."""

    return part(
        "InteractionAnchor",
        size,
        pos,
        material="SmoothPlastic",
        color=CONCRETE_DARK,
        collide=False,
        transparency=1.0,
        cast_shadow=False,
        children=[prompt],
    )


def _sleeved_supply_crate(
    name: str,
    pos: tuple[float, float, float],
    size: tuple[float, float, float],
    *,
    accent: list[float],
    object_text: str,
    hold_duration: float,
    max_distance: float,
) -> dict:
    """Create an aged, hardware-rich outer crate with an animated top lid."""

    x, y, z = pos
    sx, sy, sz = size
    top_y = y + sy / 2 + 0.14
    open_y = top_y + sz / 2 - 0.10
    open_z = z + sz / 2 - 0.10

    return model(name, [
        # A slightly enlarged shell covers the approved static crate cleanly.
        part("ArmoredCrateBody", size, pos, material="WoodPlanks", color=WOOD),
        part("LowerSteelSkid", (sx + 0.18, 0.26, sz + 0.18), (x, y - sy / 2 + 0.13, z), material="CorrodedMetal", color=STEEL),
        part("FrontSteelBand", (sx + 0.16, sy - 0.24, 0.18), (x, y, z - sz / 2 - 0.02), material="CorrodedMetal", color=STEEL_LIGHT, collide=False),
        part("WestCornerBand", (0.20, sy + 0.05, sz + 0.14), (x - sx / 2 - 0.02, y, z), material="CorrodedMetal", color=RUST, collide=False),
        part("EastCornerBand", (0.20, sy + 0.05, sz + 0.14), (x + sx / 2 + 0.02, y, z), material="Metal", color=STEEL_LIGHT, collide=False),
        part("MovingPart", (sx + 0.22, 0.28, sz + 0.22), (x, top_y, z), material="DiamondPlate", color=GREEN, collide=False),
        part("FrontLatch", (0.58, 0.62, 0.18), (x, top_y - 0.22, z - sz / 2 - 0.13), material="CorrodedMetal", color=accent, collide=False),
        part("CarryHandle", (1.15, 0.15, 0.16), (x, y + 0.12, z - sz / 2 - 0.15), material="Metal", color=AGED_WHITE, collide=False),
        part("InventoryStripe", (sx * 0.56, 0.18, 0.05), (x, y - 0.35, z - sz / 2 - 0.15), material="SmoothPlastic", color=accent, collide=False, cast_shadow=False),
        part("ReadyStateLamp", (0.24, 0.24, 0.10), (x + sx * 0.34, y + 0.38, z - sz / 2 - 0.17), material="Neon", color=accent, collide=False, cast_shadow=False),
        part("OpenPose", (sx + 0.22, 0.28, sz + 0.22), (x, open_y, open_z), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, transparency=1.0, rot=(-82, 0, 0), cast_shadow=False),
        _interaction_anchor(
            (x, y + 0.25, z - sz / 2 - 0.36),
            _prompt(
                "PrototypeCratePrompt",
                "OPEN",
                object_text,
                hold_duration=hold_duration,
                max_distance=max_distance,
            ),
        ),
    ])


def _bedroom_utility_locker() -> dict:
    """A narrow personal locker in a wall pocket outside the wake/exit lane."""

    x, y, z = -80.2, 57.45, 70.8
    return model("BedroomPersonalUtilityLocker", [
        part("LockerBack", (0.24, 6.9, 2.35), (x + 0.72, y, z), material="CorrodedMetal", color=STEEL),
        part("SouthSide", (1.55, 6.9, 0.22), (x, y, z - 1.08), material="CorrodedMetal", color=RUST),
        part("NorthSide", (1.55, 6.9, 0.22), (x, y, z + 1.08), material="Metal", color=STEEL_LIGHT),
        part("LockerTop", (1.55, 0.24, 2.35), (x, y + 3.33, z), material="Metal", color=STEEL_LIGHT),
        part("LockerBottom", (1.55, 0.24, 2.35), (x, y - 3.33, z), material="CorrodedMetal", color=STEEL),
        part("InnerShelf", (1.34, 0.18, 2.05), (x, y + 0.35, z), material="Metal", color=STEEL, collide=False),
        # The west-facing door is one animated part so no anchored hardware is
        # left floating after a server-authoritative open tween.
        part("MovingPart", (0.18, 6.15, 1.72), (x - 0.88, y, z + 0.01), material="CorrodedMetal", color=GREEN, collide=False),
        part("LatchReceiver", (0.20, 0.92, 0.18), (x - 0.79, y, z + 0.88), material="Metal", color=AGED_WHITE, collide=False),
        part("SouthSideVentUpper", (0.82, 0.12, 0.10), (x, y + 2.30, z - 1.20), material="Metal", color=CONCRETE_DARK, collide=False),
        part("SouthSideVentLower", (0.82, 0.12, 0.10), (x, y + 1.85, z - 1.20), material="Metal", color=CONCRETE_DARK, collide=False),
        part("FadedNumberPlate", (0.72, 0.42, 0.08), (x, y + 0.70, z - 1.20), material="SmoothPlastic", color=AGED_WHITE, collide=False, transparency=0.22, cast_shadow=False),
        # South edge is the implied hinge; the open pose swings into the room
        # and stays non-colliding so it cannot trap the player.
        part("OpenPose", (0.18, 6.15, 1.72), (x - 1.74, y, z - 0.86), material="SmoothPlastic", color=CONCRETE_DARK, collide=False, transparency=1.0, rot=(0, 90, 0), cast_shadow=False),
        _interaction_anchor(
            (x - 1.20, 58.0, z),
            _prompt(
                "PrototypeLockerPrompt",
                "OPEN",
                "PERSONAL LOCKER",
                hold_duration=0.42,
                max_distance=7.0,
            ),
        ),
    ])


def _offline_power_control() -> dict:
    """Communicate a tempting but honestly unavailable legacy-migration bay."""

    return model("OfflineBatteryControl", [
        part("ControlFace", (0.10, 2.35, 1.82), (-30.66, 58.1, 78.0), material="CorrodedMetal", color=CONCRETE_DARK, collide=False),
        part("EmergencyToggle", (0.16, 1.02, 0.16), (-30.75, 58.0, 77.62), material="Metal", color=RED, collide=False, rot=(0, 0, 18)),
        part("DeadStateLamp", (0.10, 0.34, 0.34), (-30.75, 58.68, 78.38), material="SmoothPlastic", color=[0.13, 0.08, 0.06], collide=False, cast_shadow=False),
        part("OfflineWarningBar", (0.08, 0.28, 1.25), (-30.76, 57.25, 78.0), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.18, cast_shadow=False),
        _interaction_anchor(
            (-31.00, 58.1, 78.0),
            _prompt(
                "OfflineControlPrompt",
                "CHECK",
                "POWER CONTROL — OFFLINE",
                hold_duration=0.55,
                max_distance=7.0,
            ),
        ),
    ])


def _workbench_inspection_point() -> dict:
    """Give the future workbench an honest inspect affordance, not fake gameplay."""

    return model("WeaponWorkbenchInspectionPoint", [
        part("InspectionPlate", (2.4, 0.52, 0.10), (-89.0, 58.65, 33.74), material="CorrodedMetal", color=STEEL, collide=False),
        part("OfflineStatusLamp", (0.28, 0.28, 0.10), (-87.95, 58.65, 33.82), material="SmoothPlastic", color=RED, collide=False, cast_shadow=False),
        part("InspectionStripe", (1.15, 0.12, 0.08), (-89.25, 58.65, 33.82), material="SmoothPlastic", color=YELLOW, collide=False, transparency=0.25, cast_shadow=False),
        _interaction_anchor(
            (-89.0, 58.1, 34.05),
            _prompt(
                "InspectStationPrompt",
                "INSPECT",
                "WEAPON WORKBENCH — INACTIVE",
                hold_duration=0.30,
                max_distance=8.0,
            ),
            size=(0.45, 0.45, 0.45),
        ),
    ])


def _inactive_service_point(
    name: str,
    pos: tuple[float, float, float],
    *,
    object_text: str,
    accent: list[float],
    max_distance: float = 7.0,
) -> dict:
    """Create a compact, readable control point without inventing gameplay."""

    x, y, z = pos
    return model(name, [
        part("RecessHousing", (0.28, 2.05, 2.25), (x, y, z), material="CorrodedMetal", color=CONCRETE_DARK, collide=False),
        part("ControlPlate", (0.18, 1.42, 1.62), (x - 0.18, y, z), material="Metal", color=STEEL, collide=False),
        part("PhysicalSwitch", (0.22, 0.72, 0.20), (x - 0.32, y - 0.10, z - 0.42), material="Metal", color=AGED_WHITE, collide=False, rot=(0, 0, 14)),
        part("StateLamp", (0.18, 0.30, 0.30), (x - 0.34, y + 0.48, z + 0.45), material="SmoothPlastic", color=accent, collide=False, cast_shadow=False),
        part("WarningStripe", (0.12, 0.20, 1.18), (x - 0.34, y - 0.62, z + 0.20), material="SmoothPlastic", color=accent, collide=False, transparency=0.20, cast_shadow=False),
        _interaction_anchor(
            (x - 0.55, y, z),
            _prompt(
                "InspectStationPrompt",
                "INSPECT",
                object_text,
                hold_duration=0.28,
                max_distance=max_distance,
            ),
        ),
    ])


def build_interactive_props() -> list[dict]:
    """Return a deliberate eight-prompt interaction pass with honest inactive states."""

    return [
        _sleeved_supply_crate(
            "StorageMedicalSupplyCrate",
            (-67.2, 55.1, 67.8),
            (2.52, 2.22, 2.52),
            accent=RED,
            object_text="MEDICAL SUPPLY CRATE",
            hold_duration=0.48,
            max_distance=7.5,
        ),
        _sleeved_supply_crate(
            "WorkshopConsumablesCrate",
            (-87.8, 55.0, 43.8),
            (2.72, 2.12, 2.42),
            accent=YELLOW,
            object_text="WORKSHOP SUPPLY CRATE",
            hold_duration=0.42,
            max_distance=7.5,
        ),
        _bedroom_utility_locker(),
        _offline_power_control(),
        _workbench_inspection_point(),
        _inactive_service_point(
            "EntranceControlInspectionPoint",
            (-65.12, 58.45, 13.8),
            object_text="ENTRANCE CONTROL — NO POWER",
            accent=RED,
            max_distance=7.5,
        ),
        _inactive_service_point(
            "UpgradeStationInspectionPoint",
            (-94.35, 58.65, 58.8),
            object_text="UPGRADE STATION — INACTIVE",
            accent=YELLOW,
        ),
        _inactive_service_point(
            "ShopServiceInspectionPoint",
            (-34.05, 58.35, 46.2),
            object_text="SERVICE COUNTER — UNATTENDED",
            accent=UTILITY_BLUE,
        ),
    ]
