# Lumio 4.0 Implementation Spec (engineer brief)
**USER DIRECTIVE (2026-11-11): "Build Lumio 4 with everything connected."** Interpretation (fixed, no fakes): every REAL data path is a first-class connection — (a) live API sync (Classroom), (b) user-authorized feed (PeTeL ICS URL the student generates for their own calendar; Shahaf public page if research verifies one), (c) fast one-tap import (Mashov/Ofek, no official API exists). UI must make the difference unmistakable. Version bump: **4.0** (README, footer "לומיו 4.0", SW cache `lumio-shell-v4.0`, package.json version 4.0.0).
**Working dir (ONLY place to write):** `~/Documents/Projects/lumio-mission/work/source/lumio-v3.3/`
**Baseline:** v3.3, 25 files, 19/19 tests passing. UI/design must be preserved (no palette/typography/layout changes; reuse existing CSS classes: `.conn`, `.cardline`, `.pill`, `.warning`, `.taskfilters`, `.tabbar`).
**No npm dependencies. No secrets. `config.mjs` values must not change.** All UI strings in Hebrew, RTL.

## Research status (FINAL — all 10 reports on disk, work/research/*.md, accessed 2026-11-11/12)
| provider | default connection state | apiRead | backgroundSync | note (evidence) |
|---|---|---|---|---|
| classroom | `awaiting_consent` when config.google set, else `manual_import_only` | true — scopes classroom.courses.readonly + classroom.coursework.me.readonly; grades reachable via StudentSubmission.assignedGrade | **true via student-owned Apps Script** (native Classroom advanced service + daily time-driven trigger on Google infra — no GCP, no refresh token, PC-off-safe, 0₪; quotas: 20 triggers, 90 min/day, 20k URLFetch/day VERIFIED) | Cloud Console OAuth client registration MANDATORY for the in-app GSI flow (free; no legitimate workaround). Apps Script path: student deploys Lumio's template once (apps-script/ folder), then daily auto sync. In-app polling fine (20 QPS/user/min). Testing mode: ~7-day consent expiry. Pub/Sub push = GCP billing + server → NOT used. |
| mashov | `manual_import_only` (+ documented `user_local_import` option) | false — NO official API (negative result after exhaustive sweep: 89 GitHub repos, npm/PyPI) | false | SSO button = IDM/EduLogin — login only, no delegated data auth. T1: no tool reads Mashov without the student's password (VERIFIED absence). T4: student running pymashov ON THEIR OWN MACHINE then importing the JSON/CSV into Lumio = legitimate user_local_import (Lumio never sees/stores credentials; presented neutrally, not endorsed; may break without notice). |
| ofek | `manual_import_only` (+ Classroom-bridge note) | false — no public API/export | false | **Ofek→Classroom teacher share = OFFICIAL one-click feature** ("פעילויות ששייכת לכיתה או לקבוצה ניתן לשתף בקליק אחד" — official FAQ VERIFIED; tutorial video exists). What lands in Classroom (due date? grade?) NOT VERIFIED → pilot with 1-2 teachers + email to webs@cet.ac.il. Card shows one-liner: teacher can share Ofek tasks to the class Classroom → they appear in Lumio automatically. |
| petel | `manual_import_only` + feed (`ics_url`) | admin-gated (Moodle WS, off by default) | false (feed refresh on demand / future cron) | 6 subject Moodles (Moodle 4.5). ICS calendar URL = REAL user-authorized feed (admin-disableable). No student grade export; no LTI/xAPI. Inquiry: petel@weizmann.ac.il. |
| shahaf | `public_page` connector (GENERIC for `*.shahaf.site`) — current Katzir B class: **no published site (katzir-b.shahaf.site = 404, VERIFIED)** | public page, no auth | false (stamp-driven cache, 15-30 min) | **Platform migrated to `*.shahaf.site`** (katzir.iscool.co.il redirects). VERIFIED URL template: `https://<school>.shahaf.site/?cls=<N>&tab=timetable&mode=student[&week=±N]` — server-rendered HTML table (6 day columns, periods with times in row labels, "מעודכן ל:" stamp), no JSON. Published today: katzir.shahaf.site (grades 10-12 only — upper track), katzir-a.shahaf.site (A-track, ז1), dror.shahaf.site (full school incl ט-5 — parser proof). Katzir B-track (grades 7-9, the user's ט'5) = NOT published (404) → honest state + import + ask text for the school (contacts: 08-9471653, katzirb@educ.org.il). Parser = tolerant HTML table parse (proven feasible); stamp change-detect for freshness. |

