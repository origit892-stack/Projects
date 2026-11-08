# BunkerGame UI Master Specification

## Goal
Replace fragmented UI with one coherent client-side system.

Visual direction: **Industrial Bunker Horror**.

## Architecture
- Bootstrap: `StarterPlayerScripts/UIBootstrap.client.luau`
- Reusable modules: `ReplicatedStorage/UI`
- Authoritative state: server systems
- UI consumes replicated state and confirmed server -> client remotes

## Phases

### Phase 1 — Foundation
Tokens, Theme, Types, Panel, Button, StatChip, ProgressBar, Notification, UIController, NotificationController, Bootstrap.

### Phase 2 — Farming migration
Replace visible farming HUD using new components, preserve existing farming remotes, verify in Studio, then remove old visual code only after parity.

### Phase 3 — Global HUD
Only after data sources are verified: day/night, wave, power/battery, survival stats.

### Phase 4 — Interaction screens
Only after each gameplay system is inspected: inventory, workbench/crafting, upgrades, shop, power, settings.

### Phase 5 — Horror overlays
Night warning, wave warning, power failure, critical state, death/respawn.

## Non-negotiable rules
- No invented systems.
- No invented Rojo mappings.
- No server-side UI controller.
- No requiring server Scripts.
- No client authority over trusted state.
- No deleting old farming UI before parity testing.
- Every phase gets preflight, implementation, AST validation, postflight, and Studio testing.
