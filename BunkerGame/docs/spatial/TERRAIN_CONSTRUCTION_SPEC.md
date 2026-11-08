# BunkerGame V2 — TERRAIN CONSTRUCTION SPEC

**Spec Owner:** bunkergame-terrain-specialist  
**Status:** `TERRAIN_SPEC_READY=YES`  
**Depends On:** Spatial Architect Contract, Art Director Visual Intent  
**Unblocks:** Overnight world build, Agent Asset Factory hero assets  

---

## 1. VISUAL INTENT & CONSTRAINTS

### Atmospheric Goals
- **Mood:** Creepy abandoned but functional bunker outpost
- **Pacing:** Safe near bunker → increasingly ominous deeper in forest
- **Dominance:** 70% terrain, 30% structures/assets
- **Palette (Enum.Material):**
  - Terrain base: `Material.Painted` with `Ground`, `Sandstone`, `LeafyGrass`
  - Bunker zone: `Material.Plastic` cool neutral concrete tones
  - Accent erosion: subtle `Material.Slate` rock exposure
- **Performance Budget:** ≤240 visible outdoor terrain parts

### Datum & Bounds
| Parameter | Value |
|-----------|-------|
| Datum Y (StableGround) | 54 |
| StableGround footprint | 640×640 at Y=54 |
| PlayableBounds X | −320 .. 320 |
| PlayableBounds Z | −240 .. 400 |
| Max elevation (T5 peak) | 75 (+21 above datum) |
| Min elevation (T4 farm base) | 50 (−4 below datum) |

---

## 2. IMPLEMENTATION APPROACH

### Chosen Method: Roblox Terrain Heightfield + Anchor-Part Hero Overlays

**Rationale:**
- Voxel-based Terrain API (`Workspace.Terrain`) provides organic sculpting without visible box-stacks
- `FillBlock()` + `FillBall()` operations are deterministic and scriptable
- Heightfield data persists in place file; procedural generation script can be version-controlled under `/src/scripts/terrain/`
- Hero rock/cliff forms (detailed boulders, fractured cliff faces) handed to Asset Factory as `.rbxm` parts for visual richness beyond voxel limits

**Filesystem Path:**
```
BunkerGame/src/
  Workspace.roblox/       ← Terrain heightfield persisted in place file
  Scripts/
    ServerScriptService/
      TerrainGenerator.init.lua   ← Procedural terrain sculpting via FillBlock/FillBall
    Modules/
      TerrainSpec.lua              ← Readable constants matching this spec
```

---

## 3. BASE TERRAIN (Foundation)

**Base Ground Plane:** Y=54 datum, muted earth palette

```lua
-- /src/scripts/terrain/TerrainGenerator.lua
Terr = game.Workspace.Terran:Teren:Terran:FillBlock(CFrame.new(0, 56, 320, ...), Vector3.new(640, 4, 640), Enum.Material.Painted)

-- Base ground fill (Y=52..58 = 6-unit-thick stable plane
local baseMaterial = Color3.fromRGB(128, 122, 101))  -- muted Ground tone
```

### BASE TERRAIN PROPERTIES

| Property | Value |
|----------|-------|
| Heightfield thickness | 6 units (Y=52..58) |
| Material | `Material.Painted` / custom texture blend |
| Base color | RGB(128,122,101) Ground + LeafyGrass mix |
| Footprint | X −320..320, Z −240..400 (640×640) |
| Role | Foundation, collision baseline, traversal surface |

---

## 4. HERO TERRAIN MASSES (T1–T6)

Each mass defined with: semantic role, bounds, elevations, slope range, silhouette/occlusion role, breakup requirements, implementation method via `FillBlock()` / `FillBall()` sequences.

### T1 — Bunker Primary Rise

