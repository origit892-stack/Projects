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

## 4.2 update (2026-11-12) — "connect once, automatic on phone AND PC"
The data layer was already cross-device (connections + items live in Supabase,
per ACCOUNT, not per device). What was missing was making the feed path work
from a phone browser — and a live CORS probe proved why: the school pages send
**no `Access-Control-Allow-Origin`** (`katzirb.shahaf.site`: HTTP 200, zero
CORS headers; `web.mashov.info` preflight: HTTP 204, zero CORS headers).
Cross-origin fetches from any browser (phone or PC) are therefore blocked, so
the in-app feed buttons previously could not work from the browser at all.

**Fix (live + verified 2026-11-12):** all feed operations now run through the
`feed-sync` edge function with the student's own gateway-verified JWT
(`verify_jwt: true`):
- `POST {mode:'check', url, kind}` — server fetches + parses, returns a
  preview (no save).
- `POST {mode:'commit', provider, url, kind}` — the one-time connect: server
  fetches, upserts the student's rows (same dedup keys as before), and sets the
  connection facts incl. `feed_url` → pg_cron picks it up from the next run.
- `POST {mode:'refresh'}` — re-fetch the student's stored feeds on demand
  (the in-app "רענן פיד" button, now working from any device).
Security: no auth → 401 (gateway); a student JWT scopes every operation to that
student's rows only; the SSRF guard (`assertSafeFeedUrl`) runs on the
user-supplied URL in every mode; Shahaf stays host-allowlisted
(`*.shahaf.site`), ICS stays https-only.

**Live verification (same HTTP a phone browser issues, temp account, fully
cleaned up afterwards):** unauth → 401; `check` katzirb → 200, 39 items,
stamp `11.11.2026, שעה: 20:35`; `commit` → 200, saved 39, readback 39
school_items rows + connection `state=synced` with feed_url/stamp;
`refresh` → 200 `{ok:true, feeds:1, okFeeds:1}`; SSRF probe
(`http://127.0.0.1/`) → 400 `NOT_HTTPS`. Real data verified untouched
afterwards: 3 real task rows, real users intact, 0 temp-user leftovers.

**Resulting UX (stated in the app per connection):**
- Feed systems (Shahaf/Petel-ICS): "אוטומטי — השרת מעדכן כל בוקר ~06:15,
  גם כשטלפון/מחשב כבויים" + "רענן פיד" = instant server refresh from ANY device.
- Mashov/Ofek/Petel (no API, no password storage): the PC's scheduled local
  script pushes to the cloud; the phone simply shows the latest data when the
  app opens — zero action on the phone. "מתחברים פעם אחת למערכת — לא לכל
  מכשיר."
- Mashov specifically: in-browser phone sync is impossible (no CORS, verified)
  without storing the password server-side — which the iron rule forbids.

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

## Lumio 4.3 — Direct Mashov connect from the app (transient login, no password storage)

**What it is.** The Mashov card now has an in-app connect that works from the
PHONE or the PC: the student types their own Mashov username (ת.ז.), password
and school ONCE; the `mashov-connect` edge function performs a single login
against Mashov's own (undocumented) web API — the same API the Mashov web app
itself uses — pulls homework / grades / timetable, upserts the rows under the
student's Lumio account, and discards the password and session immediately.

**Iron-rule compliance (the hard part).**
- The password is NEVER written to the database, NEVER logged, NEVER stored in
  secrets. It exists only in request memory for the duration of the call.
  No stored credential ⇒ no server-side re-login is even possible.
- The next refresh asks for the password again (one tap, any device) — or the
  optional PC script does it hands-free in the background (old path, unchanged).
- Provenance is honest: rows are marked `retrieval_method='unofficial_api'`
  (new CHECK value, `database-upgrade-3.sql`) + `live_verified` (a real read
  happened) — never `official_api`, never fake-`connected`.

