# PeTeL (פטל) Provider Research — Lumio Mission

- Date: 2026-11-11 · Method: read-only web search + plain GET (no login, no webservice probing)
- Verdict tags: **VERIFIED** (official source) / **NOT VERIFIED** (no evidence found) / **UNLIKELY** (evidence against)
- Source classes: [O] = official (Weizmann / PeTeL / Moodle project) · [C] = community

---

## Q1. Which PeTeL environment serves Israeli high-school students? Is it Moodle?

**VERIFIED [O]** — The in-app link `https://stweizmann.proj.ac.il/petel/` is the **MiZem PeTeL project portal (WordPress marketing site)**, title "פטל - אודות - מיזם PeTeL" (accessed 2026-11-11). It is not itself the LMS. It links out to six live per-subject environments on `petel.stweizmann.org.il`:

| Subject | Level | URL |
|---|---|---|
| Physics | High school | https://petel.stweizmann.org.il/physics |
| Chemistry | High school | https://petel.stweizmann.org.il/chemistry |
| Biology | High school | https://petel.stweizmann.org.il/biology |
| Math | JHS + HS | https://petel.stweizmann.org.il/math |
| Computer Science | HS | https://petel.stweizmann.org.il/computerscience |
| Science & Technology | JHS | https://petel.stweizmann.org.il/sciences |

Source: the portal's own link list (accessed 2026-11-11) + Terms of Use, which enumerates "the addresses … PeTeL Physics … PeTeL Chemistry … PeTeL Biology … PeTeL Mathematics … Computer Sciences … Science & Technology for JHS" — https://petel.stweizmann.org.il/chemistry/theme/petel/docs/en/petel_policy.html [O]

**VERIFIED [O]** — Moodle base platform, three independent official confirmations:
1. Terms of Use: "The System was built based on a Moodle … environment (a free learning management system distributed under the GPL v+3) and it is operated by the Department." — petel_policy.html above [O]
2. Project portal: "The PeTeL environment is created in the Moodle platform …" — https://stweizmann.proj.ac.il/petel/en-petel_about [O]
3. English about page: "built on the widely used Moodle system" — https://stweizmann.proj.ac.il/petel/en/about [O]

**VERIFIED [O]** — Live Moodle identity (plain GET evidence):
- `https://petel.stweizmann.org.il/physics/login/forgot_password.php` returned Moodle's stock password-reset page, site name **"מיזם פטל - פיזיקה | הסביבה שלי"** (PeTeL – Physics | My Environment), with "שחזור סיסמא", trilingual switcher, and a back-link to `/physics/login/index.php`. Theme dir `theme/petel/…` in the page's doc links confirms Moodle filesystem layout. (accessed 2026-11-11) [O]
- Plain-GET notes: `stweizmann.proj.ac.il/petel/login/index.php` → HTTP 403 (WordPress site, no Moodle there); `petel.stweizmann.org.il/physics/` → 301 (CloudFront); `petel.stweizmann.org.il/physics/login/index.php` → 404 via this fetcher (likely redirect/bot handling) — but the indexed forgot_password page proves the Moodle login tree exists at `/physics/login/index.php`.

**Version — UNLIKELY-to-be-old, exact version NOT VERIFIED.** The vendor's own GitHub org (PeTeL-Weizmann, "Maintained by Weizmann Institute — PeTeL") repo `moodle-local_teamwork` has default branch `moodle_45`, a table row "Moodle 4.4+ (PeTeL m45) … PHP 8.3+", and commits "Update code to support Moodle 4.5" (2025-12-22) and "Update readme and changelog" (2026-06-18). https://github.com/PeTeL-Weizmann/moodle-local_teamwork [O] → PeTeL's current build targets **Moodle 4.5**, but the live instances' exact running version was not observable (no login allowed) — tag `version_inferred`.

