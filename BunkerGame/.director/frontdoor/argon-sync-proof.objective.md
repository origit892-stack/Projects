# Objective: Complete the Argon end-to-end sync proof (BunkerGame)

## Goal
Get the repaired `src/Workspace/ArgonProof.model.json` content (specifically its
`MeshId`) to actually appear on the `ArgonProofMeshPart01` MeshPart in the LIVE
Roblox Studio session, and verify it via a Studio-side readback. This is the
final proof that the Argon file→serve→Studio pipeline works end-to-end.

## Completion gates (all must be VERIFIED, not assumed)
1. FILE_VALID_JSON — `src/Workspace/ArgonProof.model.json` is valid JSON and
   contains `MeshId=rbxassetid://779904485791`... (see exact value below).
   (Already PASS from prior work — re-verify quickly.)
2. SYNC_APPLIED — the serve's current snapshot for `ArgonProofMeshPart01`
   contains the correct `MeshId`, AND that value has been pushed to Studio.
3. STUDIO_MESHID_VERIFIED — a live Studio readback reports
   `MESHID=rbxassetid://77990448573791` on `ArgonProofMeshPart01`.

Do NOT convert UNKNOWN/FAILED/BLOCKED/UNVERIFIED into PASS.

## Exact target value
- MeshId MUST be: `rbxassetid://77990448573791`
- Intended Position: `[0,55,0]` (the file currently has a test value `[0,55.5,0]`;
  revert it to `[0,55,0]` as part of the fix).

## Verified current state (as of this handoff)
- Project root: `/Users/Ori/Documents/Projects/BunkerGame`
- Serve: PID **39326**, `argon serve --yes --color never -v`, listening on
  **port 8000** (both 127.0.0.1 and ::1), started with
  `ROBLOX_STUDIO_PATH=/Users/Ori/argon-studio-shim`. Log: `/tmp/argon_serve.log`.
  Session id in `~/.argon/sessions.toml` is `1` (pid 39326, port 8000).
- Studio plugin (Argon v2.0.23) IS connected to serve 39326 — `argon exec`
  executes code in Studio (verified repeatedly).
- Studio: place `129695090105158`, universe `8687457621`, Studio PID 32689,
  version 0.740.19.7400931. Log:
  `~/Library/Logs/Roblox/0.740.19.7400931_20260925T093526Z_Studio_764b1_last.log`
- File `src/Workspace/ArgonProof.model.json` (234 bytes) current content:
  `{"ClassName":"Model","Children":[{"Name":"ArgonProofMeshPart01","ClassName":"MeshPart","Properties":{"Anchored":true,"CanCollide":false,"Massless":true,"Size":[2,0.85,2],"Position":[0,55.5,0],"MeshId":"rbxassetid://77990448573791"}}]}`
- Project mapping (`default.project.json`): `Workspace` → `src/Workspace`.
- LIVE Studio readback (via `argon exec /tmp/readback_warn.luau 1 --yes --color never`,
  then grep Studio log for `ARGONPROOF6`) currently shows STALE values:
  `MESHID=` (empty), `POSITION=20, 54.42, -20`, while SIZE/ANCHORED/CANCOLLIDE/MASSLESS
  match the file. So the MeshId has NOT reached Studio yet.

## Root-cause findings already established (do not re-derive from scratch)
- The `http://localhost:13469/studio` ConnectFail lines in the Studio log are a
  RED HERRING (unrelated Studio service). The Argon plugin connects to
  `http://localhost:8000/` (root path). Port 8000 is correct.
- `save_mesh` (argon CLI `src/middleware/helpers/mesh_part.rs`) only writes a
  temp model when a MeshPart has `MeshContent` or `InitialSize`. Our
  `ArgonProofMeshPart01` uses `MeshId` only, so it does NOT need a temp model.
  The "Failed to load MeshPart: rbxasset://argon/39326/0" warnings in the Studio
  log are for OTHER MeshParts in the project — a red herring for THIS task.
- The EPERM on the real content path
  (`/Applications/RobloxStudio.app/Contents/Resources/content`) is macOS App
  Management protection; the `ROBLOX_STUDIO_PATH` shim
  (`/Users/Ori/argon-studio-shim`) is the established workaround and is already
  set on the serve.
