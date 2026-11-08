# Visual QA Capture

## Purpose

The Visual QA capture tool provides video evidence of actual player-facing Roblox Studio Play sessions for milestone and Director review.

## Important limitation

The execution agent must not claim that it visually reviewed an MP4 unless its current model/tool environment genuinely exposes the video pixels. Captured MP4s are primarily external Director review artifacts. Pixel-level Visual Director approval belongs to the external Director unless the active agent genuinely has video-pixel access.

## Source of truth

Captures are evidence only. They are not game source. Filesystem/Rojo remains the permanent source of truth for game changes.

## Canonical commands

- `./tools/visual_qa/visual_qa.sh record <duration_seconds> <label>` — records a player-facing Studio capture through the proven recorder and emits stable record markers.
- `./tools/visual_qa/visual_qa.sh list` — lists review MP4 captures, newest first.
- `./tools/visual_qa/visual_qa.sh frames <video_path> [interval_seconds]` — extracts 720p JPEG review frames under `visual-qa/frames/`.
- `./tools/visual_qa/visual_qa.sh latest` — reports the newest review capture path, filename, byte count, and modification timestamp.
- `./tools/visual_qa/visual_qa.sh verify` — performs a short non-recording environment check for ffmpeg, osascript, writable capture directories, executable scripts, AVFoundation screen device 2, and reports whether Roblox Studio is currently open.

## Capture policy

Record meaningful player-facing milestones, not every small implementation change. Visual capture supplements rather than replaces Studio runtime inspection, Technical QA, Gameplay QA, BDS, AST validation, Rojo validation, or independent review.

Required Master Pass milestone labels are `POST_PHASE6_BUNKER`, `POST_LIGHTING_ATMOSPHERE`, `POST_EXTERIOR_REWORK`, `POST_FOREST_WORLD`, `POST_UI_POLISH`, and `FINAL_INTEGRATED_PLAYTEST`. Preserve every prior capture; do not overwrite evidence.

## Mandatory Play/capture lifecycle

No Play session may be left running after QA or capture. Every runtime operation uses this hard gate:

1. Start Play only when runtime evidence is required.
2. Verify Play through `get_studio_state`.
3. Perform only the intended QA or player-facing recording activity.
4. If the recording shell times out, inspect the existing ffmpeg process; never start a duplicate capture.
5. Verify the intended MP4 when recording completes. Compression/frame extraction does not require Play.
6. Immediately call `start_stop_play(false)`.
7. Call `get_studio_state` and require `Current Studio Mode: Edit` and `Available DataModels: Edit`. If Play remains active, Stop again and re-verify.
8. Only after Edit is verified, run `tools/visual_qa/visual_qa.sh finish` to attempt restoration of the existing Google Chrome/ChatGPT window. Focus failure is non-blocking.
9. Filesystem edits, builders, documentation, BDS, Rojo builds, source analysis, planning, phase transitions, long shell operations, and waiting happen only after Edit is verified.

`visual_qa.sh finish` assists only with browser focus. It does not and cannot prove Roblox Studio mode; authoritative Edit verification remains a Roblox Studio tool responsibility.

## Canonical OBS background-window workflow — 2026-08-21

OBS Studio background-window capture is now the canonical Visual QA recording path. `tools/visual_qa/visual_qa.sh` controls `tools/visual_qa/obs_capture.py` through OBS WebSocket on port 4455. Verified environment: OBS 32.2.2, WebSocket protocol 5.7.4.

- Keep the existing Google Chrome / ChatGPT window foreground whenever possible.
- OBS is configured to capture the Roblox Studio window while Studio remains in the background; do not activate Roblox Studio or OBS merely to record.
- Streamlabs is unrelated to this workflow and must not be modified.
- The previous foreground AVFoundation/ffmpeg screen-capture workflow is deprecated. Historical captures remain evidence and must not be deleted.
- External Director review owns pixel-level visual approval. Agent verification is limited to recording state, artifact existence/metadata, and runtime/gameplay facts unless the active model genuinely has video-pixel access.
- Every capture uses the lifecycle: verify Edit -> Start Play -> verify Play -> `visual_qa.sh start LABEL` -> `visual_qa.sh status` and require `OBS_RECORDING=True` -> perform intended runtime walkthrough -> `visual_qa.sh stop` -> require `VISUAL_QA_OBS_STOP=PASS` -> `visual_qa.sh latest` -> immediately Stop Play -> verify Edit.
- If OBS start fails, Stop Play and verify Edit before diagnosing OBS. If OBS stop fails, inspect OBS status and never start a duplicate recording. Roblox Play must still be stopped after the intended runtime work.
- No filesystem/source/build/documentation/planning work is permitted while Studio remains in Play.
