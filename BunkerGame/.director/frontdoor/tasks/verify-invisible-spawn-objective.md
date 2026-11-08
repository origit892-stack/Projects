# Task: INDEPENDENT verification of invisible terrain spawn (READ-ONLY)
Project root: /Users/Ori/Documents/Projects/BunkerGame

You are an independent verifier. Do NOT modify any file. Verify the live source against the user objective: "delete ALL spawn platforms and create ONE invisible spawn that makes the player spawn ON the terrain."

## What to verify (independent, from live src/ — do not trust the implementer's claims, re-derive from files)
1. Read `src/Workspace/SpawnRoot.model.json` in full. Confirm:
   - It is valid JSON.
   - Top-level ClassName == "Model" (wrapper preserved so Workspace.SpawnRoot mapping holds).
   - It contains EXACTLY ONE child, a SpawnLocation named "PlayerSpawn".
   - That SpawnLocation has: Anchored=true, CanCollide=false, Neutral=true, Enabled=true, Duration=0, Transparency=1, Size=[8,1,8], Position=[0,54.5,0].
2. Confirm the visible platform is GONE: `grep -rn "TestGround" src/` must be 0 matches; no Part with CanCollide=true / Material=Concrete remains in SpawnRoot.model.json.
3. Confirm exactly ONE enabled SpawnLocation instance file exists in live src/: `grep -rln "SpawnLocation" src/` — the only INSTANCE file should be src/Workspace/SpawnRoot.model.json (other hits are code refs in .luau, which are fine and must be untouched).
4. Confirm no out-of-scope files were modified: `find src -type f -mmin -60` should return ONLY src/Workspace/SpawnRoot.model.json. Confirm default.project.json and all .luau files are untouched (mtime / content).
5. Confirm a pre-edit backup exists and is byte-identical to the ORIGINAL (pre-edit) content: backup at `.director/backups/invisible-spawn-*/SpawnRoot.model.json`. The original pre-edit content was the 381-byte file containing BOTH TestGround (Part, CanCollide=true, Material=Concrete, Size=[40,1,40], Position=[0,54.5,0]) AND PlayerSpawn (Position=[0,55,0]). Verify the backup still contains TestGround (i.e. it is the pre-edit version, not the new one) and is non-empty.
6. Sanity: Position [0,54.5,0] places the spawn center 0.5 studs above the inferred terrain surface Y=54.0 at (0,0) (terrain datum is INFERENCE; no terrain data in src/). Confirm this is consistent with spawning ON the terrain (character lands on surface, not inside it). Note any residual risk that the actual .rbxlx terrain height at (0,0) may differ (this is a known, accepted limitation — filesystem cannot verify runtime terrain height).

## Output
Compact report, each conclusion labeled VERIFIED_FACT / INFERENCE / UNKNOWN / STALE_OR_CONFLICTING, with exact file paths + line numbers + command evidence. Under ~80 lines. End with an explicit VERDICT: PASS or FAIL, and if FAIL, the exact failing item(s).