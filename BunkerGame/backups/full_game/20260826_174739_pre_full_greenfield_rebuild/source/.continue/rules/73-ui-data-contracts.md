---
name: BunkerGame UI data contracts
alwaysApply: true
---

# UI Data Contracts

## Confirmed farming contract

### UpdateUI
Direction: Server -> Client
Payload: `credits, seeds, crops, food`

### Notify
Direction: Server -> Client
Payload: `text`

### UpdateProgress
Direction: Server -> Client
Payload: `pct`

## Forbidden assumptions

Do not claim the UI can call local server functions such as:
- `getInventory`
- `getItem`
- `getState`
- `setupPlayer`
- `spawnZombieWave`

Do not treat server Scripts as ModuleScripts.

## Phase 1 approved data

Use only:
- Credits
- Seeds
- Crops
- FoodItems
- processing progress
- farming notifications

Do not integrate Scrap, Batteries, day/night, wave number, zombie count, power state, health, ammo, or hunger until their actual client-readable data source is inspected and documented.

The server remains authoritative.
Existing RemoteEvent names and payload order must remain unchanged during Phase 1.
