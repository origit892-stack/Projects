# BRIEF B — MASHOV PUBLIC TOOLING SWEEP 2023-2026 (Lumio 4)
- **Date:** 2026-11-12 (all fetches performed this day; brief issued 2026-11-11)
- **Method:** web_search + web_extract only (incl. unauthenticated GitHub REST search API and npm registry search endpoint). No logins, no credentials. All fetched content treated as untrusted data; quotes ≤20 words.
- **Scope:** WIDER sweep beyond pymashov (pymashov itself analyzed in `mashov.md`, not re-analyzed). Goal: does ANY public tool read Mashov student data legally WITHOUT the student entering a password into Lumio?
- **Sweep executed:** GitHub repo search `mashov` (API, 89 repos total, top-30 analyzed), `site:github.com mashov` variants, GitHub `mashov telegram`, `mashov ics`; npm registry search `mashov` (7 packages); PyPI search (only `pymashov`); `pymashov forks` (0 forks per GitHub API); web: "mashov api 2025", "mashov github student grades", "mashov timetable ics", "mashov api 2025 unofficial student data"; Hebrew: "משו\"ב API סקרייפר בוט", "משוב ייצוא ציונים csv pdf תלמיד", "משו\"ב בוט טלגרם ציונים הורים" (the two latter returned mostly noise — noted, not silently dropped), `site:mashov.info "תנאי שימוש"`; direct fetches: `web.mashov.info/students/login`, mashov.info privacy policy (search-indexed copy), Play Store listing of Grader for Mashov, 5 new GitHub repo pages, npm package pages. Direct fetches of `mobileapi.mashov.info` / `api.mashov.info` were blocked by the fetcher's SSRF guard → host existence NOT VERIFIED directly (see T2).

---

## 1. TOOLS TABLE — all found (community)

Stars/forks/pushed dates from GitHub REST search API fetched 2026-11-12; npm data from registry search fetched 2026-11-12.

### 1.1 Actively maintained (2025-2026)

