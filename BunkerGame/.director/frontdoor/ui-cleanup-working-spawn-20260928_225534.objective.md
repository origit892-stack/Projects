# Objective: BunkerGame — Remove HUD UI (keep weapons button), remove button glint, create a working spawn

## VERIFIED CONTEXT (do not re-derive; trust this)
- Project root: /Users/Ori/Documents/Projects/BunkerGame (Roblox/Luau, Rojo source-synced via default.project.json).
- The user runs the SOURCE-SYNCED project in Roblox Studio and presses Play to test the UI.
- `src/Workspace/` contains ONLY `ArgonProof.model.json` (a single MeshPart at Y=55). There is NO `GameWorld` Model, NO `SpawnLocation`s, NO `Runtime` Folder in the synced Workspace.
- `src/ServerScriptService/Game/ServerBootstrap.server.luau` runs a full service graph. `WorldService.Validate()` (src/ServerScriptService/Game/Services/WorldService.luau) asserts `Workspace.GameWorld` (Model) AND `Workspace.Runtime` (Folder) exist, plus 6 SpawnLocations, 8 stations, 12 plots, 18 trees, 6 scrap caches, 7 enemy spawns, 3 objectives, StableGround, PoweredLights, AudioAnchors (with SoundIds). Because `GameWorld` is absent, `bag:Init()`/`bag:Start()` fails, so ServerBootstrap kicks all players and re-raises the error.
- `Players.CharacterAutoLoads = false` is set in both `default.project.json` and ServerBootstrap. The custom `SpawnService` (which requires the full GameWorld) is the only spawn path.
- Net effect today: press Play -> server bootstrap fails -> no working spawn. The client UI still builds (ClientBootstrap -> UIController), so the user sees the full HUD + the blue weapons button.

## TASK 1 — Remove the unnecessary HUD UI, keep ONLY the weapons button
File: `src/StarterPlayer/StarterPlayerScripts/GameClient/UIController.luau`
- Keep the `ScreenGui` ("OutskirtsHUD") + `SafeAreaRoot` frame, and keep `_buildWeaponsButton()` fully intact (blue gradient tile, rifle, spider webs, spider, white "Weapons" label, hover/press/bob/web-breath/spider-crawl animations, and the click notification).
- Remove ALL other HUD elements from `_buildGui`: PhaseReadout, ObjectiveCard, ResourceReadout, SurvivalReadout (health + ration button), EquipmentHotbar, Reticle, TouchPrimary, InteractionPrompt, Notifications container, ConnectionStatus, and the entire ModalLayer (StationPanel + Header + Close + Content + Expiry).
- Remove the now-dead functions that only served the removed HUD: `_renderSnapshot`, `_renderTimers`, `_renderConnection`, `_renderInteraction`, `_rebuildPanel`, `_buildFarmPanel`, `_buildProcessorPanel`, `_buildShopPanel`, `_buildStoragePanel`, `_buildPowerPanel`, `_buildScrapPanel`, `_buildUpgradePanel`, `_panelText`, `_panelDivider`, `_panelAction`, `_stepper`, `_configureSelection`, `_openPanel`, `_closePanel`, `_clearPanelContent`, `_bindStaticButtons`, `_updateLayout`, `_updateReticlePosition`, `_onActionResult`, `_binding`, and the panel/objective/offer/upgrade/error copy tables that become unused (OBJECTIVES, ITEM_NAMES, STORAGE_ITEMS, OFFER_NAMES, UPGRADE_COPY, ERROR_MESSAGES) — remove only those that are truly unreferenced after cleanup.
- CRITICAL — InputController compatibility. `src/StarterPlayer/StarterPlayerScripts/GameClient/InputController.luau` calls these UI methods and they MUST still exist (make them safe no-ops where the backing UI was removed, so InputController never errors):
  - `SetCallbacks(callbacks)` — keep (store or ignore).
  - `SetPreferredInput(input)` — keep as a no-op (it previously called the removed `_renderSnapshot`).
  - `ShowPrompt(prompt, inputType)` — keep as a no-op.
  - `HidePrompt(prompt)` — keep as a no-op.
  - `SetPromptProgress(progress)` — keep as a no-op.
  - `IsPointerOverInteractiveUI()` — keep a minimal real implementation: return true only if the pointer is over the weapons button (the modal is gone). Used by InputController to suppress primary fire while hovering UI.
  - `ShowNotification(text, tone)` — KEEP fully working (the weapons button click uses it). Keep the Notifications container ONLY if ShowNotification needs a parent; if so, keep a minimal Notifications frame. Otherwise keep ShowNotification functional.
- Keep `_reducedMotion` detection (the weapons button animations respect it). Keep `Start()`/`Stop()` but simplify: Start builds the GUI (weapons button only) + wires reduced-motion change signal; Stop tears down connections/tweens/notifications and destroys the gui. Keep `self._refs.WeaponsCleanup` invocation in Stop.
- Do NOT change the weapons button's existing visuals. Do NOT remove the rifle/webs/spider/label/gradient.

