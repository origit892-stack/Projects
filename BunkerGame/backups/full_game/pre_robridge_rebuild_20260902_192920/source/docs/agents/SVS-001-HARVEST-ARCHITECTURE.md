# SVS-001 — First Survival Vertical Slice Architecture

**Authoring role:** World / Survival Systems Architect
**Status:** PROPOSED — requires independent Technical Architecture Review before implementation.

## 1. Scope and evidence

This architecture covers only the first end-to-end survival loop:

Find controlled harvestable tree -> equip/use Axe -> validated chop -> visible reaction/progress -> harvest -> canonical Wood reward -> feedback -> depleted state -> respawn.

Verified project constraints:
- FND-001..006 are the accepted Foundation baseline.
- `InventoryService` is the canonical per-player inventory authority.
- `ItemDefinitions` is the single canonical item registry.
- Combat/Damage is player-combat authority; resource harvesting must not pretend trees are player combatants merely to reuse DamageService.
- SessionContext is the canonical session/player eligibility boundary.
- Existing Farming still owns legacy `Player.Inventory` and must remain untouched.
- Existing UI foundation lives under `ReplicatedStorage.UI`; UI is presentation-only.
- Studio inspection found no safe existing overworld tree assets identifiable for direct conversion. The only tree-name match was a NewBunker workshop wood insert.
- `Grassblox` provides large playable ground. Farm, Rebuild/NewBunker, Scrap piles and ZombieSpawns occupy known bounded areas and remain protected.

Therefore the slice uses a small new Rojo-authored prototype grove in a clear playable area, rather than modifying unknown/binary environment assets.

## 2. Specialist ownership

- World / Survival Systems: ResourceDefinition, ResourceNodeService, node lifecycle, controlled grove integration.
- Inventory / Loot / Economy: canonical Wood ItemDefinition and reward handoff to InventoryService.
- Combat / Tools: canonical Axe identity/definition and validated tool-use intent boundary. This is a harvesting tool, not a player DamageService producer.
- UI / UX: read-only harvest feedback and Wood-gained notification using existing UI language.
- Technical QA: independent authority, exploit, mapping, AST/BDS/Rojo/regression review.
- Gameplay QA: independent end-to-end player loop review.
- Visual / World Review: independent readability/reaction review, not final art approval.

## 3. Canonical identities

Stable prototype IDs:

- ItemId `wood`
- ItemId `axe_basic`
- ToolDefinitionId `axe_basic`
- ResourceDefinitionId `tree_basic`
- ResourceNodeId: stable per authored prototype node, e.g. `prototype_tree_01`

Instance names and display strings are not canonical IDs.

## 4. ResourceDefinition boundary

World / Survival owns one small data-driven resource-definition registry.

Minimum shape:

```text
ResourceDefinition
  Id
  RequiredToolTag
  MaxHealth
  RewardItemId
  RewardQuantity
  RespawnDelaySeconds
  InteractionDistance
  HitCooldownSeconds
```

Prototype tuning values live only in this definition/ToolDefinition data, never scattered through handlers.

The schema is intentionally sufficient for trees now and later stone/ore without defining those future resources.

## 5. Resource node identity and authored world integration

Each harvestable node is an authored Model beneath a dedicated mapped prototype grove/container, with attributes:

```text
ResourceNodeId
ResourceDefinitionId
```

The model exposes explicit named presentation parts/attachments required by the implementation, rather than discovering arbitrary descendants by heuristics.

The prototype grove is additive. It does not modify or replace `farm`, `Grassblox`, `Scrap piles`, `ZombieSpawns`, NewBunker, or legacy RBXM assets.

## 6. Server-authoritative node lifecycle

`ResourceNodeService` owns mutable state for every registered node:

```text
Active -> Depleted -> Respawning -> Active
```

Minimum authoritative state:

```text
CurrentHealth
LifecycleState
CycleSerial
LastAcceptedHitByPlayer
```

Replicated attributes may expose presentation-safe state/progress, but Workspace attributes are a read model, not mutation authority.

At depletion, the server atomically changes the cycle from Active before reward grant. Only the request that wins that state transition can produce the cycle reward. This prevents duplicate rewards when multiple players hit the final health concurrently.

Respawn restores health/state and presentation after the centralized prototype delay. No persistence is introduced.

## 7. Axe / tool boundary

Combat / Tools owns a small ToolDefinition registry separate from ItemDefinition.