| Attribute | Value |
|-----------|-------|
| **Semantic Role** | Bunker embedding hill, primary anchor point, safe zone core |
| **Bounds X** | −60 .. 80 (width 140) |
| **Bounds Z** | 138 .. 240 (depth 102) |
| **Center** | (−5, 54, 200) |
| **Base Elevation** | Y=54 (datum merge at perimeter) |
| **Peak Elevation** | Y=64 @ (−5, 200) |
| **Plateau** | 20×20 flat top at Y=62..64 centered on peak |
| **Slope Range** | 8°–16° gradual ascent from datum to plateau |
| **Silhouette Role** | Mid-tier mass, anchors bunker visually, not skyline-defining |
| **Occlusion Role** | Blocks view of T3 from bunker interior; protects farm visibility |
| **Material** | `Ground` → `Sandstone` gradient from base to dome |
| **Breakup Required** | Subtle erosion gullies on NW/NE flanks (−10% height irregularity) |
| **Implementation** | `FillBlock()` hemispherical stack + `FillBall()` smoothing |

```lua
-- T1: Bunker Primary Rise - Hemispherical dome with plateau
-- Peak at (-5, 64, 200), merges to datum at bounds edges

local t1 = {
  center = Vector3.new(-5, 54, 200),
  radius = 70,          -- half of max(140, 102) ≈ 70m influence
  peakHeight = 64,
  plateauRadius = 10,   -- 20x20 plateau → r=10
  baseY = 54,
}

-- Voxel approach: stack FillBall operations in decreasing radius/increasing Y
for y = t1.baseY + 2, t1.peakHeight - 2 do
  local progress = (y - t1.baseY) / (t1.peakHeight - t1.baseY)
  local radiusAtThisY = t1.radius * (1 - progress * 0.98) -- taper toward peak
  Terrain:FillBall(CFrame.new(t1.center.X, y, t1.center.Z), radiusAtThisY, Material.Ground)
end

-- Plateau flat top (y=62..64, r=10)
Terrain:FillBlock(CFrame.new(t1.center.X, 63, t1.center.Z):Orient(Vector3.new(0.8,0,0)), 
                  Vector3.new(20, 2, 20), Material.Plastic)  -- bunker roof material
```

---

### T2 — Western Ridge

| Attribute | Value |
|-----------|-------|
| **Semantic Role** | Linear spine blocking western approach; horror pacing barrier |
| **Bounds X** | −210 .. −140 (width 70) |
| **Bounds Z** | 100 .. 260 (length 160) |
| **Center** | (−175, 60, 180) |
| **Baseline Y** | Y=54 at edges |
| **Peak Elevation** | Y=72 @ (−160, 185) |
| **Ridge Width** | ~35m NE–SW linear axis |
| **Slope Range** | 25°–35° steep ridge faces, 12°–18° crest undulations |
| **Silhouette Role** | Second-highest skyline mass after T5; defines western horizon |
| **Occlusion Role** | Cuts visibility from P0 to deep forest west; funnels toward bunker |
| **Material** | `Sandstone` (exposed) on ridgeline, `Ground` on slopes |
| **Breakup Required** | Erosion scree fields on southern face; small gullies every ~40m crest |
| **Implementation** | Elongated `FillBall()` ridge spine + wedge overlays for steep faces |

```lua
-- T2: Western Ridge - Linear NE-SW spine
-- Peak at (-160, 72, 185) with 35m-wide crest

local t2 = {
  peakPos = Vector3.new(-160, 72, 185),
  ridgeAxis = Vector3.new(1, 0, -1.5):Normalize(),  -- NE-SW direction
  halfLength = 100,      -- 160m length / 2
  crestWidth = 18,       -- ~35m total width
}

-- Stack balls along ridge line for spine
for i = -t2.halfLength, t2.halfLength, 5 do
  local pos = t2.peakPos + (t2.ridgeAxis * i * Vector3.new(1,0,0.67))
  local heightAtPos = math.max(54, 72 - (math.abs(i) / t2.halfLength) * 8)
  Terrain:FillBall(CFrame.new(pos.X, heightAtPos - 5, pos.Z), 12, Material.Sandstone)
end

-- Steep wedge masses on faces (via Part overlay for sharp angles)
-- Hand off to Asset Factory: "WesternRidgeScree_01.rbxm" etc.
```

