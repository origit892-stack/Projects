# Gate 1 Iteration 01 — Evidence Metadata

**Generated:** 2026-08-28
**Builder:** `tools/builders/generate_full_game_world.py`
**Output SHA-256:** `3f6f8632408340415f8e4bbb6837f56aae220a84a2f359f956c1e94c1ff7de72`

## Changes from Baseline

### Files Modified
- `tools/builders/generate_full_game_world.py` — 4 edits:
  1. `build_landmarks()` — Replaced tiny BunkerEntranceEarthworks (2× mounds 28×6×26) with massive asymmetric earth shoulders (WestShoulder 55×18×45, EastShoulder 50×16×42) + enlarged PortalCrown/Buttresses
  2. `build_paths()` — Replaced straight SouthApproach (single 15-wide segment Z=-210→12) with 3-segment dogleg (SouthApproachA/B/C with lateral offsets)
  3. Added `build_terrain_shelf()` — 8 new terrain parts: RearRidge, WestFlank, EastFlank, SouthBasinWest/East, ApproachEmbankW/E, NorthOverburden
  4. `build_exterior()` — Wired TerrainShelf as new sub-model

### Instance Count Changes
| Metric | Baseline | Iteration 01 | Delta |
|--------|----------|---------------|-------|
| BaseParts | 935 | 969 | +34 |
| Descendants | 1298 | 1305 | +7 |
| Exterior BaseParts | ~166 | 174 | +8 |
| Exact Position Checks | 61 | 61 | 0 |

### Validation
- Builder validation: PASS (all 61 exact position checks, budget checks)
- Rojo sourcemap: PASS
- Rojo build: PASS (1.6 MB)
- Studio sync: CONFIRMED (1305 descendants live in Edit)

## Capture Positions

| ID | Camera Position | Look-At Position | Description |
|----|----------------|------------------|-------------|
| A_approach_dogleg | (0, 56, -180) | (0, 56, -40) | Player-height initial approach showing dogleg route and terrain framing |
| B_bunker_reveal | (0, 56, -10) | (0, 62, 25) | Player-height bunker reveal — portal cut in earth shoulder |
| C_composition_3_4 | (-80, 70, -80) | (0, 58, 50) | 3/4 elevated view — foreground/midground/background separation |
| D_entrance_scale | (0, 56, 5) | (0, 62, 20) | Player-scale entrance view — PortalCrown + buttresses + earth contact |
| E_side_silhouette | (-100, 65, 80) | (0, 60, 80) | Side silhouette — terrain shelf massing and elevation hierarchy |

## Final Capture Set (7 captures)

| ID | Camera | Look-At | Status | Notes |
|----|--------|---------|--------|-------|
| A_approach_dogleg | (0, 56, -180) | (0, 56, -40) | ✓ inline | Through AbandonedCheckpoint, terrain walls visible |
| A2_approach_wide | (0, 58, -140) | (0, 58, 0) | ✓ inline | Best approach view — embankment corridor framing entrance |
| B_bunker_reveal | (0, 56, -10) | (0, 62, 25) | ✓ inline | PortalCrown + earth shoulders + buttresses framing portal |
| C_composition_3_4 | (-80, 70, -80) | (0, 58, 50) | ✓ inline | 3/4 elevated — terrain masses visible |
| D_entrance_scale | (0, 56, 5) | (0, 62, 20) | ✓ inline | Close entrance — PortalCrown dominates, earth contact visible |
| E_side_silhouette | (-100, 65, 80) | (0, 60, 80) | ✓ inline | Too close to WestFlank |
| E_side_silhouette_wide | (-200, 80, 80) | (0, 58, 80) | ✓ inline | Best silhouette — terrain above bunker roofline, trees for scale |

## Evidence Persistence

`roblox-studio_screen_capture` returns images as inline conversation attachments only — it does not write PNG files to disk. The `roblox-studio_upload_image` tool requires local file paths as input (cannot receive inline data). No available tool can decode inline image data to persistent files.

**Recommendation:** Sol inspects the 7 inline captures directly from this conversation. If persistent PNGs are required, the user must manually save from the conversation or re-capture via Studio viewport screenshot (Alt+PrtScn or Studio menu).
