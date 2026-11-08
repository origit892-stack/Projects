# Implement BunkerGame UI Foundation

This is implementation, not architecture design.

Follow rules 70-73 exactly.

## Preflight

Run:
```bash
tools/workflows/preflight.sh
bds analyze ui
bds review ui
```

Read:
- `default.project.json`
- `src/client/FarmingUI.client.lua`

Verify:
- `src/ReplicatedStorage` maps to `ReplicatedStorage`
- `src/StarterPlayer/StarterPlayerScripts` maps to `StarterPlayer/StarterPlayerScripts`

If either mapping is missing, STOP and report exact JSON evidence.

## Phase 1 only

Create only:
```text
src/ReplicatedStorage/UI/Tokens.luau
src/ReplicatedStorage/UI/Theme.luau
src/ReplicatedStorage/UI/Types.luau
src/ReplicatedStorage/UI/Components/Panel.luau
src/ReplicatedStorage/UI/Components/Button.luau
src/ReplicatedStorage/UI/Components/StatChip.luau
src/ReplicatedStorage/UI/Components/ProgressBar.luau
src/ReplicatedStorage/UI/Components/Notification.luau
src/ReplicatedStorage/UI/Controllers/UIController.luau
src/ReplicatedStorage/UI/Controllers/NotificationController.luau
src/StarterPlayer/StarterPlayerScripts/UIBootstrap.client.luau
```

Do not create other screens.
Do not delete or disable `src/client/FarmingUI.client.lua`.

Use Luau, `game:GetService()`, the exact component contracts, and the exact tokens.

Do not invent RemoteEvents.
Do not create a server UI manager.
Do not require server Scripts.

After editing:
```bash
bds ast <each changed .luau file>
tools/workflows/postflight.sh
```

Report exact files created, Roblox paths, require graph, BDS findings, Studio test steps, and unknowns.