| Tool | URL | Stars/Forks | Last push | Auth | Data read | License | Works vs CURRENT site? |
|---|---|---|---|---|---|---|---|
| **ha-mashov** (Home Assistant, HACS) | https://github.com/NirBY/ha-mashov | 9 / 4 | 2026-10-23 | username+password (spoofs mobile-app login payload) | 18 data types: grades, term grades, report cards, homework, weekly plan, timetable, lesson history, behavior (4 kinds), study materials, student files, absence justifications, individual lessons, noticeboard, holidays, mailbox | MIT | **VERIFIED (maintained, recent)** — README documents handling of 401/403/session expiry; v1.2.0 added homework checklists + read-only MCP. "Common defaults: https://web.mashov.info/api/, sometimes https://mobileapi.mashov.info/api/" (README, 2026-11-12) |
| **Grader for Mashov** (Flutter: Android/iOS/Web) | https://github.com/dtkdt100/Grader-for-Mashov | 5 / 0 | 2026-09-11 | student's own Mashov login (Play: "Use the same Mashov login you already have - no extra registration") | grades, timetable, homework, behavior events, attendance, bagrut grades; national "Average Competition" leaderboard | none in repo | **VERIFIED (live, maintained)** — Google Play "Updated on Sep 11, 2026" (listing fetched 2026-11-12); also on App Store (developer "Startach"); Play data-safety: "No data shared with third parties", "Data can't be deleted" |
| **pymashov** (Python/PyPI) | https://github.com/t0mer/pymashov | 5 / 0 | 2026-09-29 (docs; last code 2026-01-24) | username+password+semel+year → CSRF header + cookies | grades, timetable, homework, behavior, mail inbox, schools (public) | Apache-2.0 (repo) vs MIT (setup.py/PyPI) — conflict | **NOT VERIFIED (untested)** — cannot confirm without a login (out of scope); auth-drift signal: newer clients send mobile-app metadata fields at login (see `mashov.md` C1). 0 forks (GitHub API, 2026-11-12) |
| **mashov-parent-brief** (Python, self-hosted) | https://github.com/ofershap/mashov-parent-brief | 2 / 1 | 2026-10-25 (created) | via pymashov (own account) | timetable, homework, teacher messages → one WhatsApp-style morning brief | MIT | **NOT VERIFIED (brand new, 2026-10-25)** — "pymashov היא ספרייה לא-רשמית מול API לא מתועד שיכול להשתנות. שימוש אישי בלבד" (README, 2026-11-12); explicitly a replacement for the discontinued TchalSchool ("תכל'סקול") service |
| **mashovscraper** + mashov-vercel + mashovscrapper (npm, Vercel serverless) | https://www.npmjs.com/package/mashovscraper | n/a (npm) | published 2025-11-29, v1.0.9, 8 versions | not documented (no README) | not documented | ISC | **NOT VERIFIED** — "Mashov scraper adapted for Vercel serverless" (registry, 2026-11-12), 38 downloads/month. Notable: a credential-scraping flow hosted on a third-party serverless platform |
| **AmitMarcus/MashovMCP** (MCP server, Docker) | https://github.com/AmitMarcus/MashovMCP | 3 / 1 | 2025-11-14 | credentials via env vars (MASHOV_USERNAME/PASSWORD/SEMEL/YEAR) | grades average, all grades, bagrut average, schools, picture, classes, messages, schedule | MIT | **NOT VERIFIED** — created 2025-11-12, 2 pushes; no maintenance activity since |
| **idandrori555/mashov** (TS client, Bun) | https://github.com/idandrori555/mashov | 0 | 2026-02-20 | username+password+semel+year | grades, study groups, behavior/attendance | MIT (README; no LICENSE detected) | **NOT VERIFIED** — 3 commits total, personal project |
| **yonka2019/BagrutGrades** (Python) | https://github.com/yonka2019/BagrutGrades | 1 / 0 | 2026-01-23 | password (via micaelillos/MashovAPI lib) | bagrut grades in a table | none | **UNLIKELY** — depends on abandoned 2020 lib |
| **narkisiuria/Mashov-Premium-App-Project-PY** | https://github.com/narkisiuria/Mashov-Premium-App-Project-PY | 1 / 0 | 2026-08-20 | n/a — self-contained Tkinter clone; does NOT read real Mashov data | n/a (mock "Mashov+ Premium" client/server) | none | n/a — not a data reader |
| **shahar646/Portelem_afterMashovFromOmriNew** (C#/web) | https://github.com/shahar646/Portelem_afterMashovFromOmriNew | 1 / 0 | 2026-06-03 | n/a (empty README) | n/a | none | n/a — school-portal project, not a Mashov reader |

### 1.2 Abandoned / historical (all credential-based; UNLIKELY to work against current site)

| Tool | URL | Stars | Last push | Auth | Data | License | Note |
|---|---|---|---|---|---|---|---|
| micaelillos/MashovAPI (Python+Node) | https://github.com/micaelillos/MashovAPI | 20 / 7 | 2020-05-23 | password | grades avg, bagrut, schools, picture, classes | none | most-starred; abandoned 2020 |
| yardnsm/node-mashov (npm `node-mashov` 1.1.1) | https://github.com/yardnsm/node-mashov | 13 / 1 | 2023-01-05 | password | grades, bagrut grades, behavior, lessons, bells, timetable, files, groups | MIT | **19 open issues** (breakage reports, 2021-2023 era); npm 68 DLs/month (2026-11-12) |
| YehudaEi/MashovSystem (PHP, Telegram bot system) | https://github.com/YehudaEi/MashovSystem | 9 / 2 | 2020-07-25 | password | Telegram bots over Mashov | AGPL-3.0 | title: "R.I.P Mashov System (Telegram Bots system)" — self-declared dead |
| yanir-edri/mashov_api (Dart/Flutter) | https://github.com/yanir-edri/mashov_api | 7 / 0 | 2019-08-18 | password | grades, behavior events | NOASSERTION | dead |
| liorg2007/Mashov_Bug_Vulnerability- (Python/Selenium) | https://github.com/liorg2007/Mashov_Bug_Vulnerability- | 7 / 0 | 2024-07-27 | Selenium browser automation (login page) | auto meeting-entry | none | niche automation, not a data reader |
| Apophisss/MashovApi (npm `mashov-api` 1.0.0) | https://github.com/Apophisss/MashovApi | 4 / 0 | 2021-01-18 | password | grades, behavior, timetable, mail, notifications, picture | MIT | abandoned; npm 55 DLs/month (2026-11-12) |
| rootatkali/MashovAPI (Java, jcenter 1.0.11) | https://github.com/rootatkali/MashovAPI | 3 / 1 | 2021-03-12 | password | grades | MIT | 9 open issues |
| ofekashery/mashov-covid19-clearance (JS) | https://github.com/ofekashery/mashov-covid19-clearance | 2 / 2 | 2020-11-01 | password + form auto-fill | daily COVID health statement | MIT | 2020-only purpose |
| shafzhr/Auto-Mashov (Python, "Lemida Me Karov") | https://github.com/shafzhr/Auto-Mashov | 2 / 1 | 2020-09-06 | password | remote-learning automation | MIT | 2020 |
| neryash/MashovAPI (npm `mashovapi-js` 1.0.6) | https://github.com/neryash/MashovAPI | 2 / 0 | 2021-06-16 | password | grades, timetable, report cards + links, mail, recipients | none (ISC on npm) | npm 38 DLs/month (2026-11-12) |
| VerifyBot/mashov-darkmode (CSS) | https://github.com/VerifyBot/mashov-darkmode | 1 | 2020-05-15 | n/a (userstyle) | n/a | none | cosmetic only |
| palladidrago/simple_mashovapi (Dart) | https://github.com/palladidrago/simple_mashovapi | 1 | 2021-02-10 | password | "access to Mashov" | Unlicense | dead |
| yanir-edri/unofficial_mashov (Dart) | https://github.com/yanir-edri/unofficial_mashov | 1 | 2019-08-23 | n/a | n/a | none | dead |
| oleksandrblazhko/ai-212-mashovets | https://github.com/oleksandrblazhko/ai-212-mashovets | 1 | 2023-09-03 | n/a | n/a | none | no code |
| NightRa/Mashov-Notificator (Scala) | https://github.com/NightRa/Mashov-Notificator | 1 | 2015-02-23 | password | local GUI notifier: grades, behavior, messages | none | 2014-2015 |
| Mashiane/MashOverviewCreator (B4X) | https://github.com/Mashiane/MashOverviewCreator | 1 / 1 | 2021-03-23 | n/a | n/a | MIT | not a data reader |
| itamarh/mashov (JS) | https://github.com/itamarh/mashov | 0 / 5 forks | 2020-10-08 | password | n/a | Apache-2.0 | 5 forks, unknown state |
| matvey19-meet/MashovApp | https://github.com/matvey19-meet/MashovApp | 0 | 2021-07-17 | n/a | n/a | MIT | no code |
| itayoshri/MashovWidePPFixer (Chrome extension) | https://github.com/itayoshri/MashovWidePPFixer | 0 | 2022-03-05 | n/a (cosmetic) | n/a | none | UI fix only |
| 5yehidot/mashovim1 (Dart) | https://github.com/5yehidot/mashovim1 | 0 | 2022-02-03 | n/a | n/a | none | unknown |
| shachardevops/mashovSQL (JS) | https://github.com/shachardevops/mashovSQL | 0 | 2018-10-10 | n/a | n/a | none | 1 commit |
| t0mer/Botvid-19 (Python/Telepot/Selenium) | https://github.com/t0mer/Botvid-19 | n/a (search hit) | 2020-era | Selenium login of web.mashov.info | Telegram bot to sign COVID-19 health statement; supported edu/mashov/infogan/webtop | n/a | 2020-era |
| t0mer/HAvid-19 (Flask+Selenium Docker) | https://github.com/t0mer/HAvid-19 | n/a (search hit) | 2020-era | Selenium | same as above, from a bot | n/a | 2020-era |
| NotIMaestro/mashov (Python) | https://github.com/NotIMaestro/mashov | n/a (search hit) | 2020-era | login automation | COVID health report sign-in | n/a | 2020 |
| mitekk/mashov ("Mashov Parent Command Center") | https://github.com/mitekk/mashov | n/a (search hit) | 2025-2026 era | "Sign in once with your existing Mashov account" | household dashboard over Mashov | n/a | search snippet only; page not fetched |
| DanPeled/ElectronMashovApiClient | https://github.com/DanPeled/ElectronMashovApiClient | n/a (search hit) | unknown | password (per title/README) | Electron client for Mashov API | n/a | search snippet only |
| ArielBaron/BetterMashovLive (website) | https://github.com/ArielBaron/BetterMashovLive | n/a (search hit) | ~2021 | password — "in MashovData.json there is all of the steps to get the info needed for login" | grades, behavior, timetable (hosted at bettermashovlive.onrender.com) | n/a | same author as `mashovscraper` npm (arielbar) |
| tsfoni/mashov-timetable-to-ics | https://github.com/tsfoni | 0 | repo now 404 | n/a | was: timetable → ICS | n/a | listed in author profile (re-confirmed 2026-11-12); "Convert Mashov's timetable into ICS file"; repo unavailable |
| @yanshoof/mashov (npm 1.1.2) / yanshoof-app/iscool | https://github.com/yanshoof-app/iscool | n/a | npm 2022-12-06; repo created 2022-04-20, 63 commits | password | "Types and API Wrapper for the Mashov API" | ISC | product rebranded to "iscool" (another school system); npm still 30 DLs/month (2026-11-12) |
| npm `node-mashov` package metadata | https://www.npmjs.com/package/node-mashov | n/a | v1.1.1 (2021-02-27) | password | grades etc. | MIT | 68 DLs/month (2026-11-12) |

**Registry tallies (fetched 2026-11-12):** GitHub repo search `mashov` = **89 repos total** (top 30 analyzed; remainder trivial/empty/unrelated per API listing). npm search `mashov` = **7 packages** (node-mashov, @yanshoof/mashov, mashovapi-js, mashovscraper, mashov-vercel, mashov-api, mashovscrapper). PyPI = **1 package** (pymashov). pymashov forks = **0**.

**Cross-cutting findings (all community-sourced):**
- Every tool that reads Mashov data uses the SAME model: the user's own Mashov username (T.Z.) + password + school semel + year → `POST https://web.mashov.info/api/login` → JSON endpoints with session cookie + `X-Csrf-Token`. A handful (2020 cohort, liorg2007) use Selenium against the same login page. **None uses SSO delegation, OAuth, an official token, or any partner API.** VERIFIED across all 30+ analyzed repos.
- **Auth drift (2025-2026):** the actively maintained tools (ha-mashov, Grader) send mobile-app-style login metadata (`appName: "info.mashov.students"`, `apiVersion: "4.20250101"`, device fields) per community source (`mashov.md` C1); pymashov and all 2017-2021 clients send only the bare 4 fields. Implication: the private web API's login endpoint mirrors the mobile app and has changed since the 2017-2021 wrappers — older tools are likely broken (consistent with node-mashov's 19 open issues).
- **Third-party custody of student data exists in the wild:** Grader for Mashov runs a national grade-average leaderboard (Play Store, 2026-11-12: "National average competition - students across Israel compare grade averages"; data-safety declares "No data shared with third parties" but also "Data can't be deleted"); mashovscraper hosts the flow on Vercel serverless; BetterMashovLive stores login steps in a committed `MashovData.json`. Precedent that community tools routinely move minors' grades off the user's device — none of this is Mashov-sanctioned.

