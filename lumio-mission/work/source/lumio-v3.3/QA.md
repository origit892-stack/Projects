# לומיו 3.2 — QA

- בדיקת תחביר Node: עבר.
- 15 בדיקות יחידה: עברו.
- תקינות תוסף Chrome (manifest + JavaScript): עברה.
- קובצי ZIP: נבדקו לאחר יצירה.
- חיבור Supabase: דווח כעובד על ידי המשתמש בגרסה הקודמת; לא נבדק מחדש מול חשבון חי.
- מסלול חדש: תוסף Reader → פתיחת לומיו עם מטלות → אישור מפורש → שמירת נתונים. נבדק סטטית בלבד ולא מול דפי יצרנים חיים.
- סנכרון API אוטומטי של משו״ב, אופק, פטל, שחף ו-Classroom ללא OAuth: לא מאומת ולא פעיל.

## 4.0 — סיכום בדיקות (12.11.2026)
- בדיקת תחביר Node (`node --check`) על app.mjs, connectors.mjs, core.mjs, study.mjs, importers.mjs, server.mjs: עברה.
- בדיקות יחידה `npm test`: 19 בדיקות קודמות + 16 בדיקות חדשות (tests/connectors.test.mjs) — כולן עברו.
- בדיקות סטטיות על deliverables: apps-script/classroom-sync.gs (3 קריאות שירות Classroom, 2 קבועי placeholder בלבד, טריגר יומי), README-HE.md, שני ה־Edge Functions (קריאת env בלבד, ללא סודות), supabase-functions/README-HE.md (pg_cron + הערת anti-pause).
- בדיקת server: `PORT=5199 node server.mjs` → HTTP 200 ב־`/`.
- Edge Functions, Apps Script ו־pg_cron: **לא** נבדקו מול שרתים חיים — דורשים פריסה על ידי המשתמש (ראו supabase-functions/README-HE.md ו־apps-script/README-HE.md).
- הממיר של דפי שחף: נבדק על fixtures סינתטיים בלבד; הצורה אומתה מול דפי שחף מפורסמים (katzir/dror/katzir-a, 12.11.2026). אין נתוני תלמיד אמיתיים בפרויקט.