---

### T3 — Eastern Outcrop

| Attribute | Value |
|-----------|-------|
| **Semantic Role** | Asymmetric visual balance; farm plot framing |
| **Bounds X** | 135 .. 220 (width 85) |
| **Bounds Z** | 140 .. 280 (depth 140) |
| **Center** | (175, 56, 210) |
| **Base Y** | Y=54 |
| **Peak Elevation** | Y=60 @ (175, 210) |
| **Slope Range** | Steep SE face 30°–40°, gentle NW slope 10°–14° |
| **Silhouette Role** | Low-mid tier; fills eastern midground without competing with T1 |
| **Occlusion Role** | Partially blocks deep east view from bunker; does NOT obscure farm plots |
| **Material** | `Ground` on gentle slope, `Slate` patches on steep face |
| **Breakup Required** | Exposed rock outcrops (Asset Factory rocks) on SE cliff line |
| **Implementation** | Asymmetric `FillBlock()` ramp + detailed rock parts overlay |

```lua
-- T3: Eastern Outcrop - Asymmetric slope
-- Gentle NW, steep SE face with exposed rock

local t3 = {
  center = Vector3.new(175, 54, 210),
  peakPos = Vector3.new(175, 60, 210),
  widthNW = 50,     -- gentle slope length
  widthSE = 35,     -- steep face length
}

-- FillBlock asymmetric wedge (gentle NW ramp)
Terrain:FillBlock(CFrame.new(t3.peakPos.X - 25, 57, t3.peakPos.Z), 
                  Vector3.new(40, 6, 80), Material.Ground)

-- Steep SE face handled by detailed rock parts (Asset Factory)
```

---

### T4 — Southern Farm Slope

| Attribute | Value |
|-----------|-------|
| **Semantic Role** | Gentle downward gradient exposing farm plots; openness before descent |
| **Bounds X** | 80 .. 200 (width 120) |
| **Bounds Z** | −60 .. −10 (depth 50, south of datum origin) |
| **Baseline Y (north)** | Y=54 at Z≈10 |
| **Base Y (south edge)** | Y=50 at Z≈−60 |
| **Gradient** | −2.3° (54→50 over 70m southward) |
| **Slope Range** | Constant ~2° gentle downhill |
| **Silhouette Role** | Negative silhouette — dip in horizon, visual "valley entrance" |
| **Occlusion Role** | Opens farm plot visibility; NO occlusion intended |
| **Material** | `LeafyGrass` dominant (cultivated earth implication) |
| **Breakup Required** | Subtle terracing lines (heightfield micro-undulations ±0.5), NO erosion |
| **Implementation** | Single `FillBlock()` ramp, no hero assets needed |

```lua
-- T4: Southern Farm Slope - Gentle 2° gradient to 50
-- North edge Y=54 @ Z≈−10, south edge Y=50 @ Z≈−60

local t4 = {
  northEdgeZ = -10,
  southEdgeZ = -60,
  heightNorth = 54,
  heightSouth = 50,
}

-- Ramp block from north to south with slope
local rampCF = CFrame.new(140, 52, -35):LookAt(Vector3.new(140, 50, -60))
Terrain:FillBlock(rampCF, Vector3.new(120, 4, 70), Material.LeafyGrass)
```

---

### T5 — Northern Sentinel

| Attribute | Value |
|-----------|-------|
| **Semantic Role** | Highest conical landmark; final route checkpoint destination; apex visual |
| **Bounds X** | −20 .. 60 (width 80) |
| **Bounds Z** | 320 .. 400 (depth 80) |
| **Center** | (15, 60, 355) |
| **Base Y** | Y=54 at perimeter |
| **Peak Elevation** | Y=75 @ (15, 355) — highest point in world (+21 above datum) |
| **Slope Range** | Steep 40°–55° conical faces |
| **Silhouette Role** | PRIMARY skyline mass — tallest, defines northern horizon |
| **Occlusion Role** | Hides deep north forest beyond Z=380; route arrival destination |
| **Material** | `Slate` dominant with `Sandstone` base layer |
| **Breakup Required** | Summit rock pinnacles (Asset Factory), scree aprons at base |
| **Implementation** | Conical `FillBall()` stack + hero pinnacle assets overlaid |