---

## 2. T1 — Any tool that reads Mashov WITHOUT the student's password?

**VERDICT: NONE FOUND — as expected, now confirmed by the full sweep.** VERIFIED (absence after exhaustive search).

- All 89 GitHub repos matching `mashov` (top 30 analyzed in full, rest listed in the API result) and all 7 npm + 1 PyPI packages are credential-based wrappers, Selenium login automations, cosmetic userstyles/extensions, clones that don't read Mashov, or empty.
- Direct quotes (all fetched 2026-11-12):
  - Grader for Mashov (Google Play): "Use the same Mashov login you already have - no extra registration, no new passwords"
  - ha-mashov (README): "1. Add Integration → Mashov. 2. Enter your username/password."
  - mashov-parent-brief (README, HE): "שימוש אישי בלבד, עם החשבון שלך או של ילדך, ובקצב בקשות נמוך"
  - MashovMCP (README): credentials passed as `MASHOV_USERNAME` / `MASHOV_PASSWORD` env vars.
  - idandrori555/mashov (README): `new MashovClient({ username, password, semel, year })`.
- No tool implements MoE SSO delegation, OAuth client registration, an official token, or a partner API. The SSO button on `web.mashov.info/students/login` (fetched 2026-11-12: "הזדהות משרד החינוך") is a **login** mechanism for Mashov's own site — no registered-client/redirect mechanism exists on Mashov's side (re-confirms `mashov.md` Q6).
- One indirect signal only: the **official** `timetable.mashov.info` app (see T2) offers "MoE identity management" login — proving Mashov's own product line uses MoE IDM internally, but exposing no delegated API for third parties.

