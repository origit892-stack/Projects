# Pipeline repurpose — LATER task (NOT started; needs user OK)

**Why:** the Shorts cron (`714a080066ef`, 2x daily) is a proven machine that finds material, builds 9:16 video, and uploads. Pointing it (or a clone of it) at daily demo clips = a storefront that's open 24/7 with zero daily effort.

**Change (when approved):**
1. Clone the pipeline config into a second cron profile path (`~/.hermes/yt-short-pipeline/demo-mode/`) — do NOT edit the live CC-only pipeline; run both.
2. Demo-mode source = a small curated list of self-made "demo clips" (from DEMO_PLAN.md, rotated weekly) instead of CC search. Same cut/vertical/upload/upload-verify chain.
3. Same channel (PowerPlayPalace) OR a second channel "The Agent Operator" — decide with user (mixing clips + agent content on one channel dilutes the algo; second channel = cleaner but starts from 0 again).
4. Upload cadence: 1x/day is enough for a B2B proof channel (shorts pipeline proven at 2x/day; 1x/day is a lighter load on the same machinery).

**Risks/gates:**
- Requires user decision (channel strategy) — it's a change to a live production cron's sibling, not to the cron itself.
- Attribution rules don't apply to self-made content (simpler, not harder).
- First demo clip = the ffmpeg build in DEMO_PLAN.md (clip 1).

**Success metric (30 days):** channel has ≥15 clips, ≥1 profile visit per week attributed to a clip (Upwork "profile views" + Fiverr "views"), ≥1 conversation started citing a video.
