# THE OUTSKIRTS — World Bible

## Primary World

THE OUTSKIRTS is the primary vertical-slice world.

Its established world concepts include:

- an underground bunker and bunker entrance
- playable grass/ground
- farming space
- abandoned structures
- scrap/resource areas
- infected enemies
- countryside survival atmosphere

## Verified Playable-World Coordinates

Roblox Studio inspection established the following authoritative evidence:

- playable `Grassblox` ground surface: approximately world Y `53.4`
- existing bunker floor surface: approximately world Y `54`
- existing bunker shell bounds: X `-18..18`, Y `53..75`, Z `21..56`
- empty Roblox Terrain: `0` occupied cells at the time of inspection
- original Baseplate bounds: Y `-110..-90`
- rejected `Workspace/Rebuild/BedroomBlockout` bounds: Y `-1..11`

The authoritative floor surface for future bunker planning is approximately
world Y `54`.

Any future bunker rebuild must use verified playable-world coordinates. It must
not be authored around world Y `0`.

The rejected Rebuild appeared below the playable map because its floor was
approximately 54 studs below the bunker floor and its highest point remained
approximately 42 studs below the elevated playable ground.

## Existing Bunker Status

The existing bunker is functional reference, not final environment art.

Preserve these assets until their behavior is deliberately audited and migrated:

- `BunkerDoor`
- `BunkerSofa` where useful
- `BatteryButton` functionality
- `DoorShop` functionality
- `Processor`
- `Upgrade table`
- `Weapon Workbench`
- `BunkerLights` and power functionality

Their current geometry, materials, style, and composition must not dictate the
rebuild.

The existing bunker shell should remain intact as reference until an approved
replacement layout is validated. The intended long-term direction is to replace
the shell/layout while selectively migrating useful functional systems.

## Protected Overworld Systems

Preserve the following overworld gameplay content during bunker work:

- `farm`
- `Scrap piles`
- `ZombieSpawns`
- `Grassblox` and the playable ground

Do not move, delete, or redesign these systems as an incidental part of bunker
work.

## Bunker World Relationship

The rebuilt bunker must be planned as a connected multi-room place with:

- a starting bedroom
- circulation into the bunker interior
- a central/common space
- purposeful functional areas
- a clear relationship to the bunker entrance/defense point
- a legible route toward the overworld and farming access

Exact gameplay rules and final geometry require separate approved specifications.

## Future Biomes

### Snow Biome

Long-term concept:

- strong winter atmosphere
- snow-covered environment
- snowman and other environmental details
- biome-specific structures and presentation

### Sakura/Cherry-Blossom Biome

Long-term concept:

- pink foliage
- cherry-blossom atmosphere
- distinctive environmental presentation

Future biome concepts are vision only and are not permission to implement maps,
weather, enemies, resources, NPCs, or gameplay.

## Map Rule

Each future biome should have a distinctive environment and atmosphere. A biome
must not be only a recolor of another map.
