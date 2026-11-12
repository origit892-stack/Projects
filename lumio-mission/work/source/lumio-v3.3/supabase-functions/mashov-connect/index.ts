// Lumio 4.3 — mashov-connect: on-demand Mashov fetch with TRANSIENT login.
//
// The student types their OWN Mashov credentials into the app (phone or PC).
// This function performs ONE login against Mashov's own (undocumented) web API
// — the same API the Mashov web app uses (flow per t0mer/pymashov, Apache-2.0,
// verified against its docs 2026-11-12) — fetches homework / grades /
// timetable for the account's students, upserts the rows under the student's
// Lumio account, and DISCARDS everything else.
//
// Iron rule compliance: the password and the session cookies are held in
// memory for the duration of the request ONLY. They are never written to the database,
// never logged, never stored in secrets. No stored credential ⇒ no
// server-side re-login possible; the honest UI says the next refresh asks for
// the password again (or the optional PC script does it hands-free).
//
// Endpoint (student JWT, verify_jwt=true):
//   POST /functions/v1/mashov-connect
//   { "username": "...", "password": "...", "school": "name or semel", "year": "2027" }
//   → { ok, students, homework, grades, timetable } | { ok:false, error }
//
// No secrets in this file: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are
// injected by the Supabase runtime. MASHOV_BASE_URL is an optional override
// (used in integration tests against an echo endpoint; default = production).

import { createClient } from 'npm:@supabase/supabase-js@2';

const T = 20_000; // per-request timeout (ms)
const MAX_BODY = 2_000_000;

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

// tiny deterministic id helper (no crypto needed)
function h(s: string): string {
  let x = 5381;
  for (let i = 0; i < s.length; i++) x = ((x << 5) + x + s.charCodeAt(i)) >>> 0;
  return x.toString(16);
}

const HE_DAYS: [string, number][] = [['ראשון', 0], ['שני', 1], ['שלישי', 2], ['רביעי', 3], ['חמישי', 4], ['שישי', 5], ['שבת', 6]];
function normDay(v: unknown): number | null {
  if (typeof v === 'number' && Number.isInteger(v) && v >= 0 && v <= 6) return v;
  const s = String(v ?? '').toLowerCase();
  for (const [name, d] of HE_DAYS) if (s.includes(name)) return d;
  const n = Number(s);
  return Number.isInteger(n) && n >= 0 && n <= 6 ? n : null;
}
// → YYYY-MM-DD (date portion only) or null; accepts ISO, dd.mm.yyyy, dd/mm/yyyy
function normDate(v: unknown): string | null {
  if (v == null) return null;
  const s = String(v).trim();
  if (!s) return null;
  const iso = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (iso) return `${iso[1]}-${iso[2]}-${iso[3]}`;
  const eu = s.match(/^(\d{1,2})[./](\d{1,2})[./](\d{4})/);
  if (eu) return `${eu[3]}-${eu[2].padStart(2, '0')}-${eu[1].padStart(2, '0')}`;
  return null;
}

async function getJson(url: string, headers: Record<string, string>): Promise<{ status: number; data: unknown }> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), T);
  try {
    const res = await fetch(url, { headers, signal: ctrl.signal, credentials: 'omit' });
    const text = await res.text();
    if (text.length > MAX_BODY) return { status: 500, data: null };
    try { return { status: res.status, data: JSON.parse(text) }; }
    catch { return { status: res.status, data: null }; }
  } finally {
    clearTimeout(timer);
  }
}

function pickArr(d: unknown): Record<string, unknown>[] {
  if (Array.isArray(d)) return d as Record<string, unknown>[];
  if (d && typeof d === 'object') {
    const o = d as Record<string, unknown>;
    for (const k of ['items', 'students', 'homework', 'grades', 'timetable', 'lessons', 'results']) {
      if (Array.isArray(o[k])) return o[k] as Record<string, unknown>[];
    }
  }
  return [];
}

