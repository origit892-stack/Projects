# Master Game Gap Matrix

## Authority and evidence boundary

This matrix expands `FG-GREENFIELD-001` without changing its frozen contracts.
Filesystem/Rojo is authoritative. A checkpoint is only complete when its stated
acceptance criteria and durable evidence exist; implementation alone is partial.
`FULL_GAME_BACKUP=PASS` remains the immutable recovery boundary.

| Checkpoint | Current state | Objective acceptance criteria | Required evidence / remaining gap |
|---|---|---|---|
| GAME_ARCHITECTURE_AND_GAP_AUDIT | Complete | Frozen contracts, mapping, service ownership, and measured gaps are recorded. | Gate A PASS; this matrix; stale post-cutover world hash must be refreshed. |
| BUNKER_REWORK | Partial | Layout/circulation; entrance/airlock; corridor; power, command, workshop, storage/bedroom/service spaces; farm/processor route; materials, props, electrical dressing, storytelling, lighting, audio, VFX; interactions; collision/performance; walkthrough, OBS, and independent reviews all pass. | Source rework exists and entrance clearance/axe silhouette were repaired; current walkthrough, OBS, collision, power-visual, technical/gameplay/visual review evidence is missing. |
| CORE_SURVIVAL_SYSTEMS | Partial | Authoritative needs, healing, death/respawn, time/wave survival loop work at runtime. | Services exist; need night wave, death/respawn, cleanup, and multi-player runtime evidence. |
| INVENTORY_EQUIPMENT_CRAFTING | Partial | Starter kit, inventory, Axe/Tree/Wood, Rifle/ammo, item use, crafting/upgrade inputs are transactional. | Axe/rifle/tree smoke passed; require persistence/idempotency, Scrap, concurrent-hit, and all item-use evidence. |
| EXTERIOR_WORLD_AND_RESOURCE_LOOP | Partial | Clear bunker-to-yard-to-forest/salvage/farm routes, resources, loot and return loop are playable. | Source counts validate; require player-height route/collision and resource-respawn walkthrough. |
| THREATS_COMBAT_AND_RISK | Partial | Bounded zombie AI, damage, reward attribution, risk/reward retreat, dawn cleanup. | Source exists; require controlled night, kill reward, cap, and cleanup evidence. |
| FARMING_PROCESSING_AND_ECONOMY | Partial | Plant/grow/harvest, processor, shop, storage, power, exchange, upgrades are authoritative. | Source exists; require full happy-path, cancellation/refund, and concurrent transaction tests. |
| BUNKER_REPAIR_UPGRADES_AND_PROGRESSION | Partial | Power and upgrades visibly/functionally alter preparation and progression. | Power source/runtime cue exists; power-linked visuals and upgrade effect regressions remain. |
| UI_UX_ONBOARDING | Partial | Minimal HUD, panels, objective progression and keyboard/touch/gamepad/reduced-motion usability. | Basic HUD evidence only; device/panel/onboarding evidence remains. |
| AUDIO_VFX_STORYTELLING_WORLD_POLISH | Partial | Budgeted atmosphere supports readable navigation and survival tension. | Source budgets pass; fresh runtime mix/VFX/visual evidence and review remain. |
| END_TO_END_VERTICAL_SLICE | Missing evidence | Spawn -> gather -> farm/process -> power -> night -> recover works in one controlled run. | Build a source-owned regression harness and record its result. |
| FULL_INTEGRATION_QA_AND_NEW_DIRECTOR_REVIEW | Missing | Gates B-G pass, OBS package and independent technical/gameplay/visual reviews resolve findings. | 2/6-player, performance, fuzz, walkthrough, OBS, and independent reviews are required before status change. |

## Immediate execution order

1. Implement a source-owned integrated regression harness for the first complete
   onboarding loop, beginning with the currently unproven farming/processor path.
2. Run static/Rojo checks, sync it to Studio, and execute controlled Play evidence.
3. Use failures to repair service contracts before proceeding to presentation-only work.
