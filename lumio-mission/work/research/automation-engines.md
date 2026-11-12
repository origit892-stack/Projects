# Lumio 4 — BRIEF A: FREE BACKGROUND SYNC ENGINES (0 ILS/month, runs while student PC is off)

- **Research executed:** 2026-11-12 (brief written 2026-11-11)
- **Method:** `web_search` + `web_extract` only. No logins, no credentials. Official vendor docs outrank blogs. All fetched content treated as untrusted data.
- **Labels:** `VERIFIED` (official source fetched/read this session) · `NOT VERIFIED` (no official confirmation found) · `UNLIKELY` (strong negative/contradictory evidence)
- **Known context reused (cited, not re-verified):** Supabase free limits + Classroom API findings in `work/research/moe-cost.md` and `work/research/classroom.md` (both researched 2026-11-11).
- **Pages without a printed date:** labeled "page date not printed; accessed 2026-11-12".

---

## E1. Google Apps Script (script.google.com)

### E1(a) Time-driven trigger capabilities

All from the two official Apps Script pages (quotas; installable triggers) fetched this session.

| Parameter | Consumer account (gmail.com — the student case) | Google Workspace account | Source + date + quote | Label |
|---|---|---|---|---|
| Max trigger frequency | **every minute** (min) to once/month (max) | same | `developers.google.com/apps-script/guides/triggers/installable` (last updated 2026-09-03): "as frequently as every minute or as infrequently as once per month" | VERIFIED |
| Timing jitter | 9 AM trigger "chooses a time between 9 AM and 10 AM, then keeps that timing consistent from day to day" | same | same page | VERIFIED |
| Max triggers per project | **20 / user / script** | 20 / user / script | `developers.google.com/apps-script/guides/services/quotas` (accessed 2026-11-12; mirror footer shows last updated 2026-04-23): "Triggers \| 20 / user / script" | VERIFIED |
| Execution duration limit | **6 min / execution** | 6 min / execution | same quotas page: "Script runtime \| 6 min / execution" | VERIFIED |
| Daily execution quota | **Triggers total runtime 90 min / day** | 6 hr / day | same quotas page: "Triggers total runtime \| 90 min / day" | VERIFIED |
| URL Fetch calls/day | **20,000 / day** | 100,000 / day | same quotas page: "URL Fetch calls \| 20,000 / day" | VERIFIED |
| URL Fetch size | response 50 MB/call; POST 50 MB/call | same | same quotas page | VERIFIED |
| Simultaneous executions | 30 / user | 30 / user | same quotas page | VERIFIED |
| ScriptProperties | 9 KB/value; **500 KB total/property store**; 50,000 reads+writes/day | 500,000 ops/day | same quotas page | VERIFIED |
| Cost | No pricing documented; consumer (gmail.com) accounts carry full quota rows → service usable at $0; no overage model documented | same | same quotas page (consumer column) | VERIFIED (consumer availability); $0 = VERIFIED by absence of any paid tier in docs |

Additional trigger facts (same installable page, 2026-09-03): "Installable triggers always run under the account of the person who created them" → a trigger created by the **student runs as the student's own Google account on Google's servers — the student's PC being off is irrelevant**. Also: "They don't run if a file is opened in read-only (view or comment) mode. For standalone scripts, users need at least view access to the script file" — moot when the student owns the script. VERIFIED.

**Verdict E1(a):** A daily (or hourly) per-student time-driven trigger is comfortably within every consumer-account quota: 1 trigger of 20 allowed; one daily run of at most ~6 min against a 90 min/day budget; 1–20 URL Fetch calls/day against 20,000 allowed. `VERIFIED`.

### E1(b) CRITICAL — Classroom scopes without a Google Cloud project

**The pattern is NOT dead. Google ships a native Classroom service for Apps Script, so a student-authorized script can read the student's own Classroom data without the student creating any GCP project, OAuth client, or consent screen.**

