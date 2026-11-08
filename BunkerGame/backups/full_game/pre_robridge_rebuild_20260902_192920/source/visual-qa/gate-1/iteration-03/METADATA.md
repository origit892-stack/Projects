# Gate 1 Iteration 03 — Evidence Metadata

**Generated:** 2026-08-28
**Builder:** `tools/builders/generate_full_game_world.py`
**Output SHA-256:** `2f86075f5c86625ab13c1dfd78b753cc032459a106e45dc21bfc0e92e38acd21`
**Supersedes:** Iteration 02 (rejected)

## Key Changes from Iteration 02

1. **WestPortalBlock DELETED** — no fake occluder across route
2. **All terrain near route uses WedgeParts** — no visible vertical faces above ~3 studs
3. **Overburden = 4 stepped WedgePart terraces** (T1-T4) rising from Y=55.5 to Y=60.75
4. **All terrain pieces collide=True** — physical landforms, not visual walls
5. **Route corridor clear** — no terrain intersecting the 14-18 stud path

## Terrain Shelf Parts (15 total, 13 WedgeParts)

| Part | Type | Position | Size | Role |
|------|------|----------|------|------|
| ApproachWestLow | WedgePart | (-18, 55, -100) | 8×2×55 | Low west corridor flank |
| ApproachEastLow | WedgePart | (16, 54.75, -95) | 6×1.5×50 | Low east corridor flank |
| WestShoulderBroad | WedgePart | (-40, 56.5, -20) | 35×5×55 | Dominant west slope |
| WestShoulderUpper | WedgePart | (-45, 56, 30) | 30×4×45 | Upper west terrain |
| EastLowGround | WedgePart | (38, 55, 30) | 30×2×60 | East counter-space |
| EastLowTransition | WedgePart | (35, 54.75, -25) | 22×1.5×50 | East transition |
| OverburdenT1 | WedgePart | (0, 55.5, 55) | 100×3×30 | Terrace 1 (lowest) |
| OverburdenT2 | WedgePart | (0, 57.25, 85) | 110×3.5×30 | Terrace 2 |
| OverburdenT3 | WedgePart | (0, 59, 115) | 105×4×28 | Terrace 3 |
| OverburdenT4 | WedgePart | (0, 60.75, 142) | 95×3.5×25 | Terrace 4 (highest) |
| OverburdenWestFlank | WedgePart | (-55, 56.5, 100) | 25×3×85 | West flank transition |
| OverburdenEastFlank | WedgePart | (50, 55.75, 100) | 20×2.5×80 | East flank transition |
| RearRidge | WedgePart | (0, 59, 185) | 140×10×50 | Background ridge |
| RearRidgeUpper | Part | (0, 61.5, 195) | 120×5×35 | Ridge cap |
| NorthFill | Part | (0, 56, 205) | 120×4×35 | North terrain fill |

## Validation

| Check | Result |
|-------|--------|
| Builder validation (61 position checks) | PASS |
| BaseParts: 977 | PASS (< 2500) |
| CollidableParts: 254 | PASS |
| Descendants: 1313 | PASS (< 3600) |
| ExteriorBaseParts: 182 | PASS |
| Rojo sourcemap | PASS |
| Rojo build | PASS |
| Studio sync (1313 descendants) | CONFIRMED |
| Studio mode | EDIT |

## Capture Coordinates

| View | Camera | Look-At | Description |
|------|--------|---------|-------------|
| A | (0, 56, -200) | (-12, 56, -130) | Route along first segment, corridor open |
| B | (-38, 56, -70) | (0, 58, 16) | Turn/reveal, portal clearly visible |
| C | (-80, 72, -50) | (0, 58, 50) | 3/4 composition, overburden silhouette |
| D | (0, 56, 8) | (0, 60, 20) | Entrance scale, crown/sign readable |
| E | (-180, 68, 80) | (0, 60, 80) | Side silhouette, roof concealed |
