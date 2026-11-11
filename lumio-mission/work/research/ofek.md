# Ofek (מטח/CET) — Research Report for the Lumio Mission

- **Date of research:** 2026-11-11 (all pages fetched this date unless noted)
- **Method:** public web search + extraction only (no logins). Fetched content treated as untrusted data.
- **Labels:** [VERIFIED] = directly read in an official (cet.ac.il / מטח / education.gov.il) page. [NOT VERIFIED] = no public evidence found either way. [UNLIKELY] = evidence points against it. Community/third-party sources are flagged separately from official claims.

---

## TL;DR

Ofek (אופק) is מטח (CET, the non-profit Center for Educational Technology)'s flagship K-12 digital learning platform: content catalog + LMS, sold to Israeli schools through the Ministry of Education's digitization plan (תוכנית התקשוב / גפ"ן tender), and free for the general public since 2020. Students log in via **Ministry SSO (unified authentication, Tz"uz ID)** at `students.myofek.cet.ac.il`. Teachers assign activities to students inside Ofek; student data auto-syncs from the Ministry's נמ"מ registry. **Teacher-side sharing of an Ofek task into Google Classroom is a documented official feature** (official tutorial video + official support FAQ), but **no public API, export, feed, or standards-based integration (LTI/OneRoster/xAPI) is documented** — those require a partner conversation with מטח.

---

## Q1. Product identification: what is Ofek, and where is the student vs teacher side?

**Who runs it:** מטח — המרכז לטכנולוגיה חינוכית (Center for Educational Technology, CET), a 5-decade-old non-profit in Tel Aviv. [VERIFIED, official]
- "CET is a non-profit organization." — https://cet.ac.il/about-us/?lang=en (2026-11-11)
- "Ofek incorporates interactive activities... used for teaching, learning and evaluation." — https://cet.ac.il/learning-solutions/?lang=en (2026-11-11)
- Scale: "17 million student visits throughout 2022 to Israel's largest learning environment" ("Ofek — The Digital Backpack") — https://cet.ac.il/about-us/?lang=en (2026-11-11)

**What it is:** a content platform + LMS. "סביבות למידה, ספרי לימוד, תכנים דיגיטליים, כלים ואתרים" (learning environments, textbooks, digital content, tools and sites). [VERIFIED, official]
- "מערכת ניהול ומעקב — שיוך פעילויות ותכנים, תזמון, בדיקה אוטומטית, הוספת הערות אישיות" (management & tracking: assign activities, scheduling, auto-grading, personal notes) — https://www.cet-catalogue.cet.ac.il/אופק (2026-11-11)
- "הספרייה מרכזת עבורך את כל ספרי הלימוד שבית הספר שלך רכש" (the library centralizes the textbooks your school bought) — https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (2026-11-11)
- Sold to schools in the Ministry's digitization plan: "בתוכנית התקשוב בוחרים — אופק"; in the 2026-2027 digital-content tender: "אופק — סביבת תוכן דיגיטלי עם LMS" (full env. ₪5,000) — https://www.cet-catalogue.cet.ac.il/אופק and https://cet2025-catalogue.cet.ac.il/digital-content (2026-11-11)

**STUDENT side vs TEACHER side (URLs and features):**

