# Director-Authorized Greenfield Bunker Rebuild

## Status

`BKR-GREENFIELD-001` is active. This is a complete new facility, not another art pass over `Workspace.Rebuild.NewBunker`.

The direct Director instruction authorizes the rebuild and requires the final result to stop at `DIRECTOR_REVIEW`; no agent may claim human visual approval.

## Safety and Permanent Evidence

- Immutable old-bunker backup: `backups/new_bunker/20260826_143521_pre_greenfield_rebuild`.
- Backup manifest: `backups/new_bunker/20260826_143521_pre_greenfield_rebuild/BACKUP_MANIFEST.txt`.
- Backup evidence: 274 readable files, SHA-256 verified, read-only; `OLD_BUNKER_BACKUP=PASS`.
- Pre-rebuild Studio/OBS evidence: Edit mode and `OBS_RECORDING=False`.
- Protected world systems remain outside the bunker scope: `Workspace.farm`, `Workspace.Scrap piles`, `Workspace.ZombieSpawns`, `Workspace.Grassblox`, `Workspace.FarmingEnvironment`, and `ServerStorage` zombie templates.

## Overhead Exterior Defect — Forensic Disposition

### Result

The reported giant overhead obstruction was **not** a `Workspace` geometry instance. It was a render-only `Lighting.Sky` cubemap configuration. Its physical dimensions are not applicable.

- Original source path: `src/Lighting/Sky.model.json`.
- Runtime path: `Lighting.Sky`.
- Workspace physical offender: none found.
- Excluded large world candidates: `Workspace.Grassblox.flat brick` parts are horizontal playable-ground tiles, not sky obstruction.
- Legitimate foreground roof candidate: `Workspace.Rebuild.NewBunker.EnvironmentDetails.SteppedRoofSilhouette.EntranceRoofCap`, size `(25, 0.7, 13)`, position `(0, 67.3, 26)`; it is not the giant render artifact.

### Reproducible evidence

1. A full OBB foreground scan of 3,313 non-Terrain BaseParts from the exterior camera found only local entrance earthworks, portals, and the legitimate roof cap. No large foreground plane covered the sky.
2. In Play, deleting only `Lighting.Sky` removed the angular red/brown overhead surface. A blue source image probe proved the uploaded candidate image itself was correct while the sky renderer still showed the unwanted cubemap appearance.
3. The source `Sky.model.json` and unused generated sky assets were removed. `Lighting` now contains only `Atmosphere`, `Bloom`, `DepthOfField`, and `SunRays` in Edit and Play.
4. Current visual evidence: `visual-qa/captures/2026-08-26_15-03-12_OVERHEAD_SKY_DEFECT_SOURCE_REMOVED.mov` with extracted frames under `visual-qa/frames/2026-08-26_15-03-12_OVERHEAD_SKY_DEFECT_SOURCE_REMOVED.mov/`.
5. The final capture includes normal open sky and cloud views from the player spawn/exterior camera, with no giant flat or angled blocker.

## Verified Site Constraints

- Playable ground: approximately world Y `53.4`; bunker floor: world Y `54.0`.
- Terrain voxel scan around the bunker exterior found `0` occupied cells; do not author around world Y `0`.
- Preserve the external zombie target alignment at `FutureBunkerDoorMarker` position `(0, 54.1, 21.2)`.
- Keep the new footprint clear of the protected farm zone around X `55..82`, Z `209..221` and the external farm transition.

## Gameplay Compatibility Audit

### Source/live discrepancy to eliminate during cutover

The connected Edit DataModel currently has four live `GameplayTargetId` adapters, while `src/Workspace/Rebuild/NewBunker.model.json` currently contains only `legacy_weapon_upgrade`. The stale source generator only re-applies the weapon workbench attribute.

This is confirmed source/live drift. The greenfield source must contain all four target IDs before the old live model is retired; no Studio-only adapter may be relied upon.

### A/B/C/D inventory

