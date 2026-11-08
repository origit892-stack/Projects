# LONG-RUN CHECKPOINT

## Master task
Full Game Presentation Rework / Creepy Survival Production Pass

## Current phase
PHASE 1 — Tree → Axe → Wood player-facing presentation implementation.

## Completed preflight work
- Foundation contracts and Survival Vertical Slice architecture approved.
- Canonical Tree → Axe → Wood authority path implemented and previously runtime-verified.
- HarvestHitSerial=4 and one complete harvest/respawn cycle previously verified.
- NewBunker forensic inventory completed; do not repeat.
- Player-height navigation/readability correlation pass completed; do not repeat.
- NewBunker screenshot Art Director audit request remains a separate visual-review deliverable; do not substitute raycasts for it.

## Durable Studio memory status
`game.ServerStorage.ZeroScript.Memory` was created successfully before this checkpoint.

## Current Studio mode
Edit mode. Play was stopped cleanly before Phase 1 filesystem work.

## Completed audits that must NOT be repeated
- NewBunker current-state forensic inventory.
- Source/live descendant-count reconciliation.
- Existing script-reference audit.
- Player-height navigation/line-of-sight correlation study.
- Previously completed Foundation and initial Survival architecture gates.

## Current source/live drift
Connected Studio NewBunker is authoritative for CURRENT visual audit state: 1,852 descendants. Filesystem NewBunker has 1,857 descendants. Five source-only Parts are absent from Studio:
1. `EnvironmentDetails.ConcreteMoistureAndRepairBreaks.BedroomLeakSheen`
2. `EnvironmentDetails.ConcreteMoistureAndRepairBreaks.ServiceRunoffSheen`
3. `EnvironmentDetails.ConcreteMoistureAndRepairBreaks.StorageDrainSheen`
4. `Lighting.EntranceAndServiceLighting.SouthConnectorPractical.DeadTubeEnd`
5. `Lighting.WorkAndMaintenanceLighting.WorkshopEntryFill.DeadTubeEnd`
Do not silently reconcile this drift.

## Phase 1 baseline discovered
- `ResourceNodeService` remains server authority for node state, validation, reward commitment and respawn.
- `InventoryService` remains canonical inventory authority.
- Existing validation rejects invalid node IDs, unknown nodes, inactive nodes, invalid player state, no axe, unowned axe, invalid tool, invalid node, out-of-range and rate-limited attempts.
- Current axe presentation is a primitive handle + rectangular metal head.
- Current tree presentation is primitive trunk + two block canopies.
- Current hit presentation is only a small trunk tilt.
- Current Wood reward already uses canonical inventory and a notification.
- Current grove contains only three authored prototype trees and services hard-code `PrototypeHarvestGrove`; Phase 1 must verify and, if necessary, adapt presentation to the real `ForestResourceRegion`/spawned forest resource trees without weakening authority.

## Phase 1 implementation checkpoint
- Recovered the Studio-only `ForestResourceSpawner` contract and promoted it into filesystem/Rojo source-of-truth.
- Added `ResourceNodeService.RegisterNode` so deterministic forest-spawned trees enter the same authoritative state/validation/reward pipeline as prototype trees.
- Harvest targeting and presentation now cover both `PrototypeHarvestGrove` and runtime `ForestResourceRegion`.
- Replaced the rectangular prototype axe with a multi-part field-axe silhouette including handle knob, metal poll/head and wedge blade.
- Added player-facing swing motion, whole-tree hit recoil, restrained wood-chip burst, localized wood-impact cue, harvest progress billboard, tree-fall presentation, canonical Wood total feedback and respawn rise/fade presentation.
- Authority remains server-side: ResourceNodeService validation and InventoryService reward commitment are unchanged in responsibility.

## Next exact implementation action
Build/sync the filesystem checkpoint into Studio, start a fresh Play session, verify real `ForestResourceRegion` registration and complete player-facing harvest QA on an actual `forest_tree_*` node, fixing any runtime defects before Phase 1 is marked complete.

## Authorized future phases
After Phase 1 specialist QA, continue without waiting for Director input through: full UI/UX rework; legacy UI cleanup; Old Bunker dependency migration and authorized removal; filesystem/Rojo NewBunker relocation; navigation/camera-clearance repair; major creepy NewBunker art rework; room storytelling; electrical/cable art; lighting/atmosphere; audio; VFX; exterior; forest/world presentation; performance review; technical/gameplay/UI QA; independent Visual Director review; review fixes; final integrated validation.

## Stop conditions
Stop only for a genuine blocker requiring manual Director/user action, or after the complete authorized Master Execution Pass is implemented and player-facing validation is complete. Phase transitions are not stop conditions.


## Phase 1 runtime QA - visual bootstrap diagnosis
- Fresh synced Studio verified the new ForestResourceRegion-aware HarvestController and upgraded 7-descendant Axe are live.
- Real forest_tree_001 authoritative harvest passed: four legal activations advanced HitSerial to 4, granted canonical Wood=3 exactly once, completed depletion/respawn, and returned Active at CycleSerial=2 with 100/100 health.
- ClientHitPulse reached 4, proving HarvestController feedback reception.
- HarvestVisualController source is synced/enabled but its expected BillboardGui was absent; added temporary durable diagnostic attributes to distinguish script bootstrap failure from attach-path failure on the next fresh Play run.


## Phase 1 visual streaming-race fix
- Root cause verified in fresh Client runtime: Workspace.StreamingEnabled=true and HarvestVisualController attempted all 39 resource models before their HitAnchor children had streamed in. The same trees had valid HitAnchor Parts moments later.
- Fixed presentation attachment to tolerate streamed model shells: it retries when HitAnchor arrives via ChildAdded and performs a bounded delayed retry. Authority/resource state logic is unchanged.


## PHASE 1 — VERIFIED COMPLETE
Fresh synced Studio/Play evidence on real `ForestResourceRegion.forest_tree_001`:
- ForestResourceRegion spawned 36 deterministic resource trees and registered them into ResourceNodeService.
- Upgraded Axe is live with 7 descendants.
- Four legal player activations produced HarvestHitSerial=4.
- Mid-harvest player-facing progress verified at health 50/100: HarvestProgress=0.5, BillboardGui enabled, Fill X scale=0.5, ClientHitPulse=2.
- Canonical reward committed exactly once: CanonicalWoodQuantity=3.
- Depletion/respawn completed and returned the same real forest node to Active, CycleSerial=2, health 100/100.
- Post-respawn visual state restored: trunk transparency 0 and harvest progress UI hidden.
- Streaming race discovered and fixed: with Workspace.StreamingEnabled, resource Model shells can replicate before HitAnchor children; HarvestVisualController now attaches on HitAnchor ChildAdded with bounded delayed retry. Fresh Play verified attachCount=39 and progress UI on all 36 forest trees.
- ResourceNodeService and InventoryService remain authoritative; anti-exploit validation responsibility was not moved client-side.

