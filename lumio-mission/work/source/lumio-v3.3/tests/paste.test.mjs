import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parsePastedTasks} from '../core.mjs';
test('Hebrew paste import preserves source and date',()=>{const rows=parsePastedTasks('לפתור דף | מתמטיקה | 2026-11-25\nמבחן', 'mashov'); assert.equal(rows.length,2);assert.equal(rows[0].source,'mashov');assert.equal(rows[0].subject,'מתמטיקה');assert.match(rows[0].due_at,/2026-11-25/);});
test('paste import rejects empty and huge values',()=>{assert.throws(()=>parsePastedTasks(''),/הדבק/);assert.throws(()=>parsePastedTasks('a'.repeat(25001)),/25,000/);});
test('paste import only accepts known source',()=>{assert.throws(()=>parsePastedTasks('משימה','evil'),/מקור לא מוכר/);});
test('no unsafe links in pasted tasks',()=>{assert.equal(parsePastedTasks('משימה | מדעים | 2026-11-21 | javascript:alert(1)','ofek')[0].source_url,null);});
