# 04 — Architecture (Lumio 4.0)

```
                         ┌─────────────────────────────────────────────────────┐
                         │  CLOUDFLARE PAGES (free, static, Direct Upload)     │
                         │  Lumio 4.0 — index.html, app.mjs, connectors.mjs,  │
                         │  core.mjs, study.mjs, importers.mjs, sw.js, PWA    │
                         │  (no server.mjs in production — dev only)          │
                         └──────────────┬──────────────────────────────────────┘
                                        │ Supabase JS (anon public key + user JWT)
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  SUPABASE FREE TIER (user's own project)                                     │
│  • Postgres: profiles, tasks, school_items, connections  (RLS: owner only)   │
│  • Auth: Lumio accounts (email+password) — separate from any MoE identity    │
│  • Edge Functions (user-deployed, service role server-side):                 │
│      apps-script-ingest  ← key→user lookup, JWT-free, upsert for that user   │
│      feed-sync           ← cron-driven: polls every connections.feed_url     │
│  • pg_cron: 1×/day → feed-sync (DB writes = anti-pause heartbeat)            │
└──────▲───────────────────────────────────────────────────────────────────────┘
       │ POST {key, items[]} (10s timeout, retry-once)
┌──────┴──────────────────────────────┐      ┌────────────────────────────────┐
│ GOOGLE INFRA (always on, $0)        │      │ EXTERNAL FEEDS                 │
│ per-student Apps Script template:   │      │ • PeTeL ICS (personal URL)     │
│ native Classroom advanced service   │      │ • Shahaf public page           │
│ (student's own account, own data)   │      │   (*.shahaf.site, no auth)     │
│ daily 06:00 trigger → courses,      │      │   (parsed HTML table + stamp)  │
│ coursework, own submissions/grades  │      └────────────────────────────────┘
└─────────────────────────────────────┘
```

## Data paths (each with provenance)
| path | retrieval_method | verification_state | who triggers | PC-off-safe |
|---|---|---|---|---|
| Classroom via Apps Script | `official_api` | `live_verified` (once first run lands) | daily 06:00 Google trigger | YES |
| Classroom in-app GSI | `official_api` | `live_verified` | "סנכרן עכשיו" button | NO (on demand) |
| PeTeL ICS feed | `public_school_feed` (personal-authorized feed) | `live_verified` after first fetch | "רענן" button or pg_cron daily | YES (cron) / NO (button) |
| Shahaf public timetable | `public_school_feed` | `live_verified` after first fetch | "רענן" button or pg_cron daily | YES (cron) / NO (button) |
| Mashov/Ofek import | `user_import` | `user_imported_unverified` | student, per item/file | n/a |
| Manual entry | `user_entry` | `user_imported_unverified` | student | n/a |

## Design invariants
1. **Static-first**: the whole site is static files; `server.mjs` is a local dev server and is NOT deployed.
2. **RLS is the only data boundary**: the anon key is public by design; every table is owner-scoped (`auth.uid() = user_id`), unchanged by `database-upgrade-2.sql` (additive columns only, `if not exists`, re-runnable, rollback documented).
3. **No secrets in the repo/site**: the two Edge Functions read `SUPABASE_SERVICE_ROLE_KEY` from Supabase secrets (set in the user's dashboard); the Apps Script has exactly 2 user-filled placeholders (function URL + binding key).
4. **Honest states**: `ConnectionState` has 11 states; the UI renders `heStatus()` labels — "מחובר/synced" is only reachable after a real read. Opening a provider's website never changes state.
5. **Dedup**: primary key `(user_id, source, external_id, kind)`; fallback fingerprint `canonicalText(title+course+dueDate+source)`; timetable rows keyed by `shahaf:<day>:<start>` — modified rows update, never duplicate (idempotent upserts, unit-tested).
6. **Freshness**: Shahaf pages carry a "מעודכן ל:" stamp → stored, compared, change-detected. Feeds have `last_synced_at`; the UI shows "סונכרן לפני X".
7. **Two-step data control**: "נתק" (stops sync, clears binding/feed) and "מחק נתונים ממערכת" (deletes that user's rows from that source) are separate actions with separate confirmations.
8. **PWA**: shell-only service worker cache (`lumio-shell-v4.0`), network-first, no student data cached; offline state is transparent.

## Deployment checklist (user actions, 0₪)
1. Run `database.sql` → `database-upgrade.sql` → `database-upgrade-2.sql` in Supabase SQL editor (after backup; all additive, re-runnable). **Required before the new UI columns appear** (the app degrades gracefully until then — with a one-time notice).
2. Deploy the two Edge Functions (supabase-functions/README-HE.md) + set `SUPABASE_SERVICE_ROLE_KEY` secret.
3. (Optional, for ICS/public-page auto-refresh) enable `pg_cron` via the README snippet.
4. Upload the site to Cloudflare Pages (Direct Upload) — all files static.
5. (Per student, optional) Apps Script Classroom auto-sync per apps-script/README-HE.md.