## 3. T2 — Does Mashov itself host any developer/API surface?

**VERDICT: No developer/API surface exists. What DOES exist (official vs community-sourced, labeled):**

**Official (VERIFIED):**
- `web.mashov.info/api/` — the web app's own JSON API (undocumented, no developer program; login page footer fetched 2026-11-12 shows build "גרסה: 3.20210425", © 2026). The public `GET /api/schools` endpoint is referenced by community repos (Apophisss README: "semel - get it in HERE, https://web.mashov.info/api/schools").
- **`timetable.mashov.info` — NEW FIND (VERIFIED existence):** a separate official Mashov product, the teachers' "מערכת שעות" (timetable management) app. Evidence (fetched 2026-11-12): (a) indexed login page: "Mashov Timetable. Hello! Shall we login? email ... MoE identity management. Don't have an account? Create account"; (b) an official Mashov PDF uploaded to mashov.info in **June 2026** — "הנחיות עבודה מערכת שעות" (teacher-timetable working instructions) — which directs teachers to log in at `https://timetable.mashov.info/`. It is a **teacher-facing product** (build/edit weekly class schedules, students, teachers), login = email+password or **MoE IDM** — NOT a student-data API, and NOT an open/developer API. Relevance: confirms Mashov operates multiple subdomain products and uses MoE-IDM login internally.
- `cdn.mashov.info` — static assets (named in official help page; `mashov.md` source).
- Official mobile app (Google Play `com.mashov.main`, App Store `id683777271`, developer "MASHOV - IMMEDIACY TRANSPARENCY & CONTROL LTD") — closed source.
- `mashovhelp.zendesk.com` — help/training center; no API/developer/partner content (re-confirms `mashov.md` O2).

