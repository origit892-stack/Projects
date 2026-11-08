# PROJECT MEMORY

All project memory for this repository lives here (in-repo, versioned) — not only in local agent vaults.

## Standing rule (user, 2026-11-08)
- **Every new/changed file in this repo gets committed + pushed** (as `origit892-stack <origit892@gmail.com>`), including during long sessions — after each meaningful phase, not only at the end.
- Files >100 MB go through **git-lfs** (GitHub free tier: 1 GB LFS storage).
- Keep `MEMORY/` updated when project state changes (checkpoints, decisions, verified facts).

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

**LFS plan (2026-11-08, md5-verified numbers):**
- Un-ignored 17.82 GB on disk → **unique content 5.91 GB** (11.91 GB was nested duplicate copies; git dedupes by content).
- 48 files >100 MiB (5 captures.zip copies, 42 .mov copies, 1 .glb) → git-lfs (`.gitattributes`, 48 explicit paths). Unique LFS payload **4.29 GB** — **exceeds GitHub free 1 GB LFS quota** → LFS pushes largest-first until quota rejection, then stop and surface to user (paid LFS or alternative storage).
- Remaining unique ~1.62 GB (all <100 MB) → chunked normal pushes (caches → visual-qa → backups), LFS paths excluded from those commits so their pushes don't upload LFS objects.

**Security note:** user pasted a GitHub password in chat 2026-11-08 → advised rotation; pushes use the PAT already in the macOS keychain.

## Recovery keys
- Local repo: `~/Documents/Projects` (branch `main`)
- Zip original (immutable): `~/Downloads/Projects 2.zip` (1,117,781,179 bytes)
- Scratch (deletable after confirm): `~/.hermes/cache/scratch/proj2/` (extraction + overwrite backups + merge report)
