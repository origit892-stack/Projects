# Demo clips — 3 × ~30s vertical (720×1280), for Fiverr gig video + Upwork portfolio + Loom replacement

All content = REAL systems (screenshots/rendered terminal of real output). No invented footage.

## Clip 1 — "This runs without me" (hook clip; use as Fiverr gig video)
| s | Frame | Caption |
|---|---|---|
| 0-5 | Bold title on dark bg: **"This runs every day without me"** | |
| 5-12 | Terminal render: real `hermes cron list` output (shorts pipeline, schedule, last run OK) | "24/7 agent ops — scheduled, monitored, self-reporting" |
| 12-19 | Terminal render: run/ledger output (dedup ledger line / "last run ok") | "Failure? Alert + exact run id. Success? Verified on read-back." |
| 19-26 | GitHub repo page (public) | "Code you can audit: github.com/origit892-stack/Projects" |
| 26-32 | CTA card: **"Your AI employee in 1-2 weeks — $300 / $900 / $2,000 packages"** | |

## Clip 2 — "A store run by API"
| s | Frame | Caption |
|---|---|---|
| 0-4 | Title: **"124 products. Run by API."** | |
| 4-11 | Storefront screenshot (openshelf.1st4offers.com via browser) | "Live store — worldwide shipping, read-verified" |
| 11-18 | Terminal render: API GET/PUT flow (NO API key on screen — mask) | "GET before write. Read-back after. No silent failures." |
| 18-25 | Terminal render: verification output (counts match) | "Bulk ops are count-asserted — or they abort." |
| 25-30 | CTA: **"I build this class of system for your business"** | |

## Clip 3 — "I read systems before I touch them" (trust clip; use in proposals)
| s | Frame | Caption |
|---|---|---|
| 0-4 | Title: **"Before I touch your system, I read it."** | |
| 4-12 | Rendered report header: "554/554 files decoded — 0 residual" (from the RE report) | "Full RE pass on a commercial obfuscated app" |
| 12-20 | Terminal: `hermes cron list` (2nd profile: daily 08:00 research brief) | "Scheduled research that runs at 08:00 every day" |
| 20-28 | CTA: **"Operator, not tinkerer — fixed price, working delivery"** | |

## Build recipe (ffmpeg; run from this dir, `build.sh` to be created)
- Frames: `frames/frame_XX.png` at 1080×1920 (or 720×1280). Terminal frames rendered with PIL from REAL captured output (this kit contains the real `hermes cron list` text — see README proof list).
- `ffmpeg -f concat` or per-frame `-loop 1 -t 5` + `xfade=fade:duration=0.5` transitions; 30fps; H.264 yuv420p; silent AAC.
- Font: SF Mono / Menlo for terminal, SF Pro / Helvetica for captions. Dark bg #0d1117, green #3fb950 for "ok".
- Verify: `ffprobe` duration ≈ 30-32s, size 3-8MB; extract 2 frames and eyeball.

## After the video exists
- Fiverr: set as gig video (3x conversion vs no video).
- Upwork: attach to profile "portfolio" + link in proposals ("Loom/demo" ask).
- X/LinkedIn: post clip 1 with one line: "This runs every day without me. I build this for businesses — fixed price."
