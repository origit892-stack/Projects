# 10 — Implementation Log (Lumio 4.0)

> **תיקון (12.11.2026, בעקבות בדיקה חיה):** כתובת שחף העובדת של בית הספר היא
> **`katzirb.shahaf.site`** (ללא מקף) — היא **מפרסמת את מערכת השעות** ובדיקה חיה
> נלקחה בהצלחה (39 שיעורים, timestamp "מעודכן ל: 11.11.2026"). כל שורה במסמך הזה
> שאומרת "katzir-b.shahaf.site אינו פועל" הייתה נכונה לכתובת שהבחנו אז, אך
> הכתובת המתקנת היא katzirb — ולכן חוסם "המחכה לפרסום" **הוסר**.

**Working dir:** `~/Documents/Projects/lumio-mission/work/source/lumio-v3.3/` · baseline commit `bac1f4e` · 4.0 commit `7dd260e` (pushed to `origit892-stack/Projects`).

## New files
| file | purpose | size |
|---|---|---|
| `connectors.mjs` | Connector contract: 11 states, 9 error codes, 4-fact model, exact §15 Hebrew labels, dedup/fingerprint/provenance, Shahaf parser (page + table + row + URL builder), feed validation/fetch/import, 5 provider definitions with honest capabilities | ~19KB |
| `database-upgrade-2.sql` | ADDITIVE migration: tasks/school_items (+retrieval_method, verification_state, synced_at, created_at), connections (+4 fact booleans, feed_url, apps_script_key + unique index). Re-runnable, rollback documented. NOT executed against the live project (user action) | ~4.5KB |
| `tests/connectors.test.mjs` | 16 new tests: state table (11 states), exact Hebrew labels, HTTP taxonomy, dedup rules, provenance, Shahaf validation (Hebrew errors), synthetic page parse + stamp + change-detect, upsert idempotency, Israeli DST edges, empty/null safety, feed URL validation (scheme/credentials/wrong-host), synthetic ICS import, static artifact checks (no secrets, 2 placeholders, pg_cron snippet) | ~17KB |
| `apps-script/classroom-sync.gs` | Student-owned daily Classroom auto-sync: NATIVE Classroom advanced service (Courses/CourseWork/own StudentSubmissions), compact JSON, POST to `apps-script-ingest`, `setup()` creates one idempotent 06:00 trigger, Hebrew comments, exactly 2 user-fill placeholders | — |
| `apps-script/README-HE.md` | 5-step student setup, what is read/written, quota facts, undo | — |
| `supabase-functions/apps-script-ingest/index.ts` | Edge Function: key→user row lookup (service role, server-side), rejects invalid/revoked keys (401), upserts that user's tasks/school_items with provenance, 500-item cap, updates connection facts; never trusts client user_id | — |
| `supabase-functions/feed-sync/index.ts` | Cron-driven: polls all `connections.feed_url` (ICS VEVENT + tolerant shahaf table parse), upserts per-user with dedup, updates facts + stamp, chunked for <150s @100 users; DB writes = anti-pause heartbeat | — |
| `supabase-functions/README-HE.md` | Deploy steps, secret setup, pg_cron SQL, honest fallback (manual refresh) + anti-pause note | — |

## Modified files
| file | change |
|---|---|
| `app.mjs` | +231 lines: connections page rebuilt with 4-fact rows + honest per-provider buttons (open site / connect / sync / disconnect / delete-data — separate confirmations), feed connection UI (ICS + shahaf URL with validation, preview, connect, refresh, CORS Hebrew hint), Apps Script auto-sync panel (generate/rotate/revoke binding key), tasks provenance line, privacy panel (per-provider facts, revoke, export incl. school_items), graceful column-missing retry + one-time upgrade notice, footer "לומיו 4.0" |
| `public/sw.js` | +`/connectors.mjs` to ASSETS; cache `lumio-shell-v4.0`; shell-only cache comment |
| `package.json` | version 3.3.0 → 4.0.0 |
| `README.md` / `INTEGRATIONS.md` / `QA.md` / `DEPLOY.md` | 4.0 sections: what is connected (honest), what is not, upgrade-2 step, deploy notes |
| `config.mjs` | **UNCHANGED** (sha256-verified identical to baseline) |

## Verification output (real)
```
npm test → ℹ tests 35 · ℹ pass 35 · ℹ fail 0 · ℹ skipped 0 · duration_ms 77.8
node --check → OK × 7 (app, connectors, core, study, importers, server, sw)
server smoke (PORT=5199) → root: HTTP 200 · connectors.mjs: HTTP 200
secret scan (sb_secret_*/JWT shapes, all new+changed files) → CLEAN
config.mjs sha256 → identical to v3.3 baseline
```

## Deviations from spec (decisions made, all toward honesty)
1. `heStatus('unavailable')` label = "לא זמין כרגע" (contains the §15 "לא זמין" token; test-locked).
2. `validateFeedUrl` public_page host check uses the URL-parsed hostname with `/^([a-z0-9-]+)\.shahaf\.site$/i` (dot mandatory) — rejects `notshahaf.site`, `evil.com/shahaf.site`; accepts `katzir-b.shahaf.site` (test-locked).
3. Shahaf default card copy states the verified B-track 404 fact (12.11.2026) with school contacts — per final research (katzir-b not published).
4. `importFeedItems` returns `items` (not `tasks`) with a `stamp` field for public pages — used by the change-detect flow.

## Known limitations carried into rollout
- Live 2-account browser isolation re-test: blocked by Supabase email rate-limit in the QA window (08).
- Live integrations: `not_verified` per provider (01 matrix) — they become `live_verified` the moment a real authorized source is exercised (Apps Script first run / ICS URL / published page).
- `school_items` live table pending user's run of `database-upgrade.sql` (pre-existing, PGRST205 until then).
