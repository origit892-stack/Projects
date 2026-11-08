# Gate 1 Iteration 02 — Evidence Metadata

**Generated:** 2026-08-28
**Builder:** `tools/builders/generate_full_game_world.py`
**Output SHA-256:** `0aa26a75b2e7f9ec885cfa918fd6aee77b00beb98f18498f03b7e05ab19e9e2c`
**Supersedes:** Iteration 01 (rejected)

## Changes from Iteration 01

### Approach Route — Real Lateral Displacement
Replaced 3-segment near-straight path with genuine dogleg:
- SouthApproachA: (0, -210) → (-12, -140) — initial south bearing
- SouthApproachB: (-12, -140) → (-38, -70) — 26-stud westward displacement, 20° rotation
- SouthApproachC: (-38, -70) → (-18, -20) — northeast turn toward portal
- EntranceApron: (-8, -22) → (0, 24) — final approach to entrance

### Terrain Shelf — 14 Parts (3 WedgeParts)
| Part | Position | Size | Type | Purpose |
|------|----------|------|------|---------|
| OverburdenCap | (0, 72.5, 95) | 110×10×100 | Part | Covers bunker roof Z=45-145 |
| OverburdenWestTransition | (-55, 68, 95) | 30×8×100 | Part | Slopes cap down west side |
| OverburdenEastTransition | (52, 66.5, 95) | 25×6×95 | Part | Slopes cap down east side |
| RearRidge | (0, 61, 185) | 160×14×60 | Part | Background ridge above roofline |
| WestShoulderUpper | (-38, 57.5, 30) | 45×7×55 | Part | Upper west terrain mass |
| WestShoulderLower | (-42, 56.25, -25) | 55×4.5×65 | Part | Lower west terrain |
| WestPortalBlock | (-10, 59, -65) | 30×10×25 | Part | Blocks portal from initial approach |
| WestShoulderBase | (-35, 55.5, -70) | 40×3×50 | Part | Base of west shoulder |
| WestShoulderSlope | (-28, 56.5, 10) | 18×5×40 | WedgePart | Sloped west shoulder face |
| EastLowGround | (40, 55.25, 40) | 35×2.5×70 | Part | Low east counter-space |
| EastLowTransition | (38, 55, -20) | 25×2×55 | Part | East transition |
| ApproachBermWest | (-28, 55.75, -90) | 20×3.5×60 | Part | West approach berm |
| ApproachBermWestSlope | (-22, 55.25, -85) | 10×2.5×45 | WedgePart | Sloped approach face |
| NorthOverburden | (0, 58, 200) | 130×8×40 | Part | North terrain fill |

### Entrance Earthworks — Reduced Scale
- PortalCrown: 20×3×6 (was 38×6×14) — no longer clips OUTPOST title
- WestButtress: 4×10×6 (was 8×16×12)
- EastButtress: 4×10×6 (was 8×16×12)
- WestShoulder: 30×8×30 (was 55×18×45)
- EastShoulder: 22×5×22 (was 50×16×42)
- Added WestShoulderLow: 25×4×25

### Instance Count Changes
| Metric | Iteration 01 | Iteration 02 | Delta |
|--------|--------------|--------------|-------|
| BaseParts | 975 | 976 | +1 |
| Descendants | 1311 | 1312 | +1 |
| Exterior BaseParts | 180 | 181 | +1 |

## Capture Positions

| # | ID | Camera | Look-At | Description | Self-Check |
|---|-----|--------|---------|-------------|------------|
| 1 | 01_final | (-12, 56, -140) | (-12, 56, -60) | Initial approach — portal fully occluded by WestPortalBlock | ✓ PASS |
| 2 | 02_final_reveal | (-28, 56, -50) | (-5, 58, 15) | Turning/reveal beat — portal appears off-center after dogleg | ✓ PASS |
| 3 | 03_bunker_reveal | (-18, 56, -20) | (0, 60, 20) | Primary bunker reveal — PortalCrown + entrance visible | ✓ PASS |
| 4 | 04_composition_3_4 | (-100, 75, -60) | (0, 60, 50) | 3/4 elevated — foreground/midground/background separation | ✓ PASS |
| 5 | 05_entrance_scale | (0, 56, 5) | (0, 60, 20) | Entrance/player-scale — OUTPOST title visible, crown proportionate | ✓ PASS |
| 6 | 06_side_silhouette | (-180, 70, 80) | (0, 62, 80) | Side silhouette — overburden conceals bunker roof | ✓ PASS |

## Self-Check Results

- [x] Portal occluded from initial approach (01_final)
- [x] Portal revealed after dogleg turn, off-center (02_final_reveal)
- [x] No vertical trench walls — terrain slopes via WedgeParts + overlapping masses
- [x] Overburden cap covers bunker roof from Z=45 to Z=145 (06_side_silhouette)
- [x] PortalCrown does not clip OUTPOST title (03_bunker_reveal, 05_entrance_scale)
- [x] Asymmetric — dominant west shoulder, lower east counter-space
- [x] Three elevation bands visually evident
- [x] No bilateral symmetry in approach or framing
