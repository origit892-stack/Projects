# Idea2World — Research and Design Foundation

> Written for 5.0 and still the source of the design principles 6.0 applies.
> Where they live in code: `research/reference_library.py` (principles per reference),
> `research/game_research.py` (archetypes, district and landmark vocabularies),
> `research/style_analyzer.py` (turns a style + theme into one art direction).

## Purpose
Idea2World is a concept-to-Roblox world and game-design architect. It should not blindly reproduce a popular game's map, UI, characters, or proprietary assets. It extracts reusable design principles and applies them to a new concept with its own art direction.

## Reference teardown: Throw Food for Animals
Public game listing snapshot retrieved 20 Nov 2026: simulation / tycoon hybrid, 5-player server, launched 18 Sep 2026, updated 17 Nov 2026, approx. 299.7M visits and 305.6K players at retrieval, 94% rating. Its public description states: throw food as far as possible; attract and collect animals from different areas; earn money from animals; buy better food for rarer animals; train on pull-up stands to gain Throw Power; reach new areas with stronger and rarer animals. Publicly listed passes include 2x Training Power and 2x Cash.

### What the design is doing
- **One-sentence promise:** a physical action (throwing) produces discovery (animals), collection and passive income.
- **Core loop:** train throw power → buy better food → throw for distance → reach/attract animals → collect → earn passive cash → upgrade → unlock next biome.
- **Progression ladder:** power / food quality / throw distance / animal rarity / income / area access.
- **Map language:** the distance mechanic should be spatially legible. The player should see the next habitat and understand that throwing farther is the route to new content.
- **Audience hypothesis:** broad casual and collection-focused Roblox players. The loop is understandable quickly, supports short sessions and gives visible long-term collection goals.
- **UI needs:** large action affordance, power/distance feedback, currency, next area gate, rarity reveal, collection index and upgrade affordances. Keep the action lane unobstructed on mobile.
- **Art opportunity:** each area can have a strong habitat identity and a distinct silhouette, while food, animals and rarity effects share one consistent visual language.
- **What not to copy:** exact animal designs, map layout, icons, UI composition, text, prices or proprietary effects. Reuse the abstract loop, not the expression.

## Other reference patterns studied

| Experience / family | Useful design lesson | Idea2World application |
|---|---|---|
| Grow a Garden | Cozy, legible repeat actions, growth feedback, visible collection | Plant/harvest loop profile, growth-stage props, personal plots and shared plaza |
| Adopt Me! | Social ownership, collection, trading and expressive spaces | Collection hubs, display habitats, social meeting landmarks, readable inventory UI |
| Pet Simulator-style collection games | Clear rarity ladder, repeated reward reveal, upgrades and collection completion | Rarity hierarchy, reward stage, collection book and upgrade station placement |
| 99 Nights in the Forest | Safe hub vs dangerous exploration, escalating threat, co-op objectives | Safe-zone / danger-band map topology, expedition routes and resource landmarks |
| Brookhaven RP | Immediate social affordances, familiar spaces and low-friction roleplay | Compact districts, meeting points, activity clusters and minimal HUD |
| RIVALS / arena action | Readable lanes, fair sightlines, fast rounds and legible ability feedback | Combat-lane topology, spawn safety, cover and clean VFX hierarchy |
| Murder Mystery 2 | Simple round structure, social tension and clear role/state communication | Round hubs, spectator areas, objective clarity and role-aware UI requirements |

These are design-pattern summaries, not exhaustive game teardowns or claims about internal analytics.

## Cross-game principles used by the engine
1. First satisfying action should arrive quickly; tutorial copy should not block play.
2. Show one short-term goal, one medium-term unlock and one long-term collection/progression goal.
3. Make map topology communicate the core loop: lanes for throwing, districts for roleplay, radial danger bands for survival, balanced routes for PvP.
4. Mobile-first controls: large touch targets, minimal text, safe HUD margins and unobstructed central play area.
5. Effects communicate reward, rarity, danger or interaction state; ambient VFX must not compete with critical gameplay.
6. Keep the world visually coherent: palette, material families, silhouette rules, light temperature and UI motion must agree.
7. Performance budget is a design constraint: avoid unbounded particle rates, excessive transparent layers and thousands of independent moving parts.

## Current engine coverage in 5.0
- Genre-aware design brief: core loop, systems, audience hypothesis, map requirements, UI/UX direction and session design.
- Art-direction profiles: Classic Roblox Stud, Stylized Low Poly, Fantasy Cinematic, Cosmic Art and Clean Sci-Fi.
- Existing procedural terrain, biomes, routes, landmarks, themed prop clusters, lights, particle emitters and Luau export.
- Hermes MCP analysis tool: `analyze_game_idea`, in addition to the world and asset generation tools.

## Honest production boundary
5.0 still generates procedural Roblox geometry and built-in particle systems. It does not yet synthesize bespoke production-grade MeshParts, UV-unwrapped texture atlases, custom PBR maps, rigged creature animation clips, or fully implemented server-authoritative gameplay systems. The generated design brief specifies these systems and art requirements; it is not equivalent to their finished implementation. A true production pipeline for those deliverables needs dedicated mesh/texture/animation generation and import validation, plus Studio runtime and device testing.