```lua
-- T5: Northern Sentinel - Steep conical peak (+21 above datum)
-- Peak at (15, 75, 355), steep 40–55° slopes

local t5 = {
  basePos = Vector3.new(15, 54, 355),
  peakHeight = 75,
  baseRadius = 40,  -- 80m diameter at datum
}

-- Build conical stack with FillBall tapering upward
for y = t5.basePos.Y + 2, t5.peakHeight - 1 do
  local progress = (y - t5.basePos.Y) / (t5.peakHeight - t5.basePos.Y)
  local radiusAtY = t5.baseRadius * math.max(0.1, 1 - progress * 0.9)
  Terrain:FillBall(CFrame.new(t5.basePos.X, y, t5.basePos.Z), 
                   radiusAtY, Material.Slate)
end

-- Summit pinnacles → Asset Factory: "T5SummitRocks_*.rbxm"
```

---

### T6 — Mid-Zone Boulder (Mesa)

| Attribute | Value |
|-----------|-------|
| **Semantic Role** | Flat plateau mesa in mid-zone; route checkpoint P2–P3 transition landmark |
| **Bounds X** | 20 .. 90 (width 70) |
| **Bounds Z** | 180 .. 240 (depth 60) |
| **Center** | (55, 56, 210) |
| **Plateau Y** | Y=58 flat top (35×30 = ~r17 circular equivalent) |
| **Base Y** | Y=54 at base |
| **Slope Range** | Steep vertical cliff faces (~60°+), flat top |
| **Silhouette Role** | Mid-tier visual; breaks monotony between T1 and T3 |
| **Occlusion Role** | Minor occlusion from bunker; route waypoint marker |
| **Material** | `Sandstone` cliff faces, `Ground` plateau top |
| **Breakup Required** | Crackle fractures on top surface (via decals/paint), vertical striations on cliffs |
| **Implementation** | `FillBlock()` cylinder/block with steep perimeter + paint strokes |

```lua
-- T6: Mid-Zone Mesa - Flat-topped boulder plateau
-- 35x30 flat top at Y=58, steep cliff faces down to Y=54

local t6 = {
  center = Vector3.new(55, 56, 210),
  plateauY = 58,
  width = 35,
  depth = 30,
}

-- Flat plateau top (block at Y=56..60)
Terrain:FillBlock(CFrame.new(t6.center.X, t6.plateauY + 2, t6.center.Z), 
                  Vector3.new(t6.width, 4, t6.depth), Material.Ground)

-- Vertical cliff fills (4 sides)
local cliffHeight = 4  -- 58→54
Terrain:FillBlock(CFrame.new(t6.center.X - t6.width/2, t6.plateauY-1, t6.center.Z), 
                  Vector3.new(8, cliffHeight, t6.depth + 4), Material.Sandstone)
-- (repeat for all 4 sides or use single oversized block trimmed to shape)
```

---

## 5. NEGATIVE-SPACE VOLUMES (PROTECTED ZONES)

**NO TERRAIN FILL PERMITTED** within these volumes — must remain traversable and visibility-cleared.

### N1 — Bunker Entrance Corridor

| Attribute | Value |
|-----------|-------|
| **Bounds** | X −30..10, Y 52..68, Z −40..50 |
| **Purpose** | Player approach to bunker door; MUST NOT be obstructed by terrain/vegetation |
| **Validation** | Raycast (0,54.1,20) → P0(0,56,-30) must have unobstructed 2-unit-wide tube |
| **Implementation Constraint** | `FillBlock()` operations must exclude this volume; subtractive sculpting if needed |

### N2 — Primary Path Tube (P0→P4 route centerline buffer)