## Current phase
PHASE 2 — full UI/UX rework and legacy UI cleanup.

## Next exact implementation action
Audit the existing filesystem UI architecture and live legacy GUI dependencies, then implement the authorized cohesive creepy-survival HUD/screen presentation through the approved ReplicatedStorage/UI + UIBootstrap architecture while preserving gameplay state producers.


## Phase 2 implementation checkpoint
- Activated the approved ReplicatedStorage/UI + UIBootstrap path as the primary BunkerHUD owner.
- Replaced the dormant generic stats panel with a restrained creepy-survival status HUD: live humanoid vitals, canonical Wood quantity, canonical Axe readiness, and farming status bridge.
- Kept legacy FarmingUI temporarily active only to preserve its farming hotbar and processor billboard while migration is validated; destructive legacy removal is deferred until live dependency evidence is complete.
- InteractionPromptController remains independently bootstrapped.


## Phase 2 legacy dependency migration
- Live audit verified legacy `ScreenGui` only presents ReplicatedStorage DayCount/GamePhase/TimeLeft, all authored by GlobalManager. That state is now migrated into BunkerHUD CycleReadout.
- Live audit verified legacy `BunkerGui` contains no GuiObjects and only a GuiScript waiting on obsolete RemoteEvents/GroupTeleportEvent; its current runtime produces the known infinite-yield warning and no player-facing presentation. It is a removal candidate after the replacement HUD is revalidated.
- FarmingUI remains temporarily preserved because it still owns the active farming hotbar and FoodProcessor world progress billboard.


## Phase 2 HUD runtime fix
- Fresh Play verified CycleReadout live and synchronized to GlobalManager Day/GamePhase/TimeLeft.
- Found HUD Axe readiness could initialize before the server diagnostic attribute replicated even though the canonical axe Tool already existed. Readout now prefers the canonical quantity attribute when present and safely falls back to the axe_basic Tool contract during replication startup, then rebinds to attribute/tool changes.


## Phase 2 Axe readout correction
- Fresh runtime showed CanonicalAxeQuantity can transiently replicate as numeric 0 while the authoritative axe_basic Tool is already present in Backpack. The prior fallback only handled a missing attribute, so HUD still displayed MISSING.
- Corrected readiness semantics: positive canonical quantity is READY; otherwise a live axe_basic Tool contract also proves READY during bootstrap.


## Phase 2 Axe replication root-cause fix
- Source/live inspection confirmed the HUD logic itself was synced, but the Tool can enter Backpack before its ToolDefinitionId attribute is visible client-side. ChildAdded therefore evaluated MISSING and no later signal refreshed it.
- HUD now watches ToolDefinitionId attribute replication on every Tool in Backpack/Character and includes bounded startup refreshes. This preserves canonical quantity as the preferred proof while making bootstrap presentation streaming/replication-safe.


## Phase 2 primary HUD live verification PASS
- Fresh Play verified BunkerHUD, CycleReadout, live 100/100 vitals, Wood readout, and FIELD AXE READY against a real axe_basic Tool.
- Axe bootstrap replication race is resolved.
- Legacy ScreenGui state has a verified replacement path in BunkerHUD. Legacy BunkerGui remains confirmed presentation-empty/obsolete; FarmingUI remains preserved pending farming-specific migration.

## Next exact implementation action
Complete farming-specific presentation migration into the approved UI architecture, then retire only the individually verified obsolete legacy StarterGui artifacts and run fresh UI regression QA before continuing to old-bunker dependency migration.


## Phase 2 farming presentation migration implementation
- BunkerHUD now owns farming Credits/Seeds/Crops readouts and processor progress feedback through the existing FarmingRemotes contract.
- Farming server authority/world interactions are unchanged. Legacy FarmingUI remains present until fresh runtime verifies replacement bindings before any retirement.


## Phase 2 verified legacy retirement
- Fresh replacement-HUD runtime verified farming readouts (Credits=0, Seeds=5, Crops=0), processor progress surface, cycle readout, vitals, Wood, and Axe READY.
- `BunkerGui` is now excluded from the Rojo project mapping: live audit proved it has no GuiObjects and only an obsolete GuiScript blocked forever on missing ReplicatedStorage.RemoteEvents.
- `ScreenGui` is now excluded from the Rojo project mapping: its only Day/GamePhase/TimeLeft presentation has been migrated and freshly verified in BunkerHUD CycleReadout.
- The underlying `.rbxm` files remain on disk as non-mapped legacy evidence; they were not destructively deleted.
- FarmingUI remains mapped temporarily because its world-space FoodProcessor billboard has not yet been independently verified through the replacement path.


## Phase 2 legacy mapping correction
- Rojo sourcemap evidence proved `StarterGui.$path = src/StarterGui` recursively mapped the legacy `.rbxm` files despite their absence as explicit JSON children.
- Corrected retirement non-destructively by moving only the two individually audited legacy artifacts (`BunkerGui.rbxm`, `ScreenGui.rbxm`) to `docs/legacy-assets/StarterGui/`, outside the mapped source tree.
- This preserves forensic evidence while preventing those obsolete GUIs/scripts from entering fresh builds.


## Phase 2 Axe HUD robustness correction
- A later fresh session reproduced a stale MISSING readout while live Backpack inspection proved an axe_basic Tool was present.
- Removed the presentation assumption that the tool must be named exactly `Axe`; readiness now scans all Character/Backpack Tools for the durable `ToolDefinitionId=axe_basic` contract and performs one additional bounded startup refresh.
- This is presentation-only and does not change server ownership or harvest validation.


## Phase 2 latest fresh runtime checkpoint
- Fresh Play after contract-scan fix verified BunkerHUD, CycleReadout, FarmingReadout, and FIELD AXE READY with a live ToolDefinitionId=axe_basic contract.
- Legacy ScreenGui is absent in fresh runtime, confirming its archival retirement succeeded.
- Legacy BunkerGui still appears in the currently open Studio place despite being absent from the fresh filesystem sourcemap; this is confirmed source/live drift, not a filesystem mapping failure. Its obsolete GuiScript still produces the RemoteEvents infinite-yield warning. Do not claim it retired from the connected place until Studio is reconciled through the normal Rojo workflow.
- FarmingUI remains intentionally live pending processor-world-progress replacement verification.


## Phase 3 old-bunker dependency forensics
- Fresh server runtime verified NewBunker at pivot (-1.5, 61.5, 70.25), with bounds approximately X[-52,49], Y[52.8,70.2], Z[0.5,140].
- Canonical zombie entrance target resolves to NewBunker.CompositionMarkers.FutureBunkerDoorMarker at (0,54.1,21.2); entrance targeting no longer depends on legacy bunker geometry.
- BatteryButton, Processor, Upgrade table, and Weapon Workbench all overlap the NewBunker bounds and are legacy-world collision/presentation conflicts.
- farm, ZombieSpawns, and Scrap piles are outside NewBunker bounds and remain protected independent world systems.
- NewBunker currently reports 9 enabled ProximityPrompts in fresh server runtime; this differs from the prior durable 8-prompt baseline and must be audited before any legacy-object retirement.
- No destructive old-world removal is authorized from overlap evidence alone; exact gameplay dependencies and the ninth prompt must be resolved first.


