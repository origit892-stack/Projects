# MAP DESIGN — Containment Deck 07 (visual & spatial spec, exact studs)

> Status: **Design authority for Stage 1** (MapGenerator target + art spec). Derived from GDD v3 §5 (grid/rules), §20 (art/palette), §4.5 (peak moments). Where the GDD is silent, this doc decides — items marked **[WORLD-V1]** are worldbuilding proposals that need user sign-off.
> Base language of all in-game text: **English (LTR)** per DECISIONS. RTL: signs flip to Start/End automatically, numbers stay LTR.

---

## 1. What the map is about (the story it tells)

The map is **Containment Deck 07** — a sealed industrial platform floating in the dark, built around the **Core**: a quantum power lattice that feeds the whole region's grid. **[WORLD-V1]**

- **What happened:** a quantum collapse event hit this sector (the signs will say it). The Core was damaged and sealed inside a containment ring. It now runs at **12% output**.
- **What is happening:** the collapse leaks through the ring at **breach vectors** (the spawn gaps). The enemies are not aliens — they are **manifestations of the collapse itself**: entropy given shape, arriving in waves. **[WORLD-V1]** That is why the final boss is called **Core-Eater** — it is the collapse that finally learned to eat power sources.
- **Who is in charge:** A.R.I.A., the grid's AI, speaks from projector nodes on the deck. The player is the **Operator** with "A.R.I.A. clearance" — authorized to build and fuse towers on the deck.
- **What is at stake:** the Core is the region's power. If it dies, the grid dies. Every sign, scar, and cable on the map tells that story — the player should *feel* the event before a single tutorial line explains it.

**The map has four layers of storytelling:**
1. **Static** — scars, signs, cables, props (the event that happened).
2. **Live** — Core % counter, wave ticker, pylon status lights (the event in progress).
3. **Escalating** — the deck visibly degrades across the 3 Acts (cyan→amber→red; the ring tightens).
4. **Climactic** — boss waves: portals flare, gates open, the Core's pulse quickens, A.R.I.A.'s hologram turns from calm to panic.

---

## 2. The world in exact studs

**Coordinate system:** origin (0,0,0) = center of the Core. X = east, Z = south, Y = up. The 13×13 tile grid is centered on origin; tile `(c,r)` (c,r ∈ 0..12) has its center at `((c−6)×4, (r−6)×4)` studs. The Core occupies tiles (5,5)–(6,6) = studs −8..8 on both axes.

### 2.1 Platform & void
| Element | Size/position | Notes |
|---|---|---|
| Main deck | **80×80 studs**, top at y=0, slab 2 studs thick | brushed dark slate `#121A2B`, subtle 4-stud grid micro-texture (5% contrast) |
| Void below | infinite, color `#0B0F1A` | slow particle field (20 particles, 0.02 studs/s drift) + faint Core-light reflection on deck edge |
| Deck edge | 1-stud bevel around the 80×80 | under-glow strip: emissive `#19D3FF`, 0.4 stud band, 25% brightness — the deck "floats" |

### 2.2 Containment ring (the wall)
| Element | Size/position | Notes |
|---|---|---|
| Wall ring | centered at **±34 studs** (8 studs outside the 52-stud grid edge) | 6 studs tall (y 0→6), 0.8 thick |
| Panels | 8 studs long, 0.4-stud gaps between panels | `#121A2B` panels, seam strips emissive `#19D3FF` at 30% (dim — never flashes) |
| Top rail | 0.3 stud continuous strip on the wall top | white `#FFFFFF` at 40% |
| Perimeter length | 136 studs per side minus gaps ≈ 17 panels/side | 4 spawn gaps total (1 active by map, see §2.4) |
| Corner pylons | 4, at (±34, ±34) | base 3×3×1, shaft 1.5×1.5×12, antenna 0.4×0.4×4, status sphere r=0.5 |
| Pylon status light | green (Act I) → amber (Act II) → red (Act III) | 1 PointLight each, range 12, color follows status |
| Coolant channel | between wall (±34) and deck edge (±40): 2-stud-wide strip | glass walls 1.5 studs tall, emissive liquid `#19D3FF` 15% + bubble VFX (10 particles). Shifts cyan→amber→red with Acts |

