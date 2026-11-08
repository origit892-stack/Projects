# BunkerGame Asset Rework — Production Plan

## Authority
Filesystem/Rojo is permanent source of truth. Studio is inspection/QA only. Preserve gameplay contracts and existing Asset Registry entries.

## Wave A audit conclusions

### NewBunker
- Live Edit evidence: 1,981 descendants, 1,668 BaseParts, 278 Models, 27 local lights, zero embedded scripts, zero current MeshParts, and 8 enabled ProximityPrompts.
- The existing authored architecture, lighting, decay, conduit, machinery and storytelling layers are KEEP/ENHANCE foundations rather than rebuild targets.
- All eight prompt-bearing InteractiveProps are Category E — GAMEPLAY-CRITICAL. Preserve prompt hosts, MovingPart/anchor semantics, attributes, interaction distances and positions. Visual shells may wrap them only after dependency-specific QA.
- High-value custom-mesh opportunity is reusable industrial detail that improves silhouettes at gameplay distance without replacing architecture.

### Farming
- `src/Workspace/farm.rbxm` is protected legacy presentation/content and contains legacy prompt/script models; do not rewrite it casually.
- Canonical farming gameplay is runtime-authored by `src/server/FarmingSystem.server.lua`.
- `FarmingSystem` creates `Workspace.Plots`: exactly 15 canonical Plot BaseParts in a 3x5 grid and wires PlotPrompt/state/growth/harvest behavior.
- `FarmingSystem` creates `Workspace.FoodProcessor`, ProgressDummy, processor prompt and FarmingRemotes UpdateUI/Notify/UpdateProgress.
- Farming rework therefore uses visual shells/support assemblies around runtime canonical anchors. It must not substitute their functional identity.

### Survival resources
- PrototypeHarvestGrove remains canonical resource-contract reference. Live Edit has three prototype nodes with ResourceNodeId/ResourceDefinitionId.
- ResourceNodeService/HarvestService/ForestResourceSpawner architecture remains untouched. Supporting art may be added around nodes without moving/replacing canonical node models unless separately reviewed.

### Existing production assets
- `pipeline_pipe_retry_02` — Rusty Pipe — Ready. Reuse as a utility-language asset; do not duplicate.
- `old_military_ammo_crate_01` — Old Military Ammo Crate — Ready. Reuse for non-interactive storage/story clusters; do not replace interactive bunker crates blindly.
- Preserve every Asset Registry entry.
- Live Studio currently exposes a duplicate `old_military_ammo_crate_01` instance under ServerStorage.GeneratedAssets while filesystem contains one canonical source. Treat as source/live drift; do not hand-delete Studio instances as an art-pass workaround.

## Classification

### A — KEEP
- NewBunker architecture/shell and traversal geometry.
- Existing localized lighting hierarchy and route hierarchy.
- Existing structural ribs, major generator massing, established decay/stain storytelling where composition already reads.
- Canonical farming/resource gameplay architecture.

### B — ENHANCE
- Primitive pipe/conduit runs: retain route/position but selectively add mesh fittings, valves, flanges, clamps and penetrations.
- Power-room switchgear/generator areas: add a few high-quality electrical/utility hero details around existing massing.
- Workshop/storage: enrich focal clusters with reusable props while preserving clear aisles and interaction sightlines.
- Service/farm transition: improve industrial continuity with reusable utility assets.
- Farming presentation: add salvaged-industrial visual framing around runtime plots and FoodProcessor rather than replacing anchors.

### C — REPLACE WITH CUSTOM ASSET
Only visual-only primitive props whose identity is not a gameplay contract and where a mesh materially improves silhouette. Initial wave intentionally avoids replacing prompt-bearing crates, locker, workbench station, upgrade station, processor anchor or resource nodes.

### D — NEW SUPPORTING PROP
Initial highest-impact reusable kit:
1. `bunker_valve_assembly_01` — compact corroded industrial isolation valve with wheel/flange language; reusable on power/service/farm irrigation routes.
2. `bunker_electrical_junction_box_01` — aged military/industrial junction/control enclosure; reusable on corridors, power and farming support.
3. `bunker_vent_grille_01` — battered bunker ventilation grille/cover; reusable on corridors, bedroom/service/power spaces.

Potential later assets after in-game review: pipe elbow/T/flange family, cable-tray fittings, locker/tool cabinet, workbench support props, planter edge kit, irrigation manifold/pump, FoodProcessor hero shell, maintenance cart, drain/hatch kit.

### E — GAMEPLAY-CRITICAL
- All eight NewBunker InteractiveProps/prompt hosts.
- 15 runtime Plot parts and PlotPrompts.
- Runtime FoodProcessor, ProgressDummy and processor prompt.
- FarmingRemotes and unified processor HUD contract.
- PrototypeHarvestGrove/ForestResourceRegion nodes and ResourceNodeId/ResourceDefinitionId.

## Production strategy
- Do not mass-produce wishlist assets.
- Wave B creates the three-item core industrial kit above, one asset at a time through the accepted Agent Asset Factory, with visual rejection/regeneration when needed.
- Integrate only after factory publication/model inspection/canonicalization and after scale is deliberately chosen in world context.
- First dressing wave targets visual-only NewBunker utility/service/power surfaces and non-interactive storage clusters.
- Wave C follows only after reviewing Wave B in-game; it will address farming shells and FoodProcessor presentation.

## Performance constraints
- Reuse canonical meshes instead of duplicating unique geometry/textures.
- Simple support props target hundreds to low-thousands of triangles.
- Preserve traversal and prompt sightlines; decorative shells should normally be non-colliding unless collision is explicitly justified.
- Avoid adding broad new shadow-light cost during asset dressing.

## QA gates
Each asset: factory technical + visual QA, real Roblox publication, imported Model inspection, Asset Registry preservation, canonical filesystem model, Rojo 7.7.0 build, Edit-only Studio verification.
Each integration wave: source/postflight, Edit hierarchy/interaction audit, Play-only gameplay regression where required, mandatory Stop->Edit verification, and retained OBS visual evidence for external Director review.
