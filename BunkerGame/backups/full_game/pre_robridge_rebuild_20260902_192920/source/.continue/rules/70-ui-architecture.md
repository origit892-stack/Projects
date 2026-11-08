---
name: BunkerGame UI architecture
alwaysApply: true
---

# BunkerGame UI Architecture

This file is authoritative for UI architecture decisions.

Before any UI implementation:
1. Read `default.project.json`.
2. Verify that `src/ReplicatedStorage` maps to `ReplicatedStorage`.
3. Verify that `src/StarterPlayer/StarterPlayerScripts` maps to `StarterPlayer/StarterPlayerScripts`.
4. If either mapping is missing, stop and report the exact missing mapping. Do not invent one.

## Approved structure

```text
src/
├── ReplicatedStorage/
│   └── UI/
│       ├── Tokens.luau
│       ├── Theme.luau
│       ├── Types.luau
│       ├── Components/
│       │   ├── Panel.luau
│       │   ├── Button.luau
│       │   ├── StatChip.luau
│       │   ├── ProgressBar.luau
│       │   └── Notification.luau
│       └── Controllers/
│           ├── UIController.luau
│           └── NotificationController.luau
└── StarterPlayer/
    └── StarterPlayerScripts/
        └── UIBootstrap.client.luau
```

Do not create `src/client/UI`, `src/shared/UI`, a server UIManager, duplicate UIManager files, `MainUI.luau`, or a plain `Bootstrap.luau` intended to be a LocalScript.

## Script classes

- `UIBootstrap.client.luau` is a LocalScript.
- Plain `.luau` files under `src/ReplicatedStorage/UI` are ModuleScripts.

## Exact Roblox paths

When the mappings above are valid:
- `src/ReplicatedStorage/UI/Tokens.luau` -> `ReplicatedStorage.UI.Tokens`
- `src/ReplicatedStorage/UI/Theme.luau` -> `ReplicatedStorage.UI.Theme`
- `src/ReplicatedStorage/UI/Types.luau` -> `ReplicatedStorage.UI.Types`
- `src/ReplicatedStorage/UI/Components/Panel.luau` -> `ReplicatedStorage.UI.Components.Panel`
- `src/ReplicatedStorage/UI/Components/Button.luau` -> `ReplicatedStorage.UI.Components.Button`
- `src/ReplicatedStorage/UI/Components/StatChip.luau` -> `ReplicatedStorage.UI.Components.StatChip`
- `src/ReplicatedStorage/UI/Components/ProgressBar.luau` -> `ReplicatedStorage.UI.Components.ProgressBar`
- `src/ReplicatedStorage/UI/Components/Notification.luau` -> `ReplicatedStorage.UI.Components.Notification`
- `src/ReplicatedStorage/UI/Controllers/UIController.luau` -> `ReplicatedStorage.UI.Controllers.UIController`
- `src/ReplicatedStorage/UI/Controllers/NotificationController.luau` -> `ReplicatedStorage.UI.Controllers.NotificationController`
- `src/StarterPlayer/StarterPlayerScripts/UIBootstrap.client.luau` -> `StarterPlayer.StarterPlayerScripts.UIBootstrap`

## Bootstrap

```lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UI = ReplicatedStorage:WaitForChild("UI")
local UIController = require(UI.Controllers.UIController)
UIController.start()
```

Do not require server Scripts or local server functions.

## Existing farming networking

Confirmed server -> client events:
- `UpdateUI`
- `Notify`
- `UpdateProgress`

The client receives them through `OnClientEvent`.

`ProximityPrompt.Triggered` is not a RemoteEvent.

## Migration

Keep `src/client/FarmingUI.client.lua` working until the replacement is verified in Roblox Studio.
