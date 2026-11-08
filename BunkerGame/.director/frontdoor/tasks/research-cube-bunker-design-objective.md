# Task: cube mechanism + new bunker design (READ-ONLY)
Project root: /Users/Ori/Documents/Projects/BunkerGame

The user wants a NEW bunker: nice looking, organized rooms. Use existing assets if they fit; create new assets via cube if needed. A parallel implementer is DELETING src/Workspace/GameWorld.model.json (which held the StableGround ground) right now, so the new bunker must be self-contained or re-establish ground.

VERIFIED facts (trust, re-verify):
- 5 reusable assets in src/ServerStorage/GeneratedAssets/: bunker_vent_grille_01, bunker_valve_assembly_01, bunker_electrical_junction_box_01, old_military_ammo_crate_01, pipeline_pipe_retry_02. Registry: src/ReplicatedStorage/GeneratedAssets/AssetRegistry.json.
- Ground was GameWorld/Foundation/StableGround Part, top Y=54.0 (being deleted).
- cube = historical AI bunker-gen backend: cube/outputs/bunker_cube_v1.obj/.glb (manifest BUNKER_GENERATION_V3).
- Legacy builders: tools/builders/new_bunker/ (kit.py, architecture.py, power_room.py) + generate_new_bunker.py, generate_greenfield_bunker.py.
- Active builder: tools/builders/generate_full_game_world.py.

Investigate (file paths + line numbers):
1. cube mechanism (CRITICAL): what is it (CLI/Python/API/plugin)? how invoked (exact cmd/function/config)? inputs (prompt/seed/rooms/dims) and outputs (.obj/.glb/.model.json/Instances)? Is it runnable NOW (binary/package/config/server present)? Read the BUNKER_GENERATION_V3 manifest (params/output/quality). How would cube mesh output integrate into a Roblox model.json (MeshPart MeshId)? How are asset IDs obtained (AssetRegistry.json)?
2. New bunker design: map the 5 assets to rooms/elements. Recommended room layout (vocabulary + sizes) from legacy builders. Recommended footprint/position + base Y.
3. Ground dependency: GameWorld/StableGround being deleted - what ground will the new bunker sit on? Should the new bunker include its own ground/foundation to be self-contained?
4. Spawn on terrain: user wants spawn ON the ground. Current SpawnRoot.model.json PlayerSpawn at [0,55,0] on TestGround (top Y=55). Recommend spawn on ground near bunker entrance.

Output: compact report sections 1-4, each conclusion labeled VERIFIED_FACT/INFERENCE/UNKNOWN/STALE_OR_CONFLICTING, exact paths, under ~180 lines. End with RECOMMENDATION: (a) cube usable now? (b) representation + room list + footprint, (c) ground + spawn.