## Phase 3 legacy gameplay dependency audit
- The ninth NewBunker prompt is intentional and separate from the eight custom interaction prompts: `FutureBunkerLightsControlMarker.BunkerPowerPrompt` is a Default-style RESTORE POWER prompt owned by BunkerPowerService. The prior eight-custom-prompt baseline remains intact.
- Legacy BatteryButton still owns a live 20-credit -> +1 Batteries purchase loop.
- Legacy Processor still owns live Scrap -> Credits conversion at 5 Credits per Scrap. This is distinct from the farming FoodProcessor.
- Legacy Upgrade table still owns a 100-credit HarvestPower=2 upgrade.
- Legacy Weapon Workbench still owns a 200-credit GunDamage +10 upgrade loop.
- These four overlapping legacy objects therefore cannot be removed as dead geometry. Their gameplay behavior must first be migrated to NewBunker interaction seams or replacement services, then independently verified before archival/removal.


## Phase 3 legacy gameplay migration implementation
- Added narrow `LegacyBunkerGameplayService` compatibility ownership for the four verified legacy loops without refactoring GlobalManager's legacy economy boundary.
- Existing NewBunker interaction models now carry explicit GameplayTargetId adapters: battery purchase, Scrap processor, HarvestPower upgrade, and GunDamage upgrade.
- BunkerInteractionService preserves its server distance/cooldown/custom-prompt validation and delegates only explicit GameplayTargetId interactions to the owning compatibility service.
- Player-facing NewBunker prompt labels now expose the migrated operations and original prices/conversion.
- Legacy world objects remain mapped until fresh runtime proves all replacement contracts before archival.

## Phase 3 continuation recovery — 2026-08-20
- Bunker Game reopened in connected Studio in Edit mode.
- Filesystem root verified at `/Users/Ori/Documents/Projects/BunkerGame`.
- Rojo 7.7.0 verified; existing `rojo serve default.project.json --port 34872` process is active.
- Filesystem Phase 3 implementation recovered without recreation: `LegacyBunkerGameplayService.luau` exists and BunkerInteractionService delegates explicit GameplayTargetId interactions through it.
- Filesystem NewBunker contains all four intended GameplayTargetId values: `legacy_battery_station`, `legacy_weapon_upgrade`, `legacy_harvest_upgrade`, `legacy_scrap_processor`.
- Fresh Edit DataModel reconciliation proves the implementation is mapped into connected Studio: LegacyBunkerGameplayService is a live ModuleScript and all four target models carry the expected IDs.
- All four migrated station prompts are live, Enabled and Custom style in Edit state with migrated labels/prices.
- Phase 3 runtime behavior is NOT yet marked PASS; fresh Play verification remains required for authoritative mutations, rejection paths, prototype interaction regression, and console evidence.

## Phase 3 runtime verification and legacy retirement checkpoint
- Fresh Play loaded `LegacyBunkerGameplayService` and all four NewBunker GameplayTargetId adapters from current Studio mapping.
- Fresh server-authoritative compatibility QA passed battery insufficient-credit rejection and 20-credit purchase, Scrap empty rejection and 3 Scrap -> 15 Credits conversion, HarvestPower upgrade to 2 plus duplicate-upgrade rejection, and GunDamage 20 -> 30 plus insufficient-credit rejection.
- Battery station additionally passed the real NewBunker custom-prompt input path end-to-end: Credits 25 -> 5, Batteries 0 -> 1, GameplayResultSerial=1, result `BATTERY_PURCHASED`, Success feedback.
- All eight original NewBunker custom prompts remain present, enabled, Custom style, and attached to InteractionAnchor parts. The separate BunkerPowerPrompt remains the intentional ninth prompt.
- Personal locker passed real keyboard interaction regression: PrototypeOpen=true, FeedbackSerial=1, Success, ActionText=CLOSE.
- Crate/remaining-station keyboard automation after Play-only teleport exposed stale custom-prompt focus; direct server-authoritative handler QA passed, but no fabricated end-to-end prompt PASS is claimed for those targets from that automation path.
- Fresh runtime found no Workspace.BunkerDoor, BunkerLights, BunkerSofa, `Bunker walls`, or DoorShop objects. Current spawned BunkerZombie clones are marked EntranceTargetMigrated and target `Workspace.Rebuild.NewBunker.CompositionMarkers.FutureBunkerDoorMarker`.
- Binary zombie templates still contain the legacy `BunkerDoor` string internally; runtime migration disables the legacy door-aware clone scripts and supplies the durable NewBunker entrance target. Template binaries remain preserved.
- The four overlapping legacy world objects BatteryButton, Processor, Upgrade table, and Weapon Workbench are superseded by verified NewBunker compatibility contracts and are archived outside the mapped Workspace source tree under `docs/legacy-assets/Workspace/phase3-retired/`.
- Protected farm, Scrap piles, ZombieSpawns, Grassblox, and zombie templates are not removed.

## Current phase
PHASE 4 — filesystem/Rojo NewBunker relocation to the intended old-bunker location, followed immediately by navigation/camera-clearance repair.

## PHASE 4 — VERIFIED NO-OP RELOCATION
- Director/world documentation authorizes relocation to the intended old-bunker location but contains no independent destination coordinate or transform that would justify an invented offset.
- Preserved Phase 3 runtime evidence shows the legacy BatteryButton, Processor, Upgrade table, and Weapon Workbench occupied positions inside the current NewBunker footprint before retirement.
- Current NewBunker bounds are approximately X[-52,49], Y[52.8,70.2], Z[0.5,140], with its entrance contract at FutureBunkerDoorMarker (0,54.1,21.2).
- NewBunker functional reservation markers are already co-located with the retired old-bunker functional footprint: FutureBatteryButtonMarker (29.58,58.1,90), FutureProcessorMarker (25.4,54.18,75.8), FutureWeaponWorkbenchMarker (-31,54.1,48), FutureUpgradeTableMarker (-29.5,54.1,69).
- No authoritative evidence supports another translation/rotation. Moving the bunker would therefore be speculative and could violate protected farm/Scrap/ZombieSpawns/world boundaries.
- Phase 4 is consequently a verified no-op: filesystem/Rojo NewBunker remains at its existing canonical transform rather than receiving an invented relocation.

## Current phase
PHASE 5 — navigation and camera-clearance repair on the canonical NewBunker placement.

