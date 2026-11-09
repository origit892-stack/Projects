# File Ownership (enforced to prevent collisions)

- **Chief / Data layer (local 27B):** `src/shared/config/**` (JSON only), `test/*.py`, `docs/**`, meta files.
- **engineer (deepseek pool) — Track A (Server Gameplay):**
  `src/server/ServerMain.luau`, `src/server/RunState.luau`, `src/server/WaveDirector.luau`,
  `src/server/CombatService.luau`, `src/client/**` is NOT here.
- **engineer — Track B (Server Systems):**
  `src/server/EconomyService.luau`, `src/server/TowerService.luau`, `src/server/DraftService.luau`,
  `src/server/PersistenceService.luau`, `src/shared/ConfigLoader.luau`, `src/shared/Types.luau`.
- **engineer — Track C (Client UI/VFX):**
  `src/client/ClientMain.luau`, `src/client/HUDController.luau`, `src/client/BuildMenu.luau`,
  `src/shared/Remotes.luau`, `src/shared/EventBus.luau`, `src/shared/Locals.luau`.
- **Shared contract files** (`Types.luau`, `Remotes.luau`) may only be changed by the track that owns them; other tracks request a handoff.

Handoff rule: a track that needs a function from another track's file opens a handoff task; the owner implements + pushes; then the requester pulls and uses it. Merges to `main` only at stage completion, after CI (tests + luau-analyze) and Chief sign-off.
