---
name: Dungeon Crawler — Project Context
description: Core technical and visual facts about the top-down dungeon crawler game
type: project
---

Phaser 3 top-down dungeon crawler with procedurally generated dungeons (MAP_COLS x MAP_ROWS tile grid). All graphics drawn via Phaser Graphics API and Canvas — no sprite sheets. pixelArt: true. Background base is #0d0d1a.

**Tech stack:** Phaser 3, Arcade Physics, Vite, procedural Web Audio.

**Canvas size:** 1280x720.

**Biomes (by floor depth):** Stone (1-3), Overgrown (4-6), Lava (7-9), Void (10+).

**Enemy roster:** slime, skeleton, archer, mage, bomber, tank, spawner, boss.

**Player sprite:** procedural pixel-art figure — violet/purple body (0x5b21b6), golden head (0xfbbf24), armor drawn on top via _drawArmorGfx / _drawWeaponGfx.

**HUD (current state):**
- HP bar: top-left, 200x20px, rounded rect, dark navy track (#0f172a), green/amber/red fill
- Level text: below HP bar, monospace 12px, purple (#a78bfa)
- Stat text: below level, monospace 10px, grey (#6b7280)
- Floor display: top-center, monospace 16px, purple (#a855f7)
- Equipment panel: top-right, monospace 11px, grey (#9ca3af)
- Hotbar: bottom-center, 8 slots at 54px each, dark panel (#060614)
- Minimap: bottom-right above hotbar, 2px-per-tile scale
- Loot log: top-right panel, 226x190px

**Rarity colors (current):** common #9ca3af, uncommon #22c55e, rare #3b82f6, epic #a855f7, legendary #f59e0b.

**Why:** This is the established baseline to reference when proposing visual upgrades. All proposals must work within the procedural Graphics API constraint.

**How to apply:** Any new visual direction must be deliverable as hex color values and drawing instructions, not image assets. Proposals should reference specific variables and functions the developer can update directly.