## PHASE 5 — NAVIGATION / CAMERA CLEARANCE VERIFIED COMPLETE
Fresh Play-mode traversal and position verification established:
- Upgrade room contains intentional machine/rack footprints but retains usable player routes.
- Real character traversal passed Upgrade -> Common Hub -> Entrance.
- Real character traversal passed Common Hub -> Power Room -> North Portal -> Service Connector -> Farm Service.
- North Portal crossing was verified from the character's actual HumanoidRootPart position, not from character_navigation Success alone: the player reached z=99.27 near the Service target, 1.11 studs from the requested point.
- Farm Service was likewise verified from actual runtime position: target distance 1.13 studs.
- Common Hub default-camera distance was approximately 12.5 studs.
- A transient camera compression to approximately 1.14 studs occurred while passing PowerRoomShell.NorthWallSegment03, but after crossing the North Portal camera distance returned to approximately 12.5 studs and at Farm Service remained approximately 9.67 studs. This does not justify destructive geometry modification.
- No permanent navigation/camera geometry fix was required from the verified routes.
- Runtime console still contains pre-existing sound asset-type failures for rbxassetid://9120384891 and the known Studio-only legacy BunkerGui RemoteEvents infinite-yield drift. These are not counted as Phase 5 navigation failures and remain cleanup targets for the continuing master pass.

## Current phase
PHASE 6+ — major creepy NewBunker environment-art / storytelling / electrical / lighting / audio / restrained VFX / exterior and world-presentation pass.

## Next exact implementation action
Inventory the existing mapped NewBunker environment-art, electrical, lighting, audio/VFX and storytelling layers by room, identify concrete weak/redundant presentation areas, then implement the first filesystem/Rojo art packet without disturbing verified gameplay contracts or navigation clearance.

## Phase 6 service-exit storytelling runtime verification
- NewBunker generator nondeterminism was traced to direct iteration of `portal_owner_sides` as a `frozenset`; architecture generation now emits portal frames in deterministic south -> north -> west -> east order while preserving ownership and geometry semantics.
- Two consecutive generator runs are byte-identical; Rojo build and `git diff --check` pass.
- `ServiceExitEvacuationStory` is builder-owned and canonical in filesystem source: exactly one model, 17 BaseParts, all non-colliding, non-touching, and non-queryable.
- Connected Studio contained one exact duplicate sibling from prior Rojo live drift. Structural signatures were verified identical before removing only the redundant Studio copy; Edit state then contained one canonical story model.
- Fresh Play runtime verified exactly one `ServiceExitEvacuationStory`, 17 parts, with zero CanCollide/CanTouch/CanQuery parts.
- Player-facing traversal reached the Service Exit target at approximately (21, 56.5, 115) within 1.22 studs; local overlap found no collidable blockers and the Custom camera retained approximately 10.28 studs of camera distance.
- Runtime console showed no new Phase 6 regression. Remaining warnings are the already-known legacy `rbxassetid://9120384891` asset-type failure and Studio-only legacy `BunkerGui.GuiScript` RemoteEvents infinite-yield drift.
- Phase 6 service-exit storytelling packet is runtime-verified and cleared for continuation of the authorized Master Execution Pass.

## Post-Phase-6 legacy warning cleanup
- The invalid FoodProcessor `ProcessSfx` using `rbxassetid://9120384891` was removed from filesystem-owned `src/server/FarmingSystem.server.lua`; processing gameplay logic was preserved and no unverified replacement audio was invented.
- Canonical Rojo 7.7.0 build passed after the cleanup, and filesystem search confirmed no remaining `9120384891` or `ProcessSfx` references.
- Fresh Play runtime verified the previous asset-type sound failure is gone while FarmingSystem still builds 15 plots and FoodProcessor and FarmingUI still loads.
- `StarterGui.BunkerGui` was confirmed as Studio-only source/live drift: it was absent from filesystem/sourcemap and contained only the obsolete `GuiScript` LocalScript responsible for the `ReplicatedStorage:WaitForChild("RemoteEvents")` infinite-yield warning.
- Only that verified stale `BunkerGui` ScreenGui was removed from connected Studio Edit state; `FarmingUI` was explicitly preserved.
- Final fresh Play console after both cleanups contains only normal startup lines: FarmingSystem plots/FoodProcessor, client hello, and FarmingUI loaded. The prior broken-sound and legacy-BunkerGui warnings are both absent.

## Phase 6 restrained environmental VFX runtime verification
- Added restrained runtime-only NewBunker environmental VFX through filesystem/Rojo ownership: one SparseWaterDrip at the Service Exit water pool, one LowServiceMist at the service wet-sheen area, and two GeneratorExhaustHaze emitters at the diesel generator exhaust caps.
- Initial fresh Play exposed exact Studio/Rojo live duplicate drift: two source-identical BunkerEnvironmentalVFX scripts caused every attachment/emitter to instantiate twice. Only the verified redundant Studio Edit copy was removed; filesystem source remained authoritative.
- Fresh Play after reconciliation verified exactly one BunkerEnvironmentalVFX controller, four VFX attachments, and four ParticleEmitters: SparseWaterDrip=1, LowServiceMist=1, GeneratorExhaustHaze=2.
- Final runtime console is clean: FarmingSystem built 15 plots and FoodProcessor, client startup completed, and FarmingUI loaded with no warnings/errors.
- Restrained VFX packet is runtime-verified and cleared for continuation of the Phase 6+ presentation pass.

## Visual QA capture workflow — 2026-08-20
- The proven macOS Playtest Video Capture pipeline is installed under `tools/visual_qa/`; existing `record_playtest.sh`, `list_captures.sh`, and `extract_frames.sh` remain unchanged after contract inspection found no concrete defect.
- `tools/visual_qa/visual_qa.sh` is the canonical ZeroScript/agent interface for record, list, frames, latest, and verify operations with stable machine-readable markers.
- The existing system capture was externally verified to contain real Roblox Studio Play pixels. Captures remain evidence only; filesystem/Rojo remains permanent game source-of-truth.
- Pixel-level MP4 review is performed by the external Director unless the active execution model genuinely has access to the video pixels. Video capture does not replace Studio runtime inspection, Technical QA, Gameplay QA, BDS, AST/Rojo validation, or independent review.
- Required remaining Master Pass video milestones: POST_PHASE6_BUNKER, POST_LIGHTING_ATMOSPHERE, POST_EXTERIOR_REWORK, POST_FOREST_WORLD, POST_UI_POLISH, FINAL_INTEGRATED_PLAYTEST. Review MP4s are retained under `visual-qa/captures/` without overwriting prior evidence.
- Exact Phase 6 resume point: filesystem generation contains one deterministic `Corridors.ServiceElectricalContinuity` with exactly 8 noninteractive Parts; build/postflight passed. A prior live Studio duplicate was verified structurally identical and removed from live drift. Fresh Play after reconciliation now verifies exactly one runtime copy, 8 Parts, CanCollide=false, CanTouch=false, CanQuery=false. Durable source remains the singleton filesystem/Rojo generator; continuing Phase 6 must verify Edit/live reconciliation rather than treating Studio-only deletion as source.

