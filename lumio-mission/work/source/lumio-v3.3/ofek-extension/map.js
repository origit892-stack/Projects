// Lumio MOE Sync — map.js (isolated world, loaded BEFORE content.js)
// PURE mapping logic: turns a captured {url, data} (JSON the school system's
// own API returned to the page) into Lumio ingest items {kind, external_id,
// title, course_title, due_at, status, score, room, day_of_week, start_time,
// end_time, change_type}. No browser globals are touched at load time, so the
// same file is unit-testable in Node (see tests/extension-map.test.mjs).
(function () {
  'use strict';

  function h(s) {
    s = String(s == null ? '' : s);
    let x = 5381;
    for (let i = 0; i < s.length; i++) x = ((x << 5) + x + s.charCodeAt(i)) >>> 0;
    return x.toString(16).padStart(8, '0');
  }

  function str(v) { return v == null ? '' : String(v).trim(); }

  function parseDue(raw) {
    if (raw == null) return null;
    if (typeof raw === 'number') {
      const d = new Date(raw > 1e12 ? raw : raw * 1000);
      return isNaN(d.getTime()) ? null : d.toISOString();
    }
    const s = String(raw).trim();
    if (!s) return null;
    let m = s.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (m) return `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}T00:00:00Z`;
    m = s.match(/(\d{1,2})[./](\d{1,2})[./](\d{4})/);
    if (m) return `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}T00:00:00Z`;
    const d = new Date(s);
    return isNaN(d.getTime()) ? null : d.toISOString();
  }

  const HE_DAYS = { 'ראשון': 0, 'שני': 1, 'שלישי': 2, 'רביעי': 3, 'חמישי': 4, 'שישי': 5, 'שבת': 6 };
  function normDay(v) {
    if (v == null) return null;
    if (typeof v === 'number' && Number.isInteger(v) && v >= 0 && v <= 6) return v;
    const s = String(v).toLowerCase();
    for (const name in HE_DAYS) if (s.includes(name)) return HE_DAYS[name];
    const n = Number(s);
    return Number.isInteger(n) && n >= 0 && n <= 6 ? n : null;
  }

  function hhmm(v) {
    const s = str(v);
    return /^\d{1,2}:\d{2}$/.test(s) ? s : null;
  }

  function sourceOf(url) {
    const u = (url || '').toLowerCase();
    if (u.includes('mashov')) return 'mashov';
    if (u.includes('petal') || u.includes('petel')) return 'petel';
    return 'ofek'; // *.cet.ac.il / *.matan.co.il default
  }

  // Find the most likely array of records inside an arbitrary JSON blob.
  function pickArray(data) {
    if (Array.isArray(data)) return data;
    if (data && typeof data === 'object') {
      const keys = ['items', 'tasks', 'activities', 'homework', 'grades', 'results',
        'lessons', 'students', 'data', 'result', 'rows', 'list'];
      for (const k of keys) {
        if (Array.isArray(data[k]) && data[k].length) return data[k];
      }
      // single-object payloads
      return [data];
    }
    return [];
  }

  // What kind of data is this capture? URL signal first, shape second.
  function classify(url, data) {
    const u = (url || '').toLowerCase();
    if (/timetable|lessons|schedule|מערכת[- ]?שעות/.test(u)) return 'timetable';
    if (/(grade|score|report|ציון)/.test(u)) return 'grade';
    if (/(homework|assignment|task|mishma|משימה)/.test(u)) return 'task';
    // shape-based fallback
    const arr = pickArray(data);
    if (arr.length && arr[0] && typeof arr[0] === 'object') {
      const k = Object.keys(arr[0]).join(' ').toLowerCase();
      if (/(start_time|end_time|day_of_week|start_time|room|classroom|lesson)/.test(k)) return 'timetable';
      if (/(grade|score|ציון)/.test(k)) return 'grade';
    }
    return 'task';
  }

  function firstOf(o, keys) {
    for (const k of keys) {
      if (o && o[k] != null && str(o[k])) return str(o[k]);
    }
    return '';
  }

  function mapCapture(cap) {
    const url = cap && cap.url ? cap.url : '';
    const data = cap && cap.data != null ? cap.data : null;
    const source = sourceOf(url);
    const kind = classify(url, data);
    const arr = pickArray(data);
    const items = [];
    const seen = new Set();

    for (const it of arr) {
      if (!it || typeof it !== 'object') continue;
      let item = null;
      if (kind === 'task') {
        const title = firstOf(it, ['title', 'name', 'subjectTitle', 'mishma', 'description']).slice(0, 240);
        if (!title || title.length < 2) continue;
        const subject = firstOf(it, ['subject', 'course', 'courseTitle', 'subjectName', 'course_title']).slice(0, 100);
        const due = parseDue(firstOf(it, ['dueDate', 'due_date', 'submitDate', 'deadline', 'due', 'date']));
        const status = /done|completed|submitted|הושלם|הוגש/i.test(str(it.status ?? it.state)) ? 'done' : 'todo';
        item = { kind: 'task', external_id: (source + ':hw:' + h(title + '|' + subject + '|' + (due || ''))).slice(0, 200), title, course_title: subject, due_at: due, status };
      } else if (kind === 'grade') {
        const subject = firstOf(it, ['subject', 'name', 'course', 'courseTitle', 'subjectName']).slice(0, 100);
        const detail = firstOf(it, ['title', 'kind', 'type', 'examName', 'description']).slice(0, 120);
        const scoreRaw = it.grade ?? it.score ?? it.value ?? it.assignedGrade;
        const score = Number(scoreRaw);
        const title = (subject + (detail && detail !== subject ? ' — ' + detail : '')).slice(0, 240);
        if (!title || !Number.isFinite(score)) continue;
        item = { kind: 'grade', external_id: (source + ':gr:' + h(title + '|' + String(score))).slice(0, 200), title, course_title: subject, score };
      } else { // timetable
        const title = firstOf(it, ['subject', 'name', 'title', 'lessonName']).slice(0, 200);
        if (!title) continue;
        const room = firstOf(it, ['classroom', 'room', 'class', 'location', 'חדר']).slice(0, 60);
        const day = normDay(it.day_of_week ?? it.day ?? it.weekday ?? it.dayNumber);
        const start = hhmm(it.start_time ?? it.startTime ?? it.start);
        const end = hhmm(it.end_time ?? it.endTime ?? it.end);
        const teacher = firstOf(it, ['teacher', 'teacherName', 'instructor']).slice(0, 200);
        item = { kind: 'timetable', external_id: (source + ':tt:' + h(title + '|' + String(day) + '|' + String(start))).slice(0, 200), title, room, day_of_week: day, start_time: start, end_time: end, description: teacher };
      }
      if (!item || seen.has(item.external_id)) continue;
      seen.add(item.external_id);
      items.push(item);
      if (items.length >= 500) break;
    }
    return { source, kind, items };
  }

  globalThis.__lumioMap = { h, parseDue, normDay, hhmm, sourceOf, pickArray, classify, mapCapture };
})();