| Side | URL | Features (documented) |
|---|---|---|
| Content hub (all users) | `https://myofek.cet.ac.il` | Search by class/subject ("מה תרצו ללמד היום?"), activity cards with grade level + duration, favorites, digital library, learning environments/courses. [VERIFIED] myofek.cet.ac.il (2026-11-11) |
| Student login / assigned work | `https://students.myofek.cet.ac.il` | Two login options: Ministry of Education (unified auth) and מטח account. "יש להזין מספר ת״ז של תלמיד/ה או מורה בלבד" (only a student/teacher ID number). [VERIFIED] students.myofek.cet.ac.il/he (2026-11-11) |
| Student work flow | inside Ofek after login | Old official newsletter: students connect to their personal "ילקוט" (digital backpack) and "נכנסים למשימות לתלמיד" (enter student tasks), do the task, "בסיום הפעילות מגישים את המשימה למורה" (submit to teacher at the end). [VERIFIED, official but older content] http://cet.activetrail.biz/אופק |
| Teacher — LMS/assignment ("הסטודיו שלי" ecosystem) | Ofek teacher area (new site), legacy: `ebag.cet.ac.il` (יסודי), `ebaghigh.cet.ac.il` (חט"ב), `myTestBox.cet.ac.il` (תיכון) | "משייכים פעילות לתלמידים — בוחרים פעילות ומאפשרים לתלמידים להתחיל לעבוד וגם לקבל משוב" (assign activity to students, let them start and get feedback). [VERIFIED] cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (2026-11-11) |
| Teacher — authoring | "הסטודיו שלי" (My Studio) | "הסטודיו שלי הוא מוצר מתקדם ליצירת תוכן אינטראקטיבי... אפשר ליצור פעילויות למידה והערכה בקלות" — https://lo.cet.ac.il/player?document=c94ac286-ee22-478c-bb1b-a189979ccda9&language=he (2026-11-11) |
| Teacher — assessment environment | `https://ofek.cet.ac.il/eval.aspx` ("אופק-הערכה") | "מאפשרת למורים לנהל תהליך הערכה בשלמותו: תכנון... העברת משימת ההערכה לתלמידים באופן מקוון... מעקב אחר התקדמות התלמידים" — ofek.cet.ac.il/eval.aspx (2026-11-11) |
| Teacher reports | in-app | "דוח ציונים למשימות: ממוצע כיתתי, סטיית תקן... דוח מלא לפי תלמידים" (class-average score report, per-student full report) — http://cet.activetrail.biz/אופק (official newsletter, older) |

**How students log in:** Ministry of Education SSO (unified authentication). [VERIFIED, official]
- Login page: "התחברות משרד החינוך — יש להזין מספר ת״ז של תלמיד/ה או מורה בלבד" + separate "התחברות מטח" option — students.myofek.cet.ac.il/he (2026-11-11)
- Official tutorial: "איך להיכנס לאתר אופק ולבצע התחברות באמצעות הזדהות משרד החינוך" — https://www.youtube.com/watch?v=fjq91T_NEl4 (מטח channel; accessed 2026-11-11)
- The MoE itself documents unified authentication for students/staff across its services (see Q4 virtual-school page).

**Community context (separate from official):**
- Wikipedia: "אופק — מערכת ניהול למידה לבתי ספר... מציעה מערכת לניהול הלמידה (LMS)... לשייך משימות לכל תלמיד... נכון לשנת 2018, 2,300 בתי ספר" — https://he.wikipedia.org/wiki/המרכז_לטכנולוגיה_חינוכית (2026-11-11) [community]
- Critical 2020 press on the MoE+מטח remote-learning rollout: "החלטות גרועות של המשרד הממונה, בשילוב קשר חונק עם הספק המרכזי בתחום הדיגיטלי" — https://www.ha-makom.co.il/post-galit-matach-fail/ (2020-12-31) [community, opinion]
- Free access for the public was announced by מטח (official Facebook): "מטח פותח ללא עלות את אופק, כותר ומגוון סביבות הלמידה" — https://www.facebook.com/cet.ac.il/posts/1455307989970330 (2020-era post; fetched 2026-11-11) [official]

---

## Q2. Official API / export / partner content portal

**No public API, developer portal, or integration spec exists in public search results.** [NOT VERIFIED]
- Searches: `"myofek.cet.ac.il" OR "ofek.cet.ac.il" API developer integration` → 0 relevant results (2026-11-11). "Ofek מטח API אינטגרציה" → only unrelated "Ofek" companies (satellite, bank, machining). No developer.cet.ac.il, no API docs found.

**Teacher-side documented capabilities (in-app, not export):**
- Assign activities to students, track progress, auto-grade, feedback — [VERIFIED] cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (2026-11-11): "משייכים פעילות לתלמידים... לתלמידים להתחיל לעבוד וגם לקבל משוב"
- Reports in-app: "הפקת דוחות... דוח מלא לפי תלמידים" — http://cet.activetrail.biz/אופק (official newsletter) [VERIFIED, official; no download format stated]
- **Export (Excel/PDF file download) of assignments or results: NOT documented publicly. [NOT VERIFIED]**

**Student-side capabilities:** students do assigned tasks and submit them in-app; no public documentation of any student-facing export, download, or share function. [NOT VERIFIED]

**Partner channel (undocumented, inferred from official pages):** מטח has MindCET ("המרכז לחדשנות ולפיתוח טכנולוגיות בחינוך", EdTech innovation arm) and VP Technology Niv Gross / VP Marketing & Sales Gil Divan are listed in leadership — https://cet.ac.il/about-us/?lang=en, https://he.wikipedia.org/wiki/המרכז_לטכנולוגיה_חינוכית (2026-11-11) [official + community]. Any API/partner access is plausibly via a commercial agreement, but **no public partner program page exists. [NOT VERIFIED / UNLIKELY to be self-serve]**

**Contacts (all officially published):**
- Customer service: **sherut@cet.ac.il**, 03-6460800, 16 Klausner St, Tel Aviv — https://cet.ac.il/contact/?lang=en (2026-11-11)
- Technical support: **webs@cet.ac.il**, 03-6200622, WhatsApp 054-679-5116 — https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (2026-11-11)

---

## Q3. Ofek → Google Classroom sharing

**Feature exists (teacher side): VERIFIED (official, two independent sources).**
1. Official מטח YouTube playlist "ניהול הלמידה וסביבת אופק" contains a tutorial titled: **"הסטודיו שלי וניהול הלמידה — כיצד לשתף משימה מאופק לסביבות למידה אחרות כגון קלאסרום"** ("how to share a task from Ofek to other learning environments such as Classroom") — https://www.youtube.com/playlist?list=PLYH9I-4V1wQJM_y34BQjsivjUspfS3iD7 (מטח channel; fetched 2026-11-11)
2. Official Ofek support-center FAQ lists the question **"האם אני יכול לשתף פעילויות עם google classroom או Microsoft Teams?"** ("Can I share activities with Google Classroom or Microsoft Teams?") — https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (2026-11-11). The FAQ answer body is behind a JS accordion and did not render in plain fetch, so the official answer text itself is [NOT VERIFIED].

**Context from the Ministry (official):** Google Classroom is the MoE's official digital classroom space — "מרחב מקוון לניהול הלמידה הדיגיטלית... הגדרת תאריכי הגשה" — https://pop.education.gov.il/sherutey-tiksuv-bachinuch/classroom/ (2026-11-11). The MoE FAQ confirms Classroom tasks "יכולים לכלול קבצים או קישורים" (can include files or links).

**What metadata survives (student view on the Classroom side): NOT VERIFIED.**
- No official page documents the metadata mapping. [NOT VERIFIED]
- Best-supported inference (marked as such, not as fact): the share flow produces a Classroom task/announcement that carries **the link to the Ofek activity plus whatever title/description the teacher sets**. **Due date, grade, and submission state are almost certainly NOT mirrored into Classroom** — Ofek remains the system of record for completion/grades (students "מגישים את המשימה למורה" inside Ofek). [UNLIKELY for due date/grade/submission to survive; link + title only is the working assumption]
- For Lumio's purposes: this is a **legitimate partial unification path** — a student who already has Classroom in the MoE virtual-school space would see the Ofek task as a plain assignment containing a link. Lumio could mirror the *same* structure (title + link) with zero dependence on Ofek internals, and the unification value is "one place lists the task," not "one place shows the grade."

---

## Q4. Refreshable student feed / calendar; standards usage

**Student-facing feed or calendar API: none documented. [NOT VERIFIED / UNLIKELY public]**
- Inside Ofek, the student's task list ("משימות לתלמיד") is the in-app calendar of work — http://cet.activetrail.biz/אופק (official newsletter). No public ICS/RSS/JSON feed exists in any search. [NOT VERIFIED]
- Closest MoE-level aggregator: the MoE "בית הספר הווירטואלי" (virtual school) — "כל תלמיד ועובד הוראה יכולים להיכנס... באמצעות הזדהות אחידה של משרד החינוך" and students "ימצאו במקום אחד גם את המשימות הכיתתיות שהועלו, למשל, לגוגל קלאסרום" — https://pop.education.gov.il/sherutey-tiksuv-bachinuch/virtual-school/ (2026-11-11). This is an MoE product, not an Ofek API; no public API documented for it either.

**Standards (LTI 1.3 / OneRoster / xAPI):** no public evidence that Ofek/מטח implements or consumes any of them. [NOT VERIFIED]
- Searches "מטח ofek LTI OneRoster xAPI" and "מטח xAPI OR 'LTI 1.3' OR OneRoster ישראל" returned only generic standards articles (IMS Global, e-learning industry blogs), nothing מטח-specific (2026-11-11).
- **Lumio's usage right in each standard** (general knowledge about the standards, not about Ofek):
  - **LTI 1.3** — 1EdTech open spec; free to implement, certification optional (but required to display the certification logo). For Lumio as a tool: implementable today, no license fee. Usefulness is zero until Ofek/MoE becomes an LTI consumer/provider — UNLIKELY short-term.
  - **OneRoster** — 1EdTech open spec (CSV or REST); free to implement. Same situation: Lumio could *consume* it, but only if Ofek/MoE exposes it — no evidence they do. [NOT VERIFIED]
  - **xAPI** — 1EdTech (formerly ADL) open spec; free to implement; Lumio could host a Learning Record Store and write statements itself for its own analytics (that's Lumio's own data, no rights issue). It would NOT pull Ofek activity data unless Ofek sends xAPI — no evidence. [NOT VERIFIED]

---

## Q5. What identifier does Ofek receive from the Ministry login?

- **What is documented:**
  - The student login is Ministry unified authentication, keyed by **the student's (or teacher's) Tz"uz (national ID) number**: "יש להזין מספר ת״ז של תלמיד/ה או מורה בלבד" — https://students.myofek.cet.ac.il/he (2026-11-11) [VERIFIED, official]
  - Ofek's per-student data is **auto-pulled from the Ministry's נמ"מ student-registry system**: "נתוני התלמידים נמשכים באופן אוטומטי לאופק מהנמ״מ. אם אינך רואה אותם... יש ליצור קשר עם המזכירות או רכז בית הספר לשם סנכרון הנתונים" — https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (2026-11-11) [VERIFIED, official]
  - MoE side: "נדרשת הזדהות באמצעות פרטי הזדהות האחידה והמערכת תזהה אתכם" — https://pop.education.gov.il/sherutey-tiksuv-bachinuch/virtual-school/ (2026-11-11) [VERIFIED, official]