## Phase 6 silhouette / room-identity packet runtime verification
- Added two filesystem/Rojo-owned presentation-only silhouette groups: `UpgradeArea.HydraulicAccumulatorBank` and `Storage.EmergencySupplyNest`, complementing the verified `Corridors.ServiceElectricalContinuity` packet.
- Generator output is deterministic across consecutive runs. Source QA verifies HydraulicAccumulatorBank=10 BaseParts, EmergencySupplyNest=10 BaseParts, and ServiceElectricalContinuity=8 BaseParts.
- Canonical Rojo 7.7.0 build succeeded through `/Users/Ori/.aftman/bin/rojo`; the broken `/usr/local/bin/rojo` npm shim is not the project toolchain.
- Initial Studio reconciliation exposed exact duplicate live copies of the two new silhouette groups. Each duplicate pair was independently verified structurally identical before removing only the redundant Edit copy; filesystem source remained authoritative.
- Fresh Edit reconciliation then verified exactly one HydraulicAccumulatorBank, one EmergencySupplyNest, and one ServiceElectricalContinuity.
- Fresh Play runtime verified the same singleton state with exactly 28 BaseParts total: HydraulicAccumulatorBank=10, EmergencySupplyNest=10, ServiceElectricalContinuity=8. All 28 are presentation-only with CanCollide=false, CanTouch=false, and CanQuery=false.
- Fresh runtime console is clean: FarmingSystem built 15 plots and FoodProcessor, client startup completed, and FarmingUI loaded with no warnings or errors.
- Phase 6 remains active. Continue the major art rework toward stronger silhouette, material variation, depth, purposeful props, believable infrastructure, environmental storytelling, lighting hierarchy, and distinct room identity without weakening verified gameplay seams or circulation.

## Phase 6 shop / entrance silhouette runtime verification
- Added filesystem/Rojo-owned `ShopMechanicalCanopy` and `EntranceDefenseSilhouette` silhouette packets; deterministic generation, source QA, canonical Rojo 7.7.0 build, and postflight/BDS passed.
- Studio reconciliation verified each packet as a singleton after exact duplicate live drift was removed; filesystem remained authoritative.
- Fresh Play verified `ShopMechanicalCanopy` = 1 model / 8 presentation-only Parts and `EntranceDefenseSilhouette` = 1 model / 8 presentation-only Parts, with zero CanCollide/CanTouch/CanQuery parts.
- Previously verified Phase 6 packets remained intact in the same fresh Play: `EmergencySupplyNest` 1/10, `HydraulicAccumulatorBank` 1/10, and `ServiceElectricalContinuity` 1/8, all presentation-only.
- Fresh runtime console contained normal FarmingSystem/FarmingUI startup only; the live-edit join message is informational and no gameplay/runtime warning or error was present.
- Phase 6 remains active; next work continues the major bunker art rework toward the POST_PHASE6_BUNKER capture gate.

## Phase 6 Common/Power reconnect + stale BunkerGui reconciliation
- Freshly rediscovered connected Studio as Bunker Game placeId 129695090105158; Edit DataModel was available and NewBunker was present.
- Fresh Edit reconciliation verified singleton filesystem/Rojo state: CommonVentilationDrop=1/8 Parts, GeneratorCoolingManifold=1/10 Parts, ServiceElectricalContinuity=1/8 Parts; all verified presentation-only with zero CanCollide/CanTouch/CanQuery parts.
- This confirms the earlier ServiceElectricalContinuity duplicate was stale live Studio state rather than a second filesystem generator occurrence.
- Canonical project Rojo remains /Users/Ori/.aftman/bin/rojo, version 7.7.0, serving default.project.json on port 34872. The unrelated broken /usr/local npm Rojo shim was not modified.
- StarterGui.BunkerGui was re-confirmed absent from filesystem, default.project.json, and sourcemap. Live Studio contained exactly the previously identified stale ScreenGui with one obsolete GuiScript; only that verified Studio-only drift was removed and FarmingUI was preserved.
- Because the synchronous MCP Play launcher remained pending, Play was started through a foreground Roblox Studio F5 keyboard event. Fresh Studio state then exposed Client/Server DataModels normally.
- Fresh Play regression verified ServiceElectricalContinuity=1/8, HydraulicAccumulatorBank=1/10, EmergencySupplyNest=1/10, CommonVentilationDrop=1/8, GeneratorCoolingManifold=1/10; all 46 packet Parts had zero CanCollide/CanTouch/CanQuery regressions.
- Fresh Play also verified BunkerGui absent from both StarterGui and PlayerGui. Runtime game output contained normal FarmingSystem/FarmingUI startup only; the remaining Assistant-plugin version warning is Roblox tooling output, not a game regression.
- Phase 6 remains active. Continue major art rework toward POST_PHASE6_BUNKER; do not claim pixel-level visual approval before external Director MP4 review.

## Phase 6 Bedroom / Workshop silhouette packet runtime verification
- Added filesystem/Rojo-owned `Bedroom.BedroomVentilationRadiator` (9 presentation-only BaseParts) and `Workshop.WorkshopExtractionArm` (8 presentation-only BaseParts) to strengthen room silhouette with cylindrical/rotated industrial forms rather than generic box clutter.
- Both packets are outside the nearby Bedroom locker and Weapon Workbench interaction seams and preserve the established circulation intent.
- Generator output was byte-deterministic across consecutive runs; source QA, postflight/BDS, and canonical Rojo 7.7.0 build passed.
- Initial Edit reconciliation exposed two exact structural copies of each new packet. Each pair was independently verified structurally identical before only the redundant live copy was removed; filesystem/Rojo remained authoritative. Subsequent Edit QA remained singleton.
- Fresh Play runtime verified BedroomVentilationRadiator=1/9 and WorkshopExtractionArm=1/8 with zero CanCollide/CanTouch/CanQuery parts.
- Fresh Play also verified BedroomPersonalUtilityLocker retains enabled PrototypeLockerPrompt at MaxActivationDistance=7 and WeaponWorkbenchInspectionPoint retains enabled InspectStationPrompt at MaxActivationDistance=8.
- Runtime game output showed normal FarmingSystem/FarmingUI startup and normal Wave 1 gameplay; the Roblox Assistant plugin-version warning is tooling-only.
- Phase 6 remains active; pixel-level visual approval is still reserved for external Director review of the milestone MP4.

