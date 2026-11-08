#!/usr/bin/env python3
"""Assemble the director-review NewBunker model from isolated specialist modules."""

from __future__ import annotations

import json
from pathlib import Path

from new_bunker.architecture import build_architecture
from new_bunker.atmosphere import build_atmosphere
from new_bunker.bedroom import bedroom_markers, build_bedroom
from new_bunker.common_area import build_common_area
from new_bunker.cobweb_details import build_cobweb_details
from new_bunker.corridors import build_corridors
from new_bunker.decay_details import build_decay_details
from new_bunker.exterior_entrance import build_entrance, build_exterior, build_service_exit
from new_bunker.interactive_props import build_interactive_props
from new_bunker.environment_rework import build_environment_rework
from new_bunker.kit import GREEN, RUST, UTILITY_BLUE, YELLOW, model, part
from new_bunker.lighting_materials import build_lighting, build_material_details
from new_bunker.power_room import build_power_room, power_markers
from new_bunker.site import ACTIVE_OFFSET
from new_bunker.shop_story import build_environment_story, build_shop_area
from new_bunker.workshop_upgrade_storage import (
    build_storage,
    build_upgrade_area,
    build_workshop,
)


OUTPUT = Path(__file__).resolve().parents[2] / "src/Workspace/Rebuild/NewBunker.model.json"


def build_general_markers() -> list[dict]:
    return [
        part(
            "FutureBunkerDoorMarker",
            (8, 0.2, 2),
            (-60, 54.1, 9.2),
            material="SmoothPlastic",
            color=YELLOW,
            collide=False,
            transparency=1.0,
            cast_shadow=False,
        ),
        part(
            "FutureWeaponWorkbenchMarker",
            (6, 0.2, 3),
            (-91, 54.1, 36),
            material="SmoothPlastic",
            color=RUST,
            collide=False,
            transparency=1.0,
            cast_shadow=False,
        ),
        part(
            "FutureUpgradeTableMarker",
            (6, 0.2, 4),
            (-89.5, 54.1, 57),
            material="SmoothPlastic",
            color=UTILITY_BLUE,
            collide=False,
            transparency=1.0,
            cast_shadow=False,
        ),
        part(
            "FutureNPCShopMarker",
            (2, 0.2, 2),
            (-31.6, 54.1, 40.5),
            material="SmoothPlastic",
            color=GREEN,
            collide=False,
            transparency=1.0,
            cast_shadow=False,
        ),
        part(
            "FarmRouteMarker",
            (3, 0.2, 3),
            (-24, 54.1, 104),
            material="SmoothPlastic",
            color=GREEN,
            collide=False,
            transparency=1.0,
            cast_shadow=False,
        ),
    ]


def _translate_tree(node: dict, offset: tuple[float, float, float]) -> dict:
    """Translate every authored world-space position as one coherent structure."""

    properties = node.get("Properties")
    if isinstance(properties, dict):
        position = properties.get("Position")
        if isinstance(position, list) and len(position) == 3:
            properties["Position"] = [position[i] + offset[i] for i in range(3)]

        cframe = properties.get("CFrame")
        if isinstance(cframe, list) and len(cframe) >= 3:
            cframe[0] += offset[0]
            cframe[1] += offset[1]
            cframe[2] += offset[2]

    for child in node.get("Children", []):
        _translate_tree(child, offset)

    return node


def _preserve_workshop_interaction_contract(root: dict) -> None:
    """Keep the existing inactive-workbench target stable across regeneration."""

    interactive_props = next(
        child for child in root["Children"] if child["Name"] == "InteractiveProps"
    )
    weapon_workbench = next(
        child
        for child in interactive_props["Children"]
        if child["Name"] == "WeaponWorkbenchInspectionPoint"
    )
    weapon_workbench.setdefault("attributes", {})["GameplayTargetId"] = "legacy_weapon_upgrade"


def build_root() -> dict:
    root = {
        "ClassName": "Model",
        "Children": [
            model("Architecture", build_architecture()),
            model("Bedroom", build_bedroom()),
            model("Corridors", build_corridors()),
            model("CommonArea", build_common_area()),
            model("Workshop", build_workshop()),
            model("UpgradeArea", build_upgrade_area()),
            model("Storage", build_storage()),
            model("PowerRoom", build_power_room()),
            model("ShopArea", build_shop_area()),
            model("Entrance", build_entrance()),
            model("ServiceExit", build_service_exit()),
            model("InteractiveProps", build_interactive_props()),
            model("EnvironmentRework", build_environment_rework()),
            model("Lighting", build_lighting()),
            model(
                "EnvironmentDetails",
                build_environment_story()
                + build_material_details()
                + build_atmosphere()
                + build_decay_details()
                + build_cobweb_details()
                + build_exterior(),
            ),
            model(
                "CompositionMarkers",
                bedroom_markers() + power_markers() + build_general_markers(),
            ),
        ],
    }
    _preserve_workshop_interaction_contract(root)
    return _translate_tree(root, ACTIVE_OFFSET)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_root(), indent=2) + "\n", encoding="utf-8")
    print(f"generated {OUTPUT}")


if __name__ == "__main__":
    main()