Deno.serve(async (req: Request) => {
  const supabaseUrl = Deno.env.get('SUPABASE_URL');
  const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!supabaseUrl || !serviceKey) return json({ ok: false, error: 'SERVER_NOT_CONFIGURED' }, 500);
  const BASE = (Deno.env.get('MASHOV_BASE_URL') || 'https://web.mashov.info').replace(/\/$/, '');

  // student JWT only (gateway-verified); this path has no cron mode — a
  // transient login can never run without the student's fresh credentials.
  const m = (req.headers.get('authorization') || '').match(/^Bearer (.+)$/);
  let studentId: string | null = null;
  if (m) {
    try {
      const b64 = m[1].split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4)), c => c.charCodeAt(0))));
      if (typeof payload.sub === 'string') studentId = payload.sub;
    } catch { /* malformed → 401 below */ }
  }
  if (!studentId) return json({ ok: false, error: 'UNAUTHORIZED' }, 401);

  let body: Record<string, unknown> = {};
  try { body = await req.json(); } catch { return json({ ok: false, error: 'BAD_BODY' }, 400); }

  const username = String(body.username ?? '').trim().slice(0, 60);
  const password = String(body.password ?? '');
  const schoolQ = String(body.school ?? '').trim().slice(0, 80);
  const semelDirect = /^\d{4,7}$/.test(schoolQ) ? schoolQ : null;
  if (!username || !password) return json({ ok: false, error: 'MISSING_CREDENTIALS' }, 400);
  if (password.length > 100) return json({ ok: false, error: 'CREDENTIALS_TOO_LONG' }, 400);
  // NOTE: from here on, username/password/cookies are deliberately absent from
  // every log line and every DB write. Only counts and error codes travel out.
  try {
    // 1) resolve the school's semel (public, unauthenticated endpoint)
    let semel = semelDirect;
    if (!semel) {
      const s = await getJson(BASE + '/api/schools', { Accept: 'application/json' });
      const list = pickArr(s.data);
      const q = schoolQ.toLowerCase();
      const hit = q
        ? list.find(x => JSON.stringify(x).toLowerCase().includes(q))
        : null;
      if (!hit) return json({ ok: false, error: 'SCHOOL_NOT_FOUND', hint: 'הזן את שם בית הספר (או קוד סמ"ל של 4–7 ספרות).' }, 400);
      semel = String(hit.semel ?? hit.code ?? hit.id ?? '').trim();
      if (!/^\d{4,7}$/.test(semel)) return json({ ok: false, error: 'SCHOOL_SEMEL_MISSING' }, 400);
    }
    // 2) academic year (Israeli school year starts in September)
    const d = new Date();
    const year = String(body.year ?? (d.getMonth() >= 8 ? d.getFullYear() + 1 : d.getFullYear()));
    // 3) single login attempt against Mashov's own web API
    const li = await fetch(BASE + '/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ username, password, semel, year }),
    });
    const csrf = li.headers.get('x-csrf-token');
    let setCookies: string[] = [];
    try { setCookies = (li.headers as Headers).getSetCookie ? (li.headers as Headers).getSetCookie() : []; } catch { setCookies = []; }
    if (!setCookies.length) {
      const sc = li.headers.get('set-cookie');
      if (sc) setCookies = sc.split(/,(?=\s*[A-Za-z0-9._~-]+=)/).map(x => x.trim());
    }
    if (!li.ok || !csrf || setCookies.length === 0) {
      return json({ ok: false, error: li.ok ? 'LOGIN_NO_SESSION' : 'LOGIN_FAILED', hint: 'פרטי משו״ב אינם תקפים — בדוק משתמש/סיסמה ובית ספר.' }, 401);
    }
    const cookie = setCookies.map(c => c.split(';')[0]).join('; ');
    const H: Record<string, string> = { Accept: 'application/json', Cookie: cookie, 'x-csrf-token': csrf };
    // login response body: { credential: <user record>, accessToken: <...> }
    // (shape verified against Mashov's own web app bundle 2026-11-12)
    let bodyObj: Record<string, unknown> = {};
    try { bodyObj = (JSON.parse(await li.text()) || {}) as Record<string, unknown>; } catch { bodyObj = {}; }
    if (bodyObj.mfaChallengeId || bodyObj.requiresMfa) {
      return json({ ok: false, error: 'MFA_REQUIRED', hint: 'חשבון משו״ב שלכם דורש אימות שני (MFA) — חיבור מהאפליקציה לא תומך בזה עדיין. אפשרי: סקריפט סנכרון במחשב או ייבוא ידני.' }, 401);
    }
    const credential = (bodyObj.credential || {}) as Record<string, unknown>;
    if (!Object.keys(credential).length) {
      return json({ ok: false, error: 'LOGIN_FAILED', hint: 'פרטי משו״ב אינם תקפים — בדוק משתמש/סיסמה ובית ספר.' }, 401);
    }
    // 4) discover the account's students:
    //    student account → the credential itself holds studentGuid;
    //    parent account  → /api/user/bindings lists the children.
    const idOf = (o: Record<string, unknown>): string =>
      String(o.studentGuid ?? o.student_guid ?? o.guid ?? o.studentId ?? o.id ?? o.idNumber ?? '').trim();
    let students: Record<string, unknown>[] = [];
    const credId = idOf(credential);
    if (credential.studentGuid || credential.guid) students.push(credential);
    else if (credId) students.push({ id: credId, name: credential.fullName ?? credential.name, idNumber: credential.idNumber });
    if (!students.length) {
      const r = await getJson(BASE + '/api/user/bindings', H);
      if (r.status === 200) for (const b of pickArr(r.data)) { const s2 = idOf(b); if (s2) students.push({ id: s2, name: b.fullName ?? b.name, ...b }); }
    }
    if (!students.length) {
      const r = await getJson(BASE + '/api/user/details', H);
      if (r.status === 200) {
        const d = (r.data && typeof r.data === 'object' && !Array.isArray(r.data) ? r.data as Record<string, unknown> : {});
        for (const k of ['students', 'children', 'bindings']) {
          if (Array.isArray(d[k])) for (const b of d[k] as Record<string, unknown>[]) { const s2 = idOf(b); if (s2) students.push({ id: s2, name: b.fullName ?? b.name, ...b }); }
        }
        const s2 = idOf(d);
        if (s2) students.push(d);
      }
    }
    if (!students.length) {
      for (const p of ['/api/students', '/api/me/students', '/api/user/students']) {
        const r = await getJson(BASE + p, H);
        if (r.status === 200) { const arr = pickArr(r.data); if (arr.length) { students = arr; break; } }
      }
    }
    if (!students.length) return json({ ok: false, error: 'NO_STUDENTS_FOUND', hint: 'התחברת בהצלחה אך לא זוהו תלמידים לחשבון.' }, 400);
    // 5) fetch per student — defensive shape handling (undocumented API drifts)
    const now = new Date().toISOString();
    const taskRows: Record<string, unknown>[] = [];
    const schoolRows: Record<string, unknown>[] = [];
    let nHw = 0, nGr = 0, nTt = 0;
    for (const st of students.slice(0, 3)) {
      const sid = idOf(st);
      if (!sid) continue;
      // homework → tasks
      try {
        const r = await getJson(BASE + `/api/students/${encodeURIComponent(sid)}/homework`, H);
        for (const it of pickArr(r.data).slice(0, 200)) {
          const title = String(it.title ?? it.name ?? it.description ?? '').trim().slice(0, 200);
          if (!title) continue;
          const subject = String(it.subject ?? it.matzav ?? '').trim().slice(0, 100);
          const due = normDate(it.due_date ?? it.date ?? it.due_at ?? it.deadline ?? null);
          nHw++;
          taskRows.push({
            user_id: studentId, source: 'mashov',
            external_id: `mashov:hw:${sid}:${String(it.id ?? h(title + subject + String(due)))}`.slice(0, 200),
            title: (subject ? `${subject} — ` : '') + title,
            subject, description: String(it.instructions ?? it.details ?? it.note ?? '').slice(0, 2000),
            due_at: due, source_url: `${BASE}/students/main/homework`,
            retrieval_method: 'unofficial_api', verification_state: 'live_verified',
            synced_at: now, updated_at: now,
          });
        }
      } catch { /* per-endpoint failure never sinks the whole connect */ }
      // grades → school_items(kind=grade) — try the direct grades endpoint,
      // then gradingPeriods (both exist in the Mashov API surface)
      try {
        let g: unknown = null;
        const rg = await getJson(BASE + `/api/students/${encodeURIComponent(sid)}/grades`, H);
        if (rg.status === 200 && pickArr(rg.data).length) g = rg.data;
        else {
          const rg2 = await getJson(BASE + `/api/students/${encodeURIComponent(sid)}/gradingPeriods`, H);
          if (rg2.status === 200 && pickArr(rg2.data).length) g = rg2.data;
        }
        for (const it of pickArr(g).slice(0, 500)) {
          const subject = String(it.subject ?? it.name ?? '').trim().slice(0, 100);
          const detail = String(it.title ?? it.kind ?? it.type ?? '').trim().slice(0, 120);
          const score = Number(it.grade ?? it.score ?? it.value ?? NaN);
          const title = (subject + (detail ? ` — ${detail}` : '')).trim().slice(0, 240);
          if (!title) continue;
          nGr++;
          schoolRows.push({
            user_id: studentId, kind: 'grade', source: 'mashov',
            external_id: `mashov:gr:${sid}:${String(it.id ?? h(title + String(score)))}`.slice(0, 200),
            title, subject, description: String(it.description ?? it.note ?? it.teacher ?? '').slice(0, 500),
            event_date: normDate(it.date ?? it.created_at ?? null),
            score: Number.isFinite(score) ? score : null,
            retrieval_method: 'unofficial_api', verification_state: 'live_verified',
            synced_at: now, updated_at: now,
          });
        }
      } catch { /* same */ }
      // timetable → school_items(kind=timetable)
      try {
        const r = await getJson(BASE + `/api/students/${encodeURIComponent(sid)}/timetable`, H);
        for (const it of pickArr(r.data).slice(0, 200)) {
          const title = String(it.subject ?? it.name ?? it.title ?? '').trim().slice(0, 200);
          if (!title) continue;
          const room = String(it.classroom ?? it.room ?? it.class ?? '').trim().slice(0, 60);
          nTt++;
          schoolRows.push({
            user_id: studentId, kind: 'timetable', source: 'mashov',
            external_id: `mashov:tt:${sid}:${String(it.id ?? h(title + String(it.day ?? '') + String(it.start_time ?? '')))}`.slice(0, 200),
            title, subject: room, description: String(it.teacher ?? it.teacher_name ?? '').slice(0, 200),
            event_date: null,
            day_of_week: normDay(it.day_of_week ?? it.day ?? null),
            start_time: String(it.start_time ?? it.start ?? '').slice(0, 5) || null,
            end_time: String(it.end_time ?? it.end ?? '').slice(0, 5) || null,
            room: room || null, change_type: 'normal',
            retrieval_method: 'unofficial_api', verification_state: 'live_verified',
            synced_at: now, updated_at: now,
          });
        }
      } catch { /* same */ }
    }
    if (!taskRows.length && !schoolRows.length) {
      return json({ ok: false, error: 'NO_DATA_PARSED', hint: 'התחברת למשו״ב אך לא זוהו נתונים (אין משימות/ציונים עכשיו, או שהפורמט שונה). אפשר ייבוא ידני.' }, 400);
    }
    // 6) upsert under the student's account (same dedup keys as all other writers)
    const db = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });
    if (taskRows.length) {
      const { error } = await db.from('tasks').upsert(taskRows, { onConflict: 'user_id,source,external_id' });
      if (error) return json({ ok: false, error: 'DB_WRITE_FAILED' }, 500);
    }
    if (schoolRows.length) {
      const { error } = await db.from('school_items').upsert(schoolRows, { onConflict: 'user_id,kind,source,external_id' });
      if (error) return json({ ok: false, error: 'DB_WRITE_FAILED' }, 500);
    }
    const { error: ce } = await db.from('connections').upsert(
      { user_id: studentId, provider: 'mashov', state: 'synced', data_readable: true, sync_working: true, last_sync_at: now, last_error: null },
      { onConflict: 'user_id,provider' });
    if (ce) return json({ ok: false, error: 'DB_WRITE_FAILED' }, 500);
    // password/cookies: function scope ends here — nothing persisted anywhere.
    return json({
      ok: true, students: students.length, homework: nHw, grades: nGr, timetable: nTt,
      note: 'הסיסמה לא נשמרה בכלל — לעדכון הבא לוחצים "רענן נתונים".',
    });
  } catch (e) {
    return json({ ok: false, error: 'FETCH_ERROR', detail: String((e as Error).message || e).slice(0, 120) }, 502);
  }
});
