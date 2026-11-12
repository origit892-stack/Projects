# 09 — Blockers & Actionable Requests

> **תיקון (12.11.2026, בעקבות בדיקה חיה):** כתובת שחף העובדת של בית הספר היא
> **`katzirb.shahaf.site`** (ללא מקף) — היא **מפרסמת את מערכת השעות** ובדיקה חיה
> נלקחה בהצלחה (39 שיעורים, timestamp "מעודכן ל: 11.11.2026"). כל שורה במסמך הזה
> שאומרת "katzir-b.shahaf.site אינו פועל" הייתה נכונה לכתובת שהבחנו אז, אך
> הכתובת המתקנת היא katzirb — ולכן חוסם "המחכה לפרסום" **הוסר**.

Each blocker: what blocks it, why alternatives were exhausted, and ONE focused ask (letters ready to send, no personal data included).

## C1 — Classroom in-app flow: admin OAuth client (process blocker, free)
**What:** the in-app "חבר Google" sync needs a Google OAuth client registered for Lumio (Google Workspace auth requirements — verified; no legitimate third-party-client workaround exists without violating ToS or misrepresenting the app).
**Exhausted alternatives:** Apps Script path (implemented — works WITHOUT any admin action), calendar export (partial data only), no-API paths (n/a — the API exists, only the client registration is missing).
**Ask (user action, ~20 min, free):** Google Cloud Console → new project → enable Classroom API → OAuth consent screen (External, testing mode, add the student test users) → OAuth Client ID (Web, JS origin `https://<your-cloudflare-domain>`, redirect `https://<domain>/`) → put the client_id in `config.mjs` (`config.google`). Testing-mode consent expires ~7 days — for a real pilot request verification.

