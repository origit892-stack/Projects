# THE OUTSKIRTS — Gameplay Bible

## Gameplay Direction

THE OUTSKIRTS is a survival game. Gameplay systems should eventually reinforce
preparation, exploration, danger, recovery, and progression within a cohesive
world.

This document records approved direction. It does not supply missing mechanics,
numbers, controls, balance, networking contracts, or implementation details.

## Starting Flow

The player wakes near an old bed in an abandoned underground bunker bedroom.

The starting flow should eventually establish:

- the player's initial location and vulnerability
- an immediately readable route into the larger bunker
- the bunker as a survival base with old but useful infrastructure
- a relationship between the bunker interior, its entrance, and the outside

The exact tutorial, interaction, inventory, spawn, and narrative behavior is not
yet specified and must not be invented.

## Bunker-Supported Systems

The bunker layout should reserve purposeful locations for future systems:

- weapon/workbench area
- upgrade area
- storage
- power/electrical infrastructure
- NPC/shop area
- access toward farming/outside
- entrance/defense point
- central/common space

Planning a location does not authorize implementation of its gameplay system.

## Existing Functional Reference

Until deliberate migration tasks are approved, preserve the behavior associated
with:

- `BunkerDoor`
- `BunkerSofa` where useful
- `BatteryButton`
- `DoorShop`
- `Processor`
- `Upgrade table`
- `Weapon Workbench`
- `BunkerLights` and power controls

Their present visuals are not approved design requirements.

## Long-Term Gameplay Concepts

- realistic-feeling rifle/combat
- pickaxe/tool gameplay
- torch/flashlight
- farming with multiple crops such as wheat and carrots
- improved zombies
- wave survival
- NPC shop
- progression
- polished UI
- multiple maps and biomes

These concepts require future specifications before implementation. Do not infer
weapon statistics, crop timing, enemy behavior, wave rules, currencies, shop
inventory, progression curves, UI flows, or biome mechanics from this list.

## Authority and Scope

- Server/client authority remains defined by `TECH-BIBLE.md`.
- Preserve the existing farm, scrap areas, zombie spawns, and playable ground
  during bunker work.
- Do not expand an environment task into gameplay implementation.
- Do not implement a long-term concept without an explicit active task.
