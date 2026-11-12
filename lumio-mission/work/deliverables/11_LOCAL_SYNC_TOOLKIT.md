# 11 — Local Sync Toolkit (Lumio 4.1)

The "automatic even without an official API" layer. Built 2026-11-12 after the
user confirmed the three approaches (open-source wrappers, Moodle AJAX, browser
extension for Ofek) and provided the live school Shahaf URL.

## Why local
Mashov, Ofek and Petel/Moodle have **no public read API** and Lumio's iron rule
is **never holding user passwords**. So the sync runs on the student's own
machine with the student's own account; only the data (tasks/grades) travels to
Lumio, authenticated by a per-user **sync key** (capability token, revocable in
the app). The browser-extension path needs no password at all — it rides the
existing browser session.

## Components (all in the repo, source of truth: `lumio-mission/work/source/lumio-v3.3/`)

| File | What | Status |
|---|---|---|
| `local-sync/lumio_push.py` | Shared pusher (stdlib only). Key resolution: CLI → env → `~/.lumio/config.json` (0600) → built-in public defaults. | VERIFIED (py_compile; 404 path tested live pre-deploy) |
| `local-sync/mashov_sync.py` | Mashov via **pymashov** (real PyPI lib, MIT, t0mer/pymashov v0.0.2 — VERIFIED against PyPI/GitHub docs 2026-11-12: `get_homework`, `get_grades`, `POST /api/login` at web.mashov.info, no 2FA support). Homework+grades → items with `mashov:` external-id prefixes; `--dry-run`, `--save-key`, `--loop N`, `--discover` student id. | VERIFIED (py_compile, `--help`, push error path). **UNVERIFIED end-to-end**: needs the student's real account on first run (no credentials available to the agent; brief forbids credential handling). |
| `local-sync/moodle_sync.py` | Generic Moodle (e.g. Petel): login → sesskey → `core_calendar_get_action_events_by_timesort` via `/lib/ajax/service.php` (the documented internal AJAX from the user's own notes) + heuristic grade-table parse of `/grade/report/overview/`. Cookie-sesskey mode needs no password. | VERIFIED (py_compile, `--help`). **UNVERIFIED end-to-end**: Moodle instances vary; `--dry-run` is the first-run contract. |
| `local-sync/README-HE.md` | Student instructions (Hebrew): key creation, first run, Task Scheduler/launchd for full automation. | written |
| `ofek-extension/` | **Lumio Ofek Bridge** — MV3 Chrome extension. `capture.js` runs in the page **MAIN world** (document_start) wrapping fetch/XHR and scoring task-like JSON; `content.js` (isolated) shows a floating 📤 button, extracts best blob (or visible-text fallback) and POSTs to ingest with `source:'ofek'`; options page stores only the sync key + API test. host_permissions: `*.cet.ac.il`, `*.matan.co.il`, the Supabase project only. | VERIFIED (manifest JSON valid; node --check 3/3 JS). **UNVERIFIED in a real Chrome against a live Ofek session** (no student login available; MoE SSO is by design out of agent scope). |
| `ofek-extension/README-HE.md` | Install + usage + security notes. | written |

## Provenance honesty (iron rule compliance)
- Ingest now accepts `source ∈ {classroom, mashov, ofek, petel}` (whitelist;
  default `classroom` keeps the Apps Script template backward compatible).
- `retrieval_method` = `official_api` **only** for Classroom (genuine official
  API); all local-script/extension pushes are stored as the new
  **`local_sync`** method, labeled in the UI as "סנכרון מקומי (סקריפט/תוסף שלך)".
  The DB CHECK lists in `database-upgrade-2.sql` include `local_sync`
  (upgrades not yet run on the live project — the column does not exist yet).
- The connections state update targets `provider = source` (was hardcoded
  'classroom'), so a Mashov sync marks the Mashov card, not Classroom.

## What is server-side automatic (PC off) vs student-side
- **Shahaf (katzirb.shahaf.site)**: server cron (pg_cron → feed-sync) — full
  automation, no student action after connecting the feed. Live fetch verified:
  39 items, stamp `11.11.2026, שעה: 20:35`, all with end times.
- **Google Classroom**: Apps Script daily trigger (student deploys once) — full
  automation on Google infra.
- **Mashov / Moodle / Ofek**: student-machine automation (loop / scheduler /
  one-click button) — the honest limit while passwords stay off Lumio's servers.

## Remaining verification (needs the student/user, cannot be done by the agent)
1. First `mashov_sync.py --dry-run` with the real account (endpoint drift → `pip install -U pymashov`).
2. First `moodle_sync.py --dry-run` on the school Moodle (markup drift → adjust parser, output is the contract).
3. Ofek extension loaded in Chrome on a logged-in student session (capture hit-rate; JSON shape adaptation if needed).
4. ~~Supabase deploy~~ — **DONE 2026-11-12 (night)**: SQL upgrades applied live
   (incl. the `local_sync` CHECK value), both edge functions deployed via the
   Management API, `LUMIO_CRON_TOKEN` secret set, pg_cron job `lumio-feed-sync`
   live (`15 4 * * *` UTC ≈ 06:15 IST). **Full chain verified by executing the
   exact stored cron command**: pg_cron → pg_net → edge gateway (JWT) →
   feed-sync token gate → `200 {"ok":true,"feeds":0}` (read back from
   `net._http_response`). A full E2E (temp user → katzirb live feed → 39
   timetable rows → fact columns → complete cleanup) passed in the same session;
   the 3 real task rows and the 2 real users were verified untouched (the QA
   guerrillamail user was deleted).

## Evidence
- `npm test`: 38/38 pass (incl. katzirb live-shape fixture, ingest static checks
  for ALLOWED_SOURCES/local_sync/provider-row).
- `node --check`: 10/10 modules. `python3 -m py_compile`: 3/3 scripts.
- `deno check` (scratch copy, both functions): clean.
- Live site `origit892-stack.github.io/lumio-site/` serves 4.1: `/connectors.mjs`
  and `/app.mjs` verified 200 with katzirb + local_sync markers (commit `6e1d704`).
- Projects repo commit `422564b` (all of the above).
- No secrets in any of these files (scan: no `sb_secret_`, no JWTs; only the
  publishable `sb_publishable_...` key, which is public by design).