1. **The service exists.** `developers.google.com/apps-script/advanced/classroom` (last updated 2026-09-03): "The Classroom service lets you use the Google Classroom API in Google Apps Script." VERIFIED.
2. **It mirrors the public API** — "uses the same objects, methods, and parameters as the public Google Classroom API" → `Classroom.Courses.list()`, `Classroom.Courses.courseWork.list()`, `Classroom.Courses.courseWork.studentSubmissions.list()` (the exact three methods Lumio needs per `classroom.md` Q1). VERIFIED.
3. **It is an advanced service:** "This is an advanced service that must be enabled before use" (enable in the editor: Services → Add a service, or via manifest `enabledAdvancedServices`). VERIFIED.
4. **No GCP project needed for consumer scripts.** `developers.google.com/apps-script/guides/services/advanced` (accessed 2026-11-12): "If using a default Google Cloud project (created automatically by Apps Script), skip this step. The API is enabled automatically when you add the service in Step 1." VERIFIED. (Only *standard* GCP-linked projects require manual API enablement.)
5. **Authorization is platform-managed.** Same guide: "Apps Script handles the authorization flow automatically." The student authorizes once in the Apps Script editor (first-party consent UI); the platform issues short-lived access tokens when the trigger fires (the `UrlFetch` comparison in the same guide uses `ScriptApp.getOAuthToken()`). **No raw refresh token is exposed to — or required by — script code; the student's one-time grant is persistent and revocable by the student.** VERIFIED (mechanism); the grant's *indefinite* persistence (no documented expiry) is `NOT VERIFIED` officially.
6. **If an explicit refresh token were required instead** (e.g., to call Classroom from outside Apps Script), the answer is the opposite: a GCP OAuth client is mandatory — "Any application that uses OAuth 2.0 to access Google APIs must have authorization credentials that identify the application to Google's OAuth 2.0 server" (`classroom.md` Q6, VERIFIED), the GSI JS flow returns **access tokens only, no refresh token** (`classroom.md` Q4, VERIFIED), and in Testing mode "Authorizations by a test user will expire seven days from the time of consent" (`classroom.md` Q5, VERIFIED).

**Caveats (honest gaps):**
- The exact scope *strings* shown on the Apps Script consent screen could not be enumerated: the official scope-list table on `developers.google.com/apps-script/concepts/scopes` did not render in the fetched text (page fetched, table JS-rendered). The scopes are the Classroom API scopes of the methods used (courses + coursework, per the Classroom API reference in `classroom.md` Q2). `NOT VERIFIED` for exact strings.
- School (WFE) admins can restrict app access generally (`classroom.md` Q2, VERIFIED for third-party apps); whether an admin can disable *first-party Apps Script advanced services* for student users was not documented in this session. `NOT VERIFIED`.

**Verdict E1(b):** A student-authorized Apps Script project **can** read `classroom.courses.readonly` / `classroom.coursework.me.readonly`-equivalent data **without a Google Cloud project**, via the native Classroom advanced service; no refresh token is stored or needed — the Apps Script platform holds a persistent per-student grant. The student-owned-trigger pattern is **alive and is the strongest 0-ILS option found**. `VERIFIED` for all load-bearing claims; scope-string enumeration `NOT VERIFIED`.

### E1(c) Can the script POST to Supabase REST (anon key + JWT) from UrlFetchApp?

- `UrlFetchApp` is the documented path to **external** APIs: the advanced-services guide's comparison table lists "UrlFetch (HTTP)" with "Manual handling required" authorization and "Full access to all API features" — i.e., any HTTPS endpoint, including `https://<project>.supabase.co/rest/v1/...` with `apikey` (anon key) + `Authorization: Bearer <JWT>`. VERIFIED.
- Quota headroom: 20,000 fetches/day (consumer), 50 MB POST/call (quotas page, above). VERIFIED.
- Required scope: `https://www.googleapis.com/auth/script.external_request` (`developers.google.com/apps-script/reference/url-fetch/url-fetch-app`, accessed 2026-11-12). VERIFIED.
- **Egress restriction: none documented.** Neither the quotas page nor the UrlFetchApp reference lists any domain allowlist or external-egress limitation. VERIFIED (by absence across both official pages).