**Wall purpose (design intent):** the ring makes the deck read as *sealed* — everything hostile comes from the gaps, everything friendly is inside. It is also the backdrop: 6 studs of dark paneling + neon seams puts enemies (dark, rim-lit) on a mid-dark surface with high contrast.

### 2.3 The Core (center)
| Element | Size/position | Notes |
|---|---|---|
| Core base | 8×8 stud plinth, y 0→1, at center | brushed metal `#1A1F2E`, 4 corner clamps 0.5 studs |
| Vessel | 2×2 stud column, y 1→11 | dark housing with 4 vertical emissive strips (white/gold, pulse with Core HP) |
| The Core (orb) | icosahedron r=0.75, y=6, inside a glass sphere r=1.2 | white `#FFFFFF` core, `#FFC857` pulse; rotation 0.5 rad/s; **pulse rate rises as HP drops** (0.5Hz at 20 HP → 2Hz at ≤5 HP — under the 3Hz flash limit) |
| Support pylons | 4, at the base corners | 1×1×4 studs, 6 cable parts curving to the vessel |
| Shield ring | disc r=5.5, y=1.2, 0.2 thick | transparent cyan; brightens 3s during Emergency Shield ability |
| HP ring | 20 segments (one per HP unit) around the vessel base, 0.3×0.6 studs | lit = white/gold; lost = dark red, faint flicker (0.5Hz). The Core HP is read off the structure itself, not a floating bar |
| Core hologram | holo-projector at y=12 (2×2 cone, transparent) | shows `CORE OUTPUT 12%` → live Core-integrity % — the story device: the number the player protects is literally on the structure |
| Breach FX | on any leak: red vignette (0.5s, disable-able), camera shake ≤1 stud, nearest pylon light → red for 3s | GDD §20.5 |

### 2.4 Spawn points (breach vectors)
- **Positions:** Spawn-N (north wall, tiles cols 5–6), Spawn-W (west wall, rows 5–6), Spawn-SE (southeast corner region, unlocks with map modifiers/biomes). Each = an **8-stud gap** (2 tiles) in the wall ring.
| Element | Size | Notes |
|---|---|---|
| Portal ring | torus, 6 studs diameter, 5 studs tall, in the gap | dark housing, inner disc 4 studs, red `#FF3B5C`, rotates 2 rad/s |
| Portal fog | red VFX inside the gap | 15 particles, budget per active portal |
| Flanking pylons | 2 per gap, 1.5 studs tall | red emissive tips |
| Ground hazard stripes | 0.2-stud decals in the gap | yellow/black chevron, pointing inward |
| Pre-spawn telegraph | boss waves: portal flares +2s with a low horn (SFX) | GDD §4.5 |
| Breach scars | around every gap: dark scorch decal (6×6 studs) + 2 cracked-tile parts | the ring was breached *before* — history in the floor |

### 2.5 The path
| Element | Size | Notes |
|---|---|---|
| Path surface | **2 tiles wide = 8 studs**, raised 0.25 (y 0→0.25) | `#1E2A45` — *brighter than enemies* (`#1A1F2E`) so silhouettes read; GDD §20.2 rule 3 |
| Curb | 0.3-stud raised edge both sides | emissive `#19D3FF` 20% |
| Lane arrows | 4×0.5 stud floor decals every 8 studs, pointing toward Core | `#19D3FF` 15%; brighten to 60% at Speed ×2 (GDD §5.6) |
| Path length | 40–120 tiles (GDD §5.2) | reference maps: A=42, B=40, C≈60 (see §3) |
| Enemies on path | 1.5–3 studs tall bodies, dark + rim light | unique silhouette per archetype (art spec §9) |

