---
name: bunkergame-native-asset-pipeline
description: Use for BunkerGame requests to create, generate, build, place, vary, or rework visual Roblox assets such as trees, rocks, boulders, props, bunker pieces, vegetation, debris, furniture, machinery, and environmental art. Orchestrates Muse, Qwen, MiMo, Roblox Assistant native generation, BloxForge QA, Asset Library registration, Rojo persistence, and Studio verification.
---

# BunkerGame Native Asset Pipeline

This is the canonical production workflow for visual asset creation in BunkerGame.

The user gives a high-level request such as:

- "תעשה עצים אמיתיים"
- "תפזר אבנים ברחבי המפה"
- "תבנה שסתום חלוד"
- "תעשה וריאציה של העץ הזה לביום אחר"

The user must NOT need to manually coordinate agents.

## Canonical ownership

### Muse — Art Director

Muse owns:

- interpretation of the user's visual intent;
- art direction;
- deciding what Qwen must investigate;
- delegating implementation to MiMo;
- reviewing actual visual evidence after generation;
- accepting, requesting revision, or rejecting the result.

Muse must actually be invoked.

A final Muse review MUST occur after visual evidence exists.

Do not claim Muse participation without a real invocation/session.

### Qwen — Reasoner + Refrencer

Use `bunkergame-master-reasoner`.

Qwen owns:

- reasoning about the requested asset;
- proportions and silhouette;
- material/surface language;
- environment/context fit;
- generation strategy;
- reference strategy;
- finding the closest approved Asset Library family before generating something new.

Qwen is NOT the mesh generator.

Qwen must not replace Roblox Assistant.

## Reference priority

Before new generation, search the APPROVED Asset Library.

Reference priority:

1. USER_REFERENCE
2. LIBRARY_REFERENCE
3. QWEN_GENERATED_REFERENCE
4. ONLINE_REFERENCE
5. text-only generation only when a reference is unnecessary or unavailable

For a visually important asset, prefer reference-driven native generation when it materially improves quality.

Qwen must output exactly one provenance classification:

`QWEN_REFERENCE_SOURCE=USER_REFERENCE`
`QWEN_REFERENCE_SOURCE=LIBRARY_REFERENCE`
`QWEN_REFERENCE_SOURCE=QWEN_GENERATED_REFERENCE`
`QWEN_REFERENCE_SOURCE=ONLINE_REFERENCE`
`QWEN_REFERENCE_SOURCE=NONE`

### Critical library rule

Do NOT treat arbitrary Studio instances, archived content, `NOT IN USE WORLD`,
temporary meshes, rejected assets, test assets, or unregistered generated
content as approved Asset Library assets.

Only an asset explicitly registered in the canonical approved Asset Library
counts as `LIBRARY_REFERENCE`.

If a close approved family exists, use it as the base/reference for the new
variant instead of regenerating the concept from scratch.

## MiMo — Execution Orchestrator

Use `bunker-builder`.

MiMo owns execution/tool orchestration.

MiMo should receive:

- Muse art direction;
- Qwen reasoning;
- Qwen reference/provenance;
- target location/context;
- acceptance requirements.

MiMo must use real tool calls.

Do not claim MiMo participation without a real child session.

## Roblox Assistant — Creative Generator

Roblox Assistant/native Roblox generation owns:

- Mesh generation;
- native generated models;
- reference/image-to-mesh generation where available;
- creative geometry/composition;
- initial visual asset creation.

Prefer real native generation tools such as:

`roblox-studio_generate_mesh`

or the appropriate native Roblox generation operation exposed by Studio.

For important assets, use the strongest available reference.

Do NOT replace Assistant generation with fake Part/Wedge/Luau geometry when
the request requires a generated Mesh.

If native Assistant generation fails:

1. diagnose the failure;
2. retry safely when appropriate;
3. inspect whether the first call actually completed before generating again;
4. avoid duplicate generation;
5. remove accidental duplicate test output;
6. report the actual failure if generation remains unavailable.

Record actual generation evidence where available:

- generation ID;
- Assistant tag;
- RBXAssistant channel;
- MeshId;
- TextureID;
- generated Instance path.

## BloxForge — Engineering Partner

BloxForge owns technical inspection and engineering correction.

After Roblox Assistant generates the asset, BloxForge must actually inspect it.

Check as applicable:

- existence;
- class/type;
- mesh validity;
- dimensions;
- scale;
- pivot;
- orientation;
- anchoring;
- collision;
- placement;
- ground contact;
- intersections;
- topology/geometry suitability;
- performance;
- material configuration;
- gameplay obstruction;
- related technical defects.

BloxForge may correct engineering defects when necessary.

BloxForge must NOT unnecessarily replace a good Roblox Assistant asset merely
because it could construct something itself.

The collaboration model is:

`Roblox Assistant creates -> BloxForge inspects/fixes -> Assistant may revise/regenerate if the visual geometry itself is fundamentally wrong`

Do not claim BloxForge participation without an actual BloxForge MCP call.

Record the actual request/call ID when the tool exposes one.

## Muse Final Visual Review

After Assistant generation and BloxForge QA, Muse must review actual visual
evidence.

Muse evaluates:

- silhouette;
- realism;
- material/readability;
- scale impression;
- environmental fit;
- art-direction compliance;
- obvious generation artifacts;
- whether the asset is good enough to become reusable project memory.

Possible verdicts:

`MUSE_FINAL_REVIEW=PASS`
`MUSE_FINAL_REVIEW=REVISE`
`MUSE_FINAL_REVIEW=REJECT`

REVISE means return to Assistant/BloxForge as appropriate.

REJECTED assets must not enter the Asset Library.

## Asset Library

The Asset Library is BunkerGame's generative visual memory.

