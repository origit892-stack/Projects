# SYNTHETIC_SOL_APPROACH — Implementation-Ready Geometry Contract
**Status:** `SPATIAL_SPEC` — Builder-Ready / No Studio Guesswork  
**Version:** `synthetic-sol-approach-v1.0`  
**Authority:** Art Director Intent (secondary service entrance, buried utilitarian, reclaimed by nature, 70/30 terrain dominance) + SOL_GOLDEN_REFERENCE quality bar (do not copy geometry)  
**Rojo Mapping:** `src/Workspace/SyntheticSolApproach.model.json` → `Workspace.SyntheticSolApproach` (verify via `default.project.json` Workspace → `$path: src/Workspace`)  
**Scene Datum:** `X=-60, Z=140` clear zone — verified no collision with `GameWorld.Exterior.TerrainShelf EastSideSkirt` (previous failure at 140,64,67) and no overlap with `GameWorld.Bunker` shell `X -18..18, Z 21..56`. `GameWorld` and `SOL_GOLDEN_REFERENCE` are **preserved, read-only**.  
**Lighting (do not invent):** `ClockTime 10.2`, `Brightness 2.0`, `Ambient 118,118,118` (RGB 118), `FogColor 138-148 warm earth tint`, `FogStart 62`, `FogEnd 185`, `Exposure 0.05`, `Shadows true`  
**Palette (RGB 0-255 validated):** Earth terrain `138,131,122`–`148,140,128` warm, Concrete architecture `172,172,175`–`175,175,178` cool neutral, Portal interior void `38,38,42` dark, Vegetation `LeafyGrass 62,72,48` muted, Metal `CorrodedMetal 112,102,92`  
**Part Budget:** `80–100` anchored parts total. Non-primitive massing mandatory. Axis-aligned stacked boxes prohibited.

---

## 1. Design Intent (Non-Negotiable)

1. **Forgotten secondary service entrance** to underground military facility — not a main bunker door. Heavy utilitarian concrete, buried, utilitarian drainage/utility language.
2. **Terrain dominates architecture 70/30.** Environment is discovered **inside terrain**, not placed on top. Hillside is the primary mass; portal is a cut/reveal.
3. **Atmospheric survival — vulnerable, curious.** Approach must feel like trespassing an abandoned cut, not touring a monument. Warm earth vs cool concrete vs dark void color hierarchy.
4. **Quality bar = SOL golden** (silhouette hierarchy, depth layers, terrain-driven dogleg, delayed visibility, continuous geology) but **original geometry** — no copy-paste of `SOL_GOLDEN_REFERENCE` part sizes/positions.

---

## 2. World Placement & Clearance Verification

| Constraint | Value | Verification |
|---|---|---|
| **New model root** | `Workspace.SyntheticSolApproach` | `src/Workspace/SyntheticSolApproach.model.json` ClassName Model |
| **World origin** | Portal threshold center `(-60, 54.0, 95)` | Center of S-curve terminus |
| **TerrainShelf avoidance** | Never set `GameWorld.Exterior.TerrainShelf` Transparency ≠0; never move it | Previous iterations left ghost bars by making it transparent — **forbidden** |
| **Overlap avoidance** | Place at `X=-60, Z=140` cluster; nearest GameWorld feature is `Bunker` at Z~32 and `TerrainShelf EastSideSkirt` at ~140,64,67 — separation >45 studs on Z, >40 studs on X | Builder must run `GameWorld` bounds check before build; abort if AABB intersect |
| **Ghost prevention** | Do not duplicate `TerrainShelf`; build self-contained hillside mass | Background ghost was transparent duplicate bars — avoid by not instancing TerrainShelf parts |
| **Foundation** | Anchor to `StableGround` top `Y=54` (DatumY 54.0) — all terrain sits on ground, not floating | Raycast ground check Y=54.0 ±0.5 |

---

## 3. Route Definition — S-Curve Dogleg (Lateral Displacement 22 studs)

### 3.1 Centerline Polyline (traversable width 12 studs, grade <18°, no step >1.2 studs)