### 2.6 Pads (build sites)
- **Count:** 1–3 per path tile → **45–70 per map** (GDD §5.1). Every pad sits on a non-path tile **adjacent (4-way) to a path tile**.
| Element | Size | Notes |
|---|---|---|
| Pad plate | 4×4 studs (1 tile), raised 0.4 (y 0→0.4) | `#121A2B`, corner anchor bolts as *decal* (not parts) |
| Selection ring | 0.2-wide, 0.15-high ring inset 0.3 studs from the plate edge | **affordable → white, pulses 1Hz + small holo up-arrow; unaffordable → gray 30%; occupied → off** (GDD §5.6) |
| Pad ID stencil | 0.6-stud decal, corner | `P07` etc. — legibility aid + flavor |
| Arena strong pad (T2) | gold ring instead of white + 2 extra bolt decals | GDD §5.3 #11 |
| Range disc (tower selected) | flat transparent disc, radius = tower range in studs (Turret: 5 tiles = **20 studs**) | thin emissive edge; **shown only while selected** (GDD §5.6) |

### 2.7 Towers (how builds read on the map)
| Chassis | Shape (studs) | Read |
|---|---|---|
| Turret | base 3×3×0.5 + slim barrel 0.5×0.5×3 | small, precise |
| Cannon | base 3.5×3.5×0.5 + stubby barrel 1.2×1.2×1.5 on pedestal | heavy, slow |
| Coil | base 3×3×0.5 + 3 stacked rings + top sphere r=0.5 | Tesla coil, crackle VFX when firing |
| Prism | base 3×3×0.5 + glass pyramid 2×2×2.5, crystal at apex | beam emitter |
| Totem | base 3×3×0.5 + monolith 1×1×4 + holo ring r=1.5 | support — never fires; aura shown as 0.3-stud holo floor glow (3 studs radius) |
| Gem slots | 0.6-stud glowing gem(s) on the tower head, **element color** (GDD §20.1) | T2 = 2 gems side by side; T3 = 3 + a floating apex crystal (0.4 studs, slow bob); element color = effect color, always (GDD §20.2 rule 2) |
| Tower budget | 5–8 parts each | 30 towers max ≈ 240 parts |

---

## 3. Reference path layouts (13×13, tile coords c=0..12 E-W, r=0..12 N-S)

Legend: `P` path tile (2-wide lanes as drawn) · `C` Core (tiles 5–6 × 5–6) · `S`/`W` spawn gap in the ring · `F` fork · `M` merge · `.` empty deck (pads where adjacent to path)

### Map A — "The Ring Run" (default; single north spawn; 42 path tiles)
```
        0 1 2 3 4 5 6 7 8 9 10 11 12
 r0     . . . . . S S . . . . . .     S: north spawn (cols 5-6)
 r1     . . . . . P P . . . . . .
 r2     . . . . . P P P P P . . .
 r3     . . . . . . . . . P P . . .
 r4     . . . P P P P P . P P . . .
 r5     . . . P P C C . . . . . . .
 r6     . . . P P C C . . . . . . .
 r7     . . . P P P P P P P P . . .
 r8     . . . . . P P . . P P . . .
 r9     . . . . . P P . . P P . . .
 r10    . . . . . P P P P P . . . .
 r11    . . . . . . . . . . . . . .
 r12    . . . . . . . . . . . . . .
```
**Trace:** N-gap → down cols 5–6 → right r2 → down cols 8–9 → left r4 → down cols 3–4 → right r7 → down cols 8–9 → left r10 → up cols 5–6 → Core (south). No loops, no self-cross. **Character:** readable first run — the whole snake is visible at default zoom; teaches the loop without tricks. Pads concentrate in the two large empty halves (rows 8–12 W, rows 0–4 E) → early build choices are spatial.

### Map B — "Double Gate" (two spawns: N + W; one fork that re-merges; 40 path tiles)
```
        0 1 2 3 4 5 6 7 8 9 10 11 12
 r0     . . . . . S S . . . . . .     S: north spawn (cols 5-6)
 r1     . . . . . P P . . . . . .
 r2     . . . . . P P P P P P . .     F: fork
 r3     . . . P P . . . . P P . .
 r4     . . . P P . . . . P P . .
 r5     W P P P P . . . . P P . .     W: west spawn (cols 0-1)
 r6     . . . P P C C . . P P . .
 r7     . . . P P P P P P P P . .     M: merge row → Core (cols 5-6)
 r8     . . . . . . . . . . . . . .
```
**Trace:** N-gap → fork at r2 into west lane (cols 3–4) and east lane (cols 9–10); W-gap joins the west lane at r5; both lanes merge at r7 under the Core. **Character:** pressure from two directions; the fork forces split defense (AoE on the merge row is the optimal read) — this is the map that teaches *spatial economy*.