- The serve (39326) started at 13:49:53 and loaded the file at startup. The
  MeshId was added to the file AFTER that, and the watcher has not re-pushed it
  (`files_synced` stayed 0 for our file; Studio still stale). The plugin's
  initial sync therefore ran against a snapshot that lacked the MeshId.
- Plugin reconnect behavior: `AutoReconnect=false`. The plugin only reconnects
  via a manual Connect action in Studio. It demonstrably reconnected to serve
  39326 earlier (user was at the machine). If the serve is restarted, the plugin
  will disconnect and may require a manual reconnect in Studio — this is a
  potential GENUINE_BLOCKER that requires user action (clicking Connect in the
  Argon Studio plugin UI). Report it as such if it occurs; do not fabricate a
  reconnect.
- Incoming changes in Studio go through an Accept/Diff/Cancel prompt only when
  `DisplayPrompts` is set to Always/Initial AND the change count exceeds
  `ChangesThreshold`. A single MeshPart property update is below threshold, so it
  should apply without a prompt.

## Recommended approach (smallest coherent change)
1. Re-verify the file is valid JSON with the correct MeshId (gate 1).
2. Revert the file's `Position` from `[0,55.5,0]` back to `[0,55,0]` (intended
   value). Preserve the MeshId exactly.
3. Force a clean re-sync so the serve re-loads the current file and the plugin
   re-runs its initial sync with the correct snapshot. The cleanest lever is to
   restart the serve (kill 39326, relaunch in BACKGROUND with
   `ROBLOX_STUDIO_PATH=/Users/Ori/argon-studio-shim`, `-P 8000`, higher verbosity,
   stdout/stderr → a log file, capture the new PID, poll readiness).
4. After the serve is up, verify the plugin is connected by running
   `argon exec /tmp/readback_warn.luau 1 --yes --color never`. If exec fails
   (no connected client), the plugin needs a manual reconnect in Studio →
   report GENUINE_BLOCKER (user must click Connect in the Argon plugin UI).
5. Once connected, re-run the readback and grep the Studio log for `ARGONPROOF6`
   to confirm `MESHID=rbxassetid://77990448573791` (gate 3) and
   `POSITION=0, 55, 0`.
6. If the MeshId still does not appear after a clean re-sync + confirmed
   connection, investigate the serve's snapshot for the MeshPart (the serve's
   temp/snapshot data) and the plugin's diff/apply path, and report the precise
   blocker with evidence.

## Hard constraints (must follow)
- NEVER run `argon serve` in the foreground / wait-for-completion. Always start
  it in the background with stdout/stderr redirected to a log file, capture the
  PID, and poll readiness with bounded commands. Do not wait indefinitely.
- Preserve the repaired `ArgonProof.model.json` and its MeshId
  (`rbxassetid://77990448573791`).
- Do NOT wrap `run_terminal_command` commands in outer double quotes (zsh
  mangles them). For multi-line content, write to a file via a
  `cat > file <<'EOF'` heredoc first, then execute.
- The `create_new_file` tool writes to PROJECT-RELATIVE paths (an absolute
  `/tmp/...` path becomes `<project>/tmp/...`). For `/tmp` scripts, use terminal
  heredocs instead.
- Readback MUST use `warn()` (not `print()`) to appear in the Studio log file.
- Do not perform destructive Git or terrain operations. Do not kill unrelated
  processes. The two extra argon serves on ports 8001/8002 (PIDs 45150/45172)
  are spawned by a VS Code extension and are NOT part of this task — leave them.
- Report truth: only claim PASS for a gate that was directly verified with
  evidence.

## Useful reference artifacts (already on disk)
- `/tmp/readback_warn.luau` — working Studio readback (warn-based).
- `/tmp/argon_serve.log` — current serve log.
- `/tmp/argon-cli-src` — argon CLI source (Rust).
- `/tmp/argon-roblox-src` — argon Studio plugin source (Luau).
- `~/.argon/sessions.toml`, `~/.argon/stats.toml` — serve session/stats state.