## POST_PHASE6_BUNKER Director artifact
- Canonical player-facing Phase 6 capture created: `visual-qa/captures/2026-08-21_00-23-30_POST_PHASE6_BUNKER.mp4` (2,005,646 bytes).
- Capture was recorded from a fresh Play session using normal player-height runtime movement. Walkthrough covered exterior/entrance approach, Common Hub, residential route/Bedroom, Workshop, Upgrade, Storage, Power, and Service/Farm route.
- Runtime traversal to Service and Farm Service succeeded during the recorded session.
- Direct CharacterNavigation attempts into the Shop target at approximately (25,56.5,54) failed even after successfully reaching the adjacent East Utility waypoint. This is recorded as a navigation observation requiring diagnosis; it is not silently treated as a Phase 6 visual failure and no geometry was changed during capture.
- This MP4 is a Director review artifact only. No pixel-level Visual Director PASS is claimed by the execution agent.
- Phase 6 milestone capture is complete; Master Execution Pass continues into lighting/atmosphere and subsequent authorized milestones.

## POST_LIGHTING_ATMOSPHERE Director artifact
- Conservative global atmosphere pass authored in filesystem/Rojo source: Atmosphere Density=0.22, Offset=0.12, Color=(0.66,0.69,0.70), Decay=(0.30,0.35,0.39); Bloom Intensity=0.32, Threshold=1.65, Size=18.
- Postflight/BDS and canonical Rojo 7.7.0 build passed.
- Fresh Edit reconciliation verified the exact authored Atmosphere/Bloom values were live in Studio.
- Fresh Play runtime verified the same values plus NewBunker local-light budget=27, shadow-light budget=8, SparseWaterDrip=1, LowServiceMist=1, GeneratorExhaustHaze=2, and four expected VFX attachments.
- Runtime console showed normal Farming/Wave output and the known Roblox Assistant tooling warning; no lighting/atmosphere gameplay regression was observed.
- Canonical lighting/atmosphere capture created: `visual-qa/captures/2026-08-21_00-36-25_POST_LIGHTING_ATMOSPHERE.mp4` (1,362,027 bytes).
- Capture traversed Entrance/Common, Bedroom, Workshop/Upgrade, Power, and Service/Farm at player height.
- MP4 is a Director review artifact only; no pixel-level Visual Director PASS is claimed.

## DIRECTOR HOTFIX — mandatory Play/capture lifecycle
- NO PLAY SESSION MAY BE LEFT RUNNING AFTER QA OR CAPTURE.
- Every Play operation is now a hard lifecycle gate: Start Play -> verify Play -> perform only intended runtime QA/capture -> Stop Play -> verify `Current Studio Mode: Edit` and `Available DataModels: Edit` -> attempt to restore the existing Google Chrome/ChatGPT window -> continue.
- If Stop does not return Edit, Stop is retried and Studio state is re-verified before any permanent/source work.
- Filesystem edits, builders, docs, BDS, Rojo builds, source analysis, planning, phase transitions, long shell operations, and waiting are forbidden while Play remains active.
- Capture shell timeout does not authorize a duplicate recording or indefinite Play: inspect the existing ffmpeg process, let/stop the intended recording as appropriate, verify its MP4, then immediately Stop Play and verify Edit.
- `tools/visual_qa/visual_qa.sh finish` now assists with restoring Google Chrome focus after verified Edit; it explicitly does not claim to verify Roblox Studio mode.
- Legacy zombie/wave accumulation is therefore bounded by keeping runtime sessions as short as practical; any temporary isolation used for visual QA must remain Play-only and disappear on Stop.
- Interrupted checkpoint remains POST_EXTERIOR_REWORK; completed earlier milestones are not restarted.


## POST_EXTERIOR_REWORK Director artifact
- Exterior landmark packet passed deterministic generation, source QA, postflight/BDS, and canonical Rojo 7.7.0 build.
- Fresh Edit reconciliation removed only one independently verified exact live duplicate of `ExteriorUtilityLandmarks`; canonical filesystem/Rojo source remained authoritative.
- Fresh runtime verified exactly one `ExteriorUtilityLandmarks` model with 11 expected BaseParts, `ServiceVentStack` and `EntranceSignalMast` present, presentation parts non-colliding/non-touching/non-queryable, and the intentional MastFoot collision retained.
- Player traversal passed both the main entrance approach and service exterior approach.
- POST_EXTERIOR_REWORK recording used one capture process only. The shell idle-timeout was treated correctly: the existing ffmpeg process was inspected and no duplicate recording was started.
- Player-facing recording activity ended, Play was explicitly stopped immediately, and Studio was authoritatively verified back in Edit before capture-file inspection or further source work.
- Google Chrome/ChatGPT foreground restoration then passed through `visual_qa.sh finish`.
- Canonical capture: `visual-qa/captures/2026-08-21_09-58-18_POST_EXTERIOR_REWORK.mp4` (1,229,290 bytes). Raw evidence is retained separately.
- MP4 is Director evidence only; no pixel-level Visual Director PASS is claimed by the execution agent.
- Permanent lifecycle rule remains in force for every subsequent Play session: Start -> verify Play -> intended runtime work only -> Stop -> verify Edit -> restore Chrome -> continue.

## Current phase
POST_FOREST_WORLD — forest/world presentation rework and milestone capture. Completed bunker, lighting/atmosphere, and exterior phases are not restarted.

## POST_FOREST_WORLD Director artifact
- Forest/world presentation upgraded without changing harvest authority: each authored prototype tree retains exactly one canonical `Trunk`, one `HitAnchor`, and the existing ResourceNodeId/ResourceDefinitionId contract, while adding an 8-part presentation-only silhouette packet with bark core, branches, irregular canopy clusters, and root flares.
- Runtime forest spawning remains deterministic from SEED=42042 with 36 trees and the existing spacing/origin/radius contract. Added scale/canopy variation is deterministic presentation-only and does not alter resource IDs, health, reward, cooldown, or interaction semantics.
- Canonical source validation and Rojo 7.7.0 build passed. The BDS inventory still invokes the known broken `/usr/local` npm Rojo shim internally and reports EACCES there; the canonical `/Users/Ori/.aftman/bin/rojo` build succeeds and remains authoritative.
- Edit reconciliation found duplicated live presentation children caused by source/live drift: exactly two structurally identical copies of each of the 8 new presentation names on each of the 3 prototype trees. All 24 duplicate pairs were independently verified exact before removing only one redundant live copy per pair. Trunk, HitAnchor and attributes were untouched.
- Fresh Edit state then verified 8 presentation parts, one Trunk and one HitAnchor per prototype tree.
- Fresh runtime presentation QA verified 36 forest trees, exactly 8 new presentation parts per tree, zero presentation collisions, valid non-colliding HitAnchors and collidable canonical Trunks.
- An initial direct late `require(ResourceNodeService).GetState()` QA returned zero registered nodes despite correct tree presentation. Follow-up evidence proved this was a QA/module-identity artifact rather than gameplay failure: all 36 runtime trees carry valid ResourceNodeId/ResourceDefinitionId plus `HarvestState=Active`, `HarvestHealth=100`, `HarvestMaxHealth=100`, and `CycleSerial=1`, written by the authoritative ResourceNodeService registration path.
- POST_FOREST_WORLD capture completed as `visual-qa/captures/2026-08-21_10-10-57_POST_FOREST_WORLD.mp4` (1,067,341 bytes). Six review frames were extracted at 12-second intervals.
- The recording shell timeout was handled without duplicate capture. After recording completed, Play was explicitly stopped, Edit was verified, and Google Chrome/ChatGPT focus restoration passed before artifact inspection/frame extraction.
- Capture and extracted frames are Director evidence only; no pixel-level Visual Director PASS is claimed by the execution agent.