## TASK 2 — Remove the diagonal glint that sweeps across the button on press
File: same `UIController.luau`, inside `_buildWeaponsButton()`:
- The diagonal line is the Frame named "Glint" (Size 16x96, Rotation=24, white, starts Visible=false). REMOVE its creation.
- In the `button.Activated` handler, REMOVE the glint sweep block: `glint.Visible = true`, `glint.Position = ...`, the `TweenService:Create(glint, ...)` sweep, and its `sweep.Completed` handler.
- KEEP the press animation (pressSize tween + release tween) and the hover animation. KEEP the "Glow" frame (full-size hover glow, BackgroundTransparency 1->0.84) — that is NOT the diagonal line; only the "Glint" frame is.

## TASK 3 — Create a working spawn location (press Play -> player spawns and can stand/move)
The full GameWorld is intentionally NOT built source-side yet (do NOT rebuild it — out of scope). Instead add a minimal, self-contained spawn and make the server gracefully fall back to it.

3a. Add a spawn to the source Workspace (so it syncs into the place).
- Create `src/Workspace/SpawnRoot.model.json` matching the EXACT Rojo model.json format already used by `src/Workspace/ArgonProof.model.json` (top-level `{"ClassName":"Model","Children":[...]}`, each child `{"Name":...,"ClassName":...,"Properties":{...}}`).
- Children:
  - A `SpawnLocation` named "PlayerSpawn": Anchored=true, CanCollide=false, Neutral=true, Enabled=true, Duration=0, Transparency=1, Size=[6,1,6], Position=[0,55,0].
  - A simple anchored ground `Part` named "TestGround" so the character stands instead of falling: Anchored=true, CanCollide=true, Size=[40,1,40], Position=[0,54.5,0], Material="Concrete". (Top surface at Y=55 matches the spawn.)
- These live OUTSIDE any GameWorld, so they do NOT affect `WorldService.Validate()` (which only inspects `gameWorld:GetDescendants()`) and do NOT interfere with the custom SpawnService (which only reads GameWorld spawns).

3b. Make `src/ServerScriptService/Game/ServerBootstrap.server.luau` gracefully handle the missing GameWorld.
- Near the top (after the existing `Players`/`ReplicatedStorage` locals and the existing `Players.CharacterAutoLoads = false` line), add:
  `local Workspace = game:GetService("Workspace")` and `local hasGameWorld = Workspace:FindFirstChild("GameWorld") ~= nil`.
- Wrap the ENTIRE existing full-bootstrap body (service modules, bag construction, handlePlayer, the `xpcall(bag:Init/Start)`, PlayerAdded/Removing connections, the existing-player loop, and BindToClose) inside `if hasGameWorld then ... end` UNCHANGED.
- Add an `else` branch = MINIMAL SPAWN MODE:
  - `Players.CharacterAutoLoads = true` (override the earlier false so Roblox spawns the player at the enabled SpawnLocation).
  - For each already-present player with no character, call `player:LoadCharacter()` (guarded by pcall).
  - `warn("[ServerBootstrap] Workspace.GameWorld not found. Minimal spawn mode: default SpawnLocation active; full service graph disabled.")`
  - Do NOT run the service graph, admission, or service teardown in this branch.
- The full-world path must remain byte-for-byte equivalent in behavior when `GameWorld` is present.

## VERIFICATION GATES
- GATE 1: `luau-analyze` on `UIController.luau` -> 0 SyntaxErrors. (TypeErrors from missing Roblox API definitions outside Studio are expected and acceptable.)
- GATE 2: Weapons button intact (gradient/rifle/webs/spider/label + hover/press/bob/web-breath/spider-crawl) and the "Glint" frame + its sweep are gone. No active references to removed refs (e.g. `self._refs.PhasePanel`, `self._refs.Hotbar1`, `self._refs.Modal`) remain.
- GATE 3: Every UI method called by InputController.luau still exists (SetCallbacks, SetPreferredInput, ShowPrompt, HidePrompt, SetPromptProgress, IsPointerOverInteractiveUI, ShowNotification).
- GATE 4: `SpawnRoot.model.json` is valid JSON and matches the ArgonProof.model.json Rojo format.
- GATE 5: `luau-analyze` on `ServerBootstrap.server.luau` -> 0 SyntaxErrors; full path unchanged when GameWorld present; minimal mode correct when absent.
- GATE 6 (RUNTIME): Requires Roblox Studio Play testing, which is NOT available to you autonomously. Mark GATE 6 = REQUIRES_USER_VERIFICATION and tell the user to press Play and confirm: (a) they spawn at the new location and can stand/move, (b) only the weapons button shows (no other HUD), (c) pressing the button no longer shows the diagonal glint.

## HARD CONSTRAINTS
- Do NOT rebuild the full GameWorld (60+ instances) — out of scope; the minimal spawn mode is the correct fix.
- Do NOT alter the full-world spawn behavior (SpawnService/WorldService) — preserve it exactly.
- Do NOT simplify the weapons button's existing visuals — only remove the glint.
- Preserve all public/network/data contracts (Remotes, NetTypes, Config, Definitions, ProfileSchema) unchanged.
- Never convert UNKNOWN/FAILED/BLOCKED/UNVERIFIED into PASS.

## DELIVERABLE / REPORT
- Modified: `src/StarterPlayer/StarterPlayerScripts/GameClient/UIController.luau`.
- Added: `src/Workspace/SpawnRoot.model.json`.
- Modified: `src/ServerScriptService/Game/ServerBootstrap.server.luau`.
- Report each gate's status honestly; explicitly flag GATE 6 as REQUIRES_USER_VERIFICATION.