```
START  S1: (-65, 54.2, 170)  heading 355° (5° west of north)  width 10 studs  FG trench curiosity
  │
  ├─ Segment A: S1 → Bend-1  (-65→-52, 170→145)  27 studs  grade 2.5%  (descending -0.6Y)
  │
BEND-1: (-52, 53.9, 145)  heading change +26° east (to 021°)
  │
  ├─ Segment B: Bend-1 → Gap Center → Bend-2  (-52→-45→-52, 145→125→112)  32 studs through gap
  │   Gap Center = (-50, 54.0, 125)  clear throat 5.0 studs between berms
  │
BEND-2: (-52, 54.1, 112)  heading change -31° west (to 350°)
  │
  ├─ Segment C: Bend-2 → Portal  (-52→-60, 112→95)  19 studs  grade 3.1% (rising +0.4Y to threshold)
  │
PORTAL: (-60, 54.5, 95)  threshold facing 180° (south) — player arrives looking north into void
```

**Total centerline length:** ~78 studs. **Lateral displacement:** 22 studs between start X=-65 and gap apex X=-43/-45 (ΔX=20–22) — meets S-curve requirement.  
**Two heading changes:** +26° at Bend-1, -31° at Bend-2 = dogleg >35° cumulative, terrain-driven.

### 3.2 Path Surfaces (Rojo parts, not decals)

| Part | Size (X,Y,Z) | CFrame Position | Yaw | Material | Color | Notes |
|---|---|---|---|---|---|---|
| `Path_FG_Trench` | `10.0, 0.5, 18.0` | `(-65, 53.95, 170)` | 355° | Pebble | 140,132,122 | Flood-scoured, pebble+sediment |
| `Path_SegmentA` | `10.0, 0.6, 26.0` | `(-60, 53.90, 158)` | 005° | Pebble | 139,131,120 | Erosion along west edge |
| `Path_GapThroat` | `5.0, 0.6, 10.0` | `(-50, 53.85, 125)` | 021° | Pebble | 138,130,118 | Narrow compressed, broken edges |
| `Path_SegmentC` | `8.0, 0.6, 18.0` | `(-56, 54.00, 105)` | 350° | Concrete+Pebble | 155,155,158 | Concrete apron transition |
| `Path_PortalApron` | `6.0, 0.6, 6.0` | `(-60, 54.20, 92)` | 0° | Concrete | 172,172,175 | Dark threshold |

All path tops at `Y=53.85–54.20` to sit flush on `StableGround Y=54` without z-fighting; embed -0.3 studs.

### 3.3 Leading Lines (mandatory)

* **DrainageChannel (west edge, Segment A diagonal):** `Part 1.4×0.4×28.0` at `(-69.5, 53.75, 157)` yaw `012°`, Material Concrete, Color `152,148,140`, Transparency 0.05 — diagonal cut that pulls eye north-northeast into gap.
* **SaggingCable (across gap):** `Part 0.12×0.12×14.5` cylindrical, endpoints `(-55.5, 58.8, 122)` → `(-44.2, 59.2, 128)`, catenary sag `Y-0.9` at midpoint `(-49.8, 57.95, 125)`, Material CorrodedMetal, Color `112,102,92` — diagonal overhead line that frames gap throat opposite to channel.
* Both diagonals cross at ~78° in plan view, creating visual funnel to portal.

---

## 4. Route Checkpoints & Camera Eyes (Exact Coordinates)

All eyes at **player-height** (Y = floor +5.0 for 5-stud humanoid). Targets are portal focal points.

| Checkpoint | Eye Position (X,Y,Z) | LookAt Target | Purpose & Framing | Visible Portal % | Leading Element |
|---|---|---|---|---|---|
| **CP1 Curiosity** | `(-65, 59.0, 172)` | `(-60, 61.5, 95)` portal header | South start, deep foreground trench, berm walls occlude sides, only **header beam + top 35% of portal** peeks above berm gap; pipe lip + pole chevron clue visible but not portal interior | **35%** (header + jamb tops) | Drainage channel left, sagging cable top-right |
| **CP2 Mid-Bend** | `(-52, 60.0, 128)` | `(-60, 60.0, 95)` portal center | Inside gap throat, east berm high shoulder masks right half; **half portal visible** (west jamb + door seam visible, east jamb still occluded) | **60%** | Cable overhead, gap floor leading line |
| **CP3 Reveal** | `(-60, 60.0, 102)` | `(-60, 60.0, 95)` portal center (5 studs south of threshold) | Full reveal — **100% portal + dark void interior** `38,38,42`, earth overhang shadow, threshold wear strip | **100%** | Symmetrical berm framing, foreground apron |
| **CP4 Elevated Overview** | `(-75, 74.0, 165)` | `(-60, 60.0, 120)` mid-route gap | Bird 15-stud elevation, oblique south-north, verifies full S-curve depth: FG trench → twin berms → portal cut vs hillside continuity. Not a player eye, but mandatory evidence for depth layers. | Layout read | Ridge silhouette + route trace |

