import test from 'node:test';import assert from 'node:assert/strict';
import {parseICS,parseCSV,parseDataFile} from '../importers.mjs';
test('ICS imports event with stable id and date',()=>{const t=parseICS('BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:school-42\nSUMMARY:מבחן פיזיקה\nDTSTART:20261202T083000Z\nEND:VEVENT\nEND:VCALENDAR','shahaf');assert.equal(t.length,1);assert.equal(t[0].source,'shahaf');assert.equal(t[0].external_id,'ics:school-42');assert.match(t[0].due_at,/2026-12-02/)});
test('ICS unfolding and escaped comma',()=>{const t=parseICS('BEGIN:VEVENT\nSUMMARY:משימה\\, באנגלית\nDESCRIPTION:עמוד\n 10\nEND:VEVENT');assert.equal(t[0].title,'משימה, באנגלית');assert.equal(t[0].description,'עמוד10')});
test('CSV quoted fields',()=>{const t=parseCSV('title,subject,due,url\n"דף, עבודה",מתמטיקה,2026-12-01,https://example.com','mashov');assert.equal(t[0].title,'דף, עבודה');assert.equal(t[0].source,'mashov')});
test('unknown formats are rejected',()=>assert.throws(()=>parseDataFile('foo','tasks.exe')));
test('CSV without title rejected',()=>assert.throws(()=>parseCSV('x,y\na,b')));
test('reject malformed ICS date',()=>{const t=parseICS('BEGIN:VEVENT\nSUMMARY:Test\nDTSTART:ABC\nEND:VEVENT');assert.equal(t[0].due_at,null)});