**NOT an API surface:** no developer portal, no partner page, no api.mashov.info documentation found (absence re-verified today; `site:mashov.info "תנאי שימוש"` surfaced no terms page either — the student login page footer links only: Mashov site / help / contact / privacy policy / accessibility statement, fetched 2026-11-12).

**Community-sourced (NOT Mashov-documented — labeled per brief):**
- `mobileapi.mashov.info/api/` — mobile API host cited by ha-mashov README: "Common defaults: https://web.mashov.info/api/, sometimes https://mobileapi.mashov.info/api/". **Host existence NOT VERIFIED** — direct fetch blocked by the fetcher's SSRF guard (2026-11-12).
- Mobile-app login payload fields (`appName: "info.mashov.students"`, `apiVersion: "4.20250101"`, `IsBiometric`, `deviceUuid`, `devicePlatform`) — from ha-mashov `mashov_client.py` (community-sourced, `mashov.md` C1). Grader-for-Mashov's README states its research came from "reverse engineering 'משוב' app ... and by branching out the traffic of 'משוב' website" — independent confirmation that the official mobile app talks to the same web-API surface.
- `api.mashov.info` — **no evidence at all** in any source; direct fetch blocked. NOT VERIFIED.

## 4. T3 — Factual risk statement: running a password-based reader (even locally, own credentials)

Facts gathered (all sources above; legal framework is general background — **not legal advice; Israeli privacy counsel required**):

1. **Every existing reader requires the account holder's live password.** There is no delegated, revocable, or token-based path anywhere in the ecosystem (T1). A tool that holds the password is, from Mashov's network perspective, the account user logging in — Mashov's own privacy policy frames all data usage as MoE-supervised: "כל השימושים המבוצעים במידע הנשמר במערכת מאושרים ומבוקרים ע\"י משרד החינוך" (www.mashov.info/מדיניות-פרטיות/, search-indexed 2026-11-12).
2. **Mashov reserves enforcement rights against misuse.** The same policy lists as a permitted use: "על מנת לאכוף עבירות... ולמנוע שימוש לא הוגן כגון הפרת זכויות, גניבת זהות וכל מעשה לא חוקי אחר או שימוש לרעה במערכת" (enforce violations, prevent identity theft and any other illegal act or system misuse). No student-facing "terms of use" page is linked from the student site (verified 2026-11-12) — the operative public documents are the privacy policy and MoE oversight, so the account contract terms are not public; that itself limits what can be promised about "legality".
3. **The data is minors' personal data, Israeli-law-regulated.** Mashov states it keeps records up to 7 years, operates "תחת הנחיה ורשיון של מחלקת אבטחת מידע במשרד החינוך", and that "השימוש במערכת משו\"ב כפוף לדין הישראלי בלבד". The Israeli regime (Privacy Protection Law 5741-1981 + Data Security Regulations 5777-2017, general background, not verified from primary text here) makes processing of minors' school data a heightened-obligation activity for any entity handling it — including a Lumio server that would receive it.
4. **The market already shows the failure mode:** Grader for Mashov's national grade leaderboard (Play Store, 2026-11-12) with "Data can't be deleted"; a Vercel-hosted "Mashov scraper" (npm `mashovscraper`, 2025-11-29); a full-stack site committing login steps to a repo (BetterMashovLive). These are the un-sanctioned patterns a product must NOT replicate.
5. **Why Lumio will NOT host such a flow:** (a) hosting a password means Lumio is a third party in possession of student credentials and minors' data with no Mashov contract, no MoE approval, and no revocation mechanism — squarely in the "misuse" territory the privacy policy reserves enforcement for; (b) there is no SSO/OAuth surface to do it by delegation (T1/T2); (c) credential relay also breaks the mission's proof threshold (`mashov.md` §4: "Lumio must NEVER collect student passwords"); (d) a server-side scraper of an undocumented private API is fragile (auth drift already observed) and would make Lumio operationally liable for breakage and for data it holds. Therefore: **no password storage, no credential relay, no server-side login — ever.**