**Visibility progression table (enforced):**

| Stage | Distance to Portal | Heading | Occlusion | Portal Read | Clues Visible |
|---|---|---|---|---|---|
| CP1 FG curiosity | 77 studs | 355° | **65% occluded** (berm wall + hillside mass) | 35% — header/top only, jambs hidden | Drainage pipe `Cylinder 2.2mØ` at `(-67,54.8,165)` south wall + hazard chevron on pole base |
| CP2 mid-bend gap | 34 studs | 021° | 40% occluded (east berm) | 60% — west half + header | Cable diagonal, berm stratification |
| CP3 reveal | 7 studs | 350° | 0% (framed, not blocked) | 100% — full surround + void depth | Threshold plate, rust streak, rebar tips |
| CP4 elevated | 52 studs slant | Elevated 14° pitch | Overview — no occlusion test | Full layout depth verified | Background ridge continuation |

> **Occlusion rule at CP1 = 65% ±5%.** Not 0% (portal fully exposed too early, as in iteration 4) nor 100% (no curiosity). Tuned by berm heights/positions below.

---

## 5. Terrain Masses — Continuous Sloped Geology (Non-Primitive)

**Core principle:** Hillside is ONE connected landform reading as geology, not stacked boxes. Every mass uses wedges 30–35°, tilted parts, or cylinders for organic breakup.

### 5.1 Primary Hillside Mass ( پشتکار / Backwall)

Hillside runs **east-west 68 studs, north-south 42 studs**, rising from `Y=54` to `Y=82` at ridgeline.

| Mass | Class | Size (X,Y,Z) | Position (X,Y,Z) | Rotation (pitch,yaw,roll) | Material | Color | Role |
|---|---|---|---|---|---|---|---|
| `Hillside_SlopeWedge_A` | WedgePart | `22.0, 18.0, 38.0` | `(-82, 61.0, 98)` | `32° wedge slope north` (CFrame Angle X= -32°) | Ground | 142,134,122 | West flank, 32° face — meets Berm West |
| `Hillside_SlopeWedge_B` | WedgePart | `24.0, 22.0, 40.0` | `(-58, 63.5, 92)` | `33° slope north`, yaw 4° east | Ground | 144,136,124 | Central-west, behind portal overhang |
| `Hillside_SlopeWedge_C` | WedgePart | `22.0, 20.0, 38.0` | `(-36, 62.0, 96)` | `30° slope north`, yaw -3° | Ground | 141,133,121 | East flank, tall shoulder — occluder |
| `Hillside_RidgeWedge` | WedgePart | `68.0, 8.0, 14.0` | `(-60, 76.0, 78)` | `35° south face` | Ground | 148,140,128 | Ridgeline cap, 35° — skyline breaker |
| `Hillside_WestTiltSlab` | Part | `18.0, 6.0, 16.0` | `(-78, 66.0, 86)` | `tilt 18° roll, 12° pitch` | Sandstone | 146,138,126 | Tilted stratum — breaks box silhouette |
| `Hillside_EastTiltSlab` | Part | `16.0, 7.0, 14.0` | `(-38, 68.0, 84)` | `tilt -16° roll, 14° pitch` | Sandstone | 143,135,123 | Counter-tilt, asymmetry |
| `Hillside_CylinderOutcrop` | Part Cylinder | `8.0 Ø, 10.0 L` | `(-44, 66.5, 100)` | `lay 82° horizontal, yaw 22°` | Slate | 135,128,118 | Cylindrical bulge — non-primitive mass |
| `Hillside_OverhangEarth` | Part Wedge | `14.0, 4.5, 10.0` | `(-60, 70.5, 88)` | `wedge overhang -12° pitch south` | Ground | 138,130,118 | **Earth overhang above portal** — deepest shadow caster |

