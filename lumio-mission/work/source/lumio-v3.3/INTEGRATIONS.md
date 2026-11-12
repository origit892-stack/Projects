# מפת חיבורים — לומיו 3.1 (11.11.2026)

מוגדר מראש: קציר ב׳, רחובות, שכבה ט׳, כיתה 5. כל משתמש יכול לשנות את בית הספר והכיתה בפרופיל.

| מערכת | מצב בגרסה | פעולה שניתן לבצע | מה לא פועל ללא אישור נוסף |
|---|---|---|---|
| Google Classroom | ייבוא ICS/CSV/JSON ופתיחת האתר; קוד API מותנה ב-OAuth | אירועים ומועדים שנכללים בייצוא Calendar, או API לאחר הגדרת Client ID | קריאה חיה ללא Google OAuth; נתוני מטלות ללא מועד לא יופיעו בקובץ יומן |
| משו״ב | פתיחת אתר + ייבוא JSON/CSV/ICS/טקסט | העברה לחשבון לומיו של מידע שהתלמיד מורשה לייצא או לשתף | סנכרון אוטומטי דרך הזדהות משרד החינוך; ספריית pymashov לא מממשת SSO רשמי |
| אופק | פתיחת אתר + ייבוא | משימות שהמשתמש משתף או מייצא | קריאה אוטומטית מוכחת |
| פטל | פתיחת אתר + ייבוא | משימות שהמשתמש משתף או מייצא | Moodle API לא מאושר ולא אומת לשרת פטל |
| שחף | בחירת כיתה + ייבוא | קובצי פרסום מורשים של בית הספר אם מתקבלים | כתובת המידע של קציר ב׳ ואישור שימוש לא נמצאו |

## מסמכים שאומתו
- Classroom OAuth: https://developers.google.com/workspace/classroom/guides/auth
- Classroom Takeout: https://support.google.com/edu/classroom/answer/10204459
- Calendar Export ICS: https://support.google.com/calendar/answer/37111
- Shahaf public publishing: https://wiki.iscool.co.il/יצירת_אתר.ashx
- Shahaf website connection: https://wiki.iscool.co.il/חיבור_מערכת_שעות_שחף_לאתר_אינטרנט.ashx
- Mashov community code (requires direct credentials, **not** implemented here): https://github.com/t0mer/pymashov

## אבטחה והתאמה לטלפון
- אין איסוף סיסמאות, עוגיות או טוקנים ממשרד החינוך.
- כל ייבוא נשמר ב-Supabase בתוך חשבון התלמיד; יש לבדוק RLS לכל טבלה לפני הפצה רחבה.
- ייבוא ICS/CSV/JSON מתבצע מקומית בדפדפן, וממשיך לעבוד בטלפון ללא תוסף Chrome.
- ייבוא איננו סנכרון אוטומטי; קובץ ICS מיוצא הוא תמונת מצב בזמן הייצוא. סנכרון חוזר מצריך ייצוא חוזר.
- לפני פרסום מערכת לקטינים נדרשים ביקורת אבטחה, מדיניות פרטיות והסדרת הרשאות.


## 4.0 - Connector implementation status (12.11.2026)
| Provider | Default state in 4.0 | Live path | Background sync | Source of claim |
|---|---|---|---|---|
| classroom | `awaiting_consent` (OAuth client set) / `manual_import_only` | official API (OAuth) | student-owned Apps Script → `apps-script-ingest` | research reports (FINAL) |
| mashov | `manual_import_only` | user import (no official API) | none | research reports (FINAL) |
| ofek | `manual_import_only` | user import; teacher share → Classroom bridge | none | research reports (FINAL) |
| petel | `manual_import_only` + feed `ics_url` | personal ICS feed (user-authorized) | on-demand "רענן פיד" / future cron | research reports (FINAL) |
| shahaf | `not_connected` (public_page connector, generic for `*.shahaf.site`) | public page feed when school publishes (Katzir B: not published, 404 verified 12.11.2026) | none (stamp-driven, 15–30 min) | research reports (FINAL) |

<!-- RESEARCH-REFS -->
- Mashov, Ofek, PeTeL: user-initiated Chrome extension reads user-visible page elements and supports one-click handoff into Lumio, requiring confirmation. Not automatic background sync and not validated against live school pages.
- Shahaf: same reader if timetable is visible in browser; Android app itself is not accessible to this extension.
- Classroom: existing official API client remains dependent on OAuth client registration and user consent. No shortcut using Ministry-of-Education session.
- Cloud account / Android / iOS: imported items are saved in the user's existing Supabase account and appear across devices after import.