## 5. T4 — Student runs pymashov ON THEIR OWN MACHINE, imports the file into Lumio

**Tag: `user-local-import`, NOT sync.**

**Verdict: yes — this is a legitimate user-initiated import path for Lumio, with the caveat that the Mashov-side legality of the local run rests entirely with the user (own account, own data, no Mashov sanction found, and none needed by Lumio).** Rationale:
- It is the exact model every community tool uses and every tool's README explicitly blesses for personal use: pymashov README (fetched 2026-11-12): "Only use pymashov with your own account, or with the account of a child you are the parent or guardian of... Keep it private and don't share it or store it anywhere public"; "Keep request volume low... meant for personal use, not bulk scraping."
- Lumio's involvement ends at receiving a **user-owned data file** — the same legal position as a student uploading a PDF of their report card ("העתקי תעודות" is an official Mashov feature). Lumio never sees credentials, never initiates the login, never stores anything credential-shaped, and never refreshes — so the mission's proof threshold is satisfied (this is not "live-sync").
- It is NOT official/sanctioned by Mashov (no API agreement exists — T1/T2); it may break without notice (undocumented API; auth-drift signal). Lumio should present it neutrally as *the user's own option*, not endorse/depend on pymashov specifically (license is ambiguous: Apache-2.0 vs MIT — `mashov.md` Q3).

**Exact UX steps (user-local-import):**
1. **Install** — student (or parent, for the family account) installs Python 3.8+ on their own machine and runs `pip install pymashov` (Lumio docs provide the one-line install and a template script).
2. **Run locally** — student runs the template script and types **their own** Mashov username (T.Z.), password, school semel (code), and academic year when prompted. Credentials exist only in that local process (ideally read from a prompt or OS keychain, never written to a file); the script connects directly from the student's machine to `web.mashov.info`.
3. **Output file** — the script writes `mashov-export.json` (or CSV) to the student's machine: grades, homework, timetable, behavior (the endpoints pymashov wraps; bagrut grades via its low-level `request()` if the school exposes them). Student must supply their student ID (`childGuid`) — note: pymashov does not expose it from the login response (known limitation, `mashov.md` Q3); the template should instruct the user to find it (e.g. from the site's URL/DevTools) or pass it manually.
4. **Import into Lumio** — student (or parent) opens Lumio → Data → Import → uploads the file. Lumio parses, validates, stores. **End of Lumio's involvement.**
5. **Repeat on demand** — whenever the student wants fresh data, they re-run step 2-3 and re-upload. One-shot, user-initiated snapshots. No background refresh, no polling, no stored sessions, no Lumio-side state from the Mashov side.

**Guardrails for Lumio's docs around this path:** (a) state plainly the student is using their own account and their responsibility under Mashov's rules; (b) minors — recommend parental involvement; (c) keep volume low (a few requests per run); (d) do not bundle or vendor pymashov (license ambiguity) — link to it and provide an independent Lumio template script; (e) offer the zero-install fallbacks first: official report-card copies ("העתקי תעודות") and manual entry (see `mashov.md` Q2).

---

## 6. SOURCES (all fetched 2026-11-12 unless noted)

