/**
 * לומיו 4.0 — סנכרון יומי אוטומטי של Google Classroom (Apps Script)
 * ================================================================
 * הסקריפט רץ בפרויקט Apps Script שלך, בחשבון Google שלך. הוא:
 *  - קורא בלבד את הקורסים, המטלות וההגשות שלך (שירות Classroom הרשמי).
 *  - שולח את תוצאת הקריאה לחשבון לומיו שלך בלבד, דרך מפתח הסנכרון.
 *  - אינו מכיל סיסמאות, מפתחות שירות או service_role. אין כאן JWT ואין
 *    refresh token — המפתח הוא מזהה בלבד, שניתן לסובב/לבטל בלומיו.
 *
 * עלויות: 0 ₪. זה רץ על תשתית גוגל — עובד גם כשהמחשב כבוי.
 * מכסות (מוגדרות על ידי גוגל, נבדקו 2026-11-12):
 *  - עד 20 טריגרים לפרויקט (אנחנו משתמשים ב־1)
 *  - עד 90 דקות של זמן ריצה ביום
 *  - עד 20,000 קריאות URLFetch ביום
 *
 * הוראות מלאות: apps-script/README-HE.md
 */

// ---- שני קבועים בלבד שאתה מלאה (ערכי הדוגמה בלבד — אין כאן ערכים אמיתיים) ----
const LUMIO_FN_URL = 'https://YOUR-PROJECT.functions.supabase.co/apps-script-ingest';
const LUMIO_SYNC_KEY = 'PASTE-YOUR-LUMIO-SYNC-KEY';

/**
 * יוצר טריגר יומי אחד (06:00). בטוח להרצה חוזרת — מוחק קודם את כל הטריגרים
 * הקודמים של הפונקציה sync, כך שלא תיווצר כפילות.
 */
function setup(){
  const existing = ScriptApp.getProjectTriggers().filter(function(t){ return t.getHandlerFunction() === 'sync'; });
  for (let i = 0; i < existing.length; i++) ScriptApp.deleteTrigger(existing[i]);
  ScriptApp.newTrigger('sync').timeBased().everyDays(1).atHour(6).create();
}

/**
 * הסנכרון עצמו: קורא את Classroom ושולח ללומיו.
 * נקרא אוטומטית על ידי הטריגר היומי; אפשר להריץ ידנית מפעם לפעם.
 */
function sync(){
  const courses = (Classroom.Courses.list({maxResults: 100}).courses) || [];
  const items = [];
  for (let i = 0; i < courses.length; i++) {
    const course = courses[i];
    try {
      const works = (Classroom.Courses.courseWork.list(course.id, {maxResults: 100}).courseWork) || [];
      let submissions = [];
      try {
        submissions = (Classroom.Courses.courseWork.studentSubmissions(course.id, 'me', {maxResults: 100}).studentSubmissions) || [];
      } catch (e) {
        submissions = []; // אין הגשות (או אין הרשאה) — ממשיכים בלי סטטוס
      }
      const subById = {};
      for (let s = 0; s < submissions.length; s++) subById[submissions[s].courseWorkId] = submissions[s];
      for (let w = 0; w < works.length; w++) {
        const work = works[w];
        // שמרנים: מטלות, אוצר מילים וחומרי קורס בלבד
        if (['ASSIGNMENT', 'VOCABULARY', 'COURSE_MATERIAL'].indexOf(work.workType) === -1) continue;
        const sub = subById[work.id] || {};
        const title = String(work.title || '').slice(0, 240);
        if (!title) continue;
        const courseTitle = String(course.name || '').slice(0, 100);
        items.push({
          kind: 'task',
          external_id: course.id + ':' + work.id,
          title: title,
          course_title: courseTitle,
          due_at: dueISO(work.dueDate), // תאריך בלבד → סוף יום בשעון ישראל, ללא החלפת יום
          status: (sub.state === 'TURNED_IN' || sub.state === 'RETURNED') ? 'done' : 'todo',
          source: 'classroom'
        });
        // ציון שניתן — רק אם קיים ובטווח 0–100
        const grade = sub.assignedGrade;
        if (grade != null && String(grade).trim() !== '') {
          const score = Number(grade);
          if (isFinite(score) && score >= 0 && score <= 100) {
            items.push({
              kind: 'grade',
              external_id: 'grade:' + course.id + ':' + work.id,
              title: 'ציון: ' + title,
              course_title: courseTitle,
              score: score,
              source: 'classroom'
            });
          }
        }
      }
    } catch (e) {
      Logger.log('course skipped: ' + course.id + ' — ' + e.message);
    }
  }
  postToLumio(items);
}

/**
 * תאריך Classroom ({year,month,day}, שעון ישראל) → ISO.
 * שומר את התאריך כ־"שעון-ישראל-כ־UTC" (T00:00:00Z) — בדיוק כמו core.mjs באתר,
 * כך ששני מסלולי הסנכרון כותבים את אותו ערך ולא משנים יום.
 */
function dueISO(d){
  if (!d || !d.year || !d.month || !d.day) return null;
  const iso = d.year + '-' + String(d.month).padStart(2, '0') + '-' + String(d.day).padStart(2, '0');
  return iso + 'T00:00:00Z';
}

/**
 * שליחה ללומיו. נסיון חוזר אחד על תשובת 5xx (עם המתנה קצרה).
 * הערה: ל־URLFetchApp אין פרמטר timeout; ברירת המחדל של גוגל היא כ־20 שניות.
 * 401/404 = המפתח או הכתובת אינם תקינים → רושם LUMIO_BINDING_INVALID.
 */
function postToLumio(items){
  const payload = JSON.stringify({key: LUMIO_SYNC_KEY, items: items});
  const opts = {method: 'post', headers: {'Content-Type': 'application/json'}, payload: payload, muteHttpExceptions: true};
  let res;
  try {
    res = UrlFetchApp.fetch(LUMIO_FN_URL, opts);
    if (res.getResponseCode() >= 500) {
      Utilities.sleep(2000); // ניסיון חוזר אחד
      res = UrlFetchApp.fetch(LUMIO_FN_URL, opts);
    }
  } catch (e) {
    Logger.log('network error: ' + e.message);
    return;
  }
  const code = res.getResponseCode();
  if (code === 401 || code === 404) Logger.log('LUMIO_BINDING_INVALID');
  else if (code >= 200 && code < 300) Logger.log('sync ok, items=' + items.length);
  else Logger.log('lumio responded ' + code);
}
