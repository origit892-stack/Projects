# BunkerGame Pre-RoBridge Rebuild Backup Manifest

- **Timestamp:** `20260902_192920`
- **Reason:** Immutable recovery boundary immediately before any RoBridge-mediated modifications.
- **Source root:** `/Users/Ori/Documents/Projects/BunkerGame`
- **Backup root:** `/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/pre_robridge_rebuild_20260902_192920`
- **Source copy:** `/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/pre_robridge_rebuild_20260902_192920/source`
- **File count:** `33555`
- **Total source size:** `5.9G`
- **Source files (luau/lua/json):** `613`
- **Verification:** File lists match between source and backup; key file checksums verified identical.

## Studio State Captured

- **Place name:** `Bunker Game`
- **Place ID:** `129695090105158`
- **Game ID:** `8687457621`
- **Total descendants:** `5759`
- **Workspace children:** `Terrain`, `Camera`
- **Service counts:**
  - ServerStorage: 2850
  - ReplicatedStorage: 124
  - ServerScriptService: 23
  - Lighting: 6
  - StarterPlayer: 7
  - Workspace: 2
  - StarterGui: 0

## Included

Every file and symlink below `/Users/Ori/Documents/Projects/BunkerGame` at backup time, excluding:
1. `/Users/Ori/Documents/Projects/BunkerGame/backups/**` (recursive self-inclusion prevention)
2. `*.rbxlx` (historical place files, not current live state)

## Exclusions

1. `/Users/Ori/Documents/Projects/BunkerGame/backups/**` only, to prevent recursive self-inclusion.
2. `*.rbxlx` files are historical snapshots, not the current live place state.
3. Live Studio Terrain data is NOT in the filesystem - it exists only in the active Studio place.

## Integrity verification

- File count match: PASS (33555 = 33555)
- File list diff: PASS (no differences)
- Key file checksums verified:
  - `default.project.json`: `f0d6e62165e075f0f089bb59cb28ec3e4fcd32392915ab8ef8b72c96bafcd231`
  - `src/Workspace/GameWorld.model.json`: `444ef4835e70bdfb36949d98ef78b542b7bbb027b812a79a3c7a89d1ca9c4b9e`
  - `src/Lighting/init.meta.json`: `e366b28b108e750c3b3136f85c07e46cb9ff87791d6d6ed1777588fc82bf1e1c`
  - `src/ReplicatedStorage/Game/Config.luau`: `7acc96eac2f66bdde275dd72dd6abef1257fed736ee8891a206df01878cd8d9b`

## Studio/Terrain Backup Method

The Terrain data is NOT stored in the filesystem/Rojo source. It exists only in the active Studio place file.

**No safe RoBridge read-only export mechanism exists for the full place/terrain.**

The manual action required to create a recoverable Studio/Terrain backup:

1. In Roblox Studio, go to **File → Save As**
2. Save a copy of the current place to: `/Users/Ori/Documents/Projects/BunkerGame/backups/full_game/pre_robridge_rebuild_20260902_192920/studio_backup.rbxlx`
3. This preserves the Terrain and all in-place modifications

## Acceptance marker

`FILESYSTEM_BACKUP=PASS`
`STUDIO_TERRAIN_RECOVERABLE=BLOCKED_MANUAL_STUDIO_COPY_REQUIRED`
