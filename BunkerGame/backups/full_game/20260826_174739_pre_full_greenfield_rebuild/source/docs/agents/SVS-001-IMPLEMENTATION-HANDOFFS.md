# SVS-001 Specialist Implementation Handoffs

## Inventory / Loot / Economy Agent
Added canonical `wood` and `axe_basic` entries to the existing single ItemDefinitions registry. No second inventory/catalog and no Farming migration.

## Combat / Tools Agent
Added `ToolDefinitions` with `axe_basic`; harvest damage/cooldown are centralized prototype tuning. Physical Tool is a server-provisioned runtime representation and not possession authority.

## World / Survival Systems Agent
Added `ResourceDefinitions`, `ResourceNodeService`, `HarvestService`, and an additive three-tree prototype grove at the approved clear area around (35,54,95). Server owns lifecycle, health, range, cooldown, contention and reward commit.

## UI / UX Agent
Added harvest input/presentation controllers using the existing NotificationController for Wood reward feedback. UI never grants items or changes node health.