### Map C — "The Long Way" (single N spawn, S-coil, ≈60 tiles, template)
Long double-U: N spawn enters top-right, sweeps the full width top, drops down the west edge, crosses the bottom, climbs the east edge, then coils once through the middle band (rows 4–8) before arriving at the Core from the south. No forks. **Character:** maximum path length → maximum pad count (up to ~70) → the "build a lot, build smart" map; mid-map it carries a **Bridge** over the coolant channel (visual landmark) and a **Tunnel** section (sensor dead-zone) as its set-pieces. *(Exact tile map generated at Stage 1 by MapGenerator per GDD §5.4 rules; the template defines character, the generator enforces the 40–120 tile rule.)*

**Run-start choice:** the 3 map options offered per run are A/B/C permuted across biomes, with the biome's **known modifier** shown before the run (GDD §4.2 step 1) — e.g. "Frozen Archive — freeze durations +10%".

---

## 4. Tile visuals (the 12 tile types, GDD §5.3)
| Tile | Visual on the deck |
|---|---|
| Straight / Curve | standard path lane; curve = 45° rounded join, same surface |
| Fork (F) | Y-split: 1-stud chevron divider at the fork apex; both lanes glow; gold edge trim (it is an *opportunity* tile) |
| Merge (M) | inverse chevron; both lanes converge; white flash 0.3s when a wave merges through it |
| Shortcut | diagonal ramp segment (0.25→0.5 rise), **gold trim** on curbs (economy color `#FFC857`) |
| Bridge | path crosses the coolant channel on a 2-stud arch, glass side panels, red warning lights at both ends |
| Tunnel | arch portal 4 studs tall over the lane; interior is *black* — enemies vanish inside (GDD §5.3); "NO SIGNAL" sign above the mouth |
| Trading Post | small kiosk beside the path: 2×2×3 counter, holo sign "EXCHANGE", gold-light |
| Gold Mine | ore cluster (3 crystals 1.5 studs) + mini crane arm beside the path, +120 gold burst VFX on placement |
| Relic | holo-shrine: 1-stud pedestal + floating 0.8-stud artifact (slow rotation), purple glow |
| Arena | reinforced pad zone: gold ring 2 pads wide, hazard bollards |
| Boss Gate | 3-stud-tall gate across the path just before the Core approach; red core-symbol plate; **opens (slides to the sides) with a horn when a boss wave starts** |

---

## 5. Signs — full text list (in-game, English base)

Physical plates: 2×0.5×0.1 studs, `#1A1F2E` with white text (0.3-stud letters). Holo signs: transparent 4×1.5 panel + emissive text, cyan at 80%.

| # | Location | Type | Text |
|---|---|---|---|
| 1 | Deck, north of Core (large holo, 8×3) | holo | `CONTAINMENT SECTOR 07 — CORE PERIMETER` |
| 2 | Under #1 | holo small | `A.R.I.A. GRID CONTROL — OPERATOR AUTHORITY ACTIVE` |
| 3 | Each spawn gap (red plate) | plate | `⚠ BREACH VECTOR — HOSTILE WAVE INBOUND` |
| 4 | West wall, mid | plate | `QUANTUM COLLAPSE EVENT: T-0 — SEAL PROTOCOL ENGAGED` |
| 5 | Core pylons (×4) | plate | `CORE OUTPUT 12% — ESSENTIAL LOADS ONLY` (the % is **live**: it is the Core integrity) |
| 6 | Deck, west of Core (holo) | holo | `AUTHORIZED TOWERS ONLY — FUSION PERMITS REQUIRED` |
| 7 | Trading post | holo small | `GRID TRADE POST — EXCHANGE ACTIVE` |
| 8 | Gold mine | plate small | `ORE EXTRACTION — YIELD +120` |
| 9 | Relic | holo small | `UNIDENTIFIED ARTIFACT — PROTOCOL R-1` |
| 10 | Tunnel mouth | plate small | `SENSOR DEAD ZONE — NO SIGNAL` |
| 11 | Arena | plate small | `STRESS FIELD — TIER 2 RATED` |
| 12 | Boss Gate | plate red | `⚠ CORE INTEGRITY CHECK — STAY BEHIND LINE` |
| 13 | Floor stencils (decals, 0.5 studs) | decal | `DO NOT CROSS` (line around Core), `LZ` (spawn gaps), lane arrows |
| 14 | Holo-ticker (scrolling band, 12×0.6, west of Core) | holo | A.R.I.A. live lines — see §6 |
| 15 | Corner pylons (×4) | plate small | `P-01`…`P-04` + status light |
| 16 | SE wall (only if Spawn-SE active) | plate red | `⚠ BREACH VECTOR 3 — CONTAINMENT FAILING` |

