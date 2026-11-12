# 08 — QA Results (Lumio 4.0)

```yaml
project_version: "Lumio 4.0 (baseline v3.3 sha256-verified, 25 files)"
source_backup_verified: true          # git baseline bac1f4e + work/source-3.3.sha256 (25 files)
existing_ui_preserved: verified_in_code  # no CSS changes; app.mjs diff additive; zero new CSS classes (code-reviewer audit)
unit_tests: {passed: 37, failed: 0}   # 19 baseline + 18 new (connectors, shahaf, feeds, static artifact + security-shape checks)
node_syntax_check: {passed: 7, failed: 0}  # app, connectors, core, study, importers, server, sw
deno_check: {passed: 2, failed: 0}    # feed-sync + apps-script-ingest, deno 2.9.8 scratch copy (npm dep resolved)
server_smoke: {root: 200, connectors_mjs: 200}  # PORT=5199, node server.mjs
config_mjs_untouched: true            # sha256 identical to baseline
secrets_in_repo: none                 # regex scan sb_secret_*/JWT shapes over all new+changed files = CLEAN
qa_review_round: "3 reviewers (code-reviewer, security-reviewer, typescript-reviewer), read-only, VERIFIED_CONCURRENT (692s overlap)"
review_findings_fixed: 22             # all CRITICAL/HIGH/MAJOR + quick minors; see "QA round 2" below
supabase_rls_2_users: BLOCKED_live_retest   # anon probe blocked (VERIFIED); user's own 2-account manual test on v3.3 reported isolated; RLS policies unchanged by upgrade-2; live re-test blocked by Supabase email rate-limit during QA window
live_integrations:
  classroom: not_verified            # no admin OAuth client; Apps Script template not deployed by a student yet
  mashov: not_verified               # no official API exists (negative result) — import path tested with synthetic fixtures
  ofek: not_verified                 # Classroom-bridge payload unverified — teacher pilot pending
  petel: not_verified                # ICS feed parser tested on synthetic fixtures only (no real student URL)
  shahaf: parser_live_verified       # public pages fetched + shape confirmed (dror/katzir-a/katzir .shahaf.site, 2026-11-12); Katzir B-track NOT published (404)
zip_integrity: pending               # created at final packaging (see 00)
known_blockers:
  - Supabase email rate-limit blocked new test-account creation during the QA window (2-user live re-test deferred)
  - school_items table missing in the user's live project until database-upgrade.sql is run (pre-existing, documented)
  - PGRST205 on /rest/v1/school_items until that upgrade runs — the app shows the install-warning state (honest)
```

## Test evidence
- `npm test` → 37 pass / 0 fail (final run 2026-11-12, after QA round 2).
- `deno check` clean on both edge functions (scratch copy, deps resolved).
- New tests cover: all 11 connection states (4-fact table), exact §15 Hebrew labels, HTTP error taxonomy, dedup rules, provenance propagation, Shahaf row validation, synthetic Shahaf page parse + stamp + change-detect, upsert idempotency, Israeli DST date edges, empty/null inputs, feed URL validation (https-only incl. http rejection, credentials, wrong host, non-shahaf), synthetic ICS import, **static checks on deployment artifacts** (Apps Script: 3 native calls + exactly 2 placeholders + trigger; edge functions: env-only secrets, no literals) + **static security-shape checks** (SSRF guard present and invoked, cron token gate, body cap, due_at validation).

## QA round 2 — review findings and fixes (2026-11-12)
Three independent read-only reviewers (batch `89fe7c2ee9e34cff`, VERIFIED_CONCURRENT). All CRITICAL/HIGH/MAJOR findings fixed in the same pass; fixes verified by tests + deno check + re-scan.

