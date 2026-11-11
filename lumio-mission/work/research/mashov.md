# Mashov (משו"ב) Provider Research — Lumio Mission

- **Date:** 2026-11-11 (all fetches performed this day)
- **Method:** Public web search + plain page fetches only (web_search / web_extract). No logins, no credentials, no CAPTCHAs. All fetched content treated as untrusted data.
- **Scope:** Mashov (operator: "משו"ב – מיידיות שקיפות ובקרה בע"מ", part of Priority Group since 2021) — official API/partner program, user-side exports, pymashov analysis, site/role split, external providers, SSO delegation feasibility, Deno/TS architecture note.
- **Companion research:** MoE (IDM/EduLogin) side is researched separately; this report covers Mashov-side documentation only.

---

## 1. Official-source findings

### O1. Operator & MoE relationship
- **VERIFIED** — Mashov "פעולה באישור משרד החינוך": the MoE e-catalog lists "משו"ב היא מערכת משלימת מנב"ס הפועלת באישור משרד החינוך" (Mashov complements Manbas and operates under MoE approval).
  Source: https://ecat.education.gov.il/mashov (fetched 2026-11-11).
- **VERIFIED** — Privacy policy: the company "פעולות תחת הנחיה ורשיון של מחלקת אבטחת מידע במשרד החינוך" (operates under the guidance and license of the MoE Information Security department); data uses are "מאושרים ומבוקרים ע"י משרד החינוך" (approved and supervised by the MoE); annual security audits by the MoE.
  Source: https://www.mashov.info/מדיניות-פרטיות/ (fetched 2026-11-11).
- **VERIFIED (news)** — Acquired by Priority (TA Associates) in Dec 2021 for ~NIS 50M (~$15.8M); ~1,700 schools, ~1M parents/students daily.
  Source: https://www.calcalistech.com/ctech/articles/0,7340,L-3924112,00.html (2021-12-05).
- **VERIFIED** — Login page footer: "by מקבוצת פריוריטי" (by Priority Group).
  Source: https://web.mashov.info/students/login (fetched 2026-11-11).

