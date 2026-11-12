# 05 — Connector Contracts (Lumio 4.0)

Implemented in `connectors.mjs` (pure, DOM-free, node-testable). This is the shipped contract, not a proposal.

## State machine
```ts
type ConnectionState =
  | 'not_connected' | 'login_only' | 'awaiting_consent'
  | 'requires_admin' | 'connected_unverified' | 'syncing'
  | 'synced' | 'needs_reauth' | 'manual_import_only'
  | 'unavailable' | 'error';
```
Legacy v3.3 states (`api_connected`, `imported`) are mapped honestly by `heStatus()` (never crash, never overstate).

## Error taxonomy (9 explicit codes)
`PERMISSION_DENIED` (403) · `AUTH_EXPIRED` (401) · `ADMIN_APPROVAL_REQUIRED` · `API_NOT_AVAILABLE` · `RATE_LIMITED` (429) · `SOURCE_NOT_FOUND` (404) · `SOURCE_CHANGED` · `NETWORK_ERROR` (5xx/timeout) · `DATA_VALIDATION_FAILED` (default/400) — via `classifyHttpError(status, isTimeout)`.

## 4-fact model
`connectionFacts(state, hasToken, lastSyncAt) → {identityAuthenticated, permissionGranted, dataReadable, syncWorking}` — table-driven unit-tested for all 11 states. Example: `connected_unverified` → identity+permission true, data/sync false; `synced` → all true; `needs_reauth` → all false.

## Hebrew status labels (exact, from mission doc §15 — unit-locked)
| state | label |
|---|---|
| not_connected | לא מחובר |
| login_only | נפתח אתר המקור (אין סנכרון) |
| awaiting_consent | ממתיין לאישור הרשאות |
| requires_admin | נדרש אישור מנהל מערכת |
| connected_unverified | מחובר, טרם אומתה קריאת נתונים |
| syncing | מבצע סנכרון… |
| synced | סנכרון הצליח — [תאריך/שעה] |
| needs_reauth | נדרש להתחבר מחדש |
| manual_import_only | חיבור אוטומטי אינו זמין; ניתן לייבא נתונים |
| unavailable | לא זמין כרגע |
| error | שגיאה בחיבור |

## Feed contract
```ts
FEED_TYPES = ['ics_url','public_page'];
validateFeedUrl(raw, kind) → {ok, url?, error?}
  // ics_url:  http(s) only, no credentials-in-URL
  // public_page:  http(s) + hostname must match [a-z0-9-]+\.shahaf\.site (verified platform)
fetchFeed(url) → text        // 20s AbortController timeout, mode:'cors', credentials:'omit', 2MB cap
parseShahafPage(html) → {rows, stamp?, error?}   // tolerant server-rendered table parse + "מעודכן ל:" stamp
parseShahafTimetableTable(rows) → {items, skipped:[{row,reason}]}  // Hebrew validation errors
normalizeShahafRow(raw) → row  // day 0-6, HH:MM, change_type enum, room optional
buildShahafUrl(school, cls, tab='timetable', week=0) → string  // verified template
upsertTimetable(existing, incoming) → merged  // idempotent by (source, external_id); change=update
importFeedItems(text, source, kind) → {items, skipped, preview, stamp?}  // ICS via shared importer; public_page via parseShahafPage
```

## Provenance (every item carries)
```ts
provenanceFor(task, method) → {provider, capability, retrieval_method, verification_state}
retrieval_method ∈ ['official_api','public_school_feed','user_import','user_entry']
verification_state ∈ ['live_verified','sandbox_verified','fixture_only','user_imported_unverified']
```
Dedup: `dedupeKey(user_id, source, external_id, kind)`; fallback `fallbackFingerprint({title, subject, due_at, source})` (canonical text — whitespace/punctuation-insensitive, source- and course-sensitive).

## UI policy (enforced)
- "פתיחת האתר ↗" is always available; opening it NEVER changes connection state.
- "נתק" and "מחק נתונים ממערכת" are separate buttons, separate confirmations, exact counts shown.
- Feed URL input shows: "כתובת הפיד מכילה מזהה אישי שלך. היא נשמרת רק בחשבון שלך ונמחקת ב-נתק."
- Task cards show the muted provenance line: "נשמר ב: דרך API מורשה / מהמקור הציבורי של בית הספר / ייבוא ידני שלך / הזנה ידנית · סונכרן לפני X".
- No provider logo is displayed as "evidence" of an API.
