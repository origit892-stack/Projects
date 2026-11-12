# Lumio 4.0 Implementation Spec (engineer brief)
**USER DIRECTIVE (2026-11-11): "Build Lumio 4 with everything connected."** Interpretation (fixed, no fakes): every REAL data path is a first-class connection — (a) live API sync (Classroom), (b) user-authorized feed (PeTeL ICS URL the student generates for their own calendar; Shahaf public page if research verifies one), (c) fast one-tap import (Mashov/Ofek, no official API exists). UI must make the difference unmistakable. Version bump: **4.0** (README, footer "לומיו 4.0", SW cache `lumio-shell-v4.0`, package.json version 4.0.0).
**Working dir (ONLY place to write):** `~/Documents/Projects/lumio-mission/work/source/lumio-v3.3/`
**Baseline:** v3.3, 25 files, 19/19 tests passing. UI/design must be preserved (no palette/typography/layout changes; reuse existing CSS classes: `.conn`, `.cardline`, `.pill`, `.warning`, `.taskfilters`, `.tabbar`).
**No npm dependencies. No secrets. `config.mjs` values must not change.** All UI strings in Hebrew, RTL.

## Research status (FINAL — from verified reports, work/research/*.md, accessed 2026-11-11)
| provider | default connection state | apiRead | backgroundSync | note (evidence) |
|---|---|---|---|---|
| classroom | `awaiting_consent` when config.google set, else `manual_import_only` | true — scopes classroom.courses.readonly + classroom.coursework.me.readonly; grades reachable via StudentSubmission.assignedGrade | false with GSI flow (access token ONLY, no refresh token — official JS ref) | Cloud Console OAuth client registration MANDATORY (free; no legitimate workaround — third-party client = wrong app identity + ToS risk). Pub/Sub push exists but needs GCP billing + server + unreliable for non-WFE courses → NOT used. In-app polling fine (20 QPS/user/min). Testing mode: test users, ~7-day consent expiry. Existing GSI client in app.mjs stays; add re-auth handling. |
| mashov | `login_only` + `manual_import_only` | false — NO official API/partner program (multiple searches, negative result) | false | SSO button = IDM/EduLogin (Tz"uz + SMS OTP) — login only, NO delegated data auth. All community libs (pymashov et al.) = direct_credentials_only — Lumio NEVER handles credentials (user-local-import documented as theoretical fallback). Official push/SMS notifications = one-shot push, not a feed. |
| ofek | `login_only` + `manual_import_only` | false — no public API/export | false | **Ofek→Classroom teacher share = OFFICIAL feature** (Matach tutorial + official FAQ) → partial auto-unification through the existing Classroom connector; metadata on Classroom side = link + teacher-set title (due date/grade UNLIKELY — not verified). Student portal students.myofek.cet.ac.il (Tz"uz SSO). Partner ask: sherut@cet.ac.il. |
| petel | `manual_import_only` + feed (`ics_url`) | admin-gated (Moodle Web Services, off by default) | false (feed refresh on demand / future cron) | 6 subject Moodles (petel.stweizmann.org.il, Moodle 4.5 inferred). User-authorized ICS calendar URL = REAL feed path (Moodle core feature; admin can disable enablecalendarexport — verify in UI). No student grade export; no LTI/xAPI. Inquiry: petel@weizmann.ac.il. |
| shahaf | public feed (`public_page`) — `katzir.iscool.co.il` VERIFIED-LIVE | public page, no auth | false (cache TTL + hash change-detect) | Live public class-level weekly HTML table (6 days × 11 periods; subject/room/teacher/notes), no login. School's own AY-5786 PDF publishes the URL to students and confirms ט'5 exists. Exact class-code URL template = agent D running (sa-0-0b28d4d2); connector uses config-driven URL until confirmed. |

**Automation engines (agent A running, sa-0-111f0218):** Supabase free verified: 500k edge invocations/mo, 5GB egress, 500MB DB, 150s runtime, 100 secrets, auto-pause after ~1 week low DB activity (pause KILLS pg_cron; DB-touching traffic prevents it). 0₪ holds for 10 and 100 students; 1000 = egress breach at peak. Classroom refresh-token storage for background sync: policy = NO plaintext in Lumio DB; candidates being ranked: student-owned Apps Script (own container) vs Supabase Functions Secrets vs reauth-every-time.
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
export function validateFeedUrl(raw, kind) → {ok, url?, error?} // ics_url: must be http(s); public_page: http(s) + (if kind=shahaf) host allowlist from research (TBD); never accept non-http schemes
export function fetchFeed(url) → text // plain fetch, 20s timeout via AbortController, no credentials/cookies sent (mode:'cors'), size cap 2MB, non-200 → classifyHttpError
export function importFeedItems(text, source, kind) → {tasks:[...normalized], skipped:n, preview:[first 3 titles]} // kind=ics_url → reuse importers.parseICS(text, source) (import it, do not duplicate); never invent data
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
   - **Feed connection (NEW, Lumio 4):** for providers with capabilities.feeds (petel always: ICS calendar URL; shahaf only if research verified a public page — FROM-RESEARCH): a "חבר פיד אישי" row: URL input + "בדוק פיד" button → `fetchFeed` + `importFeedItems` → preview (count + 3 titles, Hebrew) → "הוסף לפיד" (stores feed_url + facts {permission:true, data:true, sync:false} + state 'synced' ONLY after a successful fetch; on CORS/network failure show exact Hebrew hint: "השרת חוסם שליפה ישירה מהדפדפן — אפשרות: הורדת קובץ ICS וייבוא"). "רענן פיד" button re-fetches + upserts (idempotent, updates changed rows, never duplicates). This is the real "everything connected" path for PeTeL.
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
- Feed functions: validateFeedUrl rejects javascript:/data:/non-http and empty; importFeedItems on a SYNTHETIC ICS (marked `// SYNTHETIC FIXTURE — not real school data`) → tasks normalized with source + external ids, count correct; importFeedItems on empty/garbage text → 0 items, no throw, no invented data.

## File 5 (MODIFY): `public/sw.js`
Add `/connectors.mjs` to ASSETS; bump CACHE to `lumio-shell-v4.0`. (Network-first stays; SW caches shell only — no API/student data in cache: state this in a comment.)

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
- If research states (table above) say `FROM-RESEARCH`, WAIT — Chief will fill them before dispatch.