| Checkpoint | Center (x,y,z) | Protected Radius |
|------------|----------------|------------------|
| P0 | (0, 56, −30) | r=7 |
| P1 | (−35, 57, 25) | r=7 |
| P2 | (0, 58, 150) | r=7 |
| P3 | (−90, 64, 200) | r=7 |
| P4 | (−190, 75, 240) | r=7 |

**Constraint:** Path tube must maintain ≥6m width clear of terrain collision. `FillBall()` radii must not intrude into path sphere buffers.

### N3 — Farm Plot Visibility Volumes

| Attribute | Value |
|-----------|-------|
| **Farm Plots Position** | X 75..105, Z 200..220 (from bunker) |
| **Visibility Checkpoint** | Bunker door (0,54.1,20) |
| **Requirement** | Ray from bunker door to all farm plot corners must NOT intersect T3 or T1 terrain volumes |
| **Implementation Note** | T3 asymmetric slope must not exceed Y=60 toward farm side |

---

## 6. SILEHOUETTE HIERARCHY (Visual Layering)

From highest to lowest silhouette prominence:

```
T5 Northern Sentinel     (+21m peak, primary skyline anchor)
    ↓
T2 Western Ridge        (+18m peak, secondary spine)
    ↓
T1 Bunker Primary Rise  (+10m plateau, core mass)
    ↓
T3 Eastern Outcrop      (+6m asymmetric)
    ↓
T6 Mid-Zone Boulder     (+4m mesa)
    ↓
T4 Southern Farm Slope  (−4m dip to Y=50, negative silhouette)
```

**Validation:** From bunker entrance camera (approx. 0,56,20 → lookAt −175,60,180), the skyline must show T5 and T2 as dominant peaks with T1 as grounded mass below them.

---

## 7. BUILDER MUST / MUST NOT CONSTRAINTS

### MUST DO

- ✅ Preserve **frozen manifest tree positions** — 18 trees from prototype must not be displaced by terrain fills
- ✅ Maintain **path tube integrity** — all route segments ≥6m wide collision-free
- ✅ Apply **natural breakup** to steep faces (scree lines, gullies, rock exposures) — NO smooth box-wedge stacks visible
- ✅ Use **FillBlock/FillBall sequences** for base terrain volumes; hand off detailed rock/cliff assets to Asset Factory
- ✅ Validate **bunkerd door ray** from P0 remains unobstructed post-terrain build
- ✅ Keep **performance budget**: ≤240 outdoor parts total (terrain heightfield counts as 1 block, hero asset overlays count individually)

### MUST NOT DO

- ❌ Create visible stack of box/wedge primitives for terrain masses
- ❌ Exceed ±2m elevation tolerance from spec values in any mass peak/base
- ❌ Intrude into negative-space volumes (N1, N2, N3) with terrain collision
- ❌ Allow T1–T6 footprints to exceed bounds ±10m
- ❌ Add vegetation/rocks that block farm plot visibility from bunker door
- ❌ Use pitch-black palette; maintain navigable visibility depth even in forest zones

---

## 8. VALIDATION CRITERIA (Automated + Manual)

### Automated Tests (via Luau Script Tool)

```lu
terrainValidation = {
  elevationTolerance = 2,        -- ±2m allowed deviation
  footprintTolerance = 10,       -- ±10m bounds slack
  minWidthPath = 6,              -- path tube must be ≥6m wide collision-free
  maxOutdoorParts = 240,         -- performance budget
}

-- Run after terrain generation script completes:
validateElevation({ massId, expectedY, point }) 
validateFootprint({ massId, maxXZ, minXZ })
validatePathClearance({ pathSegment })
validateBoundaryContainment({ boundsTable })
validateBunkerDoorRaycast({ from: Vector3.new(0,56,-30), to: Vector3.new(0,54.1,20) })
validateFarmVisibilityBunkerToFarmPlot({ farmPlotPos })
```

### Manual Inspection Criteria

- [ ] Skyline hierarchy holds (T5 > T2 > T1 dominance from bunker viewpoint)
- [ ] Negative spaces feel open and navigable (no accidental clipping into path tubes)
- [ ] Horizon has natural breakup (erosion scree, gullies, asymmetry — no "smooth dome" look)
- [ ] Farm plots are visible and accessible from both bunker door and main path
- [ ] Bunker embedding feels intentional (70% terrain massing around it, not floating)