**Grounding:** All wedge bottoms at `Y≤54.5`, no gaps. Verify contact without floating >0.2 studs. CastShadow true on all except CylinderOutcrop.

### 5.2 Occlusion Berms (Twin Berms Defining 5-Stud Gap)

Asymmetric pair — west low/long, east high/short.

| Mass | Class | Size (X,Y,Z) | Position | Rotation | Y Height | Visibility Role |
|---|---|---|---|---|---|---|
| `BermWest_Core` | Part | `8.0, 5.5, 14.0` | `(-56.5, 56.8, 126)` | yaw 8° east | top `Y=59.55` | Low shoulder — allows 35% portal peek over top at CP1 |
| `BermWest_Wedge_N` | WedgePart | `8.0, 4.0, 6.0` | `(-56.5, 56.5, 118)` | wedge slope 30° south | — | North taper into hillside |
| `BermWest_Wedge_S` | WedgePart | `8.0, 4.0, 5.0` | `(-56.5, 56.5, 134)` | wedge slope 32° north | — | South taper toward trench |
| `BermWest_GrassLip` | Part | `6.0, 0.7, 8.0` | `(-56.5, 59.9, 126)` | — | — | LeafyGrass 68,78,52 — not block |
| `BermEast_Core` | Part | `11.0, 8.2, 16.0` | `(-43.0, 58.1, 124)` | yaw -6° west, tilt 5° | top `Y=62.20` | **High shoulder — 65% occluder**, hides east jamb until CP2 |
| `BermEast_Wedge_N` | WedgePart | `11.0, 5.5, 7.0` | `(-43.0, 57.8, 115)` | wedge 33° south | — | North face steep |
| `BermEast_Wedge_S` | WedgePart | `11.0, 5.5, 6.0` | `(-43.0, 57.8, 133)` | wedge 34° north | — | South face |
| `BermEast_CylinderToe` | Part Cylinder | `6.0 Ø, 8.0 L` | `(-40.5, 56.0, 128)` | lay 15° pitch | — | Toe bulge, breaks box foot |

**Gap throat:** `5.0 studs clear` between `BermWest_Core` east face `X=-52.5` and `BermEast_Core` west face `X=-47.5` (center -50.0). Floor parts below cap gap floor at `Y=53.85`.

### 5.3 Foreground Trench & Negative-Space Volumes

| Volume | Bounds (X,Y,Z) | Purpose |
|---|---|---|
| `NegVolume_FG_Trench` | `X -70..-60, Y 53.0..59.0, Z 162..175` — 10×6×13 void | FG curiosity depression — player feels below grade, berm walls rise 4–5 studs above eye, creating mystery |
| `NegVolume_GapThroat` | `X -52.5..-47.5, Y 53.85..62.0, Z 118..132` — 5×8.15×14 slot | Compression slot — lateral walls 5 studs apart, height 2× width — tension before reveal |
| `NegVolume_PortalVoid` | `X -63..-57, Y 54.2..62.5, Z 88..95` — 6×8.3×7 deep | Dark void — deepest negative space, `Transparency 0.02` portal interior, `Color 38,38,42` absorbs light |
| `NegVolume_EastCounterSpace` | `X -38..-28, Y 54..60, Z 100..135` — 10×6×35 open | Asymmetric counter-space east of high berm — prevents enclosure, supplies breathing room |

All negative volumes must remain **collision-free sight corridors** (no parts intruding into gap throat above `Y=54.5` except cable).

---

## 6. Portal & Buried Architecture (Architecture Cut Into Terrain)

### 6.1 Concrete Surround (cool palette, heavy, thick)

