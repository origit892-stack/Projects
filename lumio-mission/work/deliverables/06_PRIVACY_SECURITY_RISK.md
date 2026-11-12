# 06 — Privacy, Security & Risk (Lumio 4.0)

Users are **school children (minors)** — the standard is maximal privacy, minimum collection.

## What is stored (and where)
| data | location | protection |
|---|---|---|
| Lumio account (email+password) | Supabase Auth (user's project) | Supabase hash policy; 2FA available in dashboard |
| tasks / school_items (incl. grades if the student syncs them) | Postgres, owner-only RLS | `USING (auth.uid()=user_id)` + `WITH CHECK`; new upgrade-2 columns inherit table-level owner policies (unchanged) |
| per-user feed URL (PeTeL ICS / Shahaf page) | `connections.feed_url` | owner-only RLS; shown with personal-identifier warning; deleted on "נתק" |
| per-user Apps Script binding key (32-hex) | `connections.apps_script_key` | owner-only RLS; shown once in privacy panel with warning; rotate/revote buttons; unique index |
| Google access/refresh tokens | **NOWHERE** | GSI returns access-only; Apps Script path stores no tokens |
| Provider passwords (Mashov/Ofek/PeTeL/MoE) | **NEVER** | no credential fields exist in the app |
| Service-worker cache | device | shell files only — no API/student data (verified in sw.js + test comment) |

## Verified security properties (this mission)
1. **RLS isolation**: anon probe of `/rest/v1/tasks` blocked (2026-11-11); user's own 2-account manual test reported no cross-visibility (2026-10, per master brief §1.3). Live 2-account browser re-test for 4.0: **blocked by Supabase email rate-limit during QA window** — see 08; RLS policies were not changed by upgrade-2 (additive columns only), so the isolation argument carries, but the live re-test remains an open QA item.
2. **No secrets in repo/ZIP**: secret scan of all new/changed files = CLEAN (regex for `sb_secret_*`, JWT shapes); `config.mjs` sha256 identical to baseline (only the pre-existing public anon key); Edge Functions read secrets from Supabase secret store only.
3. **Apps Script ingest cannot write cross-user**: server-side key→row lookup; client `user_id` is never trusted (design + code review target).
4. **Feed fetch hardening**: http(s)-only, credentials-in-URL rejected, public_page restricted to the verified `*.shahaf.site` platform, 20s timeout, 2MB cap, `credentials:'omit'`, CORS-failure mapped to an explicit Hebrew hint (no silent data invention).
5. **No security bypass anywhere in the mission**: no CAPTCHA bypass, no session injection between systems, no cross-app token transfer, no credential storage — per the master brief's hard rules (enforced by the mission design and the QA scope).

## Risk register
| # | risk | severity | mitigation | residual |
|---|---|---|---|---|
| R1 | Student grades are sensitive personal data of minors | HIGH (regulatory) | Stored only if the student's own authorized source path brings them; per-source delete button; export button; documented retention policy required before school rollout | Israeli Privacy Protection Law (2024 revision) — school + parental consent workflow needed before distribution (see 09) |
| R2 | Supabase free tier auto-pauses after ~1 week of low DB activity → cron sync stops | MEDIUM | feed-sync DB writes = documented anti-pause heartbeat; site shows "הסנכרון המזומן ממתין — רענון ידני זמין" transparent state | user must know: a fully-idle project pauses; any site use resumes it |
| R3 | Binding-key leak (Apps Script) → another party can push items into that student's account | LOW-MED | key owner-only visible; rotate/revote UI; key only ADDS items (no delete/read of other data); items carry provenance so injected data is inspectable | the student must guard the key (documented warning) |
| R4 | Community tools (pymashov etc.) break or violate Mashov ToS when run by students | LOW (user-local) | presented neutrally as the student's own option; not endorsed; import is file-based; Lumio stores no credentials | ToS risk rests with the individual user running it on their own account — documented as such |
| R5 | School publishes (or stops publishing) Shahaf pages; HTML drift | LOW | tolerant parser + stamp change-detect + "SOURCE_CHANGED" state; per-page error isolation | parser needs maintenance if the platform changes markup |
| R6 | Classroom testing-mode consent expires (~7 days) for the in-app flow | MEDIUM (pilot only) | documented in 09 (C1): production verification of the OAuth client for the school domain, or use the Apps Script path which has no consent expiry | admin action required for in-app pilot |
| R7 | Feed URLs are personal identifiers if leaked | LOW | owner-only RLS, warning UI, deleted on disconnect | standard secret-hygiene burden on the user |

## Before publishing to a whole school (checklist)
1. Parental/school consent form (Hebrew) covering: which data is synced, where it is stored (user's Supabase project), retention, deletion.
2. Data retention & deletion policy (how long, how a student deletes everything — "מחק הכול" export-then-delete).
3. Accessibility pass (screen readers, contrast) — recommended, not yet audited.
4. Confirm Supabase free-tier ToS allows student-data hosting for the project's scale (it does, with the 07 limits).
5. School IT approval if the school enforces Apps Script restrictions for student accounts (NOT VERIFIED for any specific school — ask the school admin).
