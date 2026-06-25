---
name: project_dungeon_crawler
description: Architecture and key implementation details for the top-down dungeon crawler game in this repo
type: project
---

Top-down dungeon crawler, Phaser 3 + Arcade Physics + Vite. Single-player + multiplayer (WebSocket). ~4900 lines in game.js after 2026-03-27 bugfix batch.

**Engine / stack:** Phaser 3, Arcade Physics (no Matter), Vite dev server, no external game libs.

**File layout:**
- `src/game.js` — all scene logic (MainScene + menus), ~4900 lines
- `src/enemy.js` — Enemy class with AI state machine
- `src/player.js` — pure data model (no Phaser deps), inventory/equipment/stats
- `src/mapgen.js` — seeded procedural dungeon generator; dynamic size via level param
- `src/map-manager.js`, `src/chest.js`, `src/asset-manager.js`, `src/multiplayer.js`
- `assets/data/items.json` — all item definitions (weapons, armor, consumables, passives/relics, spells)

**Key constants (game.js top):**
- PLAYER_SPEED=220, PLAYER_ACCEL=1500, PLAYER_DRAG=1200
- SWING_RANGE=95, SWING_ARC_DEG=68, KNOCKBACK_FORCE=390, ATTACK_COOLDOWN=550
- DASH_SPEED=820, DASH_DURATION=150, DASH_COOLDOWN=1400
- ATTACK_LUNGE_SPEED=260, ATTACK_LUNGE_DURATION=80 (game-feel)
- HIT_STOP_DURATION=45, HIT_STOP_TIMESCALE=0.04 (game-feel)
- DASH_GHOST_COUNT=4, DASH_GHOST_INTERVAL=28 (game-feel)
- HOTBAR_SLOTS=8, SLOT_SIZE=54, hotbar icon display size=34x34

**Inventory:** player.maxInventorySlots=20 (raised from 10 in 2026-03-27 batch)

**Map system (after 2026-03-28):**
- generateDungeon(seed, level=1) — dynamic size: cols=min(28+(level-1)*4,80), rows=min(20+(level-1)*3,56)
- Floor 1: 28×20 = 896×640px world. Floor 10: ~64×47. Cap: 80×56.
- Room count: min(4+floor(cols/8), 12) + level bonuses. Floor-1 target ≈7 rooms.
- Room dims: w in [4, min(8,floor(cols/4))], h in [3, min(6,floor(rows/4))]
- Returns { map, rooms, cols, rows }
- MapManager(seed, dungeonLevel) — stores cols/rows, exposes getMapSize()
- All world-space uses of MAP_COLS/MAP_ROWS in game.js replaced with mapManager.getMapSize()
- Minimap T = max(1, floor(min(80/cols, 60/rows))) — scales down on large maps
- Level 10+: +1 bonus room; Level 15+: +1 more room + third cross-connection corridor

**Legendary item effects (added 2026-03-27):**
- sword_doomshard: sets enemy._burning=3, enemy._burnTimer=600 on each melee hit; enemy.update() ticks 4 dmg every 600ms
- sword_voidedge: pierce already worked — _doAttack loop has no break
- chest_voidplate: _playerTakeDamage(amount, attacker=null) reflects round(mitigated*0.15) back to attacker

**Enemy burn state (enemy.js, added 2026-03-27):**
- _burning (ticks remaining), _burnTimer (ms until next tick)
- Tick fires every 600ms in update() before AI, deals 4 dmg via takeDamage(4,0,0)
- Applied only by sword_doomshard via game.js _doAttack

**Relic hooks (all verified working):**
- berserker: _doAttack scales dmg: <25% hp = 1.8x, <50% = 1.4x
- stormCrown: lightning chains to 2 extra enemies at radius 1.0–2.2x
- shadowStep: dash leaves Graphics clone, deals 8 dmg to enemies within 60px
- voidHeart: void ball hit heals 3 HP per enemy hit
- deathWard: once-per-floor survive killing blow at 1 HP (_worldState.deathWardUsed resets on floor entry)
- bloodPact: +4 HP per kill