Minimum shape:

```text
ToolDefinition
  Id
  ToolTags
  HarvestDamage
  UseCooldownSeconds
```

`axe_basic` ItemDefinition uses `GameplayRef = axe_basic` and a tool category/tag. Inventory owns item possession; the tool domain owns use semantics.

For this vertical slice the player receives/accesses one authored Roblox Tool representing the basic axe. The server never trusts a client-supplied damage number, tool tag, reward, target health, or range.

The client sends only bounded use intent identifying the target node. Server resolves:
- active player/session eligibility;
- alive/usable character state;
- actually equipped approved Axe Tool;
- canonical ToolDefinition from the server registry;
- canonical ResourceDefinition from the node registry;
- target node identity;
- distance/range;
- per-player/per-node rate limit;
- node Active state.

Only then does ResourceNodeService apply the server-owned HarvestDamage.

This does not route tree damage through player `DamageService`, because ResourceNode lifecycle is a different domain. The shared principle reused from Combat is authoritative server construction of damage/effect magnitude.

## 8. Client/server protocol

A dedicated harvest intent RemoteEvent may carry only:

```text
ResourceNodeId
```

No amount, reward, health, tool stats or success claim comes from the client.

Server result/feedback is communicated through presentation-safe events/read attributes. Result codes remain stable machine-readable values.

No per-frame networking.

## 9. Validation and exploit protection

A harvest intent is rejected unless all conditions pass:
- player is an active SessionContext participant;
- character/Humanoid/root exist and character is alive;
- approved Axe Tool is equipped in the character;
- Axe Tool identity maps to canonical `axe_basic` tool definition;
- ResourceNodeId resolves to one registered active node;
- node ResourceDefinition exists;
- tool satisfies RequiredToolTag;
- player-to-node hit anchor distance <= definition InteractionDistance plus a small centralized server tolerance if required;
- cooldown/rate limit has elapsed;
- node has not already depleted in the current CycleSerial.

Unknown IDs, stale nodes, unequipped tools, out-of-range requests and spam are rejected without mutation/reward.

## 10. Multiplayer contention

Resource health/state is shared server state. Hits from multiple eligible players may reduce the same node.

Reward policy for this first prototype: the player whose accepted hit atomically transitions the node from Active health > 0 to Depleted receives the centralized Wood reward exactly once for that cycle.

This is prototype reward ownership, not a final cooperative-loot policy.

Disconnect/death does not reserve a tree or leave a harvesting lock. There is no long-lived per-player ownership lock; only bounded cooldown state is cleaned on PlayerRemoving.

## 11. Canonical Wood reward

Inventory / Loot / Economy adds exactly one real canonical ItemDefinition for `wood`.

On successful depletion, ResourceNodeService calls canonical `InventoryService.Add(player, "wood", rewardQuantity, context)` server-side.

The context identifies the resource-harvest source and node/definition ID using bounded metadata accepted by InventoryService.

No legacy Farming `Player.Inventory` IntValue is created or changed for Wood.

If InventoryService rejects the grant, the service reports an explicit reward failure; it must not silently create a second inventory representation.

## 12. Axe item integration

Inventory / Loot / Economy adds canonical ItemDefinition `axe_basic` with `GameplayRef = axe_basic`.

The physical Roblox Tool is an equipment/runtime representation, not inventory authority. The slice does not implement a full inventory-to-hotbar/equipment persistence system.

The server validates the equipped Tool against server-authored identity/attributes and ToolDefinitions; possessing or renaming a client object is not sufficient authority.

## 13. Tree feedback

World reaction is restrained and replicated from accepted server hits:
- brief trunk/tree hit reaction driven by a replicated hit serial or bounded server event;
- small impact presentation at the node;
- progress/readability through a compact contextual world/client indicator only while relevant;
- depletion visibly changes the node (e.g. controlled fall/fade/stump/depleted presentation);
- respawn restores it;
- successful reward produces `+N Wood` through the approved Notification component/controller language.

Presentation never decides health or reward.

No final VFX/audio art pass is included. Audio is used only if a verified appropriate asset is available; otherwise the architecture permits a silent hook rather than inventing an asset ID.

## 14. UI boundary

UI / UX extends the existing `ReplicatedStorage.UI` architecture. It does not create a second HUD framework and does not migrate FarmingUI.

A small HarvestFeedback controller may consume server/read-model state and reuse Notification for Wood gain. Any progress UI is read-only and contextual.

