# Edge Functions של לומיו 4.0 — פריסה (Hebrew)

שני Edge Functions (Deno) שפונים לפרויקט Supabase **שלך**. אף סוד אינו נשמר
במשתנה git — המפתחות מוגדרים ב־dashboard.

## 1) `apps-script-ingest` — קלט לסנכרון ה־Apps Script היומי
קובץ: `supabase-functions/apps-script-ingest/index.ts`

## 2) `feed-sync` — רענון פידים (ICS / שחף) מתזמון pg_cron
קובץ: `supabase-functions/feed-sync/index.ts`

## צעדי פריסה (לכל פונקציה)
1. פתח את דשבורד Supabase שלך → **Edge Functions** → **New function**.
2. שם: `apps-script-ingest` (או `feed-sync`). הדבק את תוכן ה־index.ts המתאים.
3. הגדר סוד — ב־dashboard: **Project Settings → API / Secrets** (או
   `supabase secrets set`) הוסף:
   - `SUPABASE_SERVICE_ROLE_KEY` — מהגדרות הפרויקט שלך (המפתח **הסודי** שלך;
     לעולם לא במשתנה git). `SUPABASE_URL` מוזרק אוטומטית על ידי הרץ.
   - **רק `feed-sync`**: `LUMIO_CRON_TOKEN` — שרשרת אקראית (למשל
     `openssl rand -hex 24`) שמוגדרת כ־secret לפונקציה; בלי התאמה שלה הפונקציה
     מסרבת לרוץ (401). חייבים להגדיר, אחרת שום מינימליזם אחר לא מספיק.
4. Deploy. בדיקה: POST ל־`https://<ref>.functions.supabase.co/apps-script-ingest`
   עם `{key:"", items:[]}` צריך להחזיר 401 `LUMIO_BINDING_INVALID` (כלומר זה חי).

## תזמון pg_cron ל־feed-sync (רצוי, לא חובה)
ב־SQL Editor:
```sql
create extension if not exists pg_cron;
select cron.schedule(
  'lumio-feed-sync',
  '15 6 * * *',
  $$select net.http_post(url:='https://<ref>.functions.supabase.co/feed-sync',
    headers:=jsonb_build_object('x-lumio-cron','<CRON_TOKEN>'))$$
);
```
(אלטרנטיבה: שורת schedule בדשבורד → Database → Schedulers, אם הגרסה תומכת.)

## הערה כנה — fallback
אם pg_cron אינו זמין במנוי שלך: כפתורי **"רענן פיד"** באתר הם ה־fallback —
הם מבצעים את אותו upsert בדיוק, ומוצגים כך. אין סנכרון אוטומטי בלי הפעלה זו.

## הערה כנה — auto-pause (השהיה אוטומטית)
פרויקט Supabase חינמי עשוי להישהה (**auto-pause**) אחרי תקופה של פעילות נמוכה,
וגם אם הוא משהה — pg_cron **נעצר**. הפונקציה כותבת למסד הנתונים בכל ריצה,
ולכן כל פיד פעיל משמש "heartbeat" שממשיך את הפעילות ומונע השהיה. אם הפרויקט
מושהה בכל זאת, הסנכרון היומי יפסיק עד שהפרויקט יתעורר (כל שימוש בדשבורד מעורר
אותו); בינתיים הפידים ממשיכים לעבוד דרך כפתורי "רענן פיד" באתר.

## מה כל פונקציה רואה / כותבת
- `apps-script-ingest`: קוראת **רק** את שורת `connections` עם `apps_script_key`
  (unique); כותבת **רק** לתוך `user_id` של אותה שורה. `user_id` מתקבל מ־key
  שיוצר בעל החשבון עצמו (אי־אפשר להפיק key של אחר) — אינו מאומת מול Auth.
  קלט מגודל (1.5MB) ו־due_at עובר אימות תאריך.
- `feed-sync`: קוראת את כל `connections` עם `feed_url`; שולפת כל כתובת
  (20s, 2MB cap); upsert עם אותו dedup-key של האתר — לעולם לא מכפיל.
