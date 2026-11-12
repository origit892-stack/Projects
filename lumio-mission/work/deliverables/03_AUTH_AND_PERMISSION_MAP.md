# 03 — Auth & Permission Map (Lumio 4.0)

Four independent facts per connection (implemented as `connectionFacts()` in `connectors.mjs`, stored per-user in `connections`):

| fact | meaning |
|---|---|
| `identity_authenticated` | the user proved who they are to Lumio (Supabase Auth) and/or to the provider |
| `permission_granted` | an explicit, scoped consent/permission exists for the data path |
| `data_readable` | real data was actually read from the source (never inferred) |
| `sync_working` | a sync cycle completed end-to-end recently |

## Per-provider authorization model

### Google Classroom
| path | identity | permission | data | sync | consent surface | revocation |
|---|---|---|---|---|---|---|
| In-app GSI (needs admin OAuth client) | Lumio: Supabase; provider: Google GSI popup | 2 readonly scopes, student-consented in Google popup | on "סנכרן עכשיו" | on demand | Google consent screen (app name = Lumio's registered client) | Google account → Security → 3rd-party access → remove; Lumio "נתק" button |
| **Apps Script auto-sync (no admin needed)** | student's own Google account (script runs as them) | native Classroom service = own data only, consented when student runs `setup()` once | daily 06:00 | automatic (Google infra, PC off) | Google script consent (student's own project) | "בטל סנכרון יומי" in Lumio (revokes the binding key) or delete the script in Google |

Key facts: GSI returns **access tokens only** (no refresh token) → in-app flow cannot sync in background. The Apps Script path stores **zero tokens** in Lumio: binding = a random 32-hex per-user key (`connections.apps_script_key`, owner-visible, rotatable/revocable in the privacy panel). No refresh tokens anywhere in the system.

### Mashov / Ofek / PeTeL (no official student API)
- Lumio NEVER collects, stores, or proxies provider credentials (hard rule; no password fields exist in the app).
- `user_local_import` (Mashov): student runs a community tool on their own machine with their own login; the resulting JSON/CSV/ICS file is imported into Lumio. Lumio's involvement ends at the file — same legal position as uploading a report card. Not endorsed, presented neutrally, may break without notice.
- PeTeL ICS: the URL is the student's own personal calendar subscription (secret by nature). Stored ONLY in that user's `connections.feed_url` (RLS owner-only), shown with the warning that it contains a personal identifier, deleted on "נתק".
- Ofek Classroom-bridge: no new credentials — the teacher shares in Ofek (teacher's action, teacher's consent); the student's existing Classroom connection ingests the item.

### Shahaf public pages
- No authentication. Public class-level data only. Connector validates host is `*.shahaf.site` (verified platform) before fetching. No student PII observed in published tables.

### Ministry of Education (IDM)
- **Identity federation only, no delegated data authorization** for a new app to self-register (verified in 02, MoE section). The official SP/IDM path (sapakim.education.gov.il/tech/idm) is vendor-approval-gated (forms, GR_IDM_Team@education.gov.il) — a process blocker, not a code one. Lumio 4.0 does NOT claim any MoE SSO capability.

## What Lumio NEVER does (enforced in code + tested)
1. Never stores provider passwords/tokens (only: own Supabase session, per-user feed URL, per-user Apps Script binding key).
2. Never presents "מחובר" without `data_readable` proof (heStatus mapping + unit-tested).
3. Never trusts client-supplied `user_id` in the Apps Script ingest function (key→user row lookup server-side).
4. Never reads/writes another user's rows (RLS `auth.uid() = user_id` on all tables; new columns inherit table-level owner policies — unchanged by upgrade-2).
5. Never caches feed/student data in the service worker (shell-only cache, verified in sw.js).
