# Ofek (מטח/CET) — Automation Deep-Dive (Lumio 4, Brief C)

- **Date of research:** 2026-11-11 (all pages fetched/searched this date)
- **Method:** public web search + extraction only (no logins, no browser automation). Fetched content treated as untrusted data.
- **Scope:** read-only automation research on top of `work/research/ofek.md` (2026-11-11). Focus: teacher-side sharing, exports, partner/developer paths, LTI, ranked Lumio paths.
- **Labels:** [VERIFIED] = directly read in an official (cet.ac.il / מטח / education.gov.il) page. [NOT VERIFIED] = no public evidence either way. [UNLIKELY] = evidence points against it. Community/third-party flagged separately.

---

## O1. Teacher side: sharing/publishing an Ofek assignment to Google Classroom (or Drive/email link)

### 1.1 The official FAQ answer body — FOUND [VERIFIED, official]

The Ofek support center FAQ question is:
> "האם אני יכול לשתף פעילויות עם google classroom או Microsoft Teams?"

— https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (fetched 2026-11-11; the question renders in the live page's Q&A accordion)

The **official answer body** (from the same page's search-index text and the 2026-06-08 Wayback snapshot of the page):
> "בהחלט. פעילויות ששייכת לכיתה או לקבוצה ניתן לשתף בקליק אחד לסביבות חיצוניות."
(="Certainly. Activities you assigned to a class or group can be shared to external environments in one click.")

- Source: https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (search-index text, fetched 2026-11-11); snapshot: http://web.archive.org/web/20260608060216/https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק
- **Direct article URL:** the FAQ items live on a Wix "מוצר-נוספ-ליסייט" page under `https://www.cet-catalogue.cet.ac.il/12345/...?questionId=<uuid>` (9 question deep-links exist; e.g. `?questionId=1624e973-eccc-473e-adb8-144afbe6ac01`). Those deep links 404 on the live site today and Wayback replay is unreliable for them, so the answer was captured via the support page's own indexed text + the 2026-06-08 snapshot. [VERIFIED that the deep-link pattern exists; NOT VERIFIED which uuid is the Classroom item]

### 1.2 Official tutorial video (share dialog walkthrough) [VERIFIED title; NOT VERIFIED dialog contents]

- Official מטח video: **"הסטודיו שלי וניהול הלמידה — כיצד לשתף משימה מאופק לסביבות למידה אחרות כגון קלאסרום"** — https://www.youtube.com/watch?v=EBg33IvJsRE (channel @cetisrael; playlist "ניהול הלמידה וסביבת אופק" https://www.youtube.com/playlist?list=PLYH9I-4V1wQJM_y34BQjsivjUspfS3iD7; 1:09, 1.6K views, ~5 years old; fetched 2026-11-11)
- Companion video in same playlist: **"הסטודיו שלי — היכן אני מוצא את הקישור לשיתוף המשימה לתלמידים"** — https://www.youtube.com/watch?v=abhAnjEp9uE (1:22; fetched 2026-11-11) → the share flow produces **a link to the task**.
- The watch page for EBg33IvJsRE returned "Video unavailable" from this network (likely geo/IP block; playlist metadata still serves), and no login/browser was used, so **what the share dialog literally displays (fields, due-date picker) is NOT VERIFIED.** A transcript service attempt returned HTTP 429.
- Official "הסטודיו שלי" user guide (lo.cet.ac.il document player, doc c94ac286-ee22-478c-bb1b-a189979ccda9) contains pages "עמוד 3: משימות וניהול הלמידה", "עמוד 6: שיתוף הפעילות", "עמוד 8: שאלות (ממש) נפוצות" — https://lo.cet.ac.il/player?document=c94ac286-ee22-478c-bb1b-a189979ccda9&language=he (fetched 2026-11-11). The player is a JS SPA; page bodies not extractable without a browser. [VERIFIED structure; NOT VERIFIED body]

### 1.3 Link-sharing mechanics (community evidence)

- MyTestBox (מטח's high-school exam tool) sharing options per the community tool encyclopedia: "שיוך הפריט לקבוצת הלימוד... משלוח קישור לפריט – התלמיד לא יתבקש להתחבר, המורה לא יקבל מידע על מידת הצלחת התלמיד" (assign to study group; send link — student not asked to log in, teacher gets no success info) — https://digitalpedagogy.co/2020-04-07/my-test-box-יצירת-בחינות-מתוקשבות/ (article 2020-04-07; fetched 2026-11-11) [community]
- A school orientation deck describes the workflow "שיוך משימה מתוקשבת לתלמידים • הסטודיו שלי / BOX TEST – יצירת פעילויות מתוקשבות... + שיוך משימה ובדיקה" — https://static.s123-cdn-static-c.com/uploads/396520/normal_5f2f947243d16.pdf (school presentation; fetched 2026-11-11) [community]

### 1.4 Exactly what appears on the Classroom side — NOT VERIFIED

- No official page documents the metadata mapping. The FAQ answer only says sharing exists "בקליק אחד" (in one click). [NOT VERIFIED]
- Working assumption (inference, **not** a sourced fact): the share creates a standard Classroom item (material/announcement or assignment) carrying **the Ofek activity link plus a teacher-set title/description**. **Due date, grade, and auto-graded/submission state are UNLIKELY to be mirrored** — Ofek remains the system of record (students submit inside Ofek per the official newsletter flow, `ofek.md` Q1).
- Due-date mapping: no screenshot, teacher-forum post, or official doc found. Searches ("אופק classroom מועד הגשה", "הסטודיו שלי classroom שיתוף", site:ebag.cet.ac.il "קלאסרום") returned nothing on the mapping (2026-11-11). [NOT VERIFIED]
- Reference (Classroom side, Google): Classroom assignments support title, instructions, link, due date, point value — https://support.google.com/edu/classroom/answer/6020265?hl=iw (fetched 2026-11-11). So if the Ofek share *does* emit an assignment, any due date set would be a normal Classroom due date. The Ofek-side behavior is the unknown.
- **Can Lumio's student Classroom connector see it?** A standard Classroom item is visible to enrolled students in Classwork/Stream — that is a property of Google Classroom (per the same support doc, assignments appear in the student "מטלות" view). **So: yes in principle — partial automatic unification with zero new credentials for the title+link item.** What the item *is* (assignment vs material vs announcement) and whether a due date is set are NOT VERIFIED, which determines whether Lumio's connector classifies it as an assignment or just a post.

**Verdict O1:** Teacher share to Classroom/Teams = [VERIFIED] official feature (FAQ answer body + tutorial title + guide page "שיתוף הפעילות"). Metadata that survives on the Classroom side (title? link? due date? graded state) = [NOT VERIFIED]; due date/grade mirroring = [UNLIKELY]. Lumio's connector can surface it as a normal Classroom item = [VERIFIED in principle via Google's own docs], exact item type [NOT VERIFIED].

---

## O2. Teacher export (CSV/Excel) and student-side export

**Teacher side — no documented file export. [NOT VERIFIED]**

- No public help page or forum post documents CSV/Excel/PDF download of assignments, grades, or scores from the Ofek teacher portal, ebag.cet.ac.il, or myTestBox.cet.ac.il (searches 2026-11-11: "אופק מטח ייצוא ציונים Excel", "myTestBox ייצוא", site queries on the portal domains — nothing on export formats).
- What IS documented (in-app reports, no download format stated):
  - "הפקת דוחות... דוח מלא לפי תלמידים" — official מטח newsletter, http://cet.activetrail.biz/אופק (older content; fetched 2026-11-11) [VERIFIED, official]
  - Ofek-evaluation environment: "הצגת נתונים על הישגי התלמידים בפילוחים שונים... והפקת דוחות לנמענים מגוונים" — https://ofek.cet.ac.il/eval.aspx (fetched 2026-11-11) [VERIFIED, official]
  - Official "הסטודיו שלי" training series (listed in the lo.cet.ac.il guide) includes "הסבר על דוחות מורה" (teacher-reports walkthrough) in Meet 2 — video https://youtu.be/G5THesOd7h8, listed at https://lo.cet.ac.il/player?document=c94ac286-ee22-478c-bb1b-a189979ccda9&language=he (fetched 2026-11-11) [VERIFIED that reports are taught; format/export NOT VERIFIED]
- The teacher portals are login-walled (myTestBox.cet.ac.il returned empty crawl content — login wall), so any export button can only be confirmed inside the portal. [NOT VERIFIED]

**Student side — no export at all. [NOT VERIFIED / UNLIKELY]**

- No public documentation of any student-facing export/download/share function. [NOT VERIFIED]
- Indirect evidence of what student-side data exists *inside* the logged-in area (no API, no export): an unofficial open-source bot logs in via the MoE SSO and "reads four counters from the Ofek dashboard: tasks to do, tasks to fix, checked tasks, and tasks waiting for review" — https://github.com/t0mer/ofek-bot (repo created 2022-10-26, Apache-2.0, 38 commits; README fetched 2026-11-11) [community, unofficial; requires the student's own credentials; ToU-risk noted by the project itself]

**Verdict O2:** Teacher CSV/Excel export = [NOT VERIFIED] (reports exist in-app; no public evidence of a file export). Student-side export = [NOT VERIFIED / UNLIKELY].

---

## O3. CET/מטח partner & developer programs

**No public API, developer portal, or self-serve integration program. [NOT VERIFIED]**

- Searches (2026-11-11): "מטח ofek API integration", "Matach LTI", "CET partners developers", site:cet.ac.il "edtech/startups/innovation", site:cet-catalogue.cet.ac.il "ספקים/מפתחים/הצטרפו" — no developer portal, no API docs, no "join as a vendor" page.

**MindCET = the innovation arm (accelerator/investor, not an API program). [VERIFIED, official sites]**

- "MindCET is a center for the innovation and development of educational technology, established by the Center for Educational Technology (Metach)." — https://trump.org.il/en/partner/מינדסט (fetched 2026-11-11) [official partner listing]
- "MindCET connects startups, educators, researchers, learners, high-tech industry leaders, investors and policymakers" and "We identify, accelerate and invest in innovative EdTech solutions" — https://mindcet.io/en (fetched 2026-11-11) [official MindCET site]
- Portfolio lists ~30 EdTech startups; Negev HQ; LinkedIn company "Mindcet Labs" (E-learning) — https://mindcet.io/portfolio, https://linkedin.com/company/mindcet--ed-tech-innovation-center (fetched 2026-11-11)
- "בשנת 2012 הוקם MindCET, המרכז לחדשנות ולפיתוח טכנולוגיות בחינוך, מייסודו של מטח. משרדי ההנהלה ממוקמים בירוחם." — https://he.wikipedia.org/wiki/המרכז_לטכנולוגיה_חינוכית (fetched 2026-11-11) [community]

**Vendor channel that does exist: content licensing via the מטח catalogue (not a dev API). [VERIFIED, official]**

- Third-party learning environments are hosted/sold through the catalogue, e.g. MagniLearn ("מידע למלמדים - MagniLearn" with teacher manuals on the catalogue) — https://www.cet-catalogue.cet.ac.il/magnilearn-for-teachers (fetched 2026-11-11) [official]; AcadeMe film library partnership page — https://www.cet-catalogue.cet.ac.il/academe (fetched 2026-11-11) [official]
- Press evidence that external EdTech companies do integrate with Ofek **via partnership, not public API**: CET + eSelf "AI-based private tutor... introduced independently through CET's Ofek platform, not via the ministry... full integration with CET's pedagogical content" — https://ynetnews.com/business/article/skhub3rygx (fetched 2026-11-11) [community/press]

**What a school app would need to ask for / who approves:**

- No public process exists. The only officially published contacts are: customer service **sherut@cet.ac.il**, 03-6460800, 16 Klausner St, Tel Aviv — https://cet.ac.il/contact/?lang=en; technical support **webs@cet.ac.il**, 03-6200622, WhatsApp 054-679-5116 — https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (both fetched 2026-11-11) [VERIFIED, official].
- Realistic path (inference, flagged): commercial/partnership agreement negotiated with מטח (sales/innovation side), with MoE data-protection review for any Tz"uz-linked student data; MindCET is the plausible innovation window. [NOT VERIFIED — no public statement]

**Verdict O3:** No formal public integration path exists [NOT VERIFIED]. Integration happens via negotiated partnership (eSelf precedent) [community/press]. Official contacts identified above [VERIFIED].

---

## O4. Does Ofek USE LTI?

- **No official or vendor evidence that Ofek/מטח uses LTI for login or activity launch. [NOT VERIFIED]**
  - Searches (2026-11-11): "מטח LTI ofek", "ofek cet.ac.il LTI integration", "מטח LTI OneRoster xAPI ישראל" → only generic 1EdTech/IMS spec pages, nothing מטח- or Ofek-specific.
  - Ofek's documented login is MoE unified authentication (Tz"uz), not an LTI flow — https://students.myofek.cet.ac.il/he ("התחברות משרד החינוך — יש להזין מספר ת״ז" — fetched 2026-11-11) [VERIFIED, official, from ofek.md]
- **Would LTI create a standard hook for Lumio?** Only if Ofek (or the MoE virtual-school layer) becomes an LTI 1.3 platform and registers Lumio's tool. Per the 1EdTech LTI Core 1.3 spec, the tool is registered by the platform and its `client_id` is "issued by the learning platform during registration" — https://standards.1edtech.org/lti/specifications/core/lti-spec (fetched 2026-11-11) [standards doc, not Ofek-specific]. **So: as a consumer-side hook, LTI 1.3 requires the institution/platform (מטח or MoE, on behalf of the school) to register Lumio — Lumio cannot self-serve it.** With no evidence Ofek speaks LTI at all, this is currently a dead end; it belongs in the partner email as a roadmap question, not a plan.
- OneRoster/xAPI: still no evidence Ofek exposes or consumes them (unchanged from ofek.md Q4). [NOT VERIFIED]

**Verdict O4:** Ofek using LTI = [NOT VERIFIED] (and [UNLIKELY] short-term, given zero traces + SSO-by-MoE design). Legitimate hook for Lumio = none today; LTI 1.3 as a tool requires platform-side registration by the institution.

---

## O5. Ranked paths for Lumio 4

| # | Path | Evidence line | Student/teacher must do | Exact next action |
|---|------|---------------|------------------------|-------------------|
| **1** | **Classroom-bridge partial auto** (title + link appears in the student's Classroom) | Official FAQ: "פעילויות ששייכת לכיתה או לקבוצה ניתן לשתף בקליק אחד לסביבות חיצוניות" — cet-catalogue.cet.ac.il support page (2026-11-11); tutorial "כיצד לשתף משימה מאופק לסביבות למידה אחרות כגון קלאסרום" — youtube.com/watch?v=EBg33IvJsRE | Teacher: in Ofek/הסטודיו שלי, share the assigned task to the class's Google Classroom (one click per FAQ). Student: nothing — item appears in their existing Classroom. Lumio: existing Classroom connector ingests it as a normal item (zero new credentials) | (a) Pilot with 1–2 teachers: run the share, screenshot the resulting Classroom item (is it an assignment? material? any due date?), confirm Lumio's connector ingests it. (b) Email **webs@cet.ac.il** asking precisely: "כאשר מורה שותף פעילות מאופק לגוגל קלאסרום/Teams, מה בדיוק עובר (קישור בלבד? כותרת? תאריך הגשה? מצב הגשה/ציון?) ואיזו דרך פרסום נוצרת בקלאסרום (מטלה/חומר/הודעה)?" |
| **2** | **Teacher-assisted export** (teacher exports/copies reports → student imports into Lumio) | In-app reports documented: "הפקת דוחות... דוח מלא לפי תלמידים" — cet.activetrail.biz/אופק; "הפקת דוחות לנמענים מגוונים" — ofek.cet.ac.il/eval.aspx (2026-11-11). **File export format itself [NOT VERIFIED]** | Teacher: open per-student report in Ofek/MyTestBox; if an export button exists (Excel/PDF) export it, else copy/screenshot; student or parent pastes key items into Lumio | Bundle into the partner email to **webs@cet.ac.il** (cc **sherut@cet.ac.il**): "האם קיים ייצוא לקובץ (Excel/CSV/PDF) של משימות משויכות וציונים מהאזור של המורה? באיזה פורמט?" Pilot teacher checks the reports screen for an export button and reports back with a screenshot. |
| **3** | **Student manual import** (works today, zero infrastructure) | Student sees assigned tasks inside Ofek ("משימות לתלמיד") — official newsletter, cet.activetrail.biz/אופק; task counters on the student dashboard per community bot — github.com/t0mer/ofek-bot (2026-11-11) | Student (or parent): for each Ofek task, manually add to Lumio: title + Ofek link + due date. ~10–20 sec per task | Product: add an "add task from link" fast path to Lumio (title + URL + due date). No external contact needed. (Do NOT build on the ofek-bot scraping model for the product: it needs the student's SSO credentials and is ToU-risky per the project's own disclaimer.) |
| **4** | **Full auto-sync (API/feed/standards)** | No public API, developer portal, OneRoster/LTI/xAPI surface found in any search (2026-11-11); eSelf precedent shows integration = negotiated partnership — ynetnews.com/business/article/skhub3rygx | Nothing a student/teacher can do; requires מטח/MoE agreement | Single partnership email: **sherut@cet.ac.il** cc **webs@cet.ac.il** — ask (1) API/export/roster availability for a school app, (2) LTI 1.3/OneRoster roadmap, (3) what data a shared Classroom item carries, (4) privacy/MoE approval path for Tz"uz-linked student data. Request a meeting with the innovation side (**MindCET**, mindcet.io) or VP Technology. |

**Recommended sequence:** do #1 pilot + #3 product now (no dependencies); fire the #2/#4 email in the same week; treat #4 as the only path to grades/completion sync and price it as a partnership ask, not a build.

---

## Verdicts (one line each)

- **O1** — Teacher share to Classroom/Teams: [VERIFIED] official (FAQ answer body found: "בהחלט... בקליק אחד לסביבות חיצוניות"; tutorial + guide exist). What survives on the Classroom side: [NOT VERIFIED]; due-date/grade mirroring: [UNLIKELY]; Lumio connector visibility of a resulting Classroom item: [VERIFIED in principle] / exact item type [NOT VERIFIED].
- **O2** — Teacher CSV/Excel export: [NOT VERIFIED] (in-app reports documented, no export format public). Student-side export: [NOT VERIFIED / UNLIKELY].
- **O3** — No public partner/developer program: [NOT VERIFIED]. MindCET = innovation/acceleration arm, not an API program [VERIFIED official site]. Vendor channel = catalogue licensing [VERIFIED]. Contacts: sherut@cet.ac.il / webs@cet.ac.il [VERIFIED].
- **O4** — Ofek uses LTI: [NOT VERIFIED / UNLIKELY]; no hook for Lumio today — LTI 1.3 tool registration requires the institution/platform side [standards fact, 1EdTech spec].
- **O5** — Rank: (1) Classroom-bridge partial auto → (2) teacher-assisted export → (3) student manual import → (4) full auto = unavailable without partner contract.

---

## Source index (accessed 2026-11-11 unless noted)

Official — מטח/CET:
1. https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (support center; FAQ Q+A; contacts)
2. http://web.archive.org/web/20260608060216/https://www.cet-catalogue.cet.ac.il/מרכז-ההדרכה-והתמיכה-של-אופק (snapshot with full FAQ answers incl. Classroom answer)
3. https://www.youtube.com/watch?v=EBg33IvJsRE (official tutorial: share task to Classroom)
4. https://www.youtube.com/playlist?list=PLYH9I-4V1wQJM_y34BQjsivjUspfS3iD7 (official playlist "ניהול הלמידה וסביבת אופק")
5. https://www.youtube.com/watch?v=abhAnjEp9uE (official: where the task share link is)
6. https://www.youtube.com/watch?v=G5THesOd7h8 (official training: teacher reports walkthrough)
7. https://lo.cet.ac.il/player?document=c94ac286-ee22-478c-bb1b-a189979ccda9&language=he (official "הסטודיו שלי" user guide, incl. "שיתוף הפעילות" page)
8. https://ofek.cet.ac.il/eval.aspx (official: in-app reports "הפקת דוחות")
9. http://cet.activetrail.biz/אופק (official newsletter: per-student score reports, student flow)
10. https://cet.ac.il/contact/?lang=en (official contacts)
11. https://www.cet-catalogue.cet.ac.il/magnilearn-for-teachers (official catalogue: third-party vendor environment)
12. https://www.cet-catalogue.cet.ac.il/academe (official catalogue: vendor film-library partnership)
13. https://mindcet.io/en and https://mindcet.io/portfolio (official MindCET site)
14. https://trump.org.il/en/partner/מינדסט (official partner listing: MindCET established by מטח)
15. https://students.myofek.cet.ac.il/he (MoE SSO login, Tz"uz)

Official — Google (Classroom-side mechanics, reference only):
16. https://support.google.com/edu/classroom/answer/6020265?hl=iw (Classroom assignment fields: title, link, due date, grade)

Standards (not Ofek-specific):
17. https://standards.1edtech.org/lti/specifications/core/lti-spec (LTI Core 1.3: platform-issued client_id at tool registration)
18. https://www.imsglobal.org/about/k12/oneroster-and-lti-advantage

Community / third-party (clearly separated):
19. https://github.com/t0mer/ofek-bot (unofficial SSO-scraping bot; student dashboard counters; repo created 2022-10-26)
20. https://digitalpedagogy.co/2020-04-07/my-test-box-יצירת-בחינות-מתוקשבות/ (MyTestBox sharing workflow; article 2020-04-07)
21. https://static.s123-cdn-static-c.com/uploads/396520/normal_5f2f947243d16.pdf (school orientation deck: task-assignment workflow)
22. https://ynetnews.com/business/article/skhub3rygx (CET+eSelf partnership via Ofek; press)
23. https://he.wikipedia.org/wiki/המרכז_לטכנולוגיה_חינוכית (MindCET founding/locations)
24. https://linkedin.com/company/mindcet--ed-tech-innovation-center (MindCET Labs)