**Ticker script (rotates every 6s, calmer in Act I, faster in Act III):**
- `SCANNING… WAVE 07 INBOUND — EST. MASS 695u — RECOMMEND: FUSION`
- `CORE INTEGRITY 84% — REPAIR ADVISABLE`
- `PADS FREE: 12 — TOWERS ACTIVE: 7`
- `GOLD RESERVE NOMINAL — REROLL ADVISABLE? A.R.I.A. HAS NO OPINION.`
- (Act II, first appearance) `A.R.I.A. NOTE: the collapse is learning our patterns. So should we.`
- (Act III, first appearance) `A.R.I.A. NOTE: I'm fine. I'm only an artificial intelligence. Probably.` *(the one allowed irony — GDD §14.7)*

---

## 6. How the map escalates (live state per Act)
| State | Act I (1–20) | Act II (21–35) | Act III (36–50) |
|---|---|---|---|
| Pylon lights | 4× green | 2 amber, 2 green | 4× red |
| Coolant channel | cyan 15% | amber 20% | red 25% + faster bubbles |
| Wall seams | cyan 30% | cyan 40% | red 30%, pulse 1Hz (never >3Hz) |
| Core orb pulse | 0.5Hz | 1Hz | 1.5–2Hz |
| Ticker speed | 6s/line | 4s/line | 2.5s/line |
| Horizon haze | none | 5% red, NE only | 15% red, all sides (the collapse spreading) |
| Boss waves | portal flare +2s, horn | + gate opens, camera −2° | + red vignette pulse, A.R.I.A. holo panic |
| Music (GDD §20.4) | Build layer | + Combat layer | + Boss layer; Victory on wave 50 |

---

## 7. The six biomes (same deck skeleton, different skin + modifier, GDD §5.7)
The layout, studs, signs, and mechanics never change between biomes — only materials, palette accents, props (3–4 per biome, ≤30 parts), and the modifier.
| Biome | Material story | Signature props | Modifier |
|---|---|---|---|
| **Neon Foundry** (S1) | industrial neon factory floor | conveyor debris ×3, static robot arm, spark VFX at 1 cable | lightning damage +10% |
| **Frozen Archive** (S1) | cryo-library: frost on rails, ice glaze on glass | ice crystals on wall panels ×6, holographic index cards ×4 | freeze duration +10% |
| **Acid Gardens** (S2) | biotech greenhouse: bio-luminescent vines on panels | vines ×8 (green glow), spore drift (10 particles) | acid damage +10% |
| **Magma Core** (S2) | volcanic reactor: glowing cracks in the deck | crack decals ×12 (orange emissive), ember drift, heat shimmer (VFX-light) | fire damage +10% |
| **Void Reef** (S3) | crystal void: black glass, deep purple fog | floating crystal shards ×8 (slow rotation), dense fog | void damage +10% |
| **Solar Citadel** (S3) | golden solar temple: white marble rails, lens beams | sun panels ×4, 2 thin lens light-beams | gold +5% |