| Part | Class | Size | Position | Rotation | Material | Color |
|---|---|---|---|---|---|---|
| `Portal_WestJamb` | Part | `2.2, 10.5, 4.5` | `(-62.2, 59.8, 93.5)` | — | Concrete | 172,172,175 |
| `Portal_EastJamb` | Part | `2.2, 10.5, 4.5` | `(-57.8, 59.8, 93.5)` | — | Concrete | 173,173,176 |
| `Portal_Header` | Part | `7.2, 2.0, 4.5` | `(-60.0, 65.8, 93.5)` | — | Concrete | 174,174,177 |
| `Portal_Soffit` | Part | `5.0, 1.2, 3.5` | `(-60.0, 65.0, 91.5)` | — | Concrete | 175,175,178 |
| `Portal_Threshold` | Part | `6.5, 0.6, 3.0` | `(-60.0, 54.5, 93.0)` | — | Concrete | 168,168,170 |
| `Portal_WestChamfer` | WedgePart | `1.0, 10.5, 4.5` | `(-63.4, 59.8, 93.5)` | wedge 45° chamfer | Concrete | 172,172,175 |
| `Portal_EastChamfer` | WedgePart | `1.0, 10.5, 4.5` | `(-56.6, 59.8, 93.5)` | wedge 45° chamfer mirror | Concrete | 173,173,176 |
| `Portal_OverhangSlab` | Part | `9.0, 1.2, 5.0` | `(-60.0, 67.2, 90.5)` | tilt 8° south | Concrete | 170,170,172 |

**Burial contact:** `Hillside_OverhangEarth` sits directly on `Portal_Header` top + `Portal_OverhangSlab` with **zero gap** (interpenetration 0.15 studs deliberate to kill light leak). Side jambs interpenetrate `Hillside_SlopeWedge_B` by 0.3 studs.

### 6.2 Portal Cavity (Darkest Focal)

| Part | Size | Position | Color | Purpose |
|---|---|---|---|---|
| `Portal_Floor` | `6.0, 0.4, 6.0` | `(-60, 54.2, 90.0)` | 55,53,50 | Recessed 0.3 below threshold |
| `Portal_Ceiling` | `6.0, 0.4, 6.0` | `(-60, 62.5, 90.0)` | 52,50,48 | Low ceiling — oppression |
| `Portal_BackWall` | `6.0, 8.3, 0.6` | `(-60, 58.4, 87.2)` | 38,38,42 | **Darkest plane in scene** — absorbs, draws eye |
| `Portal_SideWest` | `0.6, 8.3, 6.0` | `(-62.7, 58.4, 90.0)` | 45,44,42 | Shadow side |
| `Portal_SideEast` | `0.6, 8.3, 6.0` | `(-57.3, 58.4, 90.0)` | 45,44,42 | Shadow side |
| `Portal_ServiceDoor` | `4.2, 6.0, 0.3` | `(-60, 57.5, 87.5)` | 58,56,52 DiamondPlate | Slight ajar 3° yaw — light slit not modeled, void only |

**Door seam line at `X=-60, Y 55.5–60.5, Z 87.5`** must remain visible at CP2/CP3 as micro-contrast.

### 6.3 Weathering & Infrastructure (restrained)

* **Rebar tips:** 2× `Part 0.18×1.2×0.18` CorrodedMetal `92,82,72` at `(-63.2, 63.5, 92.2)` and `(-56.9, 64.0, 92.8)` — bent 12°.
* **Rust streak:** `Part 0.6×4.5×0.15` Concrete `148,118,92` Trans 0.35 at `(-57.9, 60.5, 93.7)` vertical drip.
* **Water stain:** `Part 0.9×5.5×0.15` Concrete `118,128,138` Trans 0.38 at `(-62.0, 60.0, 93.7)`.
* **Exposed conduit:** `Part Cylinder 0.4Ø × 5.0L` at `(-62.5, 56.5, 94.5)` along west jamb base, Metal `102,102,105`.

---

## 7. Vegetation — Believable, Not Blocks (Foreground/Mid/Background Hierarchy)

**Palette:** Grass plates `Material Grass/LeafyGrass` `Color 62-72,70-82,48-58` variation; bushes as **spheres or tilted plates**, never cubes >1.0.