| Existing element | Classification | Verified behavior / evidence | Greenfield disposition |
| --- | --- | --- | --- |
| `Workspace.farm`, `Workspace.Scrap piles`, `Workspace.ZombieSpawns`, `Workspace.Grassblox` | A — reuse unchanged | Protected overworld systems; no bunker ownership | Leave mapped and untouched. |
| `ServerScriptService.FarmingSystem`, runtime `Workspace.Plots`, `Workspace.FoodProcessor`, `FarmingUI` | A — reuse unchanged | 15 plots, crop growth/harvest, crop-to-food processing, existing UI | Preserve unchanged; retain route from bunker to farm. |
| `ServerScriptService.GlobalManager` leaderstats/time/waves | A — reuse unchanged | Owns `Scrap`, `Credits`, `Batteries`, day/night, legacy wave lifecycle | Do not refactor in this environmental packet. |
| `ReplicatedStorage.Interaction`, prompt UI controller, and Bunker audio catalog | A — reuse unchanged | Custom prompt UI, server validation, prototype hinge cue seam | New props use the same supported prompt contract. |
| Prototype locker and two supply crates | B — reuse behavior only | Open/close through `MovingPart`, `OpenPose`, custom prompt feedback | Build fresh props; do not reuse old art. |
| Entrance-control inspection prompt | B — reuse intentional unavailable feedback | Eighth Custom prompt currently exposes an entrance inspection state with no gameplay target | Build a fresh inspect-only entry-systems point so all eight Custom prompt roles remain represented. |
| Named flicker fixtures and runtime VFX treatment | B — reuse presentation behavior only | `BunkerAtmosphereController` and `BunkerEnvironmentalVFX` target six fixture names and three anchor names | Build fresh fixture/anchor placements under the compatibility facade. |
| `legacy_battery_station` | C — migrate with adapter | 20 Credits -> +1 Batteries | Add to fresh power-bay interaction model. |
| `legacy_scrap_processor` | C — migrate with adapter | Scrap -> Credits at 5 per Scrap | Add to fresh processing/shop interaction model; distinct from Farming FoodProcessor. |
| `legacy_harvest_upgrade` | C — migrate with adapter | 100 Credits -> `HarvestPower = 2` | Add to fresh upgrade-rig interaction model. |
| `legacy_weapon_upgrade` | C — migrate with adapter | 200 Credits -> `GunDamage + 10` | Add to fresh workbench interaction model. |
| `BunkerPowerService` | C — migrate with adapter | Runtime power prompt consumes one Battery and temporarily enables bunker lights | Fresh `CompositionMarkers.FutureBunkerLightsControlMarker` plus `Lighting` subtree. |
| `BunkerEntranceContract` and `ZombieEntranceTargetMigration` | C — migrate with adapter | Zombies receive the stable entrance target marker | Fresh `CompositionMarkers.FutureBunkerDoorMarker` at the verified external alignment. |
| Legacy labels `BunkerDoor`, `BunkerLights`, `BunkerSofa`, `Bunker walls`, `DoorShop` | D — no active geometry to preserve | Fresh runtime evidence found no current Workspace instances; uninspected binary references remain `UNVERIFIED_BINARY` | Do not recreate their old art. Map only verified behavior through named facade anchors. |
| Old `Workspace.Rebuild.NewBunker` geometry and the old `Lighting.Sky` | D — retire/remove | Existing model is functional reference only; sky defect source removed | Archive evidence remains in the immutable backup; replace active source only at atomic greenfield cutover. |

## Greenfield Compatibility Facade

The facility must use a new authored layout and art direction while preserving only these existing code-level seams. Keeping these names avoids speculative rewrites of protected services.