Target population: Terms of Use: "intended for use by teachers in said fields and also by their students in middle schools and high schools in Israel (contingent upon registration…)" [O]. Auth: national unified authentication (portal: "אפשר להיכנס אליה באמצעות מנגנון הזדהות אחידה" = Ministry of Education unified login) + registration keys (Hebrew guide: "תלמידים נרשמים לקורס באמצעות מפתח רישום", updated 2022-01-24 — https://stweizmann.proj.ac.il/petel/instructions/studentsselfenroll/) [O].

---

## Q2. Moodle Web Services — what a consumer needs (OFFICIAL docs) + the hard fact

**VERIFIED [O]** — From official Moodle docs (docs.moodle.org "Using web services" for Moodle 5.0; moodledev.io "External Services" subsystem):
- **Enabled by admin, off by default**: "Access Administration > Site administration > Advanced features — Check 'Enable web services'… Note: For security reasons, web services should only be enabled if you intend to make use of it." — https://docs.moodle.org/500/en/Using_web_services (accessed 2026-11-11) [O]
- **Protocol must be enabled**: "Enable the protocols (SOAP, REST, AMF, …) as required" under Site admin > Server > Web services > Manage protocols [O]. REST endpoint URL format: `https://<site>/webservice/rest/server.php` (https://supportus.moodle.com/support/solutions/articles/80001016973…, official Moodle US support, accessed 2026-11-11) [O]
- **Auth**: token-based — "Each user will have a specific and unique security key (also known as a 'token') to access the service." Users generate it (needs `moodle/webservice:createtoken`) or an admin creates it (Manage tokens); tokens support **IP restriction** and **Valid until** [O]. OAuth2 also exists as a protocol (moodledev.io external subsystem; not expanded here).
- **Capabilities + external services**: an **External Service** is a named bundle of API functions ("so you can enable only the specific functions that you need to expose"); optionally "Authorised users only" and a "Required capability"; each function carries its own required capabilities (e.g. `webservice/rest:use` plus per-function caps) [O].
- **Formats**: `moodlewsrestformat=json` (REST returns JSON/PHP/serialized per requested format) [O/C: solin.co guide mirrors docs].
- Security model: "A token is always linked to a Moodle user… stored in `external_tokens` with `tokentype`, `contextid`, `iprestriction`, `validuntil`." — https://docs.moodle.org/dev/External_services_security [O]
- moodledev.io (v6.0 main): "Moodle has a full-featured Web Service framework… Moodle uses these web services internally for: AJAX interactions… and the official Moodle Mobile App." — https://moodledev.io/docs/apis/subsystems/external [O]

**HARD FACT — requires_admin**: Whether `webservice/rest/server.php` is enabled, which protocols are on, which external services exist, and whether a student may get a token are **site-administrator decisions made in PeTeL's admin UI; none of it is observable from outside** (web services are disabled by default; a disabled endpoint returns an error, not a catalog). No PeTeL page, terms doc, help guide, or GitHub repo mentions enabling web services. → **NOT VERIFIED for PeTeL (no public evidence either way); tag `requires_admin`.**
- Side signal: marketing says "access PeTeL seamlessly from laptops, smartphones, and tablets" (portal [O]) — responsive web, not proof of the official Moodle Mobile App (which would need the `moodle_mobile_app` service enabled). UNLIKELY-to-be-decisive either way.

---

## Q3. Any PeTeL-official documented endpoint or program for external consumers (after consent + role)?

**NOT VERIFIED (searched, none found)** — i.e., **no documented public API, feed, export program, or third-party integration exists** in any official PeTeL/Weizmann source examined. Blocker documented by sources searched:

| Source searched | Result |
|---|---|
| `site:petel.stweizmann.org.il` (search index) | Only: home, terms of use, privacy policy, accessibility statement, login pages. **No API/docs/web-service pages.** [O] |
| Terms of Use (EN+HE) + Privacy Policy — petel.stweizmann.org.il/…/theme/petel/docs/… | Mentions Moodle base, data processed ("name, username, password, class and exercise participation details, scores, comments…"), contact: **petel@weizmann.ac.il, fax 972-8-9344115, 234 Herzl St, Rehovot 76100**. No API/export/LTI mention. [O] |
| Project portal support section — https://stweizmann.proj.ac.il/petel/support/ ("תדריכים 2024") | Teacher-facing how-tos: hidden teaching units, scientific keyboard in question types, course tabs (למידה/עתידי/ארכיון), student self-enrollment with registration key. **No student data export, no ICS, no API.** [O] |
| Portal contact form | Roles: מורה / תלמיד (teacher/student) — the only official intake channel found. [O] |
| Weizmann Dept. of Science Teaching pages (stwww1.weizmann.ac.il/petel, weizmann.ac.il/ScienceTeaching) | Marketing + research project pages; LMS described academically; no integration docs. [O] |
| Vendor GitHub org `PeTeL-Weizmann` (8 repos) | Moodle plugins: question types (aitext, desmos, molecules), H5P RTL, teamwork, quiz summary option. **No LTI tool, no xAPI logstore, no webservice documentation, no mobile-app config.** [O] |

Verdict: the only official "interfaces" are the web UI itself, the contact email/form, and (per terms) teacher/school registration. **Any consumer access path requires a conversation with Weizmann (see Q7).**

---

## Q4. Moodle calendar: can a logged-in USER share/subscribe a personal calendar as ICS?

**VERIFIED [O]** — Core feature, documented in official docs (docs.moodle.org "Using Calendar", Moodle 5.0, accessed 2026-11-11):
- "Moodle allows users to export calendars… The Moodle export process creates an ics file. There are two ways… creating an ics file for immediate downloading… **or creating a url link that will create a defined calendar from a link without actually logging into the site.**" [O]
- Two UI paths at calendar bottom: **"iCal" quick link** (all events, no selection: "you cannot select individual items… all events will be included") and **"Export calendar"** with options: events = "All events" or "Events related to courses"; time = "This week / This month / Recent and next 60 days / custom range"; then **"Get calendar URL"** produces a shareable URL [O].
- **Events included**: the URL is user-relative — "The calendar will be relative to the Moodle user… if the user who generates the URL is enrolled in several courses, it is this information that will appear… There is no way (at this time) to generate a URL that only applies to one course." [O]. Event types in the calendar: User / Group / Course / Site events (docs, "Adding an event" section) [O]. Assignment due dates and quiz times appear on the calendar automatically ([C] UCL Moodle guide: "automatically draw in scheduled dates, times and deadlines from activities like the Assignment and Quiz"; consistent with core behavior).
- **URL pattern + embedded secret**: official docs example (docs.moodle.org, 2.3-era page still canonical): `…/calendar/export_execute.php?preset_what=courses&preset_time=recentupcoming&username=teacher&authtoken=35b0202e4f27…` [O]. The token is a per-user secret hash: core code computes `authtoken = sha1($USER->username . $USER->password . $CFG->calendar_exportsalt)` (moodle/moodle `calendar/export.php`, MDL-17203 [O, official repo]). So **yes, a secret token is embedded in the URL** (plus the username in plaintext).
- **Revocation**: no per-URL "revoke" button is documented for calendar export. Token validity follows (a) the user's password and (b) the site-wide admin salt — "all current tokens are invalidated if you change this hash salt" (moodle/moodle commit b20c631, official repo [O]). Moodle 3.10+ also exposes the token as an external function: `core_calendar\external\export\token` — "Return the auth token required for exporting a calendar" (phpdoc.moodledev.io/4.5, official dev docs [O]).
- **Privacy risk**: the URL works without login ⇒ **anyone holding the URL can read that user's calendar** (events, course names, due dates). There is **no per-user "share with person X" mechanism** — the URL *is* the share, and revocation requires a password change (self) or the admin rotating the calendar-export salt (invalidates *everyone's* export URLs — Moodle's own salt help text [O]). Treat a shared calendar URL like a credential.
- **PeTeL availability — UNVERIFIED, tag `moodle_version_dependent`**: export is core in all recent Moodle incl. 4.5 (target version, Q1), **but** the admin can switch it off (`enablecalendarexport` admin checkbox, visible in official moodle/moodle upgrade code [O]). No PeTeL doc confirms it's on. A student can check in the UI (Calendar block → Export calendar / iCal link at calendar bottom).

---

## Q5. Gradebook / assignments / quizzes: what can a student see & export from the PeTeL UI?

**VERIFIED [O]** — What a student sees (Moodle core, standard in any 4.x/5.0 install incl. PeTeL):
- Per-course **User report** = the student's own gradebook: "This is also what the student sees when they click the grades link in the nav drawer." (moodle.com gradebook explainer, official vendor, accessed 2026-11-11) [O]
- Per-activity grade + teacher feedback on the assignment/quiz pages (core behavior; student guides, e.g. CCA: "Your grade will appear on the page, along with any feedback provided by your instructor" [C]).
- Students can download **their own submission files** (core assignment activity behavior [C/O core docs]).
- PeTeL marketing: "Students will find all their materials, feedback, and grades in one easy-to-navigate space." (https://stweizmann.proj.ac.il/petel/en/about [O]) and "Digital Lab Reports and Portfolios … store all evaluated reports in a centralized digital portfolio" (https://stwww1.weizmann.ac.il/petel/en/about [O]). Privacy policy lists "scores" among retained data [O].

**NOT VERIFIED / UNLIKELY** — Student-side export:
- Official docs: **"Grade export is NOT intended for students."** — https://docs.moodle.org/500/en/Grade_export (export to Excel/ODS/Text/XML is a teacher/admin function) [O].
- "Grade publishing" (grades via URL + user key) is "intended for administrators only, due to the security implications. Grade publishing is disabled by default." [O] → even that URL-based path is admin-gated and almost certainly off on PeTeL (no evidence).
- No PeTeL help/FAQ/forum document any student print/export feature (support section checked, Q3) [O].
- Practical residual for a student: browser **print/save-as-PDF** of the grades page, copy-paste, and downloading own submission files — no structured export. Tag `manual_only`.

---

## Q6. LTI / xAPI on PeTeL?

**NOT VERIFIED — tag `not_verified_official_only`.**
- No LTI or xAPI statement in any PeTeL official source (terms, support, Weizmann pages) [O] — none found.
- Vendor's public GitHub org contains **no LTI plugin and no xAPI logstore** among its 8 repos (list: molecules, ml-apps, moodle-qtype_aitext, moodle-mod_hvp, moodle-tiny_embedhtml, moodle-local_teamwork, moodle-local_quiz_summary_option, redmine_mermaid, ai-studio-apps, lovable-apps) [O].
- Context from official Moodle docs (what would be required, not what PeTeL has):
  - xAPI: "The final objective of Moodle xAPI library is NOT to implement a full LRS inside Moodle but to provide an easy way to handle xAPI statements… within any plugin that needs it." — https://moodledev.io/docs/5.0/apis/subsystems/xapi [O]. So even where Moodle sites emit xAPI, it's via a plugin (e.g. marketplace "Logstore xAPI", [C] 802 sites) pointed at an *external* LRS.
  - LTI: Moodle core is an LTI *consumer* (teachers add third-party tools to courses); nothing in PeTeL sources indicates any LTI tool is configured.
- **Why an LRS does not imply open read access**: xAPI LRS endpoints are credential-protected (API key/secret auth; e.g. plugin docs: "API Key… API Secret… only basic authentication is supported" [C] frumbert/xapiactivity; same in ADLNET cmi5launch [C/O ADLNET]). Statements stored in an LRS are readable only by holders of that LRS's credentials — a third party without them cannot read. Additionally, if no xAPI plugin is installed on PeTeL (strongly suggested by the repo list), **no statements exist to read at all**.

---

## Q7. Ranked paths + exact next actions

| # | Path | Status | Rationale (evidence) |
|---|---|---|---|
| 1 | **Official API (Moodle web services/REST)** | **requires_admin** — NOT VERIFIED | Only structured, complete path (grades, assignments, calendar via `core_*` functions). Web services off by default, admin-created external service + token, all admin-gated (docs.moodle.org/500/en/Using_web_services [O]). No public PeTeL evidence it's on. |
| 2 | **Calendar ICS, user-shared URL** | **Plausible, tag `moodle_version_dependent`** — feature is core to Moodle 4.5 (PeTeL's inferred version, vendor repo [O]); docs confirm per-user URL with embedded authtoken, works without login, includes course events + assignment/quiz deadlines; admin *can* disable export (enablecalendarexport [O]) — so verify in-UI first. |
| 3 | **User import (manual copy-paste / print-PDF / download own submissions)** | **Available now**, no Weizmann consent needed, but manual, low-fidelity, per-activity; no structured export in core student UI ("Grade export is NOT intended for students" [O]). |
| 4 | **Programmatic access without admin (LTI/xAPI/LRS/grade publishing)** | **Unavailable** — no evidence of any such capability on PeTeL (Q3/Q6); grade publishing "disabled by default" [O]. |

**Exact next action (path #1, primary):**
- **Who**: PeTeL support, Department of Science Teaching, Weizmann Institute — **petel@weizmann.ac.il** (contact form on stweizmann.proj.ac.il/petel/ also accepts role "תלמיד/student"; fax 972-8-9344115; 234 Herzl St, Rehovot 76100 — all from official terms of use [O]).
- **What to request** (per student, with parental/school consent framing):
  1. Whether Moodle web services are enabled on the relevant subject environment (e.g. `…/webservice/rest/server.php`), and if not, whether they can be enabled for authorized use.
  2. Creation of a scoped **external service** exposing the minimum functions for the student's data: `core_user_get_user`, `core_course_get_courses`, `core_course_get_contents`, `core_calendar_get_events` (or the calendar export token), `gradereport_user_get_grade_items` / `core_grades_get_grades`, `mod_assign_get_grades` — with the student's own token, **IP restriction + "valid until"** (both supported per official docs [O]).
  3. Alternative if API is refused: confirmation that **calendar export is enabled** so the student can use the UI-generated ICS URL (Q4) — the only self-service structured export.
  4. Ask for their **data-protection contact** re: the privacy policy's processing of "scores, class and exercise participation details" (petel_privacy_policy.html [O]) — useful for the consent/legitimacy framing of the request.

---

## Source register

**Official [O]**
1. https://stweizmann.proj.ac.il/petel/ — portal; title "פטל - אודות - מיזם PeTeL"; per-subject login links; unified MoE auth. (accessed 2026-11-11)
2. https://petel.stweizmann.org.il/chemistry/theme/petel/docs/en/petel_policy.html — Terms of Use: Moodle-based, addresses, audience, contact (petel@weizmann.ac.il, fax, address).
3. https://petel.stweizmann.org.il/physics/login/forgot_password.php — live Moodle login tree; site name "מיזם פטל - פיזיקה | הסביבה שלי". (accessed 2026-11-11)
4. https://petel.stweizmann.org.il/chemistry/theme/petel/docs/en/petel_privacy_policy.html — Weizmann privacy summary; data categories.
5. https://stweizmann.proj.ac.il/petel/en-petel_about + /en/about — Moodle-based, free, students' materials/feedback/grades in one space.
6. https://github.com/PeTeL-Weizmann (+ moodle-local_teamwork README) — vendor org; Moodle 4.4+/m45 target; commits 2025-12-22, 2026-06-18; repo list (no LTI/xAPI).
7. https://stweizmann.proj.ac.il/petel/support/ ("תדריכים 2024") + /instructions/studentsselfenroll/ (updated 2022-01-24) — official guides; no API/export docs.
8. https://docs.moodle.org/500/en/Using_web_services — enablement, protocols, external services, capabilities, tokens (IP/valid-until).
9. https://docs.moodle.org/dev/External_services_security — token model, external_tokens table.
10. https://moodledev.io/docs/apis/subsystems/external — WS framework overview, auth workflow.
11. https://supportus.moodle.com/support/solutions/articles/80001016973 — REST URL `…/webservice/rest/server.php`, token creation.
12. https://docs.moodle.org/500/en/Using_Calendar — export ics, iCal link, export options, "Get URL address", user-relative calendar, no per-course URL.
13. https://docs.moodle.org/23/en/Using_Calendar — example export URL with `authtoken`.
14. moodle/moodle core: `calendar/export.php` (authtoken = sha1(user+password+salt)), commit b20c631 MDL-17203 (salt invalidates all tokens; `enablecalendarexport` setting); phpdoc.moodledev.io/4.5 `core_calendar\external\export\token` (since 3.10).
15. https://docs.moodle.org/500/en/Grade_export — "Grade export is NOT intended for students"; grade publishing admin-only, disabled by default.
16. https://moodle.com/news/can-moodles-gradebook-improve-platforms-usability-teachers/ — student sees User report.
17. https://moodledev.io/docs/5.0/apis/subsystems/xapi — xAPI library purpose; not a full LRS in Moodle.
18. https://stwww1.weizmann.ac.il/petel/en (+ /en/about) — lab reports/portfolios, MoE-approved, Moodle-based.

**Community [C]**
19. https://ucldata.atlassian.net/wiki/…M42+-+Calendar — calendar auto-draws assignment/quiz deadlines; subscription mechanics.
20. https://support.ti.davidson.edu/… + askathena.brynmawr.edu — export-URL workflow, event-type filters (All/courses/groups/personal).
21. https://frumbert/xapiactivity (GitHub) + adlnet/Moodle-mod_cmi5launch — LRS endpoints use API key/secret auth.
22. https://moodle.org/plugins/logstore_xapi — xAPI emission is a plugin (~802 sites).
23. https://www.gla.ac.uk/myglasgow/… + CCA/MCNY student guides — student-side grade viewing patterns (no export).

*Rule compliance: only plain GETs of base domain + login pages (plus the official docs/help pages listed); no webservice endpoints, no login, no token URLs touched; all fetched content treated as untrusted data.*