**How it works (verified against Mashov's own code, 2026-11-12).**
- `POST https://web.mashov.info/api/login` `{username, password, semel, year}`
  → session via `Set-Cookie` + `x-csrf-token` response header (verified from
  the live Angular bundle of `web.mashov.info/students/` — no Authorization
  header exists in the app; cookies + CSRF only — and from the community
  library `t0mer/pymashov`, Apache-2.0).
- School resolution: `GET /api/schools` is PUBLIC (live-verified: 200,
  ~345 KB list of `{semel, name, years}`) — the student's school name or
  semel is matched there; no credentials needed for this step.
- Student discovery: the login body is `{credential, accessToken}`; a student
  account carries its own `studentGuid` in `credential`, a parent account
  lists children via `GET /api/user/bindings` (both endpoints verified from
  the live app bundle).
- Data: `GET /api/students/{guid}/homework`, `.../grades` (fallback
  `.../gradingPeriods`), `.../timetable`.
- MFA accounts: detected (`mfaChallengeId` in the login body) and reported
  honestly as unsupported for the in-app path, with pointers to the PC script
  or manual import.

**Live verification (2026-11-12, temp account, full cleanup):**
- `unauthenticated → 401` (student JWT gate; this path has no cron mode — a
  transient login can never run unattended).
- `no credentials → 400 MISSING_CREDENTIALS`; `unknown school → 400
  SCHOOL_NOT_FOUND` (proves Supabase→Mashov egress + the public schools path);
  `fake credentials vs the public demo school (semel 100026) → 401
  LOGIN_FAILED` (proves the /api/login round trip + CSRF/cookie handling).
- CHECK constraint accepts `unofficial_api` (insert → readback → delete cycle
  under the temp user).
- Cleanup: temp user deleted, 0 rows left, 0 `lumio-tmp-*` users; the 3 real
  task rows and real users verified untouched afterwards.

**What is NOT verified (stated, not hidden).** A REAL student login end-to-end
(has not been run — it needs a real account; one attempt with dummy
credentials only). Response field shapes beyond the verified ones are handled
defensively (multiple candidate keys, per-endpoint try/catch, honest
`NO_DATA_PARSED` error if nothing recognized).

**Files:** `supabase-functions/mashov-connect/index.ts` (new),
`database-upgrade-3.sql` (applied live), `app.mjs` (mashov row + API call),
`connectors.mjs` (honest copy + `unofficial_api` provenance), tests
`connectors.test.mjs` (new 4.3 test block: 40/40).

## Lumio 4.4 — "Lumio MOE Sync" extension (the automatic-vacuum bridge) + ingest upgrade

**What it is.** This is the mechanism behind "connect through משרד החינוך and
Lumio vacuums the information automatically." Mashov, Ofek (Matan) and PeTeL all
log in through the MOE single sign-on (`lgn.edu.gov.il`); the student is already
logged into that session in their browser every day. `Lumio MOE Sync` is the
rebuilt browser extension (was "Lumio Ofek Bridge"): while the student simply
opens Mashov / Ofek / PeTeL as usual, the extension observes the JSON the page
itself receives from the school system's own API and pushes it to Lumio
**automatically** — no button, no per-refresh action, and **no password ever
touches Lumio** (the extension only rides the existing browser session).

**Why an in-browser bridge is the only honest way to do this.** The iron rule
forbids Lumio from storing the MOE/Mashov password, and `lgn.edu.gov.il`
exposes no self-service SSO/OAuth API a third-party app can log into
programmatically (MFA-gated, no public OAuth client). The MOE session exists
only inside the student's browser. So the code that can read that session must
run in the student's browser context — an extension (or the app's own JS, which
is blocked by CORS from another origin). There is no server-side,
hands-off path that does not store credentials. The one-time install + key
paste is the unavoidable cost of "automatic without a stored password"; after
that it is genuinely automatic.

**Files (all under `ofek-extension/`, rebuilt):**
- `manifest.json` — MV3 "Lumio MOE Sync" v2.0.0. host_permissions:
  `web.mashov.info`, `*.cet.ac.il`, `*.matan.co.il`, the Supabase project only.
  Two content scripts: `capture.js` (MAIN world, document_start) and
  `[map.js, content.js]` (isolated world, document_idle).