| Cluster | Part | Shape | Size | Position | Rotation | Notes |
|---|---|---|---|---|---|---|
| **FG Trench** | `Veg_GrassPlate_A1` | Part plate | `2.8, 0.3, 1.4` | `(-68.2, 54.3, 168)` | 8° tilt | Thin 0.3 lip |
| | `Veg_GrassPlate_A2` | Part plate | `3.2, 0.5, 1.8` | `(-62.5, 54.4, 172)` | -6° tilt | 0.5 mid |
| | `Veg_Bush_Sphere_A` | Part Sphere | `1.6 Ø` | `(-66.0, 54.8, 166)` | — | Sphere, not block |
| **Mid Gap** | `Veg_GrassPlate_B1` | Part plate | `2.0, 0.6, 1.2` | `(-55.0, 60.0, 126)` | 12° on berm top | Berm cap |
| | `Veg_Bush_Sphere_B` | Part Sphere | `1.4 Ø` | `(-42.5, 58.6, 124)` | — | East berm crown |
| | `Veg_Fern_Clump` | Part | `1.8, 0.8, 1.8` | `(-50.2, 54.2, 122)` | 5° | Gap floor, gap fill |
| **Portal Rim** | `Veg_GrassPlate_C1` | Part plate | `3.5, 0.8, 1.6` | `(-60.0, 70.9, 88)` | drape -18° over header | Overhang lip — must overhang header by 0.6 studs |
| | `Veg_HangingRoot` | Part | `0.15, 1.8, 0.15` | `(-61.2, 69.5, 89)` | 7° | Dangling root, portal shadow |
| **Background Depth** | `Veg_Tussock_D1` | Part | `4.0, 0.4, 2.2` | `(-78, 54.6, 110)` | — | West counter-space |
| | `Veg_TreeCluster_E` | Model 2 trunks+ canopies | `Trunk 0.6Ø×7.0, Canopy 4.5Ø Sphere` | `(-28, 56.0, 118)` + `(-32, 54.8, 130)` | lean 6-9° | Background framing, not foreground clutter |

**Density rule:** Vegetation covers **≤28%** of hillside visible surface area — terrain remains dominant. No evenly spaced grid; cluster, then leave 6–8 stud gaps.

---

## 8. Silhouette Hierarchy (Front-to-Back Read)

From any player eye south of `Z=130`, the **skyline stack** must read in this order (nearest dominant to farthest subtle):

1. **Portal void (darkest, lowest, center)** — `Luminance ~38`, rectangular negative, primary focal. Earth overhang casts 2.2-stud deep shadow onto header.
2. **Berm pair (mid, asymmetric)** — Berm East silhouette 2.7 studs taller than Berm West at same Z, creating diagonal top-edge that points to portal.
3. **Hillside ridge (largest, highest, continuous)** — `Y=76–82` wedge cap, 68 studs wide, no notches, overrides all architecture. Must read as single geological line, not separate mounds.
4. **Background tussocks/trees (soft, desaturated, fogged)** — Fog 62–185 pushes these to 40% contrast, prevents background ghost hard edge.

**Test:** Screenshot at CP1 with Brightness 2.0, Fog 62–185 — portal must be ≥2.5 stops darker than berm tops, ridge must be ≥1.5× taller than portal in pixel height.

---

## 9. Occlusion Relationships (Whose Mass Hides What, When)

| Occluder → Occluded | At CP1 (curiosity) | At CP2 (mid-bend) | At CP3 (reveal) |
|---|---|---|---|
| **BermWest → Portal west jamb** | hides lower 60% (throat floor blocks) | reveals 90% (inside gap) | fully revealed, framed |
| **BermEast → Portal east jamb + header right** | hides 100% east half, 40% header | hides 40% east half (sliver peek) | fully revealed |
| **Hillside_SlopeWedge_B → Portal top/overhang** | hides top 0 — header deliberately peeks 0.9 studs above BermWest top | hides 0 — header fully visible | frames top, not hides |
| **BermEast high shoulder → Gap exit** | hides gap exit background | frames gap like doorway | behind viewer |
| **FG trench walls → Berm bases** | trench lip hides berm feet — berms appear to grow from earth, not sit on it | — | — |

**Quantitative check (raycast):**
* Eye `(-65,59,172)` → portal center `(-60,60,95)` must hit `BermEast_Core` or `BermEast_Wedge_N` first (occluded).
* Eye `(-65,59,172)` → header top `(-60,66.5,93.5)` must **miss** berms (visible — curiosity reward).
* Eye `(-52,60,128)` → portal east jamb `(-57.8,59.8,93.5)` must hit `BermEast_Core` at grazing angle (≈40% remain hidden).
* Eye `(-60,60,102)` → portal back wall `(-60,58.4,87.2)` must hit nothing but portal surround (clear).

---

## 10. Environmental Clues (Storytelling Without Geometry Spam)