**_playerTakeDamage signature:** _playerTakeDamage(amount, attacker=null)
- Enemy melee callsites pass the enemy reference; arrow/trap calls pass null (nearest-enemy fallback)
- Voidplate reflect uses a clean for-loop to find nearest enemy (not Object.assign on enemy objects)

**window.onerror removed (2026-03-28):**
- index.html no longer shows the startup-hint overlay on JS errors
- Real errors are visible in the browser console again

**Biome colors fixed (2026-03-28):**
- getFloorTheme() now has clearly distinguishable palettes: Stone Crypt (blue-grey), Overgrown Ruins (mossy green), Lava Depths (ember red), Void Realm (cosmic purple)
- Previous values were near-black (e.g. 0x0a1e10) and appeared invisible

**_buildTorchTexture: do NOT remove/recreate on scene restart (2026-03-28):**
- The fix is to early-return if the texture key '__torch__' already exists
- Removing a canvas texture still referenced by _fogRT/_darknessRT crashes WebGL on floor 3+
- Radius is constant (TORCH_RADIUS), so reuse is always safe

**Enemy _lastFlash init:**
- Must be null (not undefined) so the boolean !== null comparison works correctly on first update() call
- The constructor calls _draw(false) directly, bypassing the cache check — _lastFlash starts null and is correctly set to false/true from that point on

**Passive items (type='passive', slot=null):**
- Absorbed on pickup via _collectWorldItem → _applyPassiveItem (no inventory slot used)
- If somehow on hotbar: _equipFromHotbar has a 'passive' branch that absorbs and clears slot
- _applyPassiveItem modifies player baseStats directly and sets _worldState.relics flags

**Toast system:**
- _showToast cancels pending _toastClearEvent before setting new 2200ms auto-clear
- Does not fire during _levelIntroActive

**Critical architectural notes:**
- physics.world.timeScale uses INVERSE scale in Arcade (higher = slower). time.timeScale is direct.
- Use window.setTimeout for real-wall-clock timing when time.timeScale is manipulated.
- Player physics body: this._physBody on this._playerContainer (Container with physics.add.existing)
- _hitStopActive flag prevents stacking hit-stops.
- Multiplayer: guest clients interpolate enemy positions from host sync; only host runs AI.
- Non-ASCII chars in add.text() corrupt Phaser canvas glyph atlas in pixelArt mode — ASCII only.
- player.equip() already removes item from inventory via removeItem before adding old item back.
- _paused = true during both pause menu and inventory; both reset it to false on close.
- _checkRoomEntry is called every frame from update() after player position sync.

**Wall physics (current — 2026-03-28 final fix):**
- Wall bodies use `this.make.image({ x, y, key: '__wt__', add: false })` — the `add: false` flag keeps the object OFF the display list entirely
- `this.physics.world.enable(img, STATIC_BODY)` registers the broadphase body independently of the display list
- `img.body.setSize(TILE_W, TILE_H)` + `img.body.reset(cx, cy)` called AFTER `_wallGroup.add(img)` — must be after add in case group's createCallbackHandler triggers refreshBody
- `_wallGroup.refresh()` intentionally omitted — would re-derive body bounds from the 1×1 '__wt__' texture, resetting every body to 1×1
- Physics world runs at `fps: 120` in the arcade config AND `this.physics.world.setFPS(120)` in create() — prevents DASH_SPEED=820 tunneling through 32px corridors

**Why display list matters for walls:**
- `this.add.zone()` silently adds to the scene display list — 500-2900+ invisible items on floors 3-cap
- On floor 3 (36×26 map), ~600 zones; on floor cap (80×56), ~2900 zones
- All display-list items are iterated by Phaser's renderer every frame; the batch stall on first frame presented as a completely black screen
- `make.image(add:false)` eliminates this with zero physics regression — body is registered in broadphase, colliders work identically, _breakWall destroy path (`physics.world.remove(wall.body.body); wall.body.destroy()`) is unchanged

**Why:** Project was at Phase 5 (procedural dungeons + progression) when improvements were made.