**Automation engines (FINAL, agent A report automation-engines.md):** Background sync design LOCKED: (1) Classroom = student-owned Apps Script with NATIVE Classroom advanced service + daily trigger → Edge Function `apps-script-ingest` (0₪, PC-off-safe, no tokens stored — quotas VERIFIED). (2) ICS feeds (PeTeL) = Supabase pg_cron → Edge Function `feed-sync` (0₪; 500k invocations/mo free, 150 s runtime; DB writes double as the anti-pause heartbeat). Supabase free verified: 5GB egress, 500MB DB, 100 secrets; auto-pause after ~1 week low activity (pause KILLS pg_cron — the feed-sync writes prevent it). 0₪ holds for 10-100 students; ~1000 breaches egress.
**MoE (from moe-cost.md):** official SP/IDM connection path EXISTS (sapakim.education.gov.il/tech/idm — SAML/OIDC/federation, vendor-approval-gated, forms + GR_IDM_Team@education.gov.il; designed for MoE-approved vendors, not self-service individuals). "ED-DATA" = no such official system found. MoE LRS = real xAPI store but vendor→MoE usage-telemetry push; NO read access for new apps. Hebrew inquiry letter drafted in report (A5).

---

## File 1 (NEW): `connectors.mjs` — pure, node-testable, no DOM
```
export const CONNECTION_STATES = ['not_connected','login_only','awaiting_consent','requires_admin','connected_unverified','syncing','synced','needs_reauth','manual_import_only','unavailable','error'];
export const ERROR_TYPES = ['PERMISSION_DENIED','AUTH_EXPIRED','ADMIN_APPROVAL_REQUIRED','API_NOT_AVAILABLE','RATE_LIMITED','SOURCE_NOT_FOUND','SOURCE_CHANGED','NETWORK_ERROR','DATA_VALIDATION_FAILED'];
export const RETRIEVAL_METHODS = ['official_api','public_school_feed','user_import','user_entry'];
export const VERIFICATION_STATES = ['live_verified','sandbox_verified','fixture_only','user_imported_unverified'];
export const PROVIDERS = [ {id, name, icon, sourceLink, capabilities:{login,apiRead,backgroundSync,assignments,exams,grades,announcements,timetable,deepLinks}, defaultState, heDescription, howToConnect (Hebrew 1-2 lines, honest), dataPaths:[{label, method}]}, ... 5 providers ... ];
export function connectionFacts(state /* ConnectionState */, hasToken, lastSyncAt, lastError) → {identityAuthenticated, permissionGranted, dataReadable, syncWorking} // 4 independent booleans; e.g. 'synced' → all true; 'connected_unverified' → identity+permission true, data/sync false; 'needs_reauth' → identity false; manual_import_only → permission false, data readable only after import...
export function heStatus(state, lastSyncAt) → Hebrew string per mission doc §15 mapping (use exactly these labels: "לא מחובר", "נפתח אתר המקור (אין סנכרון)", "ממתין לאישור הרשאות", "מחובר, טרם אומתה קריאת נתונים", "סנכרון הצליח — [זמן]", "נדרש אישור מנהל מערכת", "נדרש להתחבר מחדש", "חיבור אוטומטי אינו זמין; ניתן לייבא נתונים", plus error/unavailable variants)
export function classifyHttpError(status, isTimeout) → ERROR_TYPES // 401→AUTH_EXPIRED, 403→PERMISSION_DENIED, 429→RATE_LIMITED, 404→SOURCE_NOT_FOUND, 5xx→NETWORK_ERROR (server), timeout→NETWORK_ERROR, default→DATA_VALIDATION_FAILED
export function dedupeKey(user_id, source, external_id, kind) → string
export function fallbackFingerprint({title, subject, due_at, source}) → canonical string (reuse canonicalText logic from study.mjs — import it, do not duplicate)
export function provenanceFor(task, method) → {provider, capability, retrieval_method, verification_state}
export function normalizeShahafRow(raw) → validated timetable row or throw (day 0-6, HH:MM times, change_type enum) // used by parser + import
export function parseShahafTimetableTable(rows /* array of arrays from a public table */) → {items:[...], skipped:[{row,reason}]} // pure; SYNTHETIC fixtures in tests only
export function upsertTimetable(existing, incoming) → merged (change updates existing row by (source, external_id) instead of duplicating; cancelled/changed change_type preserved) // idempotent
export const FEED_TYPES = ['ics_url','public_page'];
export function validateFeedUrl(raw, kind) → {ok, url?, error?} // ics_url: must be http(s); public_page: must be http(s) AND host match /^([a-z0-9-]+\.?shahaf\.site)$/i (verified public platform, 2026-11-12); never accept non-http schemes, never accept credentials-in-URL
export function fetchFeed(url) → text // plain fetch, 20s timeout via AbortController, no credentials/cookies sent (mode:'cors'), size cap 2MB, non-200 → classifyHttpError
export function importFeedItems(text, source, kind) → {items:[...normalized], skipped:n, preview:[first 3], stamp?} // kind=ics_url → reuse importers.parseICS(text, source) (import it, do not duplicate); kind=public_page → parseShahafPage(text) (below); never invent data
export function parseShahafPage(htmlText) → {rows:[...], stamp?, error?} // VERIFIED platform shape (katzir/dror/katzir-a .shahaf.site, fetched 2026-11-12): server-rendered HTML <table>, 6 day columns (day headers first row), period rows with time labels in row labels; extract "מעודכן ל: <DD.MM.YYYY, שעה: HH:MM>" stamp when present → freshness + change-detect (store stamp in connections row; stamp change → refresh; row change → update, never duplicate). Tolerant: different period counts across schools (11-14 rows). Parse the HTML STRING (no live DOM dependency); tests use SYNTHETIC fixtures only. Feeds into parseShahafTimetableTable for validation.
export function buildShahafUrl(schoolSubdomain, cls, tab='timetable', week=0) → string // VERIFIED template: https://<school>.shahaf.site/?cls=<N>&tab=<tab>&mode=student[&week=<±N>]
```
**Feed persistence & privacy:** feed URL stored per user in `connections.feed_url` (new column, see upgrade-2) — RLS protects it, but the UI MUST show: "כתובת הפיד מכילה מזהה אישי שלך. היא נשמרת רק בחשבון שלך ונמחקת ב-נתק." Disconnect action deletes feed_url + can cascade-delete its data (two separate confirmations: disconnect vs delete-data, per spec §privacy). No service-worker caching of feed content (SW caches shell only).
Hebrew day names, subject handling, all validation errors in Hebrew.

