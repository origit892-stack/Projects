# FND-002 Specialist Handoff

**Owner:** Inventory / Loot / Economy Agent

## Implementation
Created the canonical ItemDefinition type/registry boundary and an isolated server-authoritative InventoryService. The canonical service deliberately does not create, replace, read, or mutate Farming's legacy `Player.Inventory` Folder.

## Files changed
- `src/ReplicatedStorage/Shared/Inventory/ItemTypes.luau`
- `src/ReplicatedStorage/Shared/Inventory/ItemDefinitions.luau`
- `src/ServerScriptService/Foundation/Inventory/InventoryService.luau`

## Public APIs
- `ItemDefinitions.get/isDefined/getAll`
- `InventoryService.GetQuantity`
- `CanAdd` / `Add`
- `CanRemove` / `Remove`
- `GetSnapshot`

## Compatibility
The canonical registry is intentionally empty: no item catalog/content was authorized. Farming continues to own its current Seeds/Crops/FoodItems representation until a dedicated migration packet.

## Deferred
Currencies, economy transactions, persistence, Dealer/Trader, loot/chests, item content and Farming migration.