| Clue | Position | Size/Shape | Material | How it reads at CP1 |
|---|---|---|---|---|
| **DrainagePipe** | `(-67.0, 54.8, 165)` embedded in FG trench south wall | Cylinder `2.2Ø × 2.0L` axis east-west, lip ring `2.4Ø×0.25` | Concrete 145,143,138 | Dark circular mouth + sediment fan — hints infrastructure buried beyond berm |
| **ToppledUtilityPole** | Base `(-55.0, 54.6, 138)` shaft `0.7Ø×9.0L` leaning 62° north, crossarm `3.5×0.35×0.35` | WoodPlanks 92,82,62 + CorrodedMetal | Pole shaft crosses west berm shoulder, crossarm points to gap |
| **HazardChevron** | On pole shaft at `(-54.2, 57.2, 134)` | Part `1.2×0.5×0.05` yellow-black 210,180,22 / 28,28,28 | SmoothPlastic | Faded chevron catches light — human intent marker |
| **CollapsedFence (3 posts only)** | Posts at `(-62,54.8,148)` 3.0L lean 18°, `(-58,54.7,142)` 1.8L broken, `(-64,54.6,152)` stump 0.9L | CorrodedMetal 102,92,82 | South of gap, not in throat — frames approach without blocking |

No additional props. Every clue must be visible at CP1 as ≤8px hint, not dominant.

---

## 11. Part Count & Budget Breakdown (Target 88 parts)

| System | Count | Class Mix |
|---|---|---|
| HillsideMass | 8 | 4 WedgePart + 2 Part tilted + 1 Cylinder + 1 Wedge overhang |
| Berms + Gap | 9 | 2 Core Part + 4 WedgePart + 2 GrassLip + 1 Cylinder toe |
| Portal Surround + Cavity | 16 | 8 surround (incl 2 wedges) + 6 cavity + 2 detail (rebar/rust) |
| Path + Leading Lines | 7 | 5 path Parts + 2 lines (channel + cable) |
| Negative-space floors/lips | 3 | 2 GapFloor/Lip Wedge + 1 PortalFloor already counted |
| Environmental Clues | 7 | 1 pipe (2 parts) + 1 pole (3 parts) + 1 fence (3 posts) — counted as 7 DNP |
| Vegetation | 14 | 6 grass plates + 3 sphere bushes + 2 tussocks + 2 tree canopies + 1 hanging root |
| Scatter / Rubble | 4 | Pebble scatter + concrete chips (≤2.5 studs, tilted) |
| **Total** | **88** | **Within 80–100, no box stacks** |

---

## 12. Builder MUST / MUST NOT Rules (Enforced at Review)

### MUST

1. **MUST verify Rojo mapping before build:** `Rojo 7.7.0` at `$HOME/.aftman/bin/rojo`; confirm `default.project.json` Workspace → `src/Workspace`; emit `sourcemap.json` and verify `SyntheticSolApproach` appears under `game.Workspace`.
2. **MUST build at clear location `X=-60, Z=140` cluster** with AABB no-intersect check against `GameWorld` and `SOL_GOLDEN_REFERENCE`. Preserve both.
3. **MUST use non-primitive massing:** ≥60% of terrain parts are WedgePart/Cylinder or tilted Part (rotation >12° on at least one axis). No stack of axis-aligned boxes as hillside — reviewer will reject if silhouette reads as plinth.
4. **MUST achieve 70/30 terrain dominance:** In CP3 reveal screenshot, hillside+berm pixel area ≥2.3× portal architecture pixel area.
5. **MUST hit occlusion targets:** CP1 65%±5%, CP2 40%±8%, CP3 0% (framed). Provide raycast evidence from exact eyes above.
6. **MUST maintain continuous sloped mass:** Wedge faces must meet edge-to-edge with ≤0.25 stud gaps; no vertical wall pretending to be hillside; hillside pitch 30–35°.
7. **MUST keep earth overhang as darkest focal:** Portal interior `38,38,42` and `Hillside_OverhangEarth` shadow must make portal ≥2.5 stops darker than any terrain.
8. **MUST implement both leading lines** (drainage channel west diagonal + sagging cable across gap) with stated dimensions/positions and diagonal crossing.
9. **MUST keep route width ≥8 studs clear** (12 studs total with shoulders), grade <18°, lateral displacement 22 studs realized in plan view, two bends 26° and -31°.
10. **MUST use specified palette** (earth 138–148 warm vs concrete 172–175 cool) — no saturated greens, no pure greys, no TerrainShelf ghost.
11. **MUST make vegetation believable:** grass plates thickness 0.3–0.8 only, bush spheres 1.2–1.8Ø, tilted/organic, not cubes; ≤28% coverage.
12. **MUST end with Studio in Edit mode** and provide evidence shots from CP1–CP4 at gameplay FOV 70°, Clock 10.2, Bright 2.0, Ambient 118, Fog 62–185.