## File 2 (MODIFY): `app.mjs` — surgical additions only
1. Import connectors module.
2. `state.connections` rows may be missing boolean fact columns until upgrade-2 runs — guard with `c.identity_authenticated ?? (c.state==='api_connected')` etc. (graceful degradation, never break old rows).
3. **Connections page rebuild (same layout/look):** each provider card shows:
   - status line = `heStatus(state, last_sync_at)` (replace `connectionLabel` body; keep function name for dashboard reuse)
   - 4 fact rows (small muted line): זהות: ✓/✗ · הרשאה: ✓/✗ · קריאת נתונים: ✓/✗ · סנכרון: ✓/✗ (from connectionFacts; label "עובדות חיבור")
   - capabilities as muted scope list (e.g. "מטלות, מועדים, הגשות שלי" — from PROVIDERS entry, honest)
   - buttons per capability: **always** "פתיחת האתר ↗"; **classroom only**: "חבר Google" (existing) when config.google set, else disabled hint "נדרש OAuth Client של מנהל לומיו"; "סנכרן עכשיו" when token exists; **all**: "נתק" (sets state not_connected + all facts false, upserts connections) and "מחק נתונים ממערכת זו" (DELETE FROM tasks/school_items where source=X AND user_id=me — two-step confirm with exact counts, then re-load).
   - Under each card: `howToConnect` one-liner (honest, e.g. mashov: "אין חיבור אוטומטי רשמי כרגע — פתח את האתר, והעתק/ייבא משימות".)
   - **Feed connection (NEW, Lumio 4):** providers with feed capability: **petel** — "חבר פיד ICS" row (personal calendar URL the student generates in PeTeL/Moodle; show the 3 Hebrew steps: יומן → שיתוף/קישור ICS → הדבק כאן); **shahaf** — "חבר מערכת שעות בית-ספר" row: URL input (placeholder `https://<school>.shahaf.site/?cls=<N>&tab=timetable&mode=student`) validated by validateFeedUrl (shahaf hosts only) + "בדוק פיד" → fetchFeed + importFeedItems(kind='public_page') → preview (count + 3 cells + stamp, Hebrew) → "הוסף" (store feed_url + facts {permission:true, data:true, sync:true ONLY after a successful fetch} + state 'synced' ONLY after success). **Honest default for the current school (Katzir B):** the shahaf card shows "בית הספר לא מפרסם כרגע את מערכת השעות של חטיבת הביניים (katzir-b.shahaf.site אינו פועל — בדיקה 12.11.2026)" + import option + a copyable one-line request for the school admin (contacts: 08-9471653 / katzirb@educ.org.il); the connector becomes live the moment the school publishes (parser proven on published pages — no re-code needed). "רענן פיד" re-fetches + upserts (idempotent, stamp change-detect, never duplicates). On CORS/network failure show the exact Hebrew hint: "השרת חוסם שליפה ישירה מהדפדפן — אפשרות: הורדת קובץ ICS וייבוא".