```text
Workspace.Rebuild.NewBunker
├── InteractiveProps
│   ├── BedroomPersonalUtilityLocker             (PrototypeLockerPrompt)
│   ├── StorageMedicalSupplyCrate                (PrototypeCratePrompt)
│   ├── WorkshopConsumablesCrate                 (PrototypeCratePrompt)
│   ├── BatteryPurchaseStation                   (OfflineControlPrompt; legacy_battery_station)
│   ├── ScrapExchangeStation                     (InspectStationPrompt; legacy_scrap_processor)
│   ├── HarvestUpgradeConsole                    (InspectStationPrompt; legacy_harvest_upgrade)
│   ├── WeaponWorkbenchStation                   (InspectStationPrompt; legacy_weapon_upgrade)
│   └── EntrySystemsInspectionPoint              (InspectStationPrompt; no GameplayTargetId)
├── CompositionMarkers
│   ├── FutureBunkerDoorMarker                   (BunkerEntranceTarget=true)
│   ├── FutureBunkerLightsControlMarker
│   ├── FutureBatteryButtonMarker
│   ├── FutureProcessorMarker
│   ├── FutureUpgradeTableMarker
│   ├── FutureWeaponWorkbenchMarker
│   └── FarmRouteMarker
├── Lighting
│   └── WakeSideFluorescent, MiddleAgedBay, StorageAisleLight,
│       WorkshopEntryFill, ServiceConnectorPractical, FarmExitEmergencyPractical
└── EnvironmentDetails
    └── WaterDripPool, ServiceWetSheen, ExhaustCap (two generator caps)
```

All four active station **Models** (not prompts or marker parts) carry their exact server-authoritative `GameplayTargetId` values. Prototype models each include the current `MovingPart` and invisible/non-colliding `OpenPose` contract. The facade preserves eight Custom prompts: three prototype prompts, four active compatibility stations, and one inspect-only entry-systems prompt. `BunkerPowerService` creates the intentional ninth Default-style `BunkerPowerPrompt` at runtime.

`BunkerEntranceContract` searches every Workspace BasePart tagged `BunkerEntranceTarget` before falling back to the marker. The new source must therefore mark its own `FutureBunkerDoorMarker` and cutover validation must show no stale old-bunker tag winning that lookup.

## New Facility Plan

### Spatial organization

The new facility uses the verified entrance alignment and floor elevation only; it does not inherit the old room layout or visual composition.

1. **Surface threshold and blast vestibule** — retains the external defense/entrance relationship at `(0, 54.1, 21.2)` with a readable downward transition.
2. **Decontamination spine** — a narrow, deliberately lit transition from the entry to the habitable interior.
3. **Central commons** — multi-height social/operational anchor with sightlines to residential, work, and service routes.
4. **Starting bedroom** — protected residential pocket, old bed, wake-up composition, personal locker, and an immediate readable route to the commons.
5. **Workshop / armory** — service benches, tool storage, weapon-workbench compatibility station, and machine-readable industrial work zone.
6. **Upgrade bay** — distinct hydraulic/electrical improvement rig with the harvest-upgrade compatibility station.
7. **Storage / medical reserve** — layered shelving, supply crate, short-horizon resource readability, and no blocking clutter.
8. **Power and utilities hall** — generator silhouettes, power-switch compatibility marker, distribution pipes, and controlled electrical light hierarchy.
9. **Service counter / scrap exchange** — unattended-but-readable processing counter for the Scrap-to-Credits compatibility station.
10. **Farm service lock** — deliberate outward route to the protected farm, with a visible maintenance transition and exterior route marker.

### Construction direction

- Concrete shell, steel reinforcement, welded plates, pipe runs, distribution trays, utilitarian fixtures, aged labels, restrained soot/water/rust/paint wear.
- Strong room identities through form, lighting, and repeatable structural language; never arbitrary clutter.
- Player routes retain a practical 5.5-stud minimum usable clearance except deliberately signposted squeeze points that must be Play-tested.
- Use source-controlled native primitives and existing verified production assets. Do not use Studio-only generated geometry as the durable build.

## Construction Waves

1. **Compatibility shell and circulation** — independent builder, new room plan, exterior threshold, floors/walls/ceilings, collision routes, markers, interaction hosts.
2. **Functional stations and power** — all four Model target IDs, all eight Custom prompts, ninth power prompt, lights, fixtures, entrance target, and prototype prompts.
3. **Industrial art pass** — structural rhythm, generator/service systems, props, readable navigation, contextual storytelling.
4. **Exterior and farm approach** — surface silhouette, safe entrance composition, route to protected farm, no sky obstruction.
5. **Verification and review** — source/Rojo, Studio, Play, interaction regression, navigation/camera, visual captures, independent QA, then `DIRECTOR_REVIEW`.