Base palette (all biomes, GDD §20.1): bg `#0B0F1A`, surface `#121A2B`, grid `#19D3FF`, elements fire `#FF6B2C` / frost `#59D8FF` / acid `#7CFF4F` / lightning `#FFD84D` / earth `#C08A5A` / void `#B45CFF`, Core white+`#FFC857`, danger `#FF3B5C`, enemy `#1A1F2E`.

---

## 8. Lighting, performance & readability budget
- **Lights (≤8 total):** 1 dim blue directional (sky), 1 PointLight at Core (white/gold, range 30), 4 pylon PointLights (range 12), up to 3 spawn-portal PointLights (red, range 8, only while active). Everything else = emissive materials (free).
- **Parts budget (GDD §22.6: ≤1,200):**
  | Group | Parts |
  |---|---:|
  | Deck, channel, bevel | 40 |
  | Wall panels + rails | 76 |
  | Spawn portals (3×8) | 24 |
  | Corner pylons (4×7) | 28 |
  | Core assembly | 26 |
  | Path (merged surfaces + curbs) | 25 |
  | Pads (70×2: plate + ring) | 140 |
  | Signs (16) + holo-projectors (6) | 22 |
  | Biome props | 30 |
  | **Base map** | **≈411** |
  | Towers (30×8 max) | 240 |
  | Enemies (40×3 max: body + rim + effect) | 120 |
  | **Runtime max** | **≈771 ≤ 1,200 ✓** |
- **VFX (≤250 particles):** Core orb 30, coolant bubbles 10, portals 15×3, tower fire pooled (≤20 concurrent), enemy dissolve pool 30, **merge animation 120 (1.2s, one-shot — the game's signature moment gets the whole budget)**, breach flash one-shot.
- **Readability rules (GDD §20.2, enforced in art review):** unique silhouette per enemy (identifiable in B/W); element color = effect color, always; enemies darker than the path; max 2 heavy VFX on screen at once; no flash >3Hz; critical info always shape+icon+text, never color alone; WCAG AA text contrast on all signs (white on `#1A1F2E` = 12.4:1 ✓).
- **Materials ≤80** (GDD §20.3), textures 512², no per-part textures on pads (decals instead).

## 9. Enemy silhouettes (art spec for the 10 archetypes)
| Enemy | Silhouette | Rim light |
|---|---|---|
| Runt | low 4-legged blob, 1.5 studs | red |
| Runner | leaning wedge on skids, 1.3 studs | red |
| Brute | barrel on two thick legs, 2.2 studs | orange |
| Goliath | tall slab with wide shoulders, 3 studs, armor plates | orange |
| Drone | ring + center rotor, 1.5 studs, hovers 3 studs above path | yellow |
| Sentinel | dome on pedestal + **shield disc** (r=1.5, cyan, visible when up) | cyan |
| Weaver | spindle with 3 trailing tendrils, 1.8 studs | green |
| Splitter | two-lobed sac on short legs, 2 studs, pulses | red |
| Phantom | wispy flame shape, semi-transparent, 1.6 studs | violet (phases out: opacity→0.15) |
| Juggernaut | wide chassis on 4 articulated legs, 3.5 studs, turret on top | red, heavier |

## 10. Camera
| Platform | Setup |
|---|---|
| PC | elevation 48°, distance 42 studs, zoom 28–60; whole 13×13 grid visible at default zoom |
| Mobile | landscape only, elevation 45°, distance 46 studs fixed; buttons ≥44px (GDD §19.5) |
| Console | elevation 42°, 10-foot UI scaling |
Camera shake: breach ≤1 stud / boss slam ≤2 studs — both disable-able (GDD §21.1).

## 11. Open items for user sign-off
1. **[WORLD-V1]** Core identity = quantum power lattice that feeds the region; enemies = collapse manifestations (not aliens). — approve/adjust?
2. **[WORLD-V1]** Sign language: dry industrial protocol tone with exactly one dry-irony A.R.I.A. line per run (ticker #5/Act II/Act III lines). — approve tone?
3. Map C exact tiles: generate at Stage 1 (template above defines character).
4. Spawn-SE (3rd gap) unlock condition: tie to biome/Act or to Boss Gate tile? (GDD says 1–3 spawn points "per opening tile" — needs a one-line rule.)