4. **Tasks page:** for each task card add a tiny muted line when data exists: `נשמר ב: {retrieval_method label} · {synced_at? 'סונכרן לפני X' : 'הזנה/ייבוא ידני'}`. Labels: official_api→"דרך API מורשה", public_school_feed→"מהמקור הציבורי של בית הספר", user_import→"ייבוא ידני שלך", user_entry→"הזנה ידנית".
5. **Profile/privacy section:** add "הגדרות פרטיות" panel: per-provider "הרשאות פעילות" (the 4 facts + last sync), "ביטול" (נתק) and "מחיקת נתונים מהמקור" buttons (same handlers as connections), and "ייצוא כל הנתונים שלי" (existing export, extended to school_items).
6. Keep ALL existing behavior: auth, tasks CRUD, imports (file/paste/reader), school items, dashboard cards, mobile bar. Footer → "לומיו 4.0 · …".
7. `trackConnection(provider, stateName, facts)` — extend upsert to include the 4 boolean columns (null-safe: only include if upgrade-2 applied? No: include them; if column missing the upsert errors → catch and retry without them, set state `schoolDataReady`-style flag `privacyColsReady`. Simpler: try upsert with facts; on error retry without facts; notice user once "להשלמת תצוגת ההרשאות יש להריץ database-upgrade-2.sql").

## File 3 (NEW): `database-upgrade-2.sql` — ADDITIVE ONLY, NOT executed by agent
Header comment: run in Supabase SQL editor AFTER database.sql + database-upgrade.sql; backup first; safe to re-run; rollback documented at bottom.
```
alter table public.tasks add column if not exists retrieval_method text not null default 'user_entry' check (retrieval_method in ('official_api','public_school_feed','user_import','user_entry'));
alter table public.tasks add column if not exists verification_state text not null default 'user_imported_unverified' check (verification_state in ('live_verified','sandbox_verified','fixture_only','user_imported_unverified'));
alter table public.tasks add column if not exists synced_at timestamptz;
alter table public.tasks add column if not exists created_at timestamptz not null default now();
alter table public.school_items add column if not exists retrieval_method text not null default 'user_entry' check (same);
alter table public.school_items add column if not exists verification_state text not null default 'user_imported_unverified' check (same);
alter table public.school_items add column if not exists synced_at timestamptz;
alter table public.school_items add column if not exists created_at timestamptz not null default now();
alter table public.connections add column if not exists identity_authenticated boolean not null default false;
alter table public.connections add column if not exists permission_granted boolean not null default false;
alter table public.connections add column if not exists data_readable boolean not null default false;
alter table public.connections add column if not exists sync_working boolean not null default false;
alter table public.connections add column if not exists feed_url text;
-- No new tables; RLS unchanged (table-level owner policies already cover new columns).
-- rollback (manual, only if needed):
-- alter table public.tasks drop column if exists retrieval_method; (… each …)
```

