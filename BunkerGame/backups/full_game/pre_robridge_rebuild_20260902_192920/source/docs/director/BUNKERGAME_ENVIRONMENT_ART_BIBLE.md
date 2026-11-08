# BunkerGame Environment Art Bible

## Authority and Scope

**Status:** Human Director approved  
**Approval scope:** Gate 1 spatial/compositional reference only  
**Authoritative reference:** `Workspace.SOL_GATE1_GOLDEN_REFERENCE`, version `v36-focused-reveal-candidate`  
**Durable artifact:** `artifacts/sol-gate1-golden-reference/SOL_GATE1_GOLDEN_REFERENCE.build.luau`  
**Required evidence:** `artifacts/sol-gate1-golden-reference/evidence/reveal-pass/`

v36 is mandatory teaching evidence for spatial design. It is **not** a
finished-art reference. Production must reproduce its spatial logic, not copy
its present vegetation, lighting, materials, path finish, or architectural
detail level.

## 1. Golden Spatial Rules

These rules are mandatory for production Gate 1.

1. **One coherent landform.** The approach, shoulders, bunker burial, and rear
   ridge must read as connected geology—not separate mounds or assembled ramps.
2. **Terrain-driven dogleg.** The primary route must make a meaningful lateral
   displacement and heading change because of the landform.
3. **Delayed visibility.** The bunker entrance must not be clearly readable
   from the initial approach or immediately before the dogleg.
4. **Reveal beat.** After the direction change, the entrance becomes the
   primary read; the route is secondary and the enclosing ridge is tertiary.
5. **Buried facility.** The bunker reads as a fortified opening cut into a
   mountain. Most roof and side-shell mass remains concealed.
6. **Direct terrain contact.** Earth meets retaining structure, portal frame,
   and exposed construction edges without a visible gap or a dirt canopy placed
   over a freestanding box.
7. **Player-scale traversal.** Route width, grade, camera clearance, entrance
   clearance, and turning space must work at Roblox avatar scale.
8. **Asymmetry.** One side supplies stronger terrain/structural framing while
   the other supplies counter-space. Do not mirror the reveal.
9. **Depth layers.** Player views must contain intentional foreground framing,
   a midground entrance/reveal, and a background ridge or landform continuation.
10. **Terrain dominance.** Even at the reveal, the hillside remains the largest
    visual mass. Architecture strengthens the discovery without exposing the
    complete bunker shell.

## 2. Future Visual Quality Targets

Every later gate must substantially exceed v36. Do not copy its placeholder
finish.

- **Vegetation:** authored forest clusters, species/age/scale variation,
  believable understory, controlled negative space, stronger tree assets, and
  no repeated silhouette rhythm.
- **Route surface:** erosion, runoff, compression, edge breakup, embedded
  stones/roots, material transitions, and terrain pressure that make the route
  feel formed rather than painted.
- **Bunker architecture:** credible structural thickness, retaining and
  drainage logic, deeper entrance sequencing, construction joints, functional
  infrastructure, and architecture appropriate to a serious buried facility.
- **Materials:** coherent high-fidelity ground, rock, concrete, metal, dampness,
  wear, and contact transitions with consistent scale and restrained variation.
- **Lighting and atmosphere:** survival-horror focal hierarchy, exterior to
  interior adaptation, readable darkness, atmospheric depth, controlled color
  relationships, and practical lighting rather than light spam.
- **Storytelling and polish:** purposeful weathering, damage, maintenance
  history, utilities, and restrained clutter. Every detail must explain
  function, history, navigation, or threat.

The following v36 qualities are explicitly **not** approved final targets:
grass, tree assets/repetition, vegetation diversity, path finish, lighting,
sky/atmosphere, material fidelity, bunker detail, weathering/storytelling, and
overall polish.

## 3. Anti-Patterns

Failed Iterations 01–05 established these rejection conditions:

- terrain balls, rounded blob chains, disconnected mounds, stacked slabs, or
  staircase wedges presented as a hillside;
- trench or box walls used in place of a continuous landform;
- a bunker box with dirt placed around or on top of it;
- exposed roof/side shell, flat facade, shallow doorway, or arbitrary primitive
  bunker massing;
- a straight approach that frames the entrance early;
- a fake rectangular occluder instead of terrain and route direction;
- a flat geometric path strip laid over the ground;
- mirrored retaining structures or centered bilateral composition;
- uniformly distributed, evenly spaced, or obviously repeated vegetation;
- disconnected retaining pieces, floating geometry, clipping, weak grounding,
  or visible terrain/architecture gaps;
- clutter, props, lighting effects, or weathering used to disguise unresolved
  massing;
- overhead/debug views used as primary art evidence;
- technical QA, worker opinion, or metric compliance presented as visual
  approval.

## 4. Objective Checks

MiMo must report these checks with current evidence. They are necessary, but
they do not replace Art Director or Human Director review.

### Spatial and Traversal

- Record the production route polyline and its segment headings. Demonstrate at
  least one deliberate heading change of **35 degrees or more** before reveal.
- Verify a continuous traversable route width of at least **12 studs** through
  the approach and dogleg.
- Sample route surface height along the centerline; report maximum grade and any
  abrupt step. No accidental step may exceed normal avatar traversal.
- Verify at least **7.5 studs** of clear entrance height and player-camera
  clearance along the intended path.
- Raycast from the initial approach and pre-dogleg cameras to the entrance focal
  point. Terrain must occlude both sightlines.
- Raycast from the reveal camera to the entrance focal point. The intended
  portal/recess must be reachable without an unintended blocker.
- Confirm no route mesh/part floats above or clips through terrain. If the route
  uses parts or meshes, sample and report surface-to-terrain offsets.
- Report the number and bounds of exposed bunker exterior components. Provide
  player views proving that roof and side shell remain substantially concealed.

### Required Visual Evidence

Capture fresh, uncropped gameplay-FOV views:

1. initial player-height approach;
2. player-height before dogleg;
3. player-height reveal moment;
4. player-height entrance/scale view;
5. player-relevant three-quarter composition;
6. side silhouette showing burial and ridge continuity.

Add close evidence for any suspected floating, clipping, transition, collision,
or camera-clearance defect. Do not substitute an elevated overview.

### Source, Persistence, and Safety

- `FILESYSTEM_SOURCE=PASS`
- `ROJO_MAPPING=PASS`
- `ROJO_BUILD=PASS`
- `ROJO_SYNC=PASS`
- `LIVE_EDIT_VERIFICATION=PASS`
- `PERSISTENCE_AFTER_RECONCILIATION=PASS`
- Production gameplay anchors and protected systems remain present and
  unchanged unless the active task explicitly authorizes a change.
- Studio is verified back in Edit mode after every runtime check.

### Visual Authority

MiMo may issue `TECHNICAL_QA=PASS`. MiMo may not issue
`VISUAL_QA=PASS`, `ART_DIRECTION=PASS`, or
`DIRECTOR_REVIEW=PASS`. Metrics can identify defects; only direct inspection
of current player-relevant evidence can approve composition and visual quality.