### MUST NOT

1. **MUST NOT copy `SOL_GOLDEN_REFERENCE` geometry** — inspector will diff part sizes/positions; similarity threshold >40% identical volumes = reject.
2. **MUST NOT make `GameWorld.Exterior.TerrainShelf` or any GameWorld part transparent** (`Transparency ≠0`) — this caused ghost bars in iterations 2–5.
3. **MUST NOT place `SyntheticSolApproach` overlapping `GameWorld`** or at previous failed location `~140,64,67 EastSideSkirt` — new approach exists to avoid dark wall overlap.
4. **MUST NOT create primitive-box 3-tier plinth or flat hillside wall** — vertical flat massing was sterile failure; require wedge/tilt/cylinder variation.
5. **MUST NOT block 100% or reveal 0% at CP1** — curiosity requires 35% header peek; full reveal too early or total hide both fail.
6. **MUST NOT use axis-aligned stacked boxes, pure Part cubes for hillside, or transparent TerrainShelf bars as background** — background ghost forbidden.
7. **MUST NOT invent new lighting, skybox, or material beyond spec** — keep Fog 62–185, Brightness 2.0, earth/concrete/void palette.
8. **MUST NOT exceed 100 parts or drop below 80** — budget is part of 70/30 discipline; clutter hides weak massing.
9. **MUST NOT leave terrain/architecture gaps** (light leaks between `Hillside_OverhangEarth` and `Portal_Header`) — interpenetrate 0.15–0.30 studs.
10. **MUST NOT present overhead/debug views as primary art evidence** — per Art Bible, require player-height CP1–CP3 plus three-quarter CP4.

---

## 13. Verification Checklist (Builder Self-QA Before Submit)

- [ ] `bds ast` passes on any Luau builder (if scripted).
- [ ] `rojo sourcemap default.project.json --output sourcemap.json` shows `SyntheticSolApproach` under `Workspace`.
- [ ] `rojo build -o game.rbxl` succeeds; Studio re-open shows model at `(-60,54,95)` not at `(140,64,67)`.
- [ ] `GameWorld` and `SOL_GOLDEN_REFERENCE` untouched (`git diff --stat` shows no changes to `GameWorld.model.json`).
- [ ] `TerrainShelf` Transparency still `0.0` (or original) — verify in Studio Inspector.
- [ ] Four evidence screenshots at CP1 eye `(-65,59,172)` FOV70 looking to `(-60,61.5,95)` shows only header + pipe/pole hint, raycast hits berm.
- [ ] CP2 `(-52,60,128)` shows half portal, CP3 `(-60,60,102)` shows full void, CP4 `(-75,74,165)` shows S-curve depth — all captured with Fog 62–185.
- [ ] No floating parts (>0.2 studs above ground) and no z-fighting on path (embed -0.3).
- [ ] Studio returned to Edit mode (not Play).

---

## 14. File Deliverable

**Source file:** `src/Workspace/SyntheticSolApproach.model.json`  
**ClassName:** Model `SyntheticSolApproach`  
**Attributes:** `Version synthetic-sol-approach-v1.0`, `ArtDirection discovery-approach-secondary-entrance`, `Datum X -60 Z 95`, `OcclusionProfile 35-60-100`, `TerrainDominance 70/30`  
**Children Models:** `HillsideMass`, `OcclusionBerms`, `PortalAssembly`, `ApproachPath`, `EnvironmentalClues`, `VegetationDressing` — matching breakdown above.

Builder may implement via hand-placed parts or deterministic `tools/builders/generate_synthetic_sol_approach.py` (seed 600140, no runtime randomness) — either must produce identical `src/Workspace/SyntheticSolApproach.model.json` committed to filesystem (never Studio-only).

---

SPATIAL_SPEC_READY=YES
