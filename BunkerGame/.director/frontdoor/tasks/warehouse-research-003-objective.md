# Task: warehouse-research-003 (researcher)

## Objective
Nail down the EXACT, currently-working command sequence to (A) generate a single mesh with the installed cube3d pipeline and (B) publish that single mesh to Roblox via the existing upload workflow, so a downstream implementer can execute it verbatim. Read-only.

## Project root
/Users/Ori/Documents/Projects/BunkerGame

## Known verified facts (do NOT re-derive; confirm only if cheap)
- cube3d CLI: `/Users/Ori/Developer/roblox-cube/.venv/bin/python -m cube3d.generate --config-path /Users/Ori/Developer/roblox-cube/cube3d/configs/open_model_v0.5.yaml --gpt-ckpt-path /Users/Ori/Developer/roblox-cube/model_weights/shape_gpt.safetensors --shape-ckpt-path /Users/Ori/Developer/roblox-cube/model_weights/shape_tokenizer.safetensors --output-dir <dir> --prompt "<text>" --resolution-base 6.0 --top-p 0.8 [--bounding-box-xyz X Y Z]` -> outputs .obj (+.mtl).
- Upload CLI: `/Users/Ori/Developer/roblox-assets/.venv/bin/roblox-assets` (subcommands list/find/inspect/create/publish/integrate).
- Auth: macOS login keychain services ROBLOX_OPEN_CLOUD_API_KEY + ROBLOX_CREATOR_USER_ID for user Ori.
- Prior task impl-publish-bunker-rooms published 10 meshes and reported the prescribed "Model publish + inspect" flow was NOT usable; it used a "direct Mesh-asset upload" instead.

## Investigate (read-only)
1. cube3d liveness: run `--help` (or import) to confirm the CLI still works. Report exit code only.
2. THE KEY ITEM — exact working single-mesh upload sequence. Find the actual script(s)/commands the prior impl-publish-bunker-rooms task used for "direct Mesh-asset upload". Look in:
   - /Users/Ori/Documents/Projects/BunkerGame/tools/ (proof/, builders/, and any new scripts)
   - /Users/Ori/Developer/roblox-assets/ (CLI source, esp. publish/roblox.py, and any mesh-upload path)
   - /Users/Ori/Developer/roblox-assets/assets/ (staging dir layout: <asset_id>/final/ + manifest.json format)
   - git log / recent files in the project for a warehouse or mesh-upload helper
   Report the EXACT commands in order: obj->glb conversion (trimesh in /usr/bin/python3), staging (dir + manifest.json fields), and the publish command. Include the manifest.json schema verbatim.
3. Confirm which Roblox asset TYPE the direct mesh upload produces (Mesh vs Model) and what ID is returned (the MeshPart MeshId = rbxassetid://<id>).
4. Confirm auth is present (keychain metadata only; do NOT print values).
5. Identify the exact `roblox-assets` subcommand + flags to publish a single .glb as a Mesh and to read back/verify the resulting asset id (e.g. `inspect`, `find`, or a GET to apis.roblox.com/assets/v1/assets/<id>).

## Constraints
- Read-only. Do not modify any files. Do not run the actual generation or publish.
- Do not print full secrets.
- Keep the report compact (under 120 lines).

## Output
A compact, copy-pasteable runbook: (1) generate command, (2) convert command, (3) staging steps + manifest.json schema, (4) publish command, (5) verify command. Each step with exact paths/flags and VERIFIED_FACT/INFERENCE/UNKNOWN classification.