### O2. No official API / partner program found (negative result)
- **VERIFIED (absence after multiple searches)** — Searched (2026-11-11): "mashov official API partner program", "Mashov API רשמי משרד החינוך", "Mashov שותפים אינטגרציה API", "משו"ב API פתוח/שותפים/אינטגרציה", "mashov API developer integrations third party", "mobileapi.mashov.info", site-scoped searches on mashovhelp.zendesk.com for "ייצוא".
  - The official marketing site (https://www.mashov.info/) has **no** developer, API, partner-integration, or open-platform page. Site is school-facing: מורים, תלמידים והורים, טפסים, תעודות, יום הורים, אתר בית ספרי, שחרורים, קינדרבל. (fetched 2026-11-11)
  - The Zendesk help center (https://mashovhelp.zendesk.com) is a training center (הדרכה) for teachers/students/parents; FAQ category (fetched 2026-11-11) contains **no** API, developer, or partner content.
  - Contact page (https://www.mashov.info/צרו-קשר/, fetched 2026-11-11) offers sales contact ("להזמנת תוכנת משוב") and support only; no developer intake.
  - One low-authority AI/SEO site claims Mashov's API is "מוגבל" (limited) relative to Moodle/Canvas — **UNVERIFIED**, not usable as evidence: https://he.seokru.com/ai-solutions/education/ (no date).
- **VERIFIED (context)** — A government-tracked vulnerability exists for Mashov (information disclosure, unauthenticated), confirming Mashov exposes network endpoints but not that a public API program exists: CVE-2024-47923 "Mashov Information Disclosure Vulnerability", tracked by the Israeli Government CVE advisory program.
  Source: https://sentinelone.com/vulnerability-database/cve-2024-47923 (fetched 2026-11-11).
- **Verdict Q1: NO official API/partner program is published as of 2026-11-11.** Any integration is via the internal web app's own (undocumented) HTTP API. Approving party for data flows is the MoE InfoSec department (per privacy policy); a partnership inquiry would go to Mashov sales/support (support@mashov.info) and MoE approval would be required per their own policy language.

### O3. User-side data (what the official UI exposes)
- **VERIFIED** — Student/parent site features (official marketing page, fetched 2026-11-11): grades ("ציונים מבחנים, בחנים, מטלות, בגרות"), homework detail ("שיעורי בית פירוט שיעורי הבית שניתנו בשיעור"), behavior events, weekly timetable, exams/events board ("לוח מבחנים ואירועים"), mailbox, Moodle spaces, and — notably — **"העתקי תעודות לשליפה לפי הצורך בהמשך"** (report-card copies retrievable on demand later).
  Source: https://www.mashov.info/משוב-תלמידים/ .
- **VERIFIED** — Data visibility to students/parents is controlled by the school: "המידע שביה"ס חושף להורים ולתלמידים" (the info the school exposes to parents and students).
  Source: https://www.mashov.info/ (fetched 2026-11-11).
- **VERIFIED** — Teacher side has Excel export: "כל מסך הוא דוח דינמי הניתן למיון, סינון, חיפוש וייצוא לאקסל" (every screen is a dynamic report sortable, filterable, searchable, and exportable to Excel); bagrut submission grades export page exists at `web.mashov.info/teachers/main/admin/importExport/hagashaGradesExport`.
  Sources: https://www.mashov.info/משוב-מורים/ (fetched 2026-11-11); URL surfaced in search results (page itself is auth-gated; existence from URL only).
- **VERIFIED** — Privacy policy: "המערכת מאפשרת החזרת הנתונים בחזרה לספק (משרד/רשת החינוך) וכן למשתמש עצמו" (the system allows returning data to the provider (Ministry/network) and to the user themselves).
  Source: https://www.mashov.info/מדיניות-פרטיות/ (fetched 2026-11-11).

### O4. Push notifications instead of pull (student/parent)
- **VERIFIED** — Official help doc "התראות ומסרונים ממשו"ב": behavior notes and grade changes are pushed (push/SMS) to parents and students on schedule; bagrut grades are pushed when they arrive from the MoE. This is the official "get your data" mechanism for students/parents — one-shot push, not a feed.
  Source: https://mashovhelp.zendesk.com/hc/he/articles/360011140540 (fetched 2026-11-11).

---

## 2. Community-source findings (information sources only)

### C1. Unofficial client libraries (all credential-scrape the internal web API)
| Project | Lang | Status | Auth model |
|---|---|---|---|
| t0mer/pymashov (PyPI `pymashov` 0.0.2) | Python | created 2026-01-21; last code commit 2026-01-24; last commit (docs) 2026-09-29; 5★, 0 forks, 0 issues | username+password+semel+year → cookies+CSRF |
| NirBY/ha-mashov (Home Assistant, HACS) | Python | active; HA 2025.3+ | same, plus spoofed mobile-app login payload (`appName: "info.mashov.students"`, `apiVersion: "4.20250101"`) |
| yardnsm/node-mashov | Node.js | created 2017, 43 commits, 13★; no recent activity visible | same |
| Apophisss/MashovApi (npm `mashov-api` 1.0.0) | Node.js | published ~2021, marked "abandoned", 0 weekly downloads | same |
| neryash/MashovAPI (npm `mashovapi-js` 1.0.6) | Node.js | published ~5 years ago, 1 weekly download | same |
| micaelillos/MashovAPI (2020) | Python+Node | abandoned | same |
| AmitMarcus/MashovMCP | Python (MCP server) | recent; wraps same endpoints | same |

Sources: GitHub repo pages + npm pages, all fetched 2026-11-11 (search results with repo metadata).

- **VERIFIED** — Multiple independent community projects confirm the working model: log in with student/parent username (T.Z.) + password + school code (semel) + school year to `https://web.mashov.info/api/...`, then call JSON endpoints with session cookie + CSRF header.
- **VERIFIED** — A mobile API host is referenced by community projects: `https://mobileapi.mashov.info/api/` ("Common defaults: https://web.mashov.info/api/, sometimes https://mobileapi.mashov.info/api/" — ha-mashov README, fetched 2026-11-11). Host existence itself **NOT VERIFIED** by direct fetch (no fetch performed).
- **VERIFIED (community, auth drift signal)** — ha-mashov's login payload sends app metadata fields (`IsBiometric`, `appName: "info.mashov.students"`, `apiVersion: "4.20250101"`, `deviceUuid`, `devicePlatform`...) while pymashov sends only `username/password/semel/year`. This suggests Mashov's login endpoint now mirrors its mobile app API and may have changed since the simple 2017–2021-era clients. Sources: https://raw.githubusercontent.com/NirBY/ha-mashov/main/custom_components/mashov/mashov_client.py and https://raw.githubusercontent.com/t0mer/pymashov/main/mashov/client.py (both fetched 2026-11-11).
- **UNLIKELY (as of today)** — that pymashov's minimal login payload still succeeds without the app-metadata fields; cannot be verified without logging in (out of scope).
- **VERIFIED** — tsfoni/mashov-timetable-to-ics ("Convert Mashov's timetable into ICS file") appears in the author's GitHub profile but the repo URL now returns HTTP 404 — a community ICS converter existed; currently unavailable. Source: https://github.com/tsfoni (profile, fetched 2026-11-11); repo fetch 404 (2026-11-11).

### C2. MoE SSO (IDM) flow as documented by a school
- **VERIFIED (school-published, not Mashov-official)** — Moshenson school page documents the student SSO path: "תלמידים יכולים להיכנס גם בעזרת כפתור 'הזדהות משרד החינוך', שם תוכלו לבחור באפשרות SMS. מקלידים מספר ת.ז. ותקבלו הודעה לטלפון עם סיסמה חד פעמית" (students can also log in via the "Ministry of Education authentication" button, choosing the SMS option: enter T.Z. and receive a one-time password by SMS). Password reset for that SSO: `https://apps2.education.gov.il/EduLogin/SelfReset.aspx` (MoE EduLogin self-reset).
  Source: https://mosenson.org/passwords/ (fetched 2026-11-11).
- **VERIFIED** — The SSO button exists on both student and teacher login pages (page text: "הזדהות משרד החינוך"), plus EMAIL and SMS one-time-login options.
  Sources: https://web.mashov.info/students/login and https://web.mashov.info/teachers/login (both fetched 2026-11-11).

---

## 3. Question answers

### Q1 — Official API / partner program?
**VERIFIED: none published.** After 6+ targeted searches (EN + HE) across the official site, help center, MoE catalog, press and GitHub: Mashov publishes no API docs, no developer portal, no partner program, no authorized third-party integration channel. The only MoE-facing data flows described officially are internal (bagrut grades and learning-group reports flow Mashov→MoE). Privacy policy states all data usage is approved/supervised by the MoE and audits happen annually — so any partner API would need MoE involvement, but no such program is documented.
**What it would take (inferred, UNVERIFIED):** sales contact via https://www.mashov.info/צרו-קשר/ or support@mashov.info (contact email per Google Play listing, fetched 2026-11-11), followed by MoE InfoSec approval per their own policy language.

### Q2 — User-side official exports?
**VERIFIED (partial):**
- Students/parents: **no CSV/Excel/ICS export documented anywhere** in official marketing or the Zendesk training center. The documented self-service data path is (a) on-screen viewing (grades, homework, timetable, events), (b) push notifications, and (c) **"העתקי תעודות"** — report-card copies retrievable in-app/on demand. That is a one-shot document (report card), not a refreshable feed, and it covers grades only (not homework/events/ICS).
- Teachers/staff: **Excel export is a core documented feature** (all report screens exportable; bagrut-grade export admin page exists).
- **No refreshable feed of any kind** is documented for students. **Verdict: one-shot export (report cards) for students; rich Excel export for teachers only. NOT VERIFIED that homework/exams/events export to CSV/ICS exists for students — no documentation found.**

### Q3 — pymashov analysis (source-level, not executed)
Tag: **`direct_credentials_only`** (no SSO/OAuth/IDM support whatsoever).

- **Methods (from `mashov/client.py`, fetched 2026-11-11):** `login()`, `ensure_logged_in()`, `close()`, `get_grades(student_id)`, `get_timetable(student_id)`, `get_homework(student_id)`, `get_behavior(student_id)`, `get_conversations(skip=, take=)` (mail inbox), `get_schools()` (public), low-level `request()` / `public_request()` for arbitrary endpoints.
- **Required params:** `username` (usually T.Z.), `password`, `semel` (school code), `year` (academic year, default string "2026"), optional `base_url` (default `https://web.mashov.info`), `timeout` (20s), `auto_login` (True).
- **Auth mechanics (from source):**
  1. `POST /api/login` with JSON `{username, password, semel, year}`.
  2. Success requires `x-csrf-token` **response header** + session cookies (e.g. `MashovAuthToken`, `Csrf-Token`); otherwise `MashovLoginError`.
  3. Every authenticated request sends `X-Csrf-Token` + `Cookie` headers (manual re-attachment, not a browser).
  4. Session is **not refreshed automatically**; expiry → re-login.
  5. **No OAuth, no IDM/EduLogin, no 2FA**: README states explicitly "Two-factor authentication is not supported: the library only performs the plain username and password login."
- **Documented endpoints table (README):** `/api/login` (POST), `/api/students/{id}/grades`, `/api/students/{id}/timetable`, `/api/students/{id}/homework`, `/api/students/{id}/behave`, `/api/mail/inbox/conversations`, `/api/schools` (public).
- **Stated limitations (from README):** unofficial, talks to "the same web API that the Mashov web app uses, which is undocumented and can change without notice"; no test suite; session not refreshed; **student ID is NOT obtainable from the library** ("the library does not provide a way to look up the student ID... from the login response, which the library currently discards"); response field names in examples are "illustrative only"; multiple unverified details left as `<!-- TODO: verify ... -->` comments in the README itself (year semantics, student-ID source, license mismatch).
- **License:** LICENSE file is **Apache-2.0** (GitHub repo metadata, fetched 2026-11-11) but setup.py/PyPI declares **MIT** — the README itself flags this contradiction (`"TODO: verify license: LICENSE is Apache 2.0, but setup.py (and therefore PyPI) declares MIT"`). Treat as ambiguous; do not rely on it for a product dependency without resolving.
- **Age/maintenance:** repo created **2026-01-21**; PyPI 0.0.1 = 2026-01-23, 0.0.2 = 2026-01-24; last code commit **2026-01-24** ("Added logging and error handling"); last commit overall **2026-09-29** (docs-only "refresh README and repo metadata (#1)"). Single author (Tomer Klein). 5 stars, 0 forks, 0 open issues. Sources: GitHub repo metadata + `api.github.com/repos/t0mer/pymashov/commits` (both fetched 2026-11-11).
- **Did site auth change since?** **UNVERIFIED but plausible signal:** a newer community integration (ha-mashov) spoofs the Mashov mobile app login payload (appName/apiVersion/device fields, apiVersion "4.20250101") while pymashov sends the bare 4-field payload. If Mashov now enforces app metadata at login, pymashov's plain login would fail. Cannot confirm without a live login (out of scope, and forbidden for Lumio anyway).
- **Q3 verdict:** `direct_credentials_only`. Theoretical option for a *user's own local* tool only. **Lumio must NEVER collect student passwords** — this rules out pymashov-style server-side credential storage entirely.

### Q4 — Student vs parents vs staff sites
**VERIFIED** (login pages + marketing + help center, fetched 2026-11-11):
- **Students & parents share ONE site:** `https://web.mashov.info/students/` titled "משו"ב תלמידים והורים" (Students and Parents). Login = school + username/T.Z. + year, or MoE SSO, or EMAIL/SMS one-time login. There is **no separate parents URL**. A parent account links multiple children; help articles cover "איך אני עובר לילד בביה"ס אחר?" (switching child/school) and "אני הורה לשני ילדים או יותר" (parent with multiple children) in the student/parent FAQ category.
- **Staff/teachers:** separate site `https://web.mashov.info/teachers/` ("משו"ב מורים"), same SSO button, plus role-based admin (reports, Excel export, bagrut-grade import/export, form/survey management).
- **Permissions:** students see their own grades/homework/behavior/timetable/events/mail; parents see what the school exposes ("המידע שביה"ס חושף להורים ולתלמידים"); teachers/staff see and export class-wide data. Bagrut grades arrive from the MoE and are pushed to student+parents.
- **MoE-side portals (separate from Mashov, official):** `students.education.gov.il` (student portal — bagrut grades/exams) and `parents.education.gov.il` (parents) are listed as distinct platforms in community tooling and MoE site. Relevance: bagrut data officially lives in MoE portals; Mashov mirrors/pushes it. (Sources: booa.co.il aggregate search snippet listing "פורטל תלמידים - משרד החינוך students.education.gov.il", fetched 2026-11-11; Ecosyste.ms project listing `parents.education.gov.il`, fetched 2026-11-11 — both secondary; treat portal URLs as **VERIFIED by multiple secondary listings**, primary fetch not performed.)
- Older URL style seen in school docs: `https://web.mashov.info/students/#!/login` (hash-routing SPA) — Source: https://mosenson.org/passwords/ (fetched 2026-11-11).

### Q5 — External API providers offering legal delegation?
**VERIFIED: none found.** Searched (2026-11-11): npm registry (mashov-api, mashovapi-js, node-mashov, pymashov), GitHub (all Mashov API/MCP projects), "mashov API provider service", "Mashov שותפים", "Mashov API רשמי". Every hit is an **unofficial, community, credential-based** wrapper (all marked "not affiliated with Mashov"). None offers user-delegated authorization, none has an agreement with Mashov, none provides revocation semantics, and the maintained-looking ones are personal projects (ha-mashov for Home Assistant, MashovMCP). No commercial Mashov-data service exists in public search. **Verdict: unavailable — no delegated third-party access exists.**

### Q6 — Can the MoE SSO (IDM) button be turned into delegated API authorization for Lumio?
**Tag: `requires_ministry_registration`.**
- **VERIFIED (Mashov-side):** the SSO button is a *login* mechanism for the Mashov site itself (redirects to MoE EduLogin, supports SMS one-time code per school-documented flow). Mashov documents **no** registered-client, client-id, redirect-URI, or OAuth2 authorization-code mechanism on its side — no developer docs of any kind exist (see Q1).
- Therefore: **SSO login to Mashov does NOT grant API access to another app.** There is no Mashov-side delegated-authorization surface to hook into. If the MoE's IDM (EduLogin/IDM) ever offers third-party OAuth client registration, that is a **Ministry-side** capability — researched separately per mission split; nothing on Mashov's public docs indicates Mashov participates in it.
- **Conclusion:** NOT POSSIBLE from Mashov-side documentation as of 2026-11-11.

### Q7 — If an API did exist: calling it from a Deno/TypeScript server (no Python host)
Short architecture note:
1. **If Mashov ever ships an official API (assumed OAuth2):** Deno server (`Deno.serve` or Hono/Encore) stores per-user tokens in a DB/Keyv; flow = authorize (redirect to Mashov/MoE authorize URL with client_id+PKCE) → token callback → refresh-token job (`Deno.cron`) → data pulls via `fetch` with `Authorization: Bearer`. No Python needed; TypeScript client is trivial.
2. **If the only API stays the private web API (status quo):** technically callable from Deno with plain `fetch` — the protocol is plain HTTPS+JSON: `POST https://web.mashov.info/api/login` (JSON body; newer clients include mobile-app metadata fields), then `GET /api/students/{id}/grades|timetable|homework|behave` and `/api/mail/inbox/conversations` with `X-Csrf-Token` + `Cookie` headers (model: pymashov/ha-mashov, community-verified, **not** Mashov-documented). **But this requires holding the student's password — forbidden for Lumio** — and is undocumented/fragile (can change without notice; CVE-2024-47923 shows endpoint surface scrutiny by the state). It is a **theoretical option only**, and only ever inside the *user's own* browser context (e.g., a local/extension tool where the password never leaves the user's device), never on a Lumio server.
3. Recommended Lumio posture: build an **import-based MVP** (user pastes/imports report-card PDFs or data, or a future official feed) and design the data layer as provider-agnostic so an official API can be plugged in later without rework.

---

## 4. PROOF THRESHOLD (binding for this mission)

> A **live-sync** claim requires an endpoint/SDK with **explicit user authorization verified live**.
> pymashov-style **direct-credential access is a theoretical option only** and **Lumio must NEVER collect student passwords** (not from students, not from parents, not "temporarily").
> Consequently, all community client libraries (pymashov, node-mashov, mashov-api, mashovapi-js, ha-mashov, MashovMCP) are **reference material for endpoint names/flow only** — none of them establishes an authorized path for Lumio.

## 5. VERDICTS & RANKED PATHS

| Q | Verdict | Tag |
|---|---|---|
| Q1 | No official API/partner program published (negative result, 6+ searches) | VERIFIED (absence) |
| Q2 | Students: on-screen view + push + report-card copies only; no CSV/Excel/ICS documented; no refreshable feed. Teachers: full Excel export | VERIFIED |
| Q3 | pymashov: 7 data methods + low-level; username/password/semel/year + CSRF header + cookies; no 2FA/OAuth; Apache-2.0 vs MIT conflict; created 2026-01-21, last code 2026-01-24, last commit 2026-09-29 (docs); auth may have drifted (app-metadata login seen in newer clients) | **direct_credentials_only** |
| Q4 | One student+parents site (`/students/`), separate teachers site (`/teachers/`), school-controlled visibility, MoE portals hold bagrut data | VERIFIED |
| Q5 | No external provider offers legal delegated access to Mashov | VERIFIED (absence) |
| Q6 | SSO button is login-only; no registered-client/redirect mechanism documented on Mashov side | **requires_ministry_registration** |
| Q7 | Deno/TS can call plain HTTPS JSON APIs natively; official-OAuth path clean; private-web-API path possible only in user's own device context and is forbidden server-side | architecture note |

**Ranked paths for Lumio:**
1. **Official API / partner program** — does not exist today; the only forward path. Requires contact with Mashov (support@sashov.info → support@mashov.info) + MoE approval. Keep warm; no documentation to wait for.
2. **User-import (MVP now)** — students/parents export what officially exists (report-card copies, on-screen data) and manually import into Lumio (PDF/CSV/typed). Zero credential exposure.
3. **User-side local tool (optional, user's own device)** — a browser-extension/local helper (ha-mashov-style) where the user's own credentials never leave their device; export → import into Lumio. NOT a server sync; not "live-sync" per the proof threshold.
4. **Live server-side sync via Mashov** — **unavailable** (no official API; credential scraping is forbidden and undocumented).

**Exact next actions:**
1. **Contact Mashov commercial/innovation:** send inquiry via https://www.mashov.info/צרו-קשר/ (form: institution, contact) asking: (a) is there or planned any official API/partner integration for a student-learning app? (b) required agreement/security review; (c) escalation to MoE. Support email: **support@mashov.info** (per Google Play listing).
2. **MoE-side (separate track per mission):** ask the MoE InfoSec / digital-education unit whether IDM (EduLogin, apps2.education.gov.il) offers third-party OAuth client registration — tag `requires_ministry_registration`.
3. **Build Lumio import path now** (report-card PDF + manual CSV) behind a provider-agnostic data interface.
4. **Re-check quarterly:** mashov.info for a developer/API page, Zendesk help center for new categories, npm/PyPI for maintained wrappers; re-verify CVE/advisory posture before any third-party tooling decision.

---

## 6. Source index (all fetched 2026-11-11 unless noted)

Official:
1. https://www.mashov.info/ (marketing home)
2. https://www.mashov.info/משוב-תלמידים/ (student/parent features)
3. https://www.mashov.info/משוב-מורים/ (teacher features, Excel export claim)
4. https://www.mashov.info/מדיניות-פרטיות/ (privacy policy)
5. https://www.mashov.info/צרו-קשר/ (contact)
6. https://web.mashov.info/students/login (student login page, SSO button)
7. https://web.mashov.info/teachers/login (teacher login page, SSO button)
8. https://mashovhelp.zendesk.com/hc/he/categories/200792431-שאלות-נפוצות (FAQ category)
9. https://mashovhelp.zendesk.com/hc/he/articles/360011140540 (push notifications doc)
10. https://mashovhelp.zendesk.com/hc/he/articles/205022502 (how to view homework)
11. https://ecat.education.gov.il/mashov (MoE e-catalog entry)
12. https://www.calcalistech.com/ctech/articles/0,7340,L-3924112,00.html (Priority acquisition, 2021-12-05)
13. https://play.google.com/store/apps/details?id=com.mashov.main (app listing, support email, updated 2026-10-11)
14. https://apps.apple.com/il/app/id683777271 (iOS app listing, provider name)

Community:
15. https://github.com/t0mer/pymashov + raw README.md + raw mashov/client.py + api.github.com commits (Q3)
16. https://pypi.org/project/pymashov/ (versions 0.0.1/0.0.2 dates)
17. https://github.com/NirBY/ha-mashov + raw mashov_client.py (mobile-app login payload, mobileapi host)
18. https://github.com/yardnsm/node-mashov (oldest Node wrapper, 2017)
19. https://github.com/Apophisss/MashovApi + npm mashov-api (abandoned)
20. https://github.com/neryash/MashovAPI + npm mashovapi-js (abandoned)
21. https://github.com/AmitMarcus/MashovMCP (MCP wrapper)
22. https://github.com/tsfoni (profile: mashov-timetable-to-ics; repo now 404)
23. https://mosenson.org/passwords/ (school-published SSO/EduLogin instructions)
24. https://sentinelone.com/vulnerability-database/cve-2024-47923 (CVE record)
25. https://allcloud.kernandlead.com/case_studies/mashov (AWS infra case study — context only)
26. https://he.seokru.com/ai-solutions/education/ (low-authority "limited API" claim — UNVERIFIED)