## Current phase
POST_UI_POLISH — audit and finish the player-facing HUD, interaction prompts, notifications, farming compatibility presentation, and visual consistency before the milestone capture.

## Canonical OBS Visual QA migration — 2026-08-21
- The foreground ffmpeg/AVFoundation capture workflow is deprecated for all new Visual QA evidence. Historical artifacts are retained and are not deleted.
- Canonical capture is now OBS Studio background-window recording controlled by `tools/visual_qa/visual_qa.sh` and `tools/visual_qa/obs_capture.py`.
- Fresh verification passed: `VISUAL_QA_OBS_VERIFY=PASS`, OBS 32.2.2, WebSocket 5.7.4, `OBS_RECORDING=False`.
- Google Chrome / ChatGPT remains foreground during normal recording; OBS captures the Roblox Studio window in the background. Roblox Studio and OBS must not be activated merely for recording.
- Streamlabs is unrelated to BunkerGame Visual QA and must not be modified.
- Every OBS capture retains the mandatory Play lifecycle: Start Play -> verify Play -> start OBS -> verify `OBS_RECORDING=True` -> runtime walkthrough -> stop OBS -> verify artifact -> immediately Stop Play -> verify `Current Studio Mode: Edit` and `Available DataModels: Edit`.
- External Director retains pixel-level approval authority. Agent capture verification does not constitute Visual Director PASS.
- Active Master Execution Pass checkpoint remains POST_UI_POLISH. `BunkerProcessorProgress` is already authored and source/build verified; next action is short runtime verification of unified HUD/farming presentation before any filesystem retirement of legacy `src/client/FarmingUI.client.lua`.

## POST_UI_POLISH runtime verification and OBS artifact
- Unified UI runtime coverage passed before retirement: exactly one `BunkerHUD`, one `BunkerInteractionUI`, one `BunkerProcessorProgress`, and live Credits/Seeds/Crops, health, Wood, Axe, cycle/day/time and FarmingRemotes bindings.
- Runtime exposed the legacy duplication concretely: the mapped `StarterGui.FarmingUI` contained `FarmingClient`, and that LocalScript created a second top-level `FarmingUI` at runtime. The unified UI already covered the required presentation responsibilities.
- Legacy farming presentation was retired through filesystem/Rojo source only. `src/client/FarmingUI.client.lua` was archived as `docs/legacy-assets/StarterGui/phase-ui-polish/FarmingUI.client.lua`, and only its explicit `StarterGui.FarmingUI` mapping was removed from `default.project.json`.
- Farming gameplay was preserved: `FarmingSystem.server.lua`, `FarmingRemotes`, `FoodProcessor`, UpdateUI, Notify, UpdateProgress, farming state and processor mechanics remain mapped and unchanged.
- Canonical Rojo 7.7.0 sourcemap/build, git diff check and postflight/BDS passed after retirement.
- Fresh post-retirement Play verified: BunkerHUD=1, BunkerInteractionUI=1, FarmingUI=0, legacy CreditsLabel=0, legacy Hotbar=0, legacy ProcessBar=0, BunkerProcessorProgress=1; unified Credits/Seeds/Crops, health, Wood, Axe and day/time readouts were present.
- POST_UI_POLISH was recorded with canonical OBS background-window capture while Chrome remained foreground. During recording, real FarmingRemotes were used with Play-only QA values to visibly exercise unified farming readouts, notification and processor progress; BunkerProcessorProgress was runtime-enabled and no legacy UI fragments were present.
- A player-input attempt near prototype_tree_01 did not advance HarvestHitSerial, so no harvest-interaction PASS is claimed from that specific capture action. Previously verified survival authority remains unchanged and will receive dedicated regression evidence later.
- Canonical POST_UI_POLISH artifact: `visual-qa/captures/2026-08-21_11-00-00_POST_UI_POLISH.mov` (134,758,420 bytes).
- OBS stop passed, artifact verification passed, Roblox Play was immediately stopped, and fresh Studio state verified `Current Studio Mode: Edit` / `Available DataModels: Edit` before continuing.
- Pixel-level visual approval remains external Director responsibility.

## Current phase
REVIEW2 evidence recapture using canonical OBS background-window workflow, followed by remaining integration/performance/regression QA and FINAL_INTEGRATED_PLAYTEST. Completed implementations are not restarted.

## REVIEW2 evidence recaptures and final integrated validation — 2026-08-21
- Canonical OBS background-window REVIEW2 recaptures completed without restarting or rewriting completed implementations:
  - `visual-qa/captures/2026-08-21_11-05-16_POST_PHASE6_BUNKER_REVIEW2.mov` — bunker walkthrough covering exterior/entrance, Common, Bedroom, Workshop, Upgrade, Storage, Power, East Utility/Shop-adjacent view and Service. Direct Shop pathfinding again failed; adjacent East Utility traversal passed and no speculative geometry change was made.
  - `visual-qa/captures/2026-08-21_11-12-11_POST_LIGHTING_ATMOSPHERE_REVIEW2.mov` — Common/Hub, Bedroom/Workshop contrast, Power and Service atmosphere/VFX route.
  - `visual-qa/captures/2026-08-21_11-16-18_POST_EXTERIOR_REWORK_REVIEW2.mov` — main exterior approach, buried silhouette/utility-landmark side and service exterior approach.
  - `visual-qa/captures/2026-08-21_11-22-18_POST_FOREST_WORLD_REVIEW2.mov` — player-facing coverage from two canonical positions inside the forest region. Direct pathfinding to `forest_tree_001` failed, so no tree-specific navigation PASS is claimed from that attempt.
