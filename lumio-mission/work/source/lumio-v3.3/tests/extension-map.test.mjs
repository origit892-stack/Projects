import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';

// Load the browser IIFE (ofek-extension/map.js) in this context. It only
// assigns globalThis.__lumioMap, so an indirect eval is enough and keeps the
// file runnable both as a Chrome content script and as a Node test target.
const root = new URL('../', import.meta.url);
const mapSrc = await readFile(fileURLToPath(new URL('ofek-extension/map.js', root)), 'utf8');
(0, eval)(mapSrc);
const M = globalThis.__lumioMap;

test('map.js exposes the expected surface', () => {
  assert.equal(typeof M.mapCapture, 'function');
  for (const k of ['h', 'parseDue', 'normDay', 'hhmm', 'sourceOf', 'pickArray', 'classify']) {
    assert.equal(typeof M[k], 'function', `missing ${k}`);
  }
});

test('source detection by host', () => {
  assert.equal(M.sourceOf('https://web.mashov.info/api/students/x/homework'), 'mashov');
  assert.equal(M.sourceOf('https://ofek.cet.ac.il/whatever'), 'ofek');
  assert.equal(M.sourceOf('https://petal.cet.ac.il/x'), 'petel');
  assert.equal(M.sourceOf('https://matan.co.il/x'), 'ofek');
  assert.equal(M.sourceOf(''), 'ofek');
});

// --- Mashov homework (shape matches the 4.3-verified /api/students/{id}/homework) ---
test('mashov homework maps to task items with stable ids', () => {
  const data = [
    { id: 1, title: 'משימת מתמטיקה', subject: 'מתמטיקה', dueDate: '2026-11-15T00:00:00Z', status: 'open' },
    { id: 2, name: 'מבחן אנגלית', subjectName: 'אנגלית', submitDate: '17.11.2026', status: 'done' },
  ];
  const { source, kind, items } = M.mapCapture({ url: 'https://web.mashov.info/api/students/abc/homework', data });
  assert.equal(source, 'mashov');
  assert.equal(kind, 'task');
  assert.equal(items.length, 2);
  assert.equal(items[0].kind, 'task');
  assert.equal(items[0].title, 'משימת מתמטיקה');
  assert.equal(items[0].course_title, 'מתמטיקה');
  assert.ok(items[0].due_at.startsWith('2026-11-15'), 'ISO due parsed: ' + items[0].due_at);
  assert.equal(items[0].status, 'todo');
  assert.equal(items[1].title, 'מבחן אנגלית');
  assert.equal(items[1].course_title, 'אנגלית');
  assert.ok(items[1].due_at.startsWith('2026-11-17'), 'dd.mm.yyyy due parsed: ' + items[1].due_at);
  assert.equal(items[1].status, 'done');
  // stable id
  const again = M.mapCapture({ url: 'https://web.mashov.info/api/students/abc/homework', data });
  assert.equal(again.items[0].external_id, items[0].external_id, 'external_id must be stable across runs');
});

test('mashov grades map to grade items with numeric scores', () => {
  const data = {
    items: [
      { subject: 'פיזיקה', title: 'מבחן יח\' 5', grade: 92, date: '2026-11-01' },
      { subject: 'היסטוריה', kind: 'עבודה חודשית', score: '85.5' },
    ],
  };
  const { source, kind, items } = M.mapCapture({ url: 'https://web.mashov.info/api/students/abc/grades', data });
  assert.equal(source, 'mashov');
  assert.equal(kind, 'grade');
  assert.equal(items.length, 2);
  assert.equal(items[0].kind, 'grade');
  assert.equal(items[0].course_title, 'פיזיקה');
  assert.ok(items[0].title.includes('פיזיקה'));
  assert.equal(items[1].course_title, 'היסטוריה');
  assert.ok(items[1].title.includes('עבודה חודשית'));
});