- **What is NOT documented:** the exact token/claim format Ofek receives (e.g., whether the SSO token carries Tz"uz as a named claim, class ID, school ID). [NOT VERIFIED] — do not assume a specific payload.
- **Implication for Lumio:** the only defensible stable cross-system identifier is **Tz"uz** (the MoE's own login key). Anything finer must come from a written commitment by מטח/MoE.

---

## Q6. Ranked paths + exact next actions

| # | Path | Status | Evidence line | Next action for Lumio |
|---|---|---|---|---|
| 1 | **Teacher-initiated Ofek→Classroom share** (user-initiated import, teacher-side) | Official feature exists; metadata behavior unconfirmed | Official tutorial title "כיצד לשתף משימה מאופק לסביבות למידה אחרות כגון קלאסרום" — youtube.com/playlist?list=PLYH9I-4V1wQJM_y34BQjsivjUspfS3iD7 (2026-11-11); FAQ "לשתף פעילויות עם google classroom או Microsoft Teams" — cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (2026-11-11) | **Pilot with 1–2 real teachers:** watch the share flow, record exactly what lands in Classroom (title? link? due date?). Then email **webs@cet.ac.il**: "נבקש דיוק מה המידע שעובר לשיתוף של פעילות מאופק לגוגל קלאסרום/Teams (קישור בלבד? כותרת? תאריך?), והאם יש מפות מתוכנתת/ייצוא נוספים." |
| 2 | **Partner agreement for read access** (teacher or student side): API/CSV export/roster | No public API; possible via contract — unknown | No developer portal or API docs found in any search (2026-11-11); only in-app reports documented (cet.activetrail.biz/אופק) | Email **sherut@cet.ac.il** (customer service; 03-6460800): ask for the partnership/integrations contact and whether any API, export (משימות/דוחות), or OneRoster/LTI integration exists for partners; ask what identifier (ת.ז?) would identify students in any feed, and what MoE/data-protection approval is required. Copy the technical contact **webs@cet.ac.il**. |
| 3 | **Teacher in-app reports, manual capture** | Works today, manual, teacher effort | "הפקת דוחות... דוח מלא לפי תלמידים" — cet.activetrail.biz/אופק (official) | Short-term stopgap: teachers screenshot/copy their per-student reports. Only viable for a handful of pilot families, not productization. |
| 4 | **Public student read (feed/calendar/exports)** | Not documented; UNLIKELY to exist | Searches for student feed/calendar/export on myofek/ofek domains → nothing (2026-11-11); only in-app "משימות לתלמיד" documented | Do not build on this assumption. Bundle the ask into the #2 email (student-facing read is the highest-sensitivity ask — expect MoE privacy review). |
| 5 | **Standards-based integration (LTI 1.3 / OneRoster / xAPI)** | No evidence Ofek supports any | Only generic standards docs found, none מטח-specific (2026-11-11) | In the #2 email, ask explicitly: "האם אופק/מטח תומכים או מתוכננים לתמוך ב-LTI 1.3 או OneRoster?"; Lumio can self-host xAPI for its own analytics regardless. |
| 6 | **MoE virtual school as aggregator** | Official MoE aggregator, no public API | "ימצאו במקום אחד גם את המשימות הכיתתיות שהועלו, למשל, לגוגל קלאסרום" — pop.education.gov.il virtual-school (2026-11-11) | If #2 stalls, ask via the school's MoE channels whether the virtual school exposes any task list for students/staff; not an Ofek commitment. |

**The single highest-leverage email (draft, Hebrew, to sherut@cet.ac.il cc webs@cet.ac.il):**
> נושא: שיתוף פעולה טכנולוגי — Lumio (אפליקציית ליווי תלמידים) + אופק
> שלום, אנחנו Lumio — אפליקציית הליווי של תלמידים בבית. תלמידים שלנו כבר משתמשים באופק דרך הזדהות משרד החינוך.
> נבקש: (1) האם קיימת אפשרות ל-API או ייצוא (משימות משויכות לתלמיד, דוחות) לצורך שיתוף פעולה? (2) האם אופק תומך ב-LTI 1.3/OneRoster או מתוכננת לתמוך? (3) במסגרת שיתוף פעילות לגוגל קלאסרום — אילו נתונים עוברים (קישור, כותרת, תאריך)? (4) איזו מידת פרטיות/אישור נדרשת לשיתוף מזהה תלמיד עם צד שלישי?
> נשמח לפגישת הכרות עם צוות ההנדסה (Niv Gross, VP Technology) או MindCET.

---

## Verdicts (one line each)

- **Q1** — Ofek = מטח's K-12 content+LMS platform; student side `students.myofek.cet.ac.il` (MoE SSO, Tz"uz), teacher side in the new Ofek teacher area (assign/track/report) + legacy `ebag.cet.ac.il`/`myTestBox.cet.ac.il`. [VERIFIED]
- **Q2** — No public API or export; teacher has in-app assign+reports; student has in-app tasks only; anything more is partner-contract territory. [NOT VERIFIED for any public dev surface]
- **Q3** — Ofek→Classroom teacher share is a real official feature; what survives on the Classroom side is NOT VERIFIED; working assumption = link + teacher-set title only (due date/grade/submission UNLIKELY).
- **Q4** — No student feed/calendar; no LTI/OneRoster/xAPI evidence; Lumio may freely implement all three as open standards but only its own data is at stake. [NOT VERIFIED for Ofek support]
- **Q5** — Login key = Tz"uz (documented); student data auto-syncs from MoE נמ"מ (documented); exact SSO token payload NOT VERIFIED — do not assume.
- **Q6** — Best path = #1 (Classroom share, already built by מטח) + one partner email to sherut@cet.ac.il/web​s@cet.ac.il covering API/export/standards/privacy in a single ask.

## Source index (all accessed 2026-11-11)

Official — מטח/CET:
1. https://cet.ac.il/about-us/?lang=en
2. https://cet.ac.il/learning-solutions/?lang=en
3. https://cet.ac.il/contact/?lang=en
4. https://myofek.cet.ac.il (and /he, /he/courses)
5. https://students.myofek.cet.ac.il/he
6. https://ofek.cet.ac.il/eval.aspx
7. https://www.cet-catalogue.cet.ac.il/אופק
8. https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק
9. https://cet2025-catalogue.cet.ac.il/digital-content
10. https://lo.cet.ac.il/player?document=c94ac286-ee22-478c-bb1b-a189979ccda9&language=he
11. http://cet.activetrail.biz/אופק (official מטח newsletter)
12. https://www.facebook.com/cet.ac.il/posts/1455307989970330
13. https://www.youtube.com/watch?v=fjq91T_NEl4 (מטח channel)
14. https://www.youtube.com/playlist?list=PLYH9I-4V1wQJM_y34BQjsivjUspfS3iD7 (מטח channel)

Official — Ministry of Education:
15. https://pop.education.gov.il/sherutey-tiksuv-bachinuch/classroom/
16. https://pop.education.gov.il/sherutey-tiksuv-bachinuch/virtual-school/

Community/third-party (clearly separated):
17. https://he.wikipedia.org/wiki/המרכז_לטכנולוגיה_חינוכית
18. https://www.ha-makom.co.il/post-galit-matach-fail/ (2020-12-31, opinion/critical)
19. https://www.openu.ac.il/lists/mediaserver_documents/innovation/chais/2023/chais-2023-sefer.pdf (2023 usage survey)
20. https://imsglobal.org/about/k12/oneroster-and-lti-advantage (generic standards background only)