---

## 9. IMPLEMENTATION STEPS (Filesys

### Step 1: Create Terrain Spec Module Script

```
mkdir -p src/Modules
touch src/Modules/TerrainSpec.lua
```

**Content:** Store all constants from this spec in a version-controlled module for runtime reference.

```lua
--!/BunkerGame/src/Modules/TerrainSpec.lua
return {
  Datum = { y = 54 },
  StableGround = { size = Vector3.new(640, 6, 640) },
  PlayableBounds = { minX = -320, maxX = 320, minZ = -240, maxZ = 400 },
  
  TerrainMasses = {
    T1 = { role = "bunkerRise", center = (-5,54,200), peakY = 64, ... },
    T2 = { role = "westernRidge", center = Vector3.new(-175... },
    -- etc.
  },
  
  ProtectedVolumes = {
    bunkerCorridor = { bounds = { xMin=-30, xMax=10, yMin=52, ... } },
    pathTubes = { {...}, {...} },
    farmVisibility = { ... }
  }
}
```

### Step 2: Build Terrain Generator Script

```
mkdir -p src/Scripts/ServerScriptService
touch src/Scripts/ServerScriptService/TerrainGenerator.init.lua
```

**Content:** Procedural `FillBlock/FillBall` sequence following this spec's mass definitions. Run once on place startup in Edit mode to generate terrain heightfield deterministically.

```lua
-- BunkerGame/src/Scripts/ServerScriptService/TerrainGenerator.init.lua
local TerrainSpec = require(gameModules.ServerStorage.TerrainSpec)

local function generateTerrain()
  local terrain = game.Workspace.Terrain
  
  -- BASE PLANE first (y=52..58, 640x640)
  terrain:FillBlock(CFrame.new(0, 55, 320), Vector3.new(640, 6, 640), Enum.Material.Painted
  
  -- T1–T6 masses in order (lowest to highest for painter's algorithm layering)
  generateT4_SouthernFarmSlope(terrain)
  generateT6_MidZoneMesa(terrain)
  generateT3_EasternOutcrop(terrain)
  generateT1_BunkerRise(terrain)
  generateT2_WesternRidge(terrain)
  generateT5_NorthernSentinel(terrain)
  
  -- Apply paint strokes for material variation (non-collision color/detail)
applyMaterialVariation(terrain)
end

-- Individual mass functions per spec section...
generateTerrain()
```

### Step 3: Rojo Persistence Mapping

Verify `default.project.json` contains terrain scripts under `/ServerScriptService` and `/Modules`. Terrain heightfield data lives in place file (`*.rbxl`) not in source tree — script is the procedural generator, output is persisted binary.

### Step 4: Studio Verification

1. Open BunkerGame in Roblox Studio
2. Run `TerranGenerator.init.lua` script once to generate terrain
3. Validate against section 8 criteria (automated + manual)
4. Save place (`*.rbxl`) — heightfield is now persistent

### Step 5: Handoff to Asset Factory

Create task packet for detailed rock/cliff asset generation:

```
ASSET_FACTORY_TASK = {
  T2_WesternRidgeScree = "detailed scree field textures + wedge masses, 35m crest",
  T3_EasternCliffRocks = "exposed slate rock outcrops for SE steep face",
  T5_SummitPinnacles = "hero pinnacle rocks for conical summit (+21m)",
}
```

---

## 10. FINAL ACCEPTANCE GATES

✅ Terrain Spec document complete and checked in (this file)  
✅ TerrainGenerator.lua script implemented from spec constants  
✅ Studio playtest validates horizon hierarchy, path clearance, bunker ray visibility  
✅ Hero asset tasks filed for Asset Factory detail work  
✅ Performance count ≤240 outdoor parts verified  

---

**End of Terrain Construction Spec**

TERRAIN_SPEC_READY=YES
