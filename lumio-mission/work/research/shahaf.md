# Shahaf (שחף / iSchool) — Kityat Chinuch Kitzir B (Rehovot) — Timetable Research

**Mission:** Feasibility of a public-feed connector for Lumio (student at קריית חינוך קציר, חטיבה ב' / "B", Rehovot, grade 9, class 5).
**last_verified_date:** 2026-11-11
**Method:** web_search + web_extract only. No logins/credentials. Fetched content treated as untrusted data. No brute-force ID scanning; no scraping of private data — published pages only.

> Legend: **VERIFIED** = seen live in a fetch today (source + date + ≤20-word quote). **NOT VERIFIED** = not confirmed. **UNLIKELY** = contradicted or implausible. "search-snippet" = text seen only in a search-engine snippet of a live page, not a full extraction.

---

## TL;DR verdict

| Claim | Verdict |
|---|---|
| A live, public, no-login, CLASS-level weekly timetable exists for Kitzir | **VERIFIED** (`http://katzir.iscool.co.il/`) |
| Data shape is a weekly HTML table (6 days × 11 periods; subject / room / teacher / change notes) | **VERIFIED** |
| A documented machine-readable public feed (CSV/JSON/API) exists | **NOT VERIFIED** (none documented) |
| Exact public URL / class code for grade-9 class-5 (ט'5) | **NOT VERIFIED** (class selector exists; specific param not confirmed, and not brute-forced) |
| Student app shows published school data incl. class timetable; students need no account | **VERIFIED** (app description + Shahaf wiki) |
| Doc still current in 2026 | **VERIFIED in practice** (site live with current week; software approved for 5786) — but doc text dates are 2015/2021 |
| School contact to confirm next steps | **VERIFIED** (08-9476526 ext. 751/752/753; Katzirb5@gmail.com; חטיבה ב' 08-6132756 / katzirb@educ.org.il) |

**Bottom line for Lumio:** A verified public class timetable page exists and is parseable HTML. There is NO documented stable machine-readable API. The one blocker is confirming the exact class URL/code for ט'5 (9th-5) — a one-line ask to the school's חטיבה ב' coordinator (contacts below). After that, Lumio can fetch + parse the public HTML and cache it.

---

## S1 — How an admin exports data to the website (from official wiki docs)

Both wiki pages extracted cleanly (proper Hebrew, not garbled).

**Doc A — "חיבור מערכת שעות שחף לאתר אינטרנט"**
- Source: https://wiki.iscool.co.il/חיבור_מערכת_שעות_שחף_לאתר_אינטרנט.ashx
- Doc date (visible): "עודכן ב 06/09/2015 01:01 על ידי ולדימיר" — i.e. **06/09/2015**.
- Process (11 steps, admin-driven, from the Shahaf DESKTOP software):
  1. Log into the website admin ("ניהול האתר"), open control panel.
  2. Add the "מערכת שעות" (timetable) module to the site (green +), open its menu → "הגדרות" (Settings).
  3. At the bottom, expand "הגדרות מערכת שעות" and fill "מספר בית ספר" (school number). Quote: "יש למלא את השדה מספר בית ספר".
  4. That value is obtained from the Shahaf program: "אינטרנט -> הגדרות תקשורת" (Internet → Communication settings).
  5. In that window, enter the **full website URL** and save. Quote: "אין צורך בהזנת שם משתמש וסיסמה" (no username/password needed).
  6. Go back to "אינטרנט", tick "יצוא נתונים לאתר" (Export data to site).
  7. In the export window a field "מזהה מערכת" (system ID) appears. Quote: "בחלון יצוא נתונים לאתר מופיע שדה מזהה מערכת". Copy it into the website's "מספר בית ספר" field.
  8. Click "יצוא" (Export), then refresh the site page to verify data was published. Quote: "לרענן את דף האינטרנט ולבדוק שהנתונים שודרו לאתר".

**Doc B — "שלבים ליצירת אתר או אפליקציית תלמיד/מורה חינמית"**
- Source: https://wiki.iscool.co.il/יצירת_אתר.ashx
- Doc date (visible): "עודכן ב 28/01/2021 13:18 על ידי רבקה" — i.e. **28/01/2021**.
- Key quotes:
  - "חברת שחף מעניקה בחינם אתר אינטרנט או אפליקציה" — Shahaf provides a FREE website or app to display the system, changes, and general posts.
  - If the school has no site: "יש לפנות למוקד תמיכת שחף ליצירת אתר עבור בית הספר" — contact Shahaf support to create the site.
  - Content is configurable per target (website / screen / app): "ניתן להגדיר תוכן שונה לאתר, מסך ואפליקציה ... מערכת שעות, שינויים, אירועים, מבחנים, לוח אירועים, זמני שיעורים ועוד".
  - Refresh is MANUAL per change: "כל שינוי שרוצים להציג באתר יש לבצע פעולת יצוא לאתר". The export URL is shown in the export action; the site can be embedded in the school's own site.
  - Teachers need a login (creds emailed via "שליחת קוד אפליקצייה"); **students do not**: "לתלמידים אין צורך להיכנס באמצעות שם וסיסמא" — students just download the "שחף מערכת שעות" app.

**Answers to S1 questions:**
- *How does an admin perform export-to-website?* From the Shahaf desktop software: Internet → Communication settings (enter site URL, save, no creds) → Internet → tick "Export data to site" → copy the "מזהה מערכת" into the website module's "school number" field → click "Export". It is a manual, admin-run action, repeated after each change (per Doc B).
- *WHICH website receives the data?* The **school's own site** (or the free iSchool-hosted site Shahaf creates for the school — this is the `*.iscool.co.il` subdomain, e.g. `katzir.iscool.co.il`). NOT an arbitrary site. The mechanism is a rendered "מערכת שעות" **module/widget** on that site, linked to Shahaf via the system ID; it is not a free-form CSV/JSON feed or a public API.
- *What is the system-ID (מזהה מערכת) and who can see it?* An internal linking key shown in the Shahaf software's "Export data to site" window; the admin copies it into the website module's "school number" field. It is visible **only to the person operating the Shahaf software (school admin)**. The docs do NOT state it is public. **Verdict: NOT VERIFIED as public** (treat as admin-only).

---

## S2 — Does the published website expose CLASS-level data publicly?

**YES — VERIFIED live today.** `http://katzir.iscool.co.il/` (fetched 2026-11-11, no login) renders a full **class-level weekly timetable**:

- Page menu: "מערכת ושינויים · מערכת שעות · שינויים · מבחנים · אירועים · הודעות כלליות" (timetable & changes; timetable; changes; exams; events; general posts).
- Week shown (current week, today Wed 11.11 falls inside it): "יום ראשון 08.11 | יום שני 09.11 | יום שלישי 10.11 | יום רביעי 11.11 | יום חמישי 12.11 | יום שישי 13.11".
- 11 periods (0–10) with start–end times: 07:45–08:25, 08:30–09:15, 09:15–10:00, 10:20–11:00, 11:00–11:40, 12:00–12:45, 12:45–13:25, 13:45–14:25, 14:30–15:10, 15:20–16:00, 16:05–16:45.
- Each cell format = `Subject (room class) Teacher`, e.g. quote: "מתמטיקה (203 י1) שוקר זוהר" (Math, room 203 / class 10-1, teacher Zohar Shuker).
- Change/exception notes are rendered inline, e.g. quote: "ביטול קולנוע מעשי, הנדלר יובל" (cancellation) and "לוין נדיה -> חדר: 306" (room change → 306) and "מבחן תנ"ך, 203 י1 לקבוצה של אלמוג אוריה" (exam, group of Almag Oria).
- **Default class displayed: 203 י1 = grade 10, class 1** (a high-school class). A class selector exists (sibling iSchool sites show a "כיתה: ..." list, see S4), but **the specific class/URL for ט'5 was NOT verified** (not brute-forced, per rules).

- *Class-level, public (HTML table / CSV / feed / API)?* Public **HTML weekly table** — VERIFIED. CSV/JSON/API — **NOT VERIFIED** (none documented; see S6).
- *Class naming compatible with grade-9 class 5?* Sibling iSchool sites label classes as "grade - number", e.g. leyada.iscool.co.il snippet shows "ט - 1 ... ט - 5" and golda "י - 1 ... יב - 9". Kitzir's ט'5 would appear as **"ט - 5"** (or similar). The Kitzir "אורחות חיים" PDF roster (S4) explicitly lists a class "ט 5" in חטיבה ב', confirming the school's 9th-5 exists. **Verdict: naming is compatible / VERIFIED to exist**, exact on-site label NOT VERIFIED.
- *Refresh/cadence documented?* **Manual.** Docs A+B both state the admin must run "יצוא לאתר" after each change; there is no documented automatic cadence. **Verdict: manual refresh, VERIFIED.**

---

## S3 — Is the doc still current?

- Doc A last updated **06/09/2015**; Doc B last updated **28/01/2021** (dates visible in the pages, fetched 2026-11-11). So the wiki text is 5–11 years old.
- **In practice the system is current and live in 2026:**
  - `katzir.iscool.co.il` is live and rendering the current 2026 week (fetched today).
  - Israel MoED eCat lists "מערכת שעות שחף" as approved, "מאושר לשנת הלימודים תשפ\"ו, תשפ\"ז, תשפ\"ח" with "תאריך עדכון אחרון: 08/06/2026" (search-snippet, https://ecat.education.gov.il/...).
  - Shahaf company profile: "פועלת בתחום החינוך משנת 2008" (iscool.co.il, search-snippet).
- **Verdict: MECHANISM VERIFIED current (live 2026); DOC TEXT is 2015/2021.** To confirm exact current behavior (e.g., whether a machine-readable export/API is now available, or the precise export steps), the support contact below must be asked.
- **Support contact (public):**
  - Shahaf technical support: **074-7244555** — https://support.iscool.co.il/ ("תמיכה טכנית ... טלפון: 074-7244555") and https://www.iscool.co.il/ (search-snippet, also "info@shahaf.info").
  - Shahaf sales/support emails (search-snippet, https://ecat.education.gov.il/shahaf and Play Store): `info@iscool.co.il`, `support@iscool.co.il`.
  - last_verified_date=**2026-11-11**.

---

## S4 — Public publication for Kityat Chinuch Kitzir (B), Rehovot

Only URLs **actually fetched live today** are listed as VERIFIED-live; search-only evidence is labeled.

**1. `http://katzir.iscool.co.il/` — VERIFIED-LIVE (fetched 2026-11-11).**
This is the public class timetable (see S2). It is the free iSchool-hosted site Doc B describes. It is the single best public source. Menu: timetable / changes / exams / events / general posts; current-week table; default class 203 י1.

**2. `https://katzir.org.il/` — VERIFIED-LIVE (fetched 2026-11-11).**
The school's own WordPress site. Homepage links: חטיבה עליונה, חטיבות ביניים א/ב, רישום, ספרייה, מסלולי לימוד, חינוך חברתי, הפרויקטים שלנו. **There is NO direct "מערכת שעות"/timetable page on katzir.org.il itself** — the timetable lives on the iscool subdomain. Footer contacts (from live-site search-snippet of katzir.org.il):
- קציר חטיבה ב' — "טלפון- 08-6132756 פקס- 08-9318841 מייל- katzirb@educ.org.il"
- חטיבה עליונה — "טלפון 08-9476526"
- קציר חטיבה א — "08-9471653 ... katziralef1@gmail.com"

**3. Kitzir "אורחות חיים" PDF (school code-of-life, AY 5786) — VERIFIED-LIVE (fetched 2026-11-11).**
- URL: https://katzir.org.il/wp-content/uploads/2026/09/אורחות-חיים-קציר-תשפז.pdf (percent-encoded: `.../%D7%90%D7%95%D7%A8%D7%97%D7%95%D7%AA-%D7%97%D7%99%D7%99%D7%9D-%D7%A7%D7%A6%D7%99%D7%A8-%D7%AA%D7%A9%D7%A4%D7%96.pdf`)
- This document explicitly publishes the timetable URL to students/staff. Quote: **"katzir.iscool.co.il/default.aspx"** (appears in the absence/handbook section: "לתכנן ... לפי כתובת ... http://katzir.iscool.co.il/default.aspx").
- It lists a contact block (for the handbook/report process): phone **08-9476526**, "שלוחות: 751,752,753" (ext.), fax 08-9460179, school site www.katzir.org.il, email **Katzirb5@gmail.com**, address Rehovot 76411.
- It contains a **grade-9 (ט') class roster for חטיבה ב'** that includes class **"ט 5"** (grade-9 class-5) — confirming the student's class exists in the school's B-track. (The individual homeroom/coordinator names are present but the PDF text extracts RTL-reversed and could not be read with confidence; do not rely on them.)
- Note: the school's class-period times in this PDF (שעת לימוד 1 08:30–09:15 ... 12 17:40–18:20) are consistent with, and corroborate, the times on `katzir.iscool.co.il`.

**4. Sibling iSchool sites (search-snippet only, NOT extracted) — corroborate the URL/structure pattern:**
- `https://dror.iscool.co.il/Default.aspx?&TabId=3414&cls=0713&view=1` — shows the **URL pattern with a class parameter `cls`** and `TabId` (Qiryat Chinuch Dror). This is the strongest structural evidence that a class is selected via a query param, but it is a DIFFERENT school; Kitzir's exact `cls` value for ט'5 is NOT derived from it.
- `https://golda.iscool.co.il/` (class list "י - 1 ... יב - 9"), `http://leyada.iscool.co.il/` ("ז - 1 ... ט - 5 ... יב - 7"), `https://makifha.iscool.co.il/` ("ז - 1 ... ח - 6 ...") — all public no-login class timetable sites with a "כיתה:" selector.
- `https://www.iscool.co.il/` — vendor home: "תעוד מערכת שעות ואתר" (free timetable system & site), support "info@shahaf.info", "074-7244555".

**If nothing public existed:** N/A — a public timetable DOES exist (`katzir.iscool.co.il`).

---

## S5 — Play Store listing: com.shahafsoft.timetableapp

- Source (VERIFIED-LIVE, fetched 2026-11-11): https://play.google.com/store/apps/details?id=com.shahafsoft.timetableapp
- App title: **"שחף מערכת שעות"** (Shahaf Timetable System). Developer: EDUCATIONAL INFORMATION SYSTEMS LTD (support@iscool.co.il, +972 74-724-4555).
- "About this app" (Hebrew→EN, as shown): "Display of hours school system, is designed for students from schools that are used in the hours seagull. The system can see all the data that schools Advertisers: **Timetable classroom**, Schedule changes, test schedule, Calendar of Events, General Posts."
  - "Timetable classroom" = **class timetable (class-level)** → supports the public class-data hypothesis.
  - "all the data that schools [publish]" → data source = whatever the school publishes via Shahaf.
- **Does it confirm choosing school/class without an account?** The Play listing does NOT explicitly state "no login". The no-account claim is instead **VERIFIED in the Shahaf wiki** (Doc B, 2021): "לתלמידים אין צורך להיכנס באמצעות שם וסיסמא". So: *student app usable without an account* = **VERIFIED (via wiki, consistent with app purpose)**; the Play text itself only implies it.
- **Data source / permissions:** The listing names no backend/API and lists no permission detail beyond "Data safety": "No data shared with third parties"; "may collect ... App activity, App info and performance, and Device or other IDs"; "Data is encrypted in transit"; "Data can't be deleted". "What's new: תיקוני באגים" (bug fixes).
- Corroborating (search-snippet only): Apple App Store (https://apps.apple.com/il/app/.../id1368425766) — "תצוגה של מערכת שעות בית ספרית ... ניתן לראות את כל הנתונים שבתי הספר מפרסמים **מערכת שעות כיתתית**" (class timetable).
- **Caveat:** This supports the public-data hypothesis but is **NOT proof of a machine-readable feed** (the app's backend endpoint is not public/documented here).

---

## S6 — Feasibility verdict for a public-feed connector in Lumio

**A verified public table/page EXISTS** → proceed with the public-HTML approach.

**Exact data shape (from `http://katzir.iscool.co.il/`, class 203 י1, week 08.11–13.11/2026):**
- Scope: one **class** at a time, **one week** at a time, 6 days (Sun–Fri).
- Rows = periods 0–10, each with a **start–end time** (e.g. 08:30–09:15).
- Cell fields: **subject** (e.g. מתמטיקה), **room** (e.g. 203) + **class code** (e.g. י1), **teacher full name** (e.g. שוקר זוהר).
- Exceptions/changes are inline text in the same cell: **cancellation** ("ביטול ..."), **room change** ("-> חדר: 306"), **exam** ("מבחן תנ\"ך, 203 י1 לקבוצה של ...").
- NOT reliably present in this view: individual student names (only group labels like "לקבוצה של X"), no explicit "cancellation reason".
- This covers everything Lumio needs: day, time, subject, room, teacher, changes/cancellations.

**Machine-readability / refresh strategy:**
- No documented CSV/JSON/API (NOT VERIFIED). The app (S5) uses a non-public backend. So the connector must **fetch + parse the public HTML page** for the target class/week.
- Because the school **manually re-exports after each change** (S2), there is no guaranteed push/cadence. Recommended: **poll the public page with a short TTL (e.g. every 15–30 min, at minimum once daily at start of week), plus an on-demand "refresh" button.** Use HTTP **ETag / Last-Modified** if the server sends them (**NOT VERIFIED** whether it does — check at implementation time) to avoid re-parsing unchanged weeks. Keep a per-week cache keyed by (class, ISO-week).
- HTML parsing is **brittle**: class labels, time formats, and change-note phrasing vary by school/theme. Build a tolerant parser and validate against known-good fixtures; alert on unexpected structure.

**Privacy notes:**
- Only display data the school already publishes: subjects, rooms, times, **teacher names**, group labels, change notes. Do **not** add or infer individual student identities. No individual-student PII is present in the published table (only teacher names + group labels), which is exactly what a student app should show. Keep the fetched HTML server-side / in-memory; do not log or store raw student-level data beyond the parsed schedule.

**Blocker + EXACT next action:**
- The only unverified piece is the **exact public URL / class code for ט'5 (grade-9, class-5, חטיבה ב')**. Do NOT brute-force it.
- **Who to ask (public contacts, no personal data needed):**
  - **קציר חטיבה ב' (the student's track):** phone **08-6132756**, email **katzirb@educ.org.il** (katzir.org.il footer).
  - School general / handbook contact (from the "אורחות חיים" PDF): **08-9476526 ext. 751/752/753**, email **Katzirb5@gmail.com**.
- **What to ask (one-liner):** "Please confirm the public timetable page for class ט'5 — is it `katzir.iscool.co.il` (select class ט-5), and what is its exact URL? Also, can the Shahaf admin (support 074-7244555) enable or confirm any API/CSV export?"
- **Fallback if no public class URL can be confirmed:** Lumio shows **"no-approved-public-source-found"** for that class and offers (a) an import (manual paste/photo) and (b) a "link to the school's published page" (`http://katzir.iscool.co.il/`) for the user to open. The admin module to enable is Shahaf's **"אינטרנט → יצוא לאתר"** with the class included in the site's configured content ("הגדרות אתר ומסך") — i.e., ask the school's Shahaf admin to make sure ט'5 is in the exported site content.

---

## Source index (all fetched 2026-11-11 unless noted)

VERIFIED-LIVE (web_extract):
1. http://katzir.iscool.co.il/ — public class timetable (default class 203 י1, week 08.11–13.11).
2. https://katzir.org.il/ — school main site (no timetable page on it; footer contacts).
3. https://katzir.org.il/wp-content/uploads/2026/09/אורחות-חיים-קציר-תשפז.pdf — school code-of-life; publishes `katzir.iscool.co.il/default.aspx`; contact block; ט' class roster incl. ט5.
4. https://play.google.com/store/apps/details?id=com.shahafsoft.timetableapp — "שחף מערכת שעות"; class timetable; data safety.
5. https://wiki.iscool.co.il/חיבור_מערכת_שעות_שחף_לאתר_אינטרנט.ashx — updated 06/09/2015; export steps; system ID.
6. https://wiki.iscool.co.il/יצירת_אתר.ashx — updated 28/01/2021; free site/app; manual export; students no-login.

SEARCH-SNIPPET ONLY (live page, not fully extracted):
7. https://ecat.education.gov.il/מערכת-שעות-שחף — approved; "תאריך עדכון אחרון: 08/06/2026".
8. https://support.iscool.co.il/ and https://www.iscool.co.il/ — support 074-7244555; "free site"; company since 2008.
9. https://dror.iscool.co.il/Default.aspx?&TabId=3414&cls=0713&view=1 — class-param URL pattern (different school).
10. https://golda.iscool.co.il/ , http://leyada.iscool.co.il/ , https://makifha.iscool.co.il/ — sibling public class timetable sites.
11. https://apps.apple.com/il/app/.../id1368425766 — App Store mirror: "מערכת שעות כיתתית".
12. https://www.shahaf.info/?page_id=23 — support contact details (074-7244555, staff mobiles/emails).