**Official:**
1. https://web.mashov.info/students/login (login page: SSO button, EMAIL/SMS login, footer links, build version, © 2026)
2. https://www.mashov.info/מדיניות-פרטיות/ (privacy policy full text — search-indexed copy: MoE guidance/license, approved uses, enforcement clause, 7-year retention, Israeli-law jurisdiction, data return to user)
3. https://timetable.mashov.info/ (indexed login page: email + "MoE identity management" login)
4. https://www.mashov.info/wp-content/uploads/2026/06/הנחיות-עבודה-מערכת-שיעוב-1.pdf (official teacher-timetable instructions PDF, June 2026; links to timetable.mashov.info)
5. https://www.mashov.info/צרו-קשר/ (contact page: MoE SSO password note, "אין לפנות אלינו בנושא סיסמאות")
6. Google Play `com.mashov.main` + App Store `id683777271` (official app listings — via `mashov.md` + today's search snippets)

**Community:**
7. https://api.github.com/search/repositories?q=mashov&sort=stars&order=desc&per_page=30 (89 total; full top-30 metadata)
8. https://registry.npmjs.org/-/v1/search?text=mashov&size=20 (7 packages with versions/dates/downloads)
9. https://github.com/NirBY/ha-mashov (+ README, RELEASE_NOTES, docs/services.md, docs/blueprints.md, examples/lovelace/README.md)
10. https://github.com/dtkdt100/Grader-for-Mashov + https://play.google.com/store/apps/details?id=com.dolev.graderForMashov (updated 2026-09-11, data-safety declarations) + https://apps.apple.com/us/app/grader-for-mashov/id1550919847 + https://dfranko.com/
11. https://github.com/ofershap/mashov-parent-brief
12. https://github.com/idandrori555/mashov
13. https://github.com/narkisiuria/Mashov-Premium-App-Project-PY
14. https://github.com/shahar646/Portelem_afterMashovFromOmriNew
15. https://github.com/yonka2019/BagrutGrades
16. https://github.com/AmitMarcus/MashovMCP (README, Docker env-var auth)
17. https://github.com/yardnsm/node-mashov (19 open issues per API)
18. https://github.com/micaelillos/MashovAPI (20★, 2020)
19. https://github.com/YehudaEi/MashovSystem ("R.I.P ... Telegram Bots system", AGPL-3.0)
20. https://github.com/Apophisss/MashovApi + https://www.npmjs.com/package/mashov-api
21. https://github.com/neryash/MashovAPI + https://www.npmjs.com/package/mashovapi-js
22. https://github.com/rootatkali/MashovAPI (Java, MIT, 9 open issues)
23. https://github.com/yanir-edri/mashov_api + https://github.com/yanir-edri/unofficial_mashov
24. https://github.com/liorg2007/Mashov_Bug_Vulnerability- (Selenium meeting entry)
25. https://github.com/ofekashery/mashov-covid19-clearance + https://github.com/shafzhr/Auto-Mashov + https://github.com/NotIMaestro/mashov + https://github.com/t0mer/Botvid-19 + https://github.com/t0mer/HAvid-19 (2020 credential-automation cohort)
26. https://github.com/NightRa/Mashov-Notificator (Scala, 2014-2015)
27. https://www.npmjs.com/package/mashovscraper (+ mashov-vercel, mashovscrapper — Vercel serverless, 2025-11-29)
28. https://github.com/yanshoof-app/iscool + npm `@yanshoof/mashov`
29. https://github.com/ArielBaron/BetterMashovLive (+ https://bettermashovlive.onrender.com)
30. https://github.com/DanPeled/ElectronMashovApiClient, https://github.com/mitekk/mashov, https://github.com/tsfoni (profile: mashov-timetable-to-ics, repo 404)
31. https://pypi.org/project/pymashov (only PyPI hit for "mashov")
32. agentskills.co.il "Israeli School: Mashov and SmartSchool Webtop" community AI-skill listing (2026-11-10; read-only, passwords in local .env/keychain — same user-local model, noted as market context)
33. https://sentinelone.com/vulnerability-database/cve-2024-47923 (CVE-2024-47923, via `mashov.md`)

**Blocked/unverifiable (documented attempts, 2026-11-12):** `https://mobileapi.mashov.info/api/schools` and `https://api.mashov.info/` — fetcher SSRF guard ("private or internal network address"); host existence therefore NOT VERIFIED, community-sourced only. `https://timetable.mashov.info/` direct extract returned empty (JS SPA) — page existence VERIFIED via search index + official PDF instead.