## File 4 (NEW): `tests/connectors.test.mjs` (node --test)
- connectionFacts for every state (table-driven, 11 states).
- heStatus returns the exact §15 labels.
- classifyHttpError: 401/403/404/429/500/timeout.
- dedupeKey + fallbackFingerprint: duplicate_same_source (same external_id twice → 1), similar_across_sources (different source → separate, merged in view by existing uniqueTasks), same_title_different_course (different subject → NOT merged by fingerprint).
- provenanceFor: method propagation; fixture data flagged fixture_only.
- parseShahafTimetableTable on a SYNTHETIC fixture (comment: `// SYNTHETIC FIXTURE — not real school data`): valid rows parse; bad day/time/change_type rejected with Hebrew error; skipped rows reported.
- upsertTimetable idempotency: same (source,external_id) twice → 1 row; changed row updates (no duplicate); cancelled change preserved.
- Date edges: due date around Israeli DST (2026-10-25/26) keeps the same local date; item without due/subject/URL survives normalizeTask (existing) + provenance defaults.
- Empty list / null fields: upsertTimetable([]), parseShahafTimetableTable([]) → empty items, no throw.
- Feed functions: validateFeedUrl rejects javascript:/data:/non-http and empty; for public_page also rejects non-shahaf hosts; importFeedItems on a SYNTHETIC ICS (marked `// SYNTHETIC FIXTURE — not real school data`) → tasks normalized with source + external ids, count correct; importFeedItems on empty/garbage text → 0 items, no throw, no invented data.
- parseShahafPage on a SYNTHETIC shahaf-style HTML fixture (12-period table + "מעודכן ל:" stamp, marked synthetic): rows parsed (day/time/subject/room), stamp extracted, second parse with an edited cell → change detected (update not duplicate); fixture without stamp → stamp null, no throw; buildShahafUrl renders the verified template.
- Static checks (file existence + content asserts only, no execution): apps-script/classroom-sync.gs contains the 3 native Classroom service calls + exactly 2 user-fill placeholder constants (no real secrets) + trigger setup; apps-script/README-HE.md exists; supabase-functions/feed-sync/index.ts and apps-script-ingest/index.ts exist and contain no secret values (env/secret reads only); supabase-functions/README-HE.md contains the pg_cron snippet and the anti-pause note.

## File 5 (MODIFY): `public/sw.js`
Add `/connectors.mjs` to ASSETS; bump CACHE to `lumio-shell-v4.0`. (Network-first stays; SW caches shell only — no API/student data in cache: state this in a comment.)