Before generation:
search it.

After successful generation:
register the asset automatically ONLY after:

1. Roblox Assistant generation succeeded;
2. BloxForge technical QA passed;
3. Muse final visual review passed.

Do NOT register:

- rejected assets;
- broken assets;
- temporary assets;
- benchmark assets;
- disposable proof assets;
- accidental duplicates.

Each approved reusable asset record should contain, when available:

- stable internal asset ID;
- asset name;
- category;
- family;
- variant;
- source/provenance;
- reference provenance;
- reference/base asset;
- Roblox MeshId;
- Roblox asset/model IDs;
- TextureID;
- filesystem path;
- dimensions;
- pivot;
- orientation;
- collision policy;
- anchoring;
- tags;
- intended uses;
- technical QA result;
- Muse approval;
- creation/orchestration trace.

When making a variation of an existing approved asset, keep it in the same
asset family unless Muse explicitly determines it represents a new family.

BloxForge owns technical registration/persistence.
Muse owns visual approval.

## Rojo / filesystem persistence

Permanent BunkerGame content must use filesystem/Rojo as source of truth.

Studio-only permanent edits are forbidden.

After Asset Library approval:

1. persist the approved asset/metadata into canonical filesystem source;
2. run appropriate validation;
3. use canonical Rojo workflow;
4. synchronize/verify in Studio;
5. verify no unrelated changes occurred.

Do not mark persistence successful merely because the asset exists in Studio.

## Studio verification

After persistence verify:

- expected asset exists;
- correct count;
- correct family/variant;
- correct placement where applicable;
- no unintended duplicates;
- no unrelated world changes;
- Studio mode is Edit.

For gameplay-affecting work, perform runtime QA as appropriate.

After every Play QA:

1. stop Play;
2. verify Studio returned to Edit;
3. do not leave a Play session running.

## Automatic variation behavior

Example:

User asks:
"אני רוצה עץ דומה אבל לביום אחר"

Required behavior:

1. search Asset Library;
2. identify closest approved tree family;
3. use that approved asset/reference as starting visual memory;
4. Qwen reasons about biome-specific changes;
5. Muse defines art direction;
6. MiMo orchestrates Assistant generation/edit;
7. BloxForge QA/fix;
8. Muse final review;
9. register as new variant in the SAME family if appropriate;
10. persist via filesystem/Rojo;
11. verify Studio.

Do not regenerate the entire concept from zero when an approved family already
provides a strong base.

## Distribution requests

For requests such as:

"תפזר אבנים ברחבי המפה"

separate:

A. asset creation/reuse
B. distribution/placement

First search the Asset Library for approved rock/boulder families.

Generate only missing variety.

Then use engineering-aware placement:

- avoid spawn obstruction;
- avoid gameplay anchors;
- avoid doorways/corridors;
- avoid critical interaction volumes;
- respect navigation;
- vary rotation and scale within approved limits;
- avoid obvious procedural repetition;
- verify counts and distribution.

## Evidence / anti-fabrication contract

Never infer participation.

A model/tool counts as invoked ONLY if actual execution evidence exists.

Every completed production asset operation must report:

ORCHESTRATION_TRACE

MUSE_INVOKED=YES|NO
MUSE_SESSION_ID=<actual id or NONE>

QWEN_INVOKED=YES|NO
QWEN_SESSION_ID=<actual id or NONE>
QWEN_REFERENCE_SOURCE=<allowed provenance or NONE>

MIMO_INVOKED=YES|NO
MIMO_SESSION_ID=<actual id or NONE>

ROBLOX_ASSISTANT_INVOKED=YES|NO
ROBLOX_ASSISTANT_TOOL=<actual tool or NONE>
ROBLOX_GENERATION_ID=<actual id or NONE>

BLOXFORGE_INVOKED=YES|NO
BLOXFORGE_TOOL=<actual tool or NONE>
BLOXFORGE_REQUEST_ID=<actual id or NONE>

MUSE_FINAL_REVIEW=PASS|REVISE|REJECT|NOT_RUN

ASSET_LIBRARY_REGISTERED=YES|NO
ASSET_FAMILY=<family or NONE>
ASSET_VARIANTS=<count>

ROJO_PERSISTENCE=YES|NO
STUDIO_VERIFICATION=YES|NO
STUDIO_MODE=<Edit/Play/UNKNOWN>

If evidence is unavailable, use NO/NONE/UNKNOWN.

Never fabricate YES.

## Success gate

A reusable production asset is COMPLETE only when:

- Muse actually participated;
- Qwen actually participated where reasoning/reference was required;
- MiMo actually participated;
- Roblox Assistant actually generated/edited the asset when generation was required;
- BloxForge actually QA'd it;
- Muse final review passed;
- reusable asset was registered in Asset Library;
- filesystem/Rojo persistence passed;
- Studio verification passed;
- Studio is left in Edit.

A disposable explicit proof/test asset is exempt from Asset Library and Rojo
only when the task explicitly says it is disposable.

## Error behavior

If an operation fails:

- identify the real failing stage;
- report the error accurately;
- attempt safe recovery;
- do not silently skip required agents;
- do not substitute a different model and claim the required model ran;
- do not fabricate evidence;
- do not register failed output;
- do not persist rejected output.

The user should receive the actual failure and recovery result.

## Core production chain

Canonical chain:

`User`
-> `Muse`
-> `Qwen reasoning/reference`
-> `Muse`
-> `MiMo`
-> `Roblox Assistant native generation`
<-> `BloxForge engineering QA/fixes`
-> `Muse final visual review`
-> `Asset Library`
-> `filesystem/Rojo`
-> `Studio verification`

This chain is mandatory for new reusable visual assets unless a step is
genuinely irrelevant and the evidence report explicitly explains why.