test('mashov timetable maps to timetable items (day/start/room)', () => {
  const data = [
    { subject: 'מתמטיקה', day: 1, startTime: '08:30', endTime: '09:15', classroom: 'כ-12', teacher: 'ד\'ר לי' },
    { name: 'אנגלית', day_of_week: 4, start_time: '10:00', end_time: '10:45', room: '3' },
  ];
  const { source, kind, items } = M.mapCapture({ url: 'https://web.mashov.info/api/students/abc/timetable', data });
  assert.equal(source, 'mashov');
  assert.equal(kind, 'timetable');
  assert.equal(items.length, 2);
  assert.equal(items[0].kind, 'timetable');
  assert.equal(items[0].title, 'מתמטיקה');
  assert.equal(items[0].day_of_week, 1);
  assert.equal(items[0].start_time, '08:30');
  assert.equal(items[0].end_time, '09:15');
  assert.equal(items[0].room, 'כ-12');
  assert.equal(items[1].title, 'אנגלית');
  assert.equal(items[1].day_of_week, 4);
});

test('Hebrew weekday names normalize to 0-6', () => {
  assert.equal(M.normDay('ראשון'), 0);
  assert.equal(M.normDay('שישי'), 5);
  assert.equal(M.normDay('ביום שלישי'), 2);
  assert.equal(M.normDay(3), 3);
  assert.equal(M.normDay('x'), null);
  assert.equal(M.normDay(9), null);
});

// --- Ofek / PeTeL (cet.ac.il) generic task capture ---
test('ofek task list maps to task items', () => {
  const data = {
    items: [
      { title: 'משימת מחשב', courseTitle: 'חשמל', dueDate: '2026-11-20' },
      { name: 'דיווח שדה', subject: 'גיאוגרפיה', deadline: '20/11/2026' },
    ],
  };
  const { source, kind, items } = M.mapCapture({ url: 'https://ofek.cet.ac.il/api/tasks', data });
  assert.equal(source, 'ofek');
  assert.equal(kind, 'task');
  assert.equal(items.length, 2);
  assert.equal(items[0].course_title, 'חשמל');
  assert.ok(items[1].due_at.startsWith('2026-11-20'), items[1].due_at);
});

// --- dedupe + robustness ---
test('duplicate records collapse to one external_id', () => {
  const one = { title: 'משימה', subject: 'מתמטיקה', dueDate: '2026-11-15' };
  const { items } = M.mapCapture({ url: 'https://web.mashov.info/api/students/x/homework', data: [one, { ...one }, { ...one }] });
  assert.equal(items.length, 1, 'three identical homework rows -> one item');
});

test('empty / junk input yields zero items and no throw', () => {
  for (const d of [null, undefined, {}, 'str', 42, [], { data: null }, { items: [] }]) {
    const r = M.mapCapture({ url: 'https://web.mashov.info/api/x/homework', data: d });
    assert.equal(Array.isArray(r.items), true);
    assert.equal(r.items.length, 0, `data=${JSON.stringify(d)}`);
  }
});

test('non-task JSON (analytics) is not misclassified into items without shape', () => {
  // An object that has no title/subject/grade/lesson shape and no URL signal
  const { items } = M.mapCapture({ url: 'https://web.mashov.info/api/health', data: { ok: true, ts: 1 } });
  assert.equal(items.length, 0);
});

test('parseDue handles ISO, dd.mm.yyyy and epoch', () => {
  assert.ok(M.parseDue('2026-11-15T00:00:00Z').startsWith('2026-11-15'));
  assert.ok(M.parseDue('17.11.2026').startsWith('2026-11-17'));
  assert.ok(M.parseDue('2026-11-15').startsWith('2026-11-15'));
  assert.ok(M.parseDue(1763136000).startsWith('2025'), 'epoch seconds parsed');
  assert.equal(M.parseDue('nope'), null);
  assert.equal(M.parseDue(null), null);
});