- `capture.js` — MAIN world. Wraps `fetch` + `XHR`; forwards only
  task/grade/timetable-shaped JSON (URL signal + shape heuristic), never
  credential fields. Hands each capture to the isolated world via a DOM
  `CustomEvent('__lumio_capture')` — **this fixes the v1 bug** where the
  isolated-world `content.js` tried to read `window.__lumioCaptured` (a
  MAIN-world global it cannot see), which is why v1 was never live-verifiable.
- `map.js` — PURE mapping (no browser globals at load → unit-testable in Node):
  `{url, data}` → Lumio ingest items `{kind, external_id, title, course_title,
  due_at, status, score, room, day_of_week, start_time, end_time, ...}`.
  Handles Mashov homework/grades/timetable + Ofek/PeTeL task shapes (multiple
  candidate keys, Hebrew weekday names, ISO/dd.mm.yyyy/epoch dates). Stable
  `external_id` per record ⇒ idempotent upserts.
- `content.js` — isolated world. Listens for captures, maps them, buffers per
  source, and auto-pushes on a 3s debounce + on `pagehide`. Reads only the
  per-system **sync key** (capability token, not a password) from
  `chrome.storage.local`. Small floating status chip (מחובר / מסנכרן / ✓ סונכרן).
- `options.html` / `options.js` — **one sync key per system** (mashov / ofek /
  petel), matching Lumio's per-connection key model; each provided key is
  validated live against the ingest before saving.
- `README-HE.md` — install, how-it-works, security.

