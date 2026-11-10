# PROJECT MEMORY

All project memory for this repository lives here (in-repo, versioned) — not only in local agent vaults.

## Standing rule (user, 2026-11-08)
- **Every new/changed file in this repo gets committed + pushed** (as `origit892-stack <origit892@gmail.com>`), including during long sessions — after each meaningful phase, not only at the end.
- Files >100 MB go through **git-lfs** (GitHub free tier: 1 GB LFS storage).
- Keep `MEMORY/` updated when project state changes (checkpoints, decisions, verified facts).

## 2026-11-10 — chat-bridge added (synced from live copy)
**What:** Chat Bridge (v0.1.1) — Chrome extension + local daemon (`127.0.0.1:8765`) exposing the user's OPEN ChatGPT conversation over MCP to Hermes/OpenCode. 21 files synced from the live operational copy at `~/Downloads/chat-bridge`. No secrets in the tree (token lives only in `~/.chat-bridge/config.json`, mode 0600; sample configs are placeholders only).

**Included 2026-11-10 patch (not in the upstream 0.1.0 release):**
- `extension/content.js` re-mapped to the current ChatGPT DOM: `data-chatgpt-search-unit-key` (role) + `data-chatgpt-search-message-ids` (stable UUIDs, upsert by key); `cleanText()`; ProseMirror composer detection; send-button detection (data-testid → aria-label → composer footer). Old selectors kept as fallback.
- `extension/manifest.json` bumped 0.1.0 → 0.1.1 (version marker, forces Chrome to notice changes).
- Verified live end-to-end that day: auto-capture (12 messages), read, send (test round-trip, ChatGPT replied), DB auto-update.

**Operating model (important):** the OPERATIONAL copy is `~/Downloads/chat-bridge` (the Chrome extension loads from there; the daemon runs from there). The repo copy is the versioned source. Change flow: edit in `~/Downloads/chat-bridge` → **reload the extension in chrome://extensions** (Chrome caches content scripts until extension reload — page reload is NOT enough) → verify in daemon log/DB → re-sync to repo + commit.

**Known bug (user-confirmed 2026-11-10 — DO NOT fix in v0.1.x, superseded by v2):**
- Symptom: extension popup shows `Bridge unavailable: Failed to fetch`.
- Confirmed trigger: the daemon process was down (port 8765 connection-refused; happened once in-session after a process-session cleanup). The popup has no graceful degraded state — no retry/auto-reconnect, no hint to restart the daemon.
- User order: leave it; v2 replaces the transport/architecture anyway. (Restarting a dead daemon is normal ops, not "fixing" the bug.)

**v2 requirements (user, 2026-11-10):**
- Multi-provider support: **Claude, Gemini, ChatGPT, Grok** — the bridge must work with the user's open conversations on all four web UIs (per-provider DOM adapters + unified capture/storage/MCP). Design should also subsume the known bug (robust daemon-status/transport handling).


## 2026-11-08 — Two-copy merge + full push (COMPLETE)
**Problem:** two copies of this project — `~/Documents/Projects` (M1 Pro, 18 GB) and `Projects 2.zip` (snapshot of the other machine, zipped 2026-11-02). Both were on the same git commit `4ff775d`, so no history divergence — only working-tree differences.

**Merge (working-tree, file-level):**
- 53,708 zip-only files brought in: `masterpiece/`, `starry-night/`, `abandoned-warehouse/`, `video-bridge/`, `ori-projects/video-bridge/`, `src/` (Rojo packages), `documentations/`, `.playwright-cli/`, nested repos `dungeon-crawler-updated/.git` + `games/stick fight/.git` restored, WhatsApp reference image.
- 35 content conflicts resolved newest-first: 33 zip-won (europa-park-planner ×2, games/*.html, פיננסיה/trading_ai, fail_games), 2 local-won (`.DS_Store`, `default.project.json`).
- Merge report: `~/.hermes/cache/scratch/proj2/merge_report.json` (local, deletable after user confirms).
- First push commit: `fe3c4b6` "Merge 'Projects 2.zip' snapshot into main" — pushed & verified (local HEAD == origin/main).

**Size management (GitHub limits):**
- 109 MB `abandoned_warehouse_interior.glb` > 100 MB pre-receive limit → gitignored (on disk only).
- `BunkerGame/backups/` (12 GB) + `BunkerGame/visual-qa/` (4.6 GB) contain files up to 570 MB → initially gitignored; **2026-11-08 follow-up: user ordered EVERYTHING into git** → moved to git-lfs + chunked pushes (see below).
- Warning-only in git: `BunkerGame/artifacts/sharp_bunker/concept_61021.ply` (63 MB).

**LFS result (2026-11-08, FINAL — all landed):**
- Un-ignored 17.82 GB on disk → **unique content 5.91 GB** (11.91 GB was nested duplicate copies; git dedupes by content).
- **All 48 files >100 MiB pushed via git-lfs** (4.29 GB unique: captures.zip, 14 .mov sizes ×3 copies, .glb) — 17 chunked commits `4cae21b`→`9d15342`, every push succeeded (account LFS quota was larger than the assumed free 1 GB — no rejections).
- `git lfs ls-files` = 48; 0 untracked files left in the tree; local HEAD == origin/main == `9d15342`.
- Nested repos `dungeon-crawler-updated` (fa4f45b) + `games/stick fight` (ec5e519) kept as gitlinks at their existing SHAs (worktrees dirty internally — separate repos, untouched).

**Security note:** user pasted a GitHub password in chat 2026-11-08 → advised rotation; pushes use the PAT already in the macOS keychain.

## Recovery keys
- Local repo: `~/Documents/Projects` (branch `main`)
- Zip original (immutable): `~/Downloads/Projects 2.zip` (1,117,781,179 bytes)
- Scratch (deletable after confirm): `~/.hermes/cache/scratch/proj2/` (extraction + overwrite backups + merge report)