## File 5b (NEW): `apps-script/classroom-sync.gs` + `apps-script/README-HE.md` — student-owned background Classroom sync (0₪, works with PC OFF — VERIFIED quota: 20 triggers, 90 min/day, 20k URLFetch/day, 6 min/run)
`classroom-sync.gs` (STANDALONE Apps Script, pasted by the student into their own script.google.com project — runs on Google infra under the STUDENT'S own Google account, so NO OAuth client, NO GCP, NO refresh token ever):
- Exactly 2 user-fill placeholder constants at top (placeholders only, no real values): `const LUMIO_FN_URL = 'https://YOUR-PROJECT.functions.supabase.co/apps-script-ingest';` and `const LUMIO_SYNC_KEY = 'PASTE-YOUR-LUMIO-SYNC-KEY';`
- `sync()` using the NATIVE Classroom advanced service: `Classroom.Courses.list({maxResults:100})` → per course `Classroom.Courses.courseWork.list(courseId,{maxResults:100})` (keep ASSIGNMENT/VOCABULARY/COURSE_MATERIAL) → for assignments `Classroom.Courses.courseWork.studentSubmissions(workId)` for own status + `assignedGrade`; map to compact JSON items[{kind:'task'|'grade', external_id, title, course_title, due_at (date-only → end-of-day Israel time, never shift the day), status, grade?, source:'classroom'}]
- POST `{key: LUMIO_SYNC_KEY, items}` to LUMIO_FN_URL (10 s timeout, retry once on 5xx; on 401/404 → log 'LUMIO_BINDING_INVALID').
- `setup()` creates ONE daily time-driven trigger (06:00 Israel, `ScriptApp.newTrigger('sync').timeBased().everyDays(1).atHour(6)`) after removing old ones (idempotent).
- Hebrew comments throughout.
`README-HE.md`: 5-step student setup (script.google.com → פרויקט חדש → הדבק את קובץ classroom-sync.gs → הדבק את כתובת ה-FN ואת מפתח הסנכרון מהאתר → הרץ `setup()` פעם אחת עם אישור → סיום); what the script reads (own courses/works/submissions only), what it writes (their own Lumio account only), quota facts, how to undo (delete the project in Google; or "בטל סנכרון יומי" in Lumio).
**Binding security model (fixed):** Lumio generates a random 32-hex sync key per user, stored in `connections.apps_script_key` (added in upgrade-2: `alter table public.connections add column if not exists apps_script_key text;` + `create unique index if not exists connections_apps_script_key_unique on public.connections(apps_script_key);`). The key is a device-style token: shown once in the privacy panel with a warning ("מי שמחזיק את המפתח יכול להוסיף נתונים לחשבון — שמרו אותו; אפשר לסובב/לבטל כאן"), a "סובב מפתח" button (new random key; old invalid immediately), "בטל סנכרון יומי" (nulls the key). NO JWT in the script, NO refresh tokens stored anywhere, NO service_role in the script.

## File 5c (NEW): `supabase-functions/apps-script-ingest/index.ts`, `supabase-functions/feed-sync/index.ts`, `supabase-functions/README-HE.md`
Two Supabase Edge Functions (Deno, server-side; the user deploys to their own Supabase project; NO secrets in the repo — README instructs setting secrets in the dashboard):
- `apps-script-ingest`: body {key, items[]}; service-role lookup of the `connections` row by apps_script_key (unique) → if missing or state='not_connected' → 401; upsert tasks for THAT row's user_id only (source='classroom', retrieval_method='official_api', verification_state='live_verified', synced_at=now(), dedup on (user_id, source, external_id, kind); grade items → school_items kind='grade'); cap 500 items (truncate + `partial:true` in response); update connections facts (data_readable=true, sync_working=true, last_sync_at=now()); NEVER trust a client-supplied user_id.
- `feed-sync`: cron-driven; reads all `connections` with feed_url (service role), fetches each (20 s, 2 MB cap), normalizes (ICS: minimal VEVENT parse; public_page: minimal tolerant shahaf table parse — mirrored in Deno), upserts that user's items with the same dedup keys, updates facts + feed stamp; chunked to stay <150 s at 100 users; writes to the DB on every run = documented anti-pause heartbeat for the Supabase project.
- `README-HE.md`: exact deploy steps (Supabase dashboard → Edge Functions → New function → paste → `supabase secrets set SUPABASE_SERVICE_ROLE_KEY=...` from the project's settings — user's own secret, never in repo); pg_cron SQL: `create extension if not exists pg_cron;` + `select cron.schedule('lumio-feed-sync','15 6 * * *', $$select net.http_post(url:='https://<ref>.functions.supabase.co/feed-sync', headers:=jsonb_build_object('Authorization','Bearer <SERVICE_ROLE>'))$$);` (or the dashboard scheduler UI); honest fallback note: if pg_cron is not available on the plan, "רענן" buttons on the site are the fallback (labeled as such); anti-pause note (DB writes keep the project awake; if it auto-pauses, the site shows "הסנכרון המזומן ממתין — רענון ידני זמין").

## File 6 (MODIFY): docs
- README.md: add a 4.0 section (Hebrew): new connection facts, disconnect + delete-data buttons, feed connections (PeTeL ICS / Shahaf if verified), upgrade-2 step (after school_items upgrade), what is still NOT connected (honest list per research).
- INTEGRATIONS.md: add 4.0 matrix row (per-provider state + source of each claim — Chief fills the research refs before merge; engineer leaves a `<!-- RESEARCH-REFS -->` marker).
- QA.md: add 3.4 test summary (counts filled after run).
- DEPLOY.md: note upgrade-2 + that Cloudflare static upload is unchanged (all files static).

## Verification before done (engineer must run + report real output)
1. `npm test` — ALL pass (old 19 + new). Paste the summary tail.
2. `node --check` on every .mjs (app, connectors, core, study, importers, server).
3. Start `PORT=5199 node server.mjs`; `curl -s http://localhost:5199/ | head -c 200` (HTTP 200 check), then kill.
4. `git -C ~/Documents/Projects status --short lumio-mission/work/source | head` → list changed files (do NOT commit — Chief commits).

## Hard rules
- No changes outside the working dir. Never touch `config.mjs` values. Never add secrets. No mock/fixture data shown as real anywhere in UI (every imported/fixture row carries verification_state and the UI labels it as user/import data).
- "connected" UI text must only appear for state `synced`/`connected_unverified` per the heStatus mapping. Opening the provider's website never changes connection state.
- All research states in the table above are FINAL (10 reports on disk). Implement them exactly; anything you cannot implement honestly gets the documented state, never a fake.