**Ingest upgrade (`apps-script-ingest`, live + E2E-verified 2026-11-12):**
- Now accepts `kind='timetable'` (Mashov's personal timetable flows too), not
  just task/grade — written to `school_items` with `day_of_week`/`start_time`/
  `end_time`/`room`/`change_type`.
- **Authoritative source:** the pushed `source` field is now taken from the
  sync key's own connection row (`provider`), not from the (untrusted) request
  body — a key can no longer be used to write another source's rows.
- Deployed with `verify_jwt:false` (it self-authenticates via the
  key→user binding; the pushers use the public anon key, not a user JWT).

**Live E2E verification (2026-11-12, throwaway user + connection + key, full
cleanup — real rows untouched):**
- deploy → `201 OK`; anon-key probe → `401 LUMIO_BINDING_INVALID` (new code
  live, still reachable with the anon key the extension/scripts send).
- push `{key, source:'mashov', items:[1 task,1 grade,1 timetable]}` → `200
  {ok:true, saved:{tasks:1, grades:1, timetable:1}}`; read-back 1/1/1 rows for
  the temp user; timetable row `day=2, start=09:00, room=12` as sent.
- authoritative-source rule: same mashov key with body `source:'ofek'` → row
  stored as `source=mashov` (rows with `source=ofek`: 0, `source=mashov`: 1).
- cleanup: temp user + connection + rows deleted (`200`), 0 leftovers; the 3
  real task rows and real users verified intact.

**App copy (connectors.mjs + app.mjs):** Mashov / Ofek / PeTeL cards now lead
with the extension as the **automatic** path (one-time install + key paste),
with Mashov's no-extension transient login (4.3) kept as the alternative. The
top warning line reflects "install once → automatic." No new CSS classes, no
layout/palette change.

**What is NOT verified (stated, not hidden).** The extension has **not** been
run in a real Chrome against a live MOE-logged-in Mashov/Ofek/PeTeL session
(no student credentials available to the agent; MoE SSO is by design out of
agent scope). The mapper is unit-tested against the known Mashov API shapes
(11 tests) and the ingest is E2E-tested live, but the in-browser capture
hit-rate and any JSON-shape drift must be confirmed on first real use (the
README documents the fallback + adaptation path). The 4.3 real-Mashov-login
E2E is likewise still pending a real account.

**Files (4.4):** `ofek-extension/*` (manifest, capture.js, map.js, content.js,
options.html, options.js, README-HE.md), `supabase-functions/apps-script-ingest/
index.ts` (timetable + authoritative source), `connectors.mjs` + `app.mjs`
(copy), `tests/extension-map.test.mjs` (new, 11 tests).

## Lumio 4.4.1 — phone‑first Mashov connect (no extension, password‑only refresh)
The 4.4 extension is **PC‑only** (mobile Chrome/Edge has no "Load unpacked").
So phone‑only students get the automatic path from the **app itself**, via the
4.3 `mashov-connect` edge function — no extension, no dev mode. 4.4.1 makes it
a first‑class phone flow and closes the "re‑type everything" gap:

- **Device‑local remember of the non‑secret parts** (`app.mjs`): after a
  successful connect, the student's **username (ID number) + school** are stored
  in the phone's `localStorage` (keys `lumio_mashov_user` / `lumio_mashov_school`).
  The **password is never stored** (iron rule). A refresh ("רענן נתונים") on the
  same device now only re‑asks for the **password**. A "מחק מידע שמור במכשיר"
  button clears the stored identifiers. `localStorage` is per‑origin, per‑device,
  and nothing is sent anywhere but the student's own connect call — this is
  standard "remember username", not credential storage.
- **Device‑honest copy** (`connectors.mjs` + `app.mjs`): each card now states
  plainly what a phone‑only student can and can't do:
  - **Mashov** → in‑app connect, **phone, no extension** (ID+password+school once;
    then password‑only refresh). The extension is listed as the optional
    desktop full‑auto path (phone then reads from the cloud).
  - **PeTeL** → **deadlines automatic from the phone**: paste the personal
    ICS diary link once → server refreshes daily (even with phone/PC off).
    Homework = desktop extension or manual import.
  - **Ofek** → no public API; automatic = desktop extension (phone reads from
    cloud); **no PC?** manual import from the phone.
  - **Shahaf** → one‑click auto (server public feed) — already phone‑automatic.
- **No fake connected states**: a card only shows ✓ after a real data read
  succeeds (unchanged rule).

**Files (4.4.1):** `app.mjs` (localStorage pre‑fill + clear action + copy),
`connectors.mjs` (device‑honest copy).

## Evidence
- `npm test`: 51/51 pass (40 prior + 11 new `extension-map.test.mjs`: source
  detection, Mashov homework/grades/timetable mapping, Hebrew weekday
  normalization, Ofek tasks, dedupe, empty/junk robustness, due-date parsing).
- `node --check`: all extension JS (capture/map/content/options) + app.mjs +
  connectors.mjs clean; `ofek-extension/manifest.json` valid JSON.
- `deno check` (2.9): feed-sync + apps-script-ingest both clean (ingest now
  with timetable + authoritative-source logic).
- Ingest live E2E (temp user, full cleanup): deploy 201, push saved
  task/grade/timetable, timetable fields intact, authoritative-source rule
  proven, 3 real tasks + real users verified untouched, 0 temp leftovers.
- `python3 -m py_compile`: 3/3 local-sync scripts.
- 4.2 live CORS probes (2026-11-12): `katzirb.shahaf.site` → 200, no
  `Access-Control-Allow-Origin`; `web.mashov.info/api/login` preflight → 204,
  no CORS headers; `OPTIONS` with `Origin: https://origit892-stack.github.io`
  → no `Access-Control-Allow-*` at all.
- Live site `origit892-stack.github.io/lumio-site/` serves 4.4: `/connectors.mjs`
  + `/app.mjs` with the MOE Sync copy (verified after deploy).
- Live site serves **4.4.1** (verified after deploy, 2026-11-13): `/connectors.mjs`
  has the phone‑first Mashov copy ("גם מהטלפון בלי שום תוסף", "ללא מחשב");
  `/app.mjs` has the `lumio_mashov_user` localStorage pre‑fill (3 refs), the
  "מחק מידע שמור במכשיר" clear action, and the "רענן נתונים (סיסמה בלבד)"
  password‑only refresh. `npm test` 51/51; `node --check` clean.
- No secrets in any of these files (scan: no `sb_secret_`, no JWTs; only the
  publishable `sb_publishable_...` key, which is public by design).