**Verdict E1(c):** Yes — a daily per-student script can POST its Classroom sync payload to Supabase REST with anon key + JWT, well within quotas, with no documented egress restriction. `VERIFIED`.

### E1(d) Safe refresh-token storage location (only needed for the fallback design)

- **Student-owned ScriptProperties** of the student's own container: data lives in the **student's own Google account**; only editors of that script project can read it; Lumio's operator never sees it. Capacity: 9 KB/value, 500 KB total per property store (quotas page) — a refresh token (~100–200 chars) fits trivially. VERIFIED (limits); risk profile is analysis.
- **vs Supabase-side storage:** centralizes every student's credential with the app operator in one place; the 100-secrets/project cap (`moe-cost.md` B1, VERIFIED) bounds it at ~100 students with no headroom; and policy FORBIDS plaintext token storage in Lumio's own DB (Supabase *is* Lumio's DB). Encrypted Supabase secrets are operator-held — same trust concentration, minus the plaintext violation.
- **vs reauthorization-every-time:** the GSI flow needs a user gesture and returns no refresh token (`classroom.md` Q4) → directly contradicts "runs while the PC is off."

**Verdict E1(d):** Ranking: (1) Apps Script native advanced service — **no token stored at all** (best); (2) refresh token in the student's own ScriptProperties — acceptable, student-held; (3) Supabase Functions Secret — capped at 100, centralized, policy-sensitive; (4) reauthorize-every-time — dead for this use case. `VERIFIED` for quotas; ranking is analysis.

---

## E2. Supabase

### E2(a) Scheduled Edge Functions (cron) on the FREE plan

- Official pattern: `supabase.com/docs/guides/functions/schedule-functions` (page date not printed; accessed 2026-11-12): "The hosted Supabase Platform supports the `pg_cron` extension" and "In combination with the `pg_net` extension, this allows us to invoke Edge Functions periodically on a set schedule." VERIFIED.
- `supabase.com/docs/guides/cron` (**Updated Feb 23, 2026**): jobs "can run anywhere from every second to once a year"; "we recommend no more than 8 Jobs run concurrently. Each Job should run no more than 10 minutes." VERIFIED.
- **Free-plan availability:** *neither page states any plan restriction* — the docs are plan-neutral. So: **NOT VERIFIED officially that cron is limited to paid plans; UNLIKELY to be restricted** — consistent with `moe-cost.md` B1 (community free-tier reports, e.g. r/Supabase "28 pg_cron jobs on free tier"; Supabase's own pricing page, accessed 2026-11-11, lists no cron allowance either way). An empirical check on a free project (`create extension pg_cron; select cron.schedule('k','* * * * *','select 1')`) settles it definitively.

**Verdict E2(a):** Official docs describe the pg_cron+pg_net → Edge Function pattern with **no plan gate**; exact free-plan entitlement is `NOT VERIFIED` officially but `UNLIKELY` to be restricted; one free-project experiment would `VERIFY` it at 0 ILS.

### E2(b) Scheduled function reading per-user feed URLs + upserting on users' behalf

- **Invocation pattern (documented):** schedule-functions page shows cron → `net.http_post` → Edge Function, with the service key passed in the `apikey` header: "The function receives the secret key on the apikey header. To accept it, disable `verify_jwt` and use `auth: 'secret'`." VERIFIED.
- **Security caveat from the same official page:** "Any role that can log in to your database can read the secret key while the request waits. `pg_net` writes the decrypted key to `net.http_request_queue` until it sends the request." → prefer Supabase Vault + least-privilege DB roles if using this pattern. VERIFIED.
- **Secrets on Free:** 100 secrets/project, 100 functions/project, 150 s runtime (free plan) — `supabase.com/docs/guides/functions/limits` per `moe-cost.md` B1 (accessed 2026-11-11). VERIFIED.
- **Per-user loop itself** (read `connections.feed_url` rows with service_role, fetch each ICS in the Deno function, upsert `school_items` keyed by `user_id`): standard Edge Function DB capability; **no dedicated official doc describes this exact multi-user polling pattern** — it is a design built on documented primitives. Label: invocation `VERIFIED`, per-user loop `NOT VERIFIED as a documented pattern` / `UNLIKELY` to hit a limit (100 students × 1 fetch each ≈ 100 subrequests, 1 function invocation, ≪150 s).

**Verdict E2(b):** Technically sound and built entirely on documented free-plan primitives; service_role via function secret is allowed (100/project). The specific per-user polling loop is a design pattern, not a documented feature. `UNLIKELY` to be a problem at pilot scale.

### E2(c) Auto-pause interaction — does an edge cron job keep the project unpaused?

Official `supabase.com/docs/guides/platform/free-project-pausing` (page date not printed; accessed 2026-11-12):
- "Supabase pauses Free Plan projects that show low activity over a 7-day period." VERIFIED.
- "A Free plan project is considered inactive if it does not receive sufficient user database activity over the past week." VERIFIED.
- "Typically a few user requests to the database each day over the previous week is enough to keep the project from being paused." VERIFIED.
- "A warning email roughly one week before the pause takes effect"; after the warning, pause can be prevented by visiting the dashboard or "making API calls to your project or sending requests via your connected application." VERIFIED.
- Restore: manual — "Click **Resume project**", "up to 1 year after it was paused." VERIFIED. **No auto-resume is documented** → treat auto-resume as non-existent (`NOT VERIFIED` → assume absent).

**Does the cron job itself count?** The docs never state that pg_cron scheduler activity qualifies as "user database activity". Structurally it does touch the DB (each run executes SQL, writes `net.http_request_queue` / `cron.job_run_details`; the Lumio sync function then reads `connections` and upserts `tasks`), and the community keep-alive pattern (daily `cron.schedule` job) is widely reported to hold free projects up (`moe-cost.md` B1) — but the official pages are silent. Label: `NOT VERIFIED` officially / `UNLIKELY` to be a problem.

**Verdict E2(c):** A daily pg_cron → sync function **should** keep the project unpaused (it generates DB activity), but official docs do not guarantee scheduler activity counts; a *paused* project runs no cron (DB offline) and does not auto-resume. Mitigations: monitor the warning email + an **external** keep-alive (Cloudflare cron or GitHub Actions ping — see E3/E4) that hits the project even if the DB-side scheduler ever stops. `VERIFIED` for all quoted behavior; cron-as-activity `NOT VERIFIED`/`UNLIKELY`-to-bite.

---

## E3. Cloudflare Workers (free plan)

All from `developers.cloudflare.com/workers/platform/limits/` (page date not printed; accessed 2026-11-12) and `developers.cloudflare.com/workers/configuration/cron-triggers/` (**Last updated Oct 17, 2026**), consistent with `moe-cost.md` B2 (Workers pricing page, last updated Oct 2, 2026).

| Question | Free-plan answer | Quote | Label |
|---|---|---|---|
| Cron triggers per account | **5** (paid: 250) | "Number of Cron Triggers per account \| 5" (limits table) | VERIFIED |
| Minimum interval | 5-field cron; `* * * * *` (every minute) is a documented example; **no minimum-interval restriction stated** → once/day is trivially allowed | cron-triggers page: "`* * * * *` — At every minute" | VERIFIED |
| Free invocation quota | **100,000 requests/day**, "resetting at midnight UTC"; overage → Error 1027 | limits page | VERIFIED |
| Cron CPU (free) | 10 ms per cron invocation — but "Waiting on network requests (such as `fetch()` calls…) does **not** count toward CPU time" | limits page | VERIFIED |
| Cron wall time | 15 min per cron invocation | limits page ("Cron Trigger \| 15 min") | VERIFIED |
| Subrequests per invocation | 50 (free) | limits page | VERIFIED |
| Can a Worker call Supabase REST? | **Yes** — outbound `fetch()` to any origin; cron is explicitly marketed for this | cron-triggers page: "Cron Triggers are ideal for running periodic jobs, such as for maintenance or **calling third-party APIs** to collect up-to-date data." | VERIFIED |

**Verdict E3:** Free Cloudflare gives 5 cron triggers/account + 100k requests/day + 50 subrequests — enough for one watchdog worker (or a small fleet of per-user pollers up to 5 triggers) calling Supabase REST. Binding caps: 5 triggers, 50 subrequests/invocation (→ batch per-user ICS fetches), 10 ms free-plan cron CPU (I/O excluded). `VERIFIED`.

---

## E4. GitHub Actions (public repos)

From `docs.github.com` pages fetched this session (events page accessed 2026-11-12 via full-text extraction; billing page accessed 2026-11-12; runner + hardening pages accessed 2026-11-12).

| Question | Answer | Quote (source, date) | Label |
|---|---|---|---|
| Scheduled workflows free on public repos? | **Yes** — standard GitHub-hosted runners are free in public repos (larger runners still billed) | "The use of standard GitHub-hosted runners is free: In public repositories, For GitHub Pages, For Dependabot" (`docs.github.com/en/billing/concepts/product-billing/github-actions`, page date not printed; accessed 2026-11-12) | VERIFIED |
| Monthly minute limits (current policy) | Public: **no minute cap documented** for standard runners. Private (Free plan): **$12 USD/month** included compute; 500 MB artifact storage; 10 GB cache/repo | billing page table: "GitHub Free \| 500 MB \| $12 USD \| 10 GB" | VERIFIED |
| Min cron granularity | **5 minutes** | "The shortest interval you can run scheduled workflows is once every 5 minutes." (events-that-trigger-workflows) | VERIFIED |
| Reliability caveats | Schedules can be **delayed under high load**; "some queued jobs may be dropped"; **public-repo scheduled workflows auto-disable after 60 days without repository activity**; `@daily`-style shortcuts not supported | events page notes (accessed 2026-11-12) | VERIFIED |
| Student-PII handling on GH-hosted runners | Per-job **ephemeral VM**: "GitHub automatically provisions a new VM for that job… When the job has finished, the VM is automatically decommissioned." (`use-github-hosted-runners`) | same | VERIFIED |
| PII in logs | "Use secrets for sensitive information"; "**automatic redaction is not guaranteed**" (`security-hardening-for-github-actions`) → anything echoed (names, emails, task titles) persists in run logs; no official doc found that *prohibits* processing student PII itself | hardening guide (accessed 2026-11-12) | VERIFIED (quotes); "no prohibition doc" = NOT VERIFIED absence |
| Can a workflow step call Supabase REST? | **Yes** — `run:` steps execute arbitrary shell on the runner (docs examples run arbitrary commands); no egress restriction documented | events page examples (`run: \|…`) | VERIFIED (low-risk) |

**Verdict E4:** Public-repo scheduled Actions are free and can poll Supabase, but they are the **weakest of the three engines** for a student-data pipeline: public code, log-retained output with no guaranteed redaction, load-time delays/drops, and the 60-day public-repo auto-disable trap. `VERIFIED`.

---

## E5. RECOMMENDATION

### (a) Daily Classroom API poll with per-student credential — storage options ranked

| Rank | Option | Mechanism | Pros | Cons / binding quota |
|---|---|---|---|---|
| **1** | **Student-owned Apps Script, native Classroom advanced service** | Each student: own script project (template), 1 daily time-driven trigger; `Classroom.Courses/CourseWork/StudentSubmissions` → POST to Supabase REST (anon key + JWT) | **Zero tokens stored anywhere**; runs on Google infra while PC is off; 0 ILS; no GCP project/consent screen/OAuth verification for students; 1st-party authorization surface | N script projects (1 per student) — deploy-from-template needed; WFE admins *might* restrict Apps Script (NOT VERIFIED extent); exact consent-screen scope strings NOT VERIFIED; per-student quotas generous (20 triggers, 90 min/day, 20k fetches/day, 6 min/run) |
| 2 | Refresh token in the **student's own ScriptProperties** | Same script; student-created GCP OAuth client + manual OAuth via `UrlFetchApp`; token in ScriptProperties (9 KB/value, 500 KB store) | Token stays student-held; works even if advanced service is insufficient | Student must run GCP Console + OAuth setup (heavy for a 12–18-year-old); Classroom scopes are Sensitive → OAuth verification/testing-mode **7-day grant expiry** (`classroom.md` Q2/Q5, VERIFIED) |
| 3 | Supabase Functions Secret | Operator stores per-student refresh tokens as named secrets; edge function refreshes + polls | Centralized ops | **100 secrets/project hard cap** (`moe-cost.md` B1, VERIFIED) → dies at ~100 students, no headroom; centralizes all student credentials with the operator; plaintext in Lumio's own DB **FORBIDDEN by policy** (encrypted secrets still operator-held) |
| 4 | Reauthorization every time | GSI popup per session | Nothing stored | GSI returns **access tokens only**, refresh needs a user gesture (`classroom.md` Q4, VERIFIED) → **violates "PC off" requirement**. Dead end. |

### (b) Per-user ICS feed polling (URL in Supabase `connections` table) — engine = ?

| Rank | Engine | Why | Binding free quota |
|---|---|---|---|
| **1** | **Supabase pg_cron → Edge Function** (1 job/day) | Function reads `connections.feed_url`, `fetch()`es each ICS, upserts `school_items`; data lands in the same DB the static site reads; doubles as the project's own anti-pause activity | 500k invocations/mo (~30/mo used), 150 s runtime (100 students × ~0.2 s ICS ≈ fine), 100 functions |
| 2 | **Cloudflare Worker cron** (independent of Supabase DB) | Same polling logic; also serves as the **external watchdog** that pings Supabase (an API call to the project = documented anti-pause activity) even if the DB-side cron ever stops | 5 cron triggers/account, 100k requests/day, 50 subrequests/invocation (→ chunk user batches), 15 min wall |
| 3 | GitHub Actions (public repo) | Free + trivial | 60-day public-repo auto-disable trap, load delays/drops, public logs (E4) |

### Recommended architecture (10–100 student school pilot, 0 ILS)

Each student owns a template Apps Script with one daily time-driven trigger that reads their own Classroom data via the native advanced service and POSTs it to Supabase REST; a single Supabase pg_cron job fires an Edge Function that polls every registered ICS feed URL and upserts it — that same DB traffic is the project's anti-pause heartbeat; an optional free Cloudflare cron worker provides an independent external keep-alive/watchdog.

```
STUDENT PC (may be off all week)        GOOGLE INFRA (always on)                  SUPABASE FREE (auto-pauses if idle)
┌───────────────────────────┐        ┌───────────────────────────────┐          ┌───────────────────────────────────┐
│ Lumio static site         │        │ per-student Apps Script       │          │ tasks / school_items tables (RLS) │
│ (Cloudflare Pages, JS)    │manual──▶│ • Classroom advanced service  │──REST───▶│ connections.feed_url (ICS)        │
│ GSI login + view/refresh  │sync    │ • time-driven trigger 1×/day  │ anon key │                                   │
└───────────────────────────┘        │ • POSTs JSON to Supabase      │ + JWT    │ pg_cron 1×/day ──▶ Edge Function  │
                                     └───────────────────────────────┘          │   fetch ICS per user, upsert rows │
 ICS calendar feeds (per student) ◀─────────────────────────────────────────────┤   DB writes = anti-pause activity │
                                                                                └───────────────────────────────────┘
 CLOUDFLARE FREE (optional watchdog)
 Worker cron 1×/day ──▶ ping/sync against Supabase (API call = documented anti-pause activity; also fails over if
                        pg_cron ever stops or project is mid-warning)
 GITHUB ACTIONS (last-resort fallback only: public repo, 5-min cron, free; 60-day auto-disable trap)
```

### Exact free quotas that bound this design

- **Supabase Free:** 500,000 Edge Function invocations/mo (at 100 students ≈ 8.8k/mo ≈ 1.8%, per `moe-cost.md` B3); 500 MB DB (~10+ years); 5 GB egress (~18% at 100 students at the B3 assumptions — **first cap to watch at scale**); 100 functions; 100 secrets; 150 s/function. VERIFIED (`moe-cost.md` B1, 2026-11-11 sources).
- **Apps Script (per student, consumer):** 20 triggers/user/script; 90 min trigger-runtime/day; 20,000 URL Fetch/day; 6 min/execution; 500 KB ScriptProperties. VERIFIED (quotas page, accessed 2026-11-12).
- **Cloudflare Free:** 5 cron triggers/account; 100,000 requests/day; 50 subrequests/invocation; 15 min cron wall. VERIFIED (limits page, accessed 2026-11-12).
- **GitHub Free:** public-repo standard runners free/unlimited; $12/mo included if private. VERIFIED (billing page, accessed 2026-11-12).

### Exact failure mode when the PC is off for more than 1 week

- **Student side: nothing fails.** Apps Script time-driven triggers execute on Google's servers under the student's own account ("Installable triggers always run under the account of the person who created them") regardless of the student's machine. The only week-scale student-side failures are account-level (revoked consent, suspended/deactivated school account, admin restriction) — `NOT VERIFIED` as a documented auto-timeout; plan for it with a re-deploy runbook.
- **Supabase side (the real week-scale risk):** if *all* DB activity stops for 7 days → Supabase sends a warning email ≈1 week before pausing → project pauses → **pg_cron cannot run (DB offline)** → ICS polling halts → no auto-resume → operator must click "Resume project" (1-year restore window). In the recommended design this self-defuses: the daily per-student sync POSTs + the cron job itself are DB activity, so a fleet of offline PCs does not idle the project. Residual gap: official docs do not state that pg_cron scheduler activity counts as "user database activity" (`NOT VERIFIED`/`UNLIKELY`) — hence the Cloudflare external watchdog, whose API call is the documented post-warning anti-pause action.

---

## Sources

**Google (official, developers.google.com):**
1. `developers.google.com/apps-script/advanced/classroom` — Classroom advanced service ("use the Google Classroom API in Google Apps Script"; "must be enabled before use"; "same objects, methods, and parameters as the public Google Classroom API") — last updated 2026-09-03; full text extracted 2026-11-12.
2. `developers.google.com/apps-script/guides/services/advanced` — advanced services enablement ("default Google Cloud project… The API is enabled automatically when you add the service"; "Apps Script handles the authorization flow automatically"; UrlFetch comparison) — accessed 2026-11-12, full text extracted.
3. `developers.google.com/apps-script/guides/services/quotas` (+ `.md.txt`) — quotas/limitations tables (20 triggers/user/script; 6 min/execution; 90 min/day consumer trigger runtime; 20k URL Fetch/day; 50 MB POST/call; 500 KB properties; 9 KB/value) — accessed 2026-11-12 (mirror footer: last updated 2026-04-23).
4. `developers.google.com/apps-script/guides/triggers/installable` — time-driven triggers ("as frequently as every minute… once per month"; jitter note; "always run under the account of the person who created them"; read-only-mode caveat) — last updated 2026-09-03; full text extracted 2026-11-12.
5. `developers.google.com/apps-script/reference/url-fetch/url-fetch-app` — UrlFetchApp + `script.external_request` scope — accessed 2026-11-12 (search snippet of official page).
6. `developers.google.com/apps-script/concepts/scopes` — Apps Script scope concepts; **scope table did not render in extraction** (limitation noted in E1(b)) — accessed 2026-11-12.
7. `developers.google.com/classroom/quickstart/apps-script` — official Classroom-in-Apps-Script quickstart — last updated 2026-09-03; accessed 2026-11-12.

**Supabase (official, supabase.com/docs):**
8. `supabase.com/docs/guides/functions/schedule-functions` — pg_cron + pg_net → Edge Function; secret via `apikey`, `verify_jwt` off, `auth:'secret'`; `net.http_request_queue` secret-exposure caveat — page date not printed; full text extracted 2026-11-12.
9. `supabase.com/docs/guides/cron` — "every second to once a year"; ≤8 concurrent jobs, ≤10 min each — **Updated Feb 23, 2026**; full text extracted 2026-11-12.
10. `supabase.com/docs/guides/platform/free-project-pausing` — 7-day low-activity pause; "sufficient user database activity"; "a few user requests to the database each day"; warning email ~1 week prior; manual "Resume project", 1-year window — page date not printed; full text extracted 2026-11-12.
11. `supabase.com/docs/guides/functions/limits` + `supabase.com/pricing` + `supabase.com/docs/guides/platform/billing-on-supabase` (Updated Sep 17, 2026) — free plan: 500k invocations/mo, 500 MB DB, 5 GB egress, 100 functions, 100 secrets, 150 s runtime — cited via `work/research/moe-cost.md` B1 (accessed 2026-11-11; not re-fetched this session per brief's known-context rule).

**Cloudflare (official, developers.cloudflare.com):**
12. `developers.cloudflare.com/workers/platform/limits/` — account plan limits (Free: 100k requests/day, 5 cron triggers/account, 50 subrequests, 128 MB, 100 workers), cron CPU 10 ms free ("Waiting on network requests… does not count toward CPU time"), cron wall time 15 min, Error 1027 overage — page date not printed; full text extracted 2026-11-12.
13. `developers.cloudflare.com/workers/configuration/cron-triggers/` — cron trigger setup, 5-field expression (`* * * * *` = every minute), "calling third-party APIs to collect up-to-date data", limits pointer — **Last updated Oct 17, 2026**; full text extracted 2026-11-12.
14. `developers.cloudflare.com/workers/platform/pricing/` — Free 100,000 requests/day, 10 ms CPU — **Last updated Oct 2, 2026** — cited via `moe-cost.md` B2 (accessed 2026-11-11).

**GitHub (official, docs.github.com):**
15. `docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows` — `schedule` event: 5-minute minimum, POSIX cron, UTC/timezone, high-load delays + dropped jobs, **60-day public-repo auto-disable**, no `@daily` shortcuts — page date not printed; full text extracted 2026-11-12.
16. `docs.github.com/en/billing/concepts/product-billing/github-actions` — "standard GitHub-hosted runners is free: In public repositories…"; GitHub Free $12/mo included compute; 500 MB artifacts; 10 GB cache; larger runners billed on public repos — page date not printed; full text extracted 2026-11-12.
17. `docs.github.com/en/actions/how-tos/manage-runners/github-hosted-runners/use-github-hosted-runners` — "GitHub automatically provisions a new VM for that job… the VM is automatically decommissioned" — accessed 2026-11-12.
18. `docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions` — "Use secrets for sensitive information"; "automatic redaction is not guaranteed" — accessed 2026-11-12.

**Local prior research (cited as known context):**
19. `work/research/moe-cost.md` (2026-11-11) — Supabase free limits, auto-pause analysis, community pg_cron-on-free evidence, B3 scale model.
20. `work/research/classroom.md` (2026-11-11) — Classroom REST methods/scopes/rate limits; GSI access-token-only flow; 7-day Testing-mode grant expiry; sensitive-scope verification; WFE admin controls.

**Community (lower weight, labeled in text):**
21. r/Supabase threads + github.com/orgs/supabase/discussions/37405 — pg_cron keep-alive on free tier in practice (via `moe-cost.md` B1) — NOT VERIFIED officially.
22. crontap.com/guides/supabase-cron-jobs — "Free projects can pause… their database jobs cannot run while paused" (third-party) — NOT VERIFIED officially; consistent with #10.