- Every REVIEW2 capture obeyed the mandatory lifecycle: fresh Play verification, Play-only zombie/wave isolation, OBS start/status verification, intended walkthrough only, OBS stop/artifact verification, immediate Play stop, then fresh Edit verification before further work.
- Final source preflight passed after REVIEW2: no mapped stale FarmingUI/BunkerGui/broken-sound references, legacy FarmingUI remains archived outside mapped source, `BunkerProcessorProgress` remains canonical, `git diff --check` passed, canonical Rojo 7.7.0 sourcemap/build passed, and project postflight/BDS passed.
- Fresh FINAL server integration audit passed: ForestResourceRegion=36 trees, all 36 Active with valid HitAnchor; PrototypeHarvestGrove present; FoodProcessor and FarmingRemotes UpdateUI/UpdateProgress/Notify present; NewBunker present with 9 enabled prompts including 8 Custom prompts; ResourceNodeService, HarvestService and ForestResourceSpawner present; four environmental ParticleEmitters present.
- Fresh FINAL client integration audit passed: BunkerHUD=1, BunkerInteractionUI=1, BunkerProcessorProgress=1; FarmingUI=0, CreditsLabel=0, legacy Hotbar=0, legacy ProcessBar=0; Credits/Seeds/Crops, health, Wood, Axe and day/time readouts all present.
- Canonical final integrated capture: `visual-qa/captures/2026-08-21_11-27-12_FINAL_INTEGRATED_PLAYTEST.mov` (201,379,860 bytes at initial artifact verification). The recorded route covered exterior, Common Hub, Bedroom/Workshop, Upgrade, Power, Service/Farm route, FoodProcessor and canonical forest region.
- FINAL OBS stop and artifact verification passed. Roblox Play was immediately stopped afterward and fresh Studio state verified `Current Studio Mode: Edit` / `Available DataModels: Edit`.
- All temporary zombie/wave isolation used during REVIEW2/final capture was Play-only and disappeared on Stop; no isolation state was persisted to filesystem/Rojo source.
- Pixel-level visual quality approval remains external Director responsibility. These artifacts are the evidence set for that review; the execution agent does not claim Visual Director PASS.

## Master Execution Pass status
IMPLEMENTATION / TECHNICAL EXECUTION COMPLETE FOR THE AUTHORIZED MASTER PASS. Filesystem/Rojo remains source of truth. Remaining external gate: Director pixel-level review of retained milestone/REVIEW2/final video evidence and any explicitly requested follow-up fixes arising from that review.

## FUTURE GAMEPLAY VISION — foundation constraint
- Future authorized survival scope includes a polished real gameplay hotbar, Axe, Pickaxe, Gun, additional tool/inventory slots, mineable rock/resource nodes, canonical mining rewards, combat/weapon feedback, bunker progression/resource use, and broader survival gathering.
- Current/foundation world design must therefore not optimize only for trees. Preserve believable opportunities for forest resources, future rock/mineral resource areas, scavenging, combat sightlines, exploration routes, and legible bunker-return routes.
- This vision is a compatibility/design constraint only. Do NOT implement Pickaxe, Gun, mining, hotbar, ammunition/reload, or combat until a focused Director task authorizes them.
- Future mining should preferably extend the existing generic resource architecture — resource spawning, `ResourceNodeService`, and canonical Inventory — rather than introducing an unrelated one-off mining stack.
- The eventual hotbar is a real gameplay interface, not decorative HUD text. Expected core slots begin with `1 — Axe`, `2 — Pickaxe`, `3 — Gun`, with polished selected/equipped state, responsive input presentation, visual/icon identity, and gameplay-driven tool/ammo/resource state where relevant.
- Future world/art passes must preserve enough spatial diversity for these systems even when their gameplay is not yet implemented.

## DIRECTOR FIX PASS — TASK 1: WORLD VISUAL FOUNDATION
- Task 1 executed as an additive overworld visual-foundation pass only. No Task 2 gameplay was started.
- Canonical source is `src/Workspace/WorldVisualFoundation.model.json`, generated by `tools/builders/generate_world_visual_foundation.py` and mapped through the existing `src/Workspace` Rojo mapping.
- Foundation contains four deliberately distinct presentation zones:
  - `WestRidgeFutureResourceOpportunity` — rocky ridge composition reserving believable future mineral/resource staging space.
  - `NorthExplorationClearing` — broad open clearing with edge framing, preserving long sightlines and future encounter/scavenging flexibility.
  - `SouthWestScavengeApproach` — environmental approach toward the existing southwest world without modifying protected Scrap piles or ZombieSpawns.
  - `EastBunkerReturnTransition` — legible return corridor between overworld exploration and bunker circulation while remaining outside protected farm, PrototypeHarvestGrove and NewBunker geometry.
- The packet is presentation-only: 42 anchored Parts, all non-collidable, non-touchable and non-queryable; zero ProximityPrompts, scripts, ResourceNodeId, ResourceDefinitionId or ToolDefinitionId gameplay hooks.
- No Pickaxe, Gun, mining, hotbar, ammunition/reload or combat implementation was added.
- Initial Edit synchronization exposed two exact duplicate WorldVisualFoundation roots. Forensic comparison verified both roots were exact 42-Part / 57-descendant duplicates with identical geometry and foundation attributes; exactly one duplicate was removed from Edit state, leaving the filesystem/Rojo-authored singleton.
- Initial composition QA identified 22 protected AABB overlap pairs, all isolated to `EastBunkerReturnTransition`: the first ReturnTrack crossed PrototypeHarvestGrove/service-side NewBunker earthworks and its return landmark overlapped the ServiceApron. Source was corrected rather than modifying protected content.
- Corrected East transition uses a narrower track centered near `(68, 53.48, 119)` with size approximately `(14, 0.18, 38)` and shifted edge/landmark dressing.
- Fresh Edit QA after the correction passed: WorldVisualFoundation root=1, Parts=42, and zero overlap pairs against `farm`, `Scrap piles`, `ZombieSpawns`, `PrototypeHarvestGrove`, and `Rebuild.NewBunker`.
- Runtime contract passed: root=1, Parts=42, all four zones present, zero collidable Parts, zero prompts/scripts/gameplay IDs.
- Player navigation QA passed as a continuous world loop: bunker/world -> West Ridge -> North Exploration Clearing -> SouthWest Scavenge Approach -> East Bunker Return Transition -> bunker entrance. All four foundation opportunities are reachable without introducing blocking geometry or dead-end dependence.
- Existing farming, Scrap piles, ZombieSpawns, PrototypeHarvestGrove, forest/resource services, NewBunker and survival gameplay were preserved.
- Task 1 explicitly reserves spatial diversity for future forest resources, mineral/resource gathering, scavenging, combat sightlines, exploration and bunker-return routes while leaving future gameplay architecture unimplemented.
- Play QA used temporary Play-only zombie/wave isolation. Play was stopped immediately after QA and fresh Studio state verified `Current Studio Mode: Edit` / `Available DataModels: Edit`.
- Task 1 technical/composition/navigation validation does not constitute external Director pixel-level visual approval.

## Director Fix Pass status
TASK 1 — WORLD VISUAL FOUNDATION: TECHNICAL PASS. STOP HERE. Task 2 and future Pickaxe/Gun/mining/hotbar/combat systems remain unauthorized until the external Director explicitly starts their focused task.