## 15. Prototype grove placement rule

Implementation will author a small controlled set (not the whole map) on verified playable `Grassblox` ground, outside the inspected bounds of:
- Rebuild/NewBunker;
- farm;
- Scrap piles;
- ZombieSpawns.

Exact positions must be verified in Studio before source authoring and again after Rojo sync. The grove must be easy to reach/read from normal play without obstructing protected content.

## 16. Prototype tuning policy

Permitted temporary values:
- MaxHealth
- Axe HarvestDamage
- RewardQuantity
- RespawnDelaySeconds
- InteractionDistance
- hit/use cooldown

All live in ResourceDefinitions/ToolDefinitions and are labeled prototype tuning. They are not final balance.

## 17. Extension seams intentionally supported

Without changing the service ownership model, future packets may add:
- stronger axes / tool tiers;
- different tree definitions/yields;
- stone/ore ResourceDefinitions;
- biome-specific resource definitions/presentation;
- durability as a separate approved tool-state concern.

None is implemented now.

## 18. Explicit non-goals

No guns, rifle, Dealer, Trader, chest/key systems, other melee catalogue, armor/shields, zombie/wave rewrite, bosses, revive, weather, lobby, biome work, persistence, final art, or Farming migration.

## 19. Architecture acceptance criteria

Implementation may begin only if independent review confirms:
- one ResourceDefinition owner;
- Wood/Axe use the canonical ItemDefinition registry;
- rewards use InventoryService only;
- client cannot construct harvest damage/reward;
- ResourceNodeService owns shared node lifecycle and contention;
- Axe validation is server-side;
- SessionContext is consumed rather than redefining active-player semantics;
- no protected legacy system requires modification;
- UI remains presentation-only;
- the architecture can extend to other resource nodes without a mega-framework.

## 20. Architecture review resolutions

### R-AXE-001 — Canonical Axe possession and runtime equipment bootstrap

Resolved. `axe_basic` has two deliberately separate representations with one authority chain:

1. Canonical possession is owned only by `InventoryService` under ItemId `axe_basic`.
2. A small server-owned prototype equipment/bootstrap adapter ensures the active player has the approved prototype entitlement by calling `InventoryService.Add` only when canonical quantity is absent.
3. Only after canonical possession is confirmed may that server adapter provision the authored Roblox Axe `Tool` into the player's runtime equipment container.
4. The physical Tool carries server-authored identity needed to resolve `ToolDefinitionId = axe_basic`, but Backpack/Character/Tool presence never creates or proves canonical inventory possession by itself.
5. On equip/use, the harvest server validates both the equipped approved Tool representation and canonical `InventoryService.GetQuantity(player, "axe_basic") > 0`.

This bootstrap is a prototype vertical-slice adapter, not the future inventory/hotbar/equipment architecture. It does not grant arbitrary items from the client and does not migrate Farming inventory.

### R-REWARD-001 — Idempotent depletion/reward commit

Resolved. ResourceNodeService owns an explicit server-only reward commit for each `CycleSerial`.

Conceptual terminal transition:

```text
Active
 -> RewardPending { CycleSerial, WinnerPlayer, RewardItemId, RewardQuantity }
 -> Depleted
 -> Respawning
 -> Active(next CycleSerial)
```

Rules:
- The accepted final hit atomically changes `Active` to `RewardPending` and records exactly one winner before any InventoryService grant is attempted.
- Once `RewardPending` is established, all further harvest intents for that node/cycle are rejected. No second player can become winner.
- ResourceNodeService performs the canonical `InventoryService.Add` using the recorded server-owned reward data.
- On successful grant, the same cycle advances to `Depleted` and emits success feedback exactly once.
- If InventoryService rejects/fails the grant, the node remains server-owned `RewardPending`; it does not select another winner, respawn, or issue a second grant implicitly.
- A bounded server retry path may retry the exact same recorded grant for the same winner/cycle. The reward record includes a commit flag/attempt state so successful commit cannot be applied twice.
- Player disconnect during RewardPending does not transfer the reward to another player. The pending record remains tied to the winning player identity for the bounded prototype retry window; unresolved failure is surfaced to server diagnostics rather than inventing an alternate inventory representation.

The prototype expects canonical Wood grant to succeed for an active player under normal conditions. This failure policy exists to preserve exactly-once semantics, not to introduce persistence or an offline reward mailbox.