## Non-Negotiable Review Gates

- Gate A: architecture/compatibility facade is reviewed before cutover. The direct recovery review passed the source/staging foundation gate; later independent technical, gameplay, and visual review remains required at Gates F–G.
- Gates B–D: static, Rojo, and live-DataModel source mapping evidence.
- Gate E: player-facing interaction, power, entrance target, farming protection, navigation, and console evidence.
- Gates F–G: regression and independent technical/gameplay/visual review.
- Gate H: Director review only; no automated or self-review approval claim.

## Gate A — Direct Recovery Review (2026-08-26)

This recovery-session review deliberately continued the existing staging facility;
it did not recreate the old bunker, repeat the sky forensics, or alter protected
world systems. It is an architecture/foundation gate only, not Visual Director
approval and not a substitute for the required later independent Gate G review.

### Reviewed source and live staging evidence

- `tools/builders/greenfield_bunker/facility.py` remains independent of the
  legacy `new_bunker` builder and generated deterministic staging output twice
  byte-for-byte.
- The live Edit staging model is `Workspace.Rebuild.GreenfieldBunker`, with
  `FacilityVersion=BKR-GREENFIELD-001`, `FacilityMode=staging`, floor elevation
  `54`, 17 purposeful shell/connector rooms, all seven marker roles, all four
  exact `GameplayTargetId` model adapters, and eight enabled Custom prompts.
- Candidate active output was generated without touching the live old bunker.
  It contains the same facade plus `Spawn.BedroomStartSpawn`, has the entrance
  marker at `(0, 54.1, 21.2)` with `BunkerEntranceTarget=true`, and preserves
  the exact fixture/VFX anchor names consumed by existing services.
- The reviewed circulation graph is: surface threshold -> blast vestibule ->
  decontamination spine -> central commons; commons branches to bedroom /
  workshop, upgrade, and power; power leads through the service bridge into the
  utility spine; the service cross passage connects upgrade, Scrap exchange,
  utilities, and the farm service lock. The north utility branch supplies a
  deliberate redundant service route to the farm lock.
- Minimum generated doorway width is `7` studs and minimum head clearance is
  `8` studs. Fresh Play measured a standard character at approximately
  `4.65 x 6.25 x 4.13` studs and retained a Custom-camera distance of
  approximately `6.55` studs in both the entrance and repaired power-service
  bridge.
- The active farm route terminates at a maximum X of `53.10`, clear of the
  protected farm-zone boundary at X `55`; the facility itself remains outside
  the protected farm, Scrap, zombie-spawn, Grassblox, and FarmingEnvironment
  ownership boundaries.

### Correction made during review

The original staging grid had seven exact coplanar floor overlaps where the
power/service and Scrap/service intersections had been modeled as overlapping
rooms. `facility.py` now separates the power-service vestibule, utility south
and north branches, service cross passage, storage, Scrap exchange, and upgrade
bridge into adjoining shells. Static active-output analysis now reports
`GREENFIELD_FLOOR_OVERLAPS=PASS 0`; the bridges have exposed-edge closure walls
instead of unsupported open floor slabs.

### Targeted Play evidence

Fresh Play was started only for the repaired staging graph, then stopped and
verified back to Edit. Actual character navigation passed: bedroom ->
residential -> commons -> power -> power-service bridge -> utility -> storage ->
service cross -> Scrap exchange -> farm service lock -> upgrade -> commons ->
entrance. The Play console contained normal FarmingSystem startup and wave
messages only. OBS remained idle.

`GREENFIELD_GATE_A=PASS`

The active old `Workspace.Rebuild.NewBunker` remains untouched until the
atomic source-controlled cutover and its subsequent runtime regression gates.