## C2 — Mashov: no official student API (documented dead-end, not a bug)
**What:** exhaustive sweep (89 GitHub repos, npm/PyPI, official sites, Hebrew+English search, 2026-11-11/12) found NO official API, partner program, or export surface for students; the SSO button is login-only (IDM/EduLogin), no delegated authorization; no tool can read Mashov without the student's own password.
**Status:** Lumio offers `manual_import_only` + neutral `user_local_import` documentation (student's own machine, own account, own file).
**Ask (optional, long-term):** letter B2 below to Mashov support asking about a partner/integration program or a student export (CSV/ICS) for grades+homework.

### Letter B2 (Hebrew, ready to send)
> שלום, אנו פונים מטעם פרויקט לימודי לתלמידים ("לומיו") המשלב משימות ומבחנים ממקורות שונים במקום אחד, בהסכמת כל תלמיד בנפרד. אנו מחפשים מסלול רשמי ומוּרשֶׁה לקריאת נתונים לימודיים של תלמיד (משימות, ציונים, מערכת שעות) עבור אפליקציה פרטית ששומרת את הנתונים רק בחשבון של אותו תלמיד (Supabase, RLS). שאלות: (1) קיים API רשמי או תוכנית שותפים לגישה לימודית? (2) קיים ייצוא אישי (CSV/ICS) של משימות וציונים דרך הפורטל? (3) האם כפתור "הזדהות משרד החינוך" יכול להפוך ל-delegated authorization לנתונים (OIDC/SAML) עבור רישום אפליקציה מורשית, ואם כן מה תנאי הסף? לא נשמור סיסמאות ולא נבצע חיבור ישיר לאתר. תודה.

## C3 — Ofek: what survives in the Classroom share (1-teacher pilot)
**What:** the Ofek→Classroom teacher share is an OFFICIAL one-click feature (verified), but the exact payload on the Classroom side (due date? grade? item type?) is NOT verified.
**Ask:** 1-2 teachers share an Ofek task to the class Google Classroom; screenshot the resulting item; confirm Lumio ingests it.

### Letter B3-ofek (Hebrew, to webs@cet.ac.il, cc sherut@cet.ac.il)
> שלום, בהקשר של פרויקט תלמידים המשלב משימות ממערכות שונות: כאשר מורה שותף פעילות מאופק לגוגל קלאסרום (לפי ההנחיה הרשמית), מה בדיוק עובר לקלאסרום — קישור בלבד, כותרת, תאריך הגשה, מצב הגשה/ציון? ואיזו דרך פרסום נוצרת (מטלה/חומר/הודעה)? נשמח לדוגמה מסונתזת. כמו כן: האם קיים ייצוא לקובץ (CSV/Excel/PDF) של משימות משויכות וציונים מאזור המורה, ובאיזה פורמט?

## C4 — PeTeL: ICS visibility + optional Web Services
**What:** the ICS feed path is implemented; whether the PeTeL installation exposes the personal calendar share to students is not verifiable without a student session (admin can disable `enablecalendarexport`).
**Ask (student, 1 min):** in PeTeL → יומן → look for a share/ICS link; if present, connect it in Lumio ("חבר פיד ICS"). If absent:

### Letter B3 (Hebrew, to petel@weizmann.ac.il)
> שלום, אנו פונים בשאלה ממערכת תלמידים: האם ניתן לתלמיד לקבל קישור ICS אישי ליומן (Moodle calendar subscription) כדי לצפות בו בכלי לוח שנה חיצוני, ובמה נדרש אישור? כמו כן, האם פטל מפעילה Moodle Web Services (External Services) עבור צרכנים מורשים, ואם כן מהי פניית הפתיחה — אנו עוסקים בקריאה של נתוני התלמיד עצמו בלבד, בהסכמתו, בלי שימור נתונים חוץ מחשבון הפרטי שלו. תודה.

## C5 — ~~Shahaf: Katzir B-track timetable not published~~ — **RESOLVED 2026-11-12**
**Status:** the school's working Shahaf subdomain is **`katzirb.shahaf.site`** (no hyphen) and it **is publishing** the full timetable — live fetch verified 2026-11-12 (39 periods parsed, stamp "מעודכן ל: 11.11.2026", `?cls=N` selects the class). The earlier 404 on `katzir-b.shahaf.site` was a wrong-guess subdomain, not a real blocker. The Ofek-extension-era assumption ("await publication") is obsolete; the admin letter B4 is retired (kept for other schools that truly do not publish). The connector is wired in-app: paste `https://katzirb.shahaf.site/` (optionally `?cls=N`), "בדוק פיד" — and once the Supabase scheduler is live, it refreshes automatically server-side (pg_cron → feed-sync), PC off.

## C6 — Ministry of Education IDM: SP registration is vendor-gated (process blocker)
**What:** an official SP/IDM connection path EXISTS (sapakim.education.gov.il/tech/idm — SAML/OIDC/federation) but it is for MoE-approved vendors with forms + security review (GR_IDM_Team@education.gov.il); there is no self-service individual registration. "ED-DATA" as a public student-data API: no such official system found. MoE LRS: vendor→MoE telemetry push only, no read access.
**Conclusion:** MoE SSO in Lumio = future, vendor-approval-gated. Lumio 4.0 honestly does not claim it.

### Letter B1 (Hebrew, to GR_IDM_Team@education.gov.il — optional, months-long path)
> שלום, אנו פונים מטעם פרויקט לימודי לתלמידים ("לומיו") שפותח בישראל, המציע לכל תלמיד חשבון פרטי המשלב משימות ומבחנים ממקורות שונים. אנו מעוניינים ברישום האפליקציה כ-Service Provider מורשה במערכת הזדהות מרכזית (IDM) של משרד החינוך, כך שתלמידים יזדהו ב-IDM וקבלו הרשאת קריאה מינימלית לנתוני המטלות שלהם בלבד (אבטחה: Supabase RLS, שמירה רק בחשבון התלמיד, מינימום הרשאות, אפשרות ביטול/מחיקה מלאה). שאלות: (1) מה תנאי הסף לרישום ספק פרטי (חברה/עמותה/פרט)? (2) קיימת סביבת sandbox לבדיקות? (3) אילו טפסים/אישורי אבטחה נדרשים, וכמה זמן תהליך? אנו מוכנים לספק מפרט טכני (scopes, redirect URIs, סוגי נתונים). תודה.

## User actions summary (in order)
1. Run the 3 SQL files in Supabase (backup first): `database.sql` (done), `database-upgrade.sql` (adds school_items — **still pending in the live project**), `database-upgrade-2.sql` (new 4.0 columns).
2. Deploy the 2 Edge Functions + pg_cron (supabase-functions/README-HE.md).
3. Upload to Cloudflare Pages (Direct Upload).
4. Classroom: either C1 (admin client) or per-student Apps Script (apps-script/README-HE.md) — or both.
5. Optional letters B1-B4 as appropriate (C2/C3/C4/C5 above).