| # | Sev | Finding | Fix |
|---|-----|---------|-----|
| H1 | CRIT | SSRF: feed-sync fetched user-writable `feed_url` server-side with no validation | `assertSafeFeedUrl` + `isPrivateIp` (RFC1918/loopback/link-local/metadata/CGNAT, v4+v6-mapped), https-only, shahaf allowlist, DNS-resolve check, invoked before every fetch |
| M1 | MED | feed-sync endpoint unauthenticated (URL derivable) | `LUMIO_CRON_TOKEN` secret gate (401 without matching `x-lumio-cron`) |
| M2 | MED | README cron snippet embedded SERVICE_ROLE key in SQL | snippet now sends only the cron token |
| M3 | MED | "Delete data" didn't stop daily Classroom sync (re-ingest within 24h) | classroom deletion now also nulls `apps_script_key` with a dedicated confirm |
| M4 | MED | ICS feeds accepted any host + plain http (token sniffable) | https-only for all feed types |
| MAJ-1 | MAJ | Apps Script due dates shifted +1 day during Israeli DST (hardcoded +02:00) | `T00:00:00Z` wall-clock-as-UTC — identical to `core.mjs` convention; both sync paths now write the same value (also fixes the two-writers due_at mismatch) |
| MAJ-2 | MAJ | ingest never set `state`, so daily sync left "awaiting consent" with four ✓ facts | success path now sets `state:'synced'` |
| MAJ-3 | MAJ | manual/import rows stamped `synced_at` → false "סונכרן" on hand-typed data | `synced_at` only for `official_api` / `public_school_feed` |
| MAJ-4 | MAJ | legacy v3.3 `api_connected`/`imported` rows contradicted their own fact row | legacy states mapped to honest facts in `connectionFacts` (tested) |
| H2 | HIGH | feed-sync chunking fully sequential → worst case >150s | `Promise.all` within batches, CHUNK=20 (100 feeds ≈ 100s) |
| H4 | HIGH | two writers, divergent rows (end_time/description/source_url clobbered) | edge mirrors now field-for-field identical to client parsers (ICS dedup key verbatim, DESCRIPTION/URL carried, shahaf end parsed) |
| CR5/M3 | MIN | ICS dedup key mismatch without UID → duplicate rows | client expression copied verbatim |
| M4 | MED | cron overwrote user task status on feed rows | no `status` in feed upserts (DB default on insert, preserved on update) |
| TS L3 | LOW | bad shahaf time cell sank the whole feed upsert | `TIME_OK` validation skips bad rows like the client |
| M5 | MED | degradation retries treated ANY error as "column missing" | degrade only on PostgREST "could not find the … column"; other errors surface; degraded feed-save now notifies about upgrade-2 |
| M7 | MED | `disconnectProvider` fire-and-forget, no catch | wrapped in try/catch with Hebrew error |
| M10/CR10 | MED | `DATA_VALIDATION_FAILED` hint missing; dead AbortError branch | Hebrew hint added (timeout maps to NETWORK_ERROR message) |
| L1–L5 | LOW | `javascript:` href self-XSS, body size, ICS truncation, README doc/code contradiction, due_at garbage | `safeHref` on all stored-data hrefs; 1.5MB raw-body cap; ICS field caps; README rewritten; `due_at` validated to ISO or null |
| docs | MIN | README auto-pause claim referenced a UI string that doesn't exist; typos | honest rewrite (no such indicator exists); typos fixed |

Deliberately NOT changed: `importers.mjs` ICS `+02:00` floating-time convention (v3.3 baseline behavior, shared by browser + edge mirrors — changing one writer alone would re-introduce divergence); Apps Script `status` (kept — submission state is source-authoritative, matches v3.3 classroom behavior).

## UI before/after (screenshots)
- Before (v3.3): `work/evidence/ui-before-desktop.png`, `ui-before-mobile.png` (2026-11-11)
- After (4.0): auth screen + registration attempts captured (`~/.hermes/cache/browser-use/workspace/lumio4/`); full logged-in captures deferred to the 2-user live re-test.

## QA items intentionally NOT claimed
1. "הכול עובד" — not claimed. Live integration verification is provider-by-provider above; anything `not_verified` stays so until a real authorized source is exercised.
2. Mobile-device (real phone) pass — desktop + 390×844 emulated captures done; a real iPhone/Android pass is a pre-rollout item.
3. PWA installability on a real device — manifest + SW present and cached-shell-verified; install test deferred to rollout checklist.
4. Edge functions deployed to the live project — not done (user action, steps in READMEs); `deno check` + static tests only.
5. pg_cron anti-pause over 7+ days — designed, not stress-tested.
