---
name: MyGame — Dungeon Crawler
description: Core project facts for the top-down dungeon crawler at /Users/origan/Desktop/claude code/MyGame
type: project
---

Top-down dungeon crawler built with Phaser 3 (Arcade physics, Canvas/WebGL), Vite (esbuild), and a Node.js WebSocket server for multiplayer (ws package). No TypeScript, no external asset pipeline beyond esbuild.

**Stack summary:**
- game.js (~4370 lines): all scene logic — BootScene, MenuScene, PartyScene, InstructionsScene, ClassSelectScene, MainScene
- player.js: pure-data Player model (inventory, equipment, XP, hotbar)
- enemy.js: Enemy class with 8 types (slime, skeleton, archer, mage, bomber, tank, spawner, boss)
- mapgen.js: seeded Mulberry32 PRNG, 50×35 tile grid, 8–12 rooms, L-shaped corridors
- map-manager.js: thin wrapper around mapgen with a carve() method
- chest.js: Chest entity (loot table, proximity open, visual states)
- asset-manager.js: procedural Canvas-drawn item icons (weapon, armor, consumable, spell, passive)
- multiplayer.js: WebSocket client (party create/join, position sync, enemy sync)
- assets/data/items.json: 25 items across weapon/tool/armor/consumable/spell/passive types

**Current feature set:**
- 3 classes (Warrior, Mage, Rogue) with class-specific perks and starting loadouts
- 8 enemy types with distinct AI (melee, ranged, exploding, tank, spawner)
- Procedural multi-floor dungeons with floor themes (Stone, Overgrown, Lava, Void) at floors 1/4/7/10+
- 4 room types: spawn, portal, shop, trap, treasure (+ optional boss lair floor 7+)
- Core abilities: melee swing arc, fireball (3-bolt spread), lightning strike, void ball, dash
- Fog of war + torch glow system (hard mode only); easy mode = full visibility
- Inventory (10 slots), 8-slot hotbar, 3 equipment slots (head, chest, main_hand)
- Passive item absorption (rings) that permanently buff player stats
- Level-up perk choice (12-perk pool, pick 3 each level-up)
- Kill streak combo system, lifesteal, HP-per-kill perks
- Achievement system (11 achievements), high score tracking (top 5 runs)
- Auto-save to localStorage (every 5s + on floor transition)
- Procedural Web Audio music (bass heartbeat + chord cycles + dread accents)
- WebSocket multiplayer: up to 4 players, party code system, host controls AI

**Architecture notes:**
- All game logic in a single MainScene class inside game.js — monolithic but functional
- Item loot drops from enemies are fully random (any item from registry) — no drop tables yet
- Shop re-rolls items on every open
- Portal unlocked when all enemies in _enemies array are dead (optional bosses excluded)
- Tilemap built with pure graphics objects (no Phaser tilemap/tileset API)
- Pixel art mode on (pixelArt: true, roundPixels: true)
- Fixed 1280×720 canvas with FIT scale mode

**Why:** This is the user's primary active game project. It is already playable end-to-end.
**How to apply:** When suggesting features, respect the monolithic game.js pattern (do not propose splitting into many files unless explicitly asked). Prefer Phaser 3 Arcade physics approaches over Matter.js — the project uses Arcade exclusively.
