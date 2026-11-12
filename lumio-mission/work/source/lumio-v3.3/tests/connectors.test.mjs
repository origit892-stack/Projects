import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {
 CONNECTION_STATES, RETRIEVAL_METHODS, PROVIDERS,
 connectionFacts, heStatus, classifyHttpError, dedupeKey, fallbackFingerprint, provenanceFor,
 normalizeShahafRow, parseShahafTimetableTable, upsertTimetable, validateFeedUrl,
 importFeedItems, parseShahafPage, buildShahafUrl
} from '../connectors.mjs';
import {normalizeTask} from '../core.mjs';

const root=new URL('../',import.meta.url);
const read=p=>readFile(fileURLToPath(new URL(p,root)),'utf8');

// connectionFacts — table-driven, every one of the 11 states covered.
const FACT_TABLE=[
 ['not_connected',false,null,{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['login_only',false,null,{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['awaiting_consent',false,null,{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['awaiting_consent',true,null,{identityAuthenticated:true,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['requires_admin',false,null,{identityAuthenticated:true,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['connected_unverified',false,'2026-11-12T08:00:00Z',{identityAuthenticated:true,permissionGranted:true,dataReadable:false,syncWorking:false}],
 ['syncing',false,null,{identityAuthenticated:true,permissionGranted:true,dataReadable:false,syncWorking:false}],
 ['synced',false,'2026-11-12T08:00:00Z',{identityAuthenticated:true,permissionGranted:true,dataReadable:true,syncWorking:true}],
 ['needs_reauth',true,'2026-11-12T08:00:00Z',{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['manual_import_only',false,null,{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['unavailable',false,null,{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['error',false,null,{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false}],
 ['error',false,'2026-11-12T08:00:00Z',{identityAuthenticated:false,permissionGranted:false,dataReadable:true,syncWorking:false}]
];
test('connectionFacts covers every state (11 states, table-driven)',()=>{
 const covered=new Set(FACT_TABLE.map(r=>r[0]));
 assert.ok(CONNECTION_STATES.every(s=>covered.has(s)),'every state has an expected facts row');
 for(const [state,hasToken,lastSyncAt,expected] of FACT_TABLE){
  assert.deepEqual(connectionFacts(state,hasToken,lastSyncAt),expected,`facts for state=${state} hasToken=${hasToken}`);
 }
});

test('heStatus returns the exact §15 Hebrew labels',()=>{
 const ts='2026-11-12T08:00:00Z';
 assert.equal(heStatus('not_connected',null),'לא מחובר');
 assert.equal(heStatus('login_only',null),'נפתח אתר המקור (אין סנכרון)');
 assert.equal(heStatus('awaiting_consent',null),'ממתין לאישור הרשאות');
 assert.equal(heStatus('requires_admin',null),'נדרש אישור מנהל מערכת');
 assert.equal(heStatus('connected_unverified',null),'מחובר, טרם אומתה קריאת נתונים');
 assert.equal(heStatus('syncing',null),'מבצע סנכרון…');
 assert.match(heStatus('synced',ts),/^סנכרון הצליח — /);
 assert.equal(heStatus('synced',null),'סנכרון הצליח');
 assert.equal(heStatus('needs_reauth',null),'נדרש להתחבר מחדש');
 assert.equal(heStatus('manual_import_only',null),'חיבור אוטומטי אינו זמין; ניתן לייבא נתונים');
 assert.match(heStatus('error',null),/שגיאה/);
 assert.match(heStatus('unavailable'),/אינו זמין/);
 // legacy v3.3 states must not crash and must stay honest
 assert.match(heStatus('api_connected',ts),/^סנכרון הצליח — /);
 assert.match(heStatus('imported',ts),/ייבוא ידני/);
});

test('classifyHttpError maps statuses and timeout',()=>{
 assert.equal(classifyHttpError(401),'AUTH_EXPIRED');
 assert.equal(classifyHttpError(403),'PERMISSION_DENIED');
 assert.equal(classifyHttpError(404),'SOURCE_NOT_FOUND');
 assert.equal(classifyHttpError(429),'RATE_LIMITED');
 assert.equal(classifyHttpError(500),'NETWORK_ERROR');
 assert.equal(classifyHttpError(503),'NETWORK_ERROR');
 assert.equal(classifyHttpError(null,true),'NETWORK_ERROR');
 assert.equal(classifyHttpError(400),'DATA_VALIDATION_FAILED');
});

test('dedupeKey stable; fingerprint dedup rules (same source, cross source, different course)',()=>{
 const k1=dedupeKey('u1','mashov','ext-1','task');
 const k2=dedupeKey('u1','mashov','ext-1','task');
 assert.equal(k1,k2); // duplicate_same_source: same external_id twice → one key → one row
 const fpA=fallbackFingerprint({title:'עבודה במתמטיקה',subject:'מתמטיקה',due_at:'2026-11-20T00:00:00Z',source:'mashov'});
 const fpB=fallbackFingerprint({title:'עבודה  במתמטיקה!',subject:'מתמטיקה',due_at:'2026-11-20T13:00:00Z',source:'mashov'});
 assert.equal(fpA,fpB); // canonical text → identical
 const fpC=fallbackFingerprint({title:'עבודה במתמטיקה',subject:'מתמטיקה',due_at:'2026-11-20T00:00:00Z',source:'ofek'});
 assert.notEqual(fpA,fpC); // similar_across_sources → separate records (merged in view by uniqueTasks)
 const fpD=fallbackFingerprint({title:'עבודה במתמטיקה',subject:'היסטוריה',due_at:'2026-11-20T00:00:00Z',source:'mashov'});
 assert.notEqual(fpA,fpD); // same_title_different_course → NOT merged
});

test('provenanceFor: method propagation; fixture data stays fixture_only',()=>{
 const t=normalizeTask({title:'משימה',subject:'מתמטיקה'},'mashov');
 assert.deepEqual(provenanceFor(t,'user_import'),{provider:'mashov',capability:'assignments',retrieval_method:'user_import',verification_state:'user_imported_unverified'});
 assert.equal(provenanceFor(t,'official_api').verification_state,'live_verified');
 assert.equal(provenanceFor(t,'public_school_feed').verification_state,'live_verified');
 const fixture={...t,verification_state:'fixture_only'};
 assert.equal(provenanceFor(fixture,'user_import').verification_state,'fixture_only');
 assert.equal(provenanceFor(t,'not_a_method').retrieval_method,'user_entry');
});

test('normalizeShahafRow validates day/time/change_type with Hebrew errors',()=>{
 assert.throws(()=>normalizeShahafRow({title:'מתמטיקה',day:9,start_time:'08:00'}),/יום/);
 assert.throws(()=>normalizeShahafRow({title:'מתמטיקה',day:-1,start_time:'08:00'}),/יום/);
 assert.throws(()=>normalizeShahafRow({title:'מתמטיקה',day:0,start_time:'25:00'}),/שעת התחלה/);
 assert.throws(()=>normalizeShahafRow({title:'מתמטיקה',day:0,start_time:'8:5'}),/שעת התחלה/);
 assert.throws(()=>normalizeShahafRow({title:'מתמטיקה',day:0,start_time:'08:00',change_type:'weird'}),/שינוי/);
 assert.throws(()=>normalizeShahafRow({day:0,start_time:'08:00'}),/כותרת/);
 const r=normalizeShahafRow({title:'מתמטיקה',day:3,start_time:'10:00',end_time:'10:45',room:'204',change_type:'cancelled'});
 assert.deepEqual({day:r.day_of_week,start:r.start_time,end:r.end_time,room:r.room,ct:r.change_type},{day:3,start:'10:00',end:'10:45',room:'204',ct:'cancelled'});
});

// SYNTHETIC FIXTURE — not real school data
const SYNTH_TABLE=[
 ['שעה','ראשון','שני','שלישי','רביעי','חמישי','שישי'],
 ['07:30-08:15','מתמטיקה 5','מתמטיקה 5','','היסטוריה (204)','אנגלית',''],
 ['08:15-09:00','מתמטיקה 5 — בוטל','','','','',''],
 ['שורה ללא שעה','פריז','','','','',''],
 ['25:99-26:00','מתמטיקה','','','','','']
];
test('parseShahafTimetableTable parses valid rows and reports skipped rows',()=>{
 const {items,skipped}=parseShahafTimetableTable(SYNTH_TABLE);
 assert.equal(items.length,5); // 4 cells in row 1 + 1 cancelled cell in row 2
 const first=items.find(x=>x.day_of_week===0&&x.start_time==='07:30');
 assert.equal(first.title,'מתמטיקה 5');
 assert.equal(first.source===undefined?first.external_id:'x','shahaf:0:07:30');
 const cancelled=items.find(x=>x.day_of_week===0&&x.start_time==='08:15');
 assert.equal(cancelled.change_type,'cancelled');
 assert.equal(cancelled.title,'מתמטיקה 5');
 const roomRow=items.find(x=>x.day_of_week===3&&x.start_time==='07:30');
 assert.equal(roomRow.room,'204');
 assert.equal(roomRow.title,'היסטוריה');
 assert.equal(skipped.length,2); // row without a time + invalid 25:99 time
 assert.match(skipped[0].reason,/[א-ת]/);
 assert.match(skipped[1].reason,/[א-ת]/);
});

test('upsertTimetable idempotency: update not duplicate; cancelled/changed preserved',()=>{
 assert.deepEqual(upsertTimetable(),[]);
 assert.deepEqual(upsertTimetable(null,null),[]);
 const base={source:'shahaf',external_id:'shahaf:0:07:30',title:'מתמטיקה 5',day_of_week:0,start_time:'07:30',end_time:'08:15',room:null,change_type:'normal'};
 const once=upsertTimetable([],[{...base}]);
 assert.equal(once.length,1);
 const twice=upsertTimetable(once,[{...base}]);
 assert.equal(twice.length,1); // same (source,external_id) twice → 1 row
 const changed=upsertTimetable(twice,[{...base,title:'מתמטיקה 5 — חדש',change_type:'changed'}]);
 assert.equal(changed.length,1);
 assert.equal(changed[0].title,'מתמטיקה 5 — חדש');
 assert.equal(changed[0].change_type,'changed');
 const cancelled=upsertTimetable(changed,[{...base,title:'מתמטיקה 5 — חדש',change_type:'cancelled'}]);
 assert.equal(cancelled.length,1);
 assert.equal(cancelled[0].change_type,'cancelled');
});

test('Israeli DST edge (2026-10-25/26) keeps the local date; minimal item survives',()=>{
 const a=normalizeTask({title:'מבחן',subject:'מתמטיקה',due:'2026-10-25'});
 const b=normalizeTask({title:'מבחן',subject:'מתמטיקה',due:'2026-10-26'});
 assert.equal(String(a.due_at).slice(0,10),'2026-10-25');
 assert.equal(String(b.due_at).slice(0,10),'2026-10-26');
 assert.notEqual(fallbackFingerprint(a),fallbackFingerprint(b));
 const minimal=normalizeTask({title:'משימה קצרה'});
 assert.ok(minimal);
 assert.equal(minimal.due_at,null);
 assert.equal(minimal.subject,'');
 assert.equal(minimal.source_url,null);
 const prov=provenanceFor(minimal,'user_entry');
 assert.equal(prov.retrieval_method,'user_entry');
 assert.equal(prov.verification_state,'user_imported_unverified');
});

test('empty/null inputs never throw and never invent data',()=>{
 assert.deepEqual(parseShahafTimetableTable([]),{items:[],skipped:[]});
 assert.deepEqual(parseShahafTimetableTable(null),{items:[],skipped:[]});
 const emptyIcs=importFeedItems('','petel','ics_url');
 assert.equal(emptyIcs.items.length,0);
 assert.equal(emptyIcs.preview.length,0);
 const garbage=importFeedItems('לא קובץ ICS בכלל','petel','ics_url');
 assert.equal(garbage.items.length,0);
 const garbagePage=importFeedItems('<html><body>בלי טבלאות</body></html>','shahaf','public_page');
 assert.equal(garbagePage.items.length,0);
 assert.equal(garbagePage.stamp,null);
});

test('validateFeedUrl rejects unsafe and wrong-host URLs',()=>{
 assert.equal(validateFeedUrl('','ics_url').ok,false);
 assert.equal(validateFeedUrl('javascript:alert(1)','ics_url').ok,false);
 assert.equal(validateFeedUrl('data:text/calendar,hi','ics_url').ok,false);
 assert.equal(validateFeedUrl('ftp://example.com/ics','ics_url').ok,false);
 assert.equal(validateFeedUrl('https://user:pass@example.com/ics','ics_url').ok,false);
 assert.equal(validateFeedUrl('http://petel.example.org/ics/personal','ics_url').ok,false);
 assert.equal(validateFeedUrl('https://example.com/','public_page').ok,false);
 assert.equal(validateFeedUrl('https://notshahaf.site/x','public_page').ok,false);
 assert.equal(validateFeedUrl('https://evil.com/shahaf.site/','public_page').ok,false);
 const okPetel=validateFeedUrl('https://petel.example.org/ics/personal','ics_url');
 assert.equal(okPetel.ok,true);
 const okShahaf=validateFeedUrl('https://katzirb.shahaf.site/?cls=1&tab=timetable&mode=student','public_page');
 assert.equal(okShahaf.ok,true);
 assert.match(okShahaf.url,/shahaf\.site/);
});

// SYNTHETIC FIXTURE — not real school data
const SYNTH_ICS='BEGIN:VCALENDAR\nBEGIN:VEVENT\nUID:p-1\nSUMMARY:תרגול 3\nDTSTART:20261120T080000Z\nEND:VEVENT\nBEGIN:VEVENT\nUID:p-2\nSUMMARY:מעבדה\nDTSTART:20261121T100000Z\nLOCATION:המעבדה 2\nEND:VEVENT\nEND:VCALENDAR';
test('importFeedItems on synthetic ICS → normalized tasks with source + external ids',()=>{
 const r=importFeedItems(SYNTH_ICS,'petel','ics_url');
 assert.equal(r.items.length,2);
 assert.equal(r.items[0].source,'petel');
 assert.ok(r.items[0].external_id.startsWith('ics:'));
 assert.equal(r.items[1].external_id,'ics:p-2');
 assert.equal(r.skipped,0);
 assert.equal(r.preview.length,2);
 assert.match(r.items[0].due_at,/2026-11-20/);
});

// SYNTHETIC FIXTURE — not real school data
function synthShahafHtml(editCell){
 const rows=['<tr><th>שעה</th><th>ראשון</th><th>שני</th><th>שלישי</th><th>רביעי</th><th>חמישי</th><th>שישי</th></tr>'];
 for(let i=0;i<12;i++){
  const hh=String(7+Math.floor(i/3)).padStart(2,'0');
  const mm=i%3===0?'30':i%3===1?'45':'00';
  const cell=i===editCell?'שיעור שונה':'שיעור '+i;
  rows.push(`<tr><td>${hh}:${mm}-${hh}:50</td><td>${cell}</td><td></td><td></td><td></td><td></td><td></td></tr>`);
 }
 return `<html><head></head><body><div>מעודכן ל: 12.11.2026, שעה: 08:15</div><table>${rows.join('')}</table></body></html>`;
}
test('parseShahafPage: synthetic 12-period table, stamp, change detection, stamp-less fixture',()=>{
 const p1=parseShahafPage(synthShahafHtml());
 assert.equal(p1.rows.length,13); // header + 12 period rows
 assert.match(p1.stamp,/12\.11\.2026/);
 const t1=parseShahafTimetableTable(p1.rows);
 assert.equal(t1.items.length,12);
 const same=upsertTimetable(t1.items,t1.items);
 assert.equal(same.length,12); // re-fetch of an unchanged feed → no duplicates
 const p2=parseShahafPage(synthShahafHtml(5));
 const t2=parseShahafTimetableTable(p2.rows);
 const merged=upsertTimetable(t1.items,t2.items);
 assert.equal(merged.length,12); // edited cell → update, not duplicate
 assert.equal(merged[5].title,'שיעור שונה');
 const noStamp=parseShahafPage('<table><tr><th>שעה</th><th>ראשון</th><th>שני</th></tr><tr><td>08:00-08:45</td><td>א</td><td></td></tr></table>');
 assert.equal(noStamp.stamp,null);
 assert.equal(noStamp.rows.length,2);
});

test('buildShahafUrl renders the verified template',()=>{
 assert.equal(buildShahafUrl('katzir-b',5),'https://katzir-b.shahaf.site/?cls=5&tab=timetable&mode=student');
 assert.equal(buildShahafUrl('dror',12,'timetable',-1),'https://dror.shahaf.site/?cls=12&tab=timetable&mode=student&week=-1');
 assert.throws(()=>buildShahafUrl('bad school',5));
 assert.throws(()=>buildShahafUrl('katzir','x'));
});

test('PROVIDERS: 5 providers with honest capabilities and Hebrew copy',()=>{
 assert.equal(PROVIDERS.length,5);
 const ids=PROVIDERS.map(p=>p.id);
 for(const id of ['classroom','mashov','ofek','petel','shahaf'])assert.ok(ids.includes(id),`missing ${id}`);
 for(const p of PROVIDERS){
  assert.ok(CONNECTION_STATES.includes(p.defaultState),`${p.id} defaultState`);
  assert.ok(p.heDescription.length>0);
  assert.ok(p.howToConnect.length>0);
  assert.ok(Array.isArray(p.dataPaths)&&p.dataPaths.length>0);
  for(const d of p.dataPaths)assert.ok(RETRIEVAL_METHODS.includes(d.method),`${p.id} dataPath method`);
 }
 assert.equal(PROVIDERS.find(p=>p.id==='mashov').capabilities.apiRead,false);
 assert.equal(PROVIDERS.find(p=>p.id==='classroom').capabilities.apiRead,true);
 assert.equal(PROVIDERS.find(p=>p.id==='shahaf').capabilities.timetable,true);
});

test('legacy v3.3 states get honest facts; shahaf guards reject junk (QA round 2)',()=>{
 const sync=new Date().toISOString();
 const a=connectionFacts('api_connected',false,sync);
 assert.deepEqual(a,{identityAuthenticated:true,permissionGranted:true,dataReadable:true,syncWorking:true});
 assert.deepEqual(connectionFacts('api_connected',false,null),{identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false});
 assert.equal(connectionFacts('imported').dataReadable,true);
 assert.throws(()=>buildShahafUrl('katzir','0x10'),/מספר כיתה/);
 assert.throws(()=>normalizeShahafRow({title:'x',day:'',start_time:'08:00'}),/יום/);
});

// Live-verified shape of katzirb.shahaf.site (fetched 2026-11-12, 39 items):
// header cells carry day name + date, period labels are "N HH:MM HH:MM"
// (space-separated, no dash), a 00:00 filler row exists, stamp at page bottom.
const KATZIRB_HTML=`<html dir="rtl"><body>
<table class="TTTable"><tr><td></td><td>יום ראשון 08.11</td><td>יום שני 09.11 חג הסיגד</td><td>יום שלישי 10.11</td></tr>
<tr><td>0 07:50 08:25</td><td></td><td>חג הסיגד</td><td></td></tr>
<tr><td>1 08:30 09:15</td><td><b>אנגלית</b> (ז1) בורג רוית</td><td><b>אנגלית</b> (ז1) בורג רוית</td><td>בוברמן רז -&gt; חדר: ז5</td></tr>
<tr><td>10 00:00 00:00</td><td></td><td></td><td></td></tr></table>
<div>מעודכן ל: 11.11.2026, שעה: 20:35</div></body></html>`;
test('katzirb.shahaf.site live shape: dated headers, space-separated end time, stamp, filler row',()=>{
 const out=importFeedItems(KATZIRB_HTML,'shahaf','public_page');
 assert.equal(out.stamp,'11.11.2026, שעה: 20:35');
 assert.equal(out.skipped,0);
 assert.equal(out.items.length,4);
 const eng=out.items.find(i=>i.title.includes('אנגלית'));
 assert.equal(eng.start_time,'08:30');
 assert.equal(eng.end_time,'09:15');
 assert.equal(eng.day_of_week,0);
 const hag=out.items.find(i=>i.title.includes('חג הסיגד'));
 assert.equal(hag.day_of_week,1);
 assert.equal(hag.end_time,'08:25');
 assert.ok(!out.items.some(i=>i.start_time==='00:00'),'filler 00:00 row must yield nothing');
});

test('edge functions ship SSRF guard + cron token + body cap (static checks only, no execution)',async()=>{
 const fs=await import('node:fs');
 const read=(p)=>fs.readFileSync(new URL(p,import.meta.url),'utf8');
 const feed=read('../supabase-functions/feed-sync/index.ts');
 assert.ok(feed.includes('function assertSafeFeedUrl'),'feed-sync missing SSRF guard');
 assert.ok(feed.includes('function isPrivateIp'),'feed-sync missing private-IP check');
 assert.ok(feed.includes('await assertSafeFeedUrl(c.feed_url, isShahaf)'),'guard not invoked before fetch');
 assert.ok(feed.includes('LUMIO_CRON_TOKEN'),'feed-sync missing cron token gate');
 assert.ok(feed.includes("u.protocol !== 'https:'"),'feed-sync must allow https only');
 const ingest=read('../supabase-functions/apps-script-ingest/index.ts');
 assert.ok(ingest.includes('MAX_BODY_BYTES'),'ingest missing body cap');
 assert.ok(ingest.includes('Number.isNaN(d.getTime())'),'ingest missing due_at validation');
 assert.ok(ingest.includes('ALLOWED_SOURCES'),'ingest missing source whitelist');
 assert.ok(ingest.includes("'local_sync'"),'ingest must label local-script pushes honestly');
 assert.ok(ingest.includes(".eq('provider', source)"),'ingest must update the right provider row');
});

test('deployment artifacts exist and contain no secrets (static checks only, no execution)',async()=>{
 const gs=await read('apps-script/classroom-sync.gs');
 for(const call of ['Classroom.Courses.list(','Classroom.Courses.courseWork.list(','Classroom.Courses.courseWork.studentSubmissions('])assert.ok(gs.includes(call),'missing native call: '+call);
 const placeholders=gs.match(/^const [A-Z][A-Z0-9_]* = /gm)||[];
 assert.equal(placeholders.length,2,'exactly two user-fill placeholder constants');
 assert.ok(gs.includes("ScriptApp.newTrigger('sync')"));
 assert.ok(!/eyJ[A-Za-z0-9_-]{10,}/.test(gs),'no JWT-like tokens in Apps Script');
 const readmeHe=await read('apps-script/README-HE.md');
 assert.ok(readmeHe.length>200,'README-HE.md has content');
 const ingest=await read('supabase-functions/apps-script-ingest/index.ts');
 const feed=await read('supabase-functions/feed-sync/index.ts');
 for(const code of [ingest,feed]){
  assert.ok(code.includes('Deno.env.get'),'env reads only, never literal secrets');
  assert.ok(!/eyJ[A-Za-z0-9_-]{10,}/.test(code),'no JWT-like tokens in edge function');
  assert.ok(!code.includes('sb_secret_'),'no service-role key literal');
 }
 const fnReadme=await read('supabase-functions/README-HE.md');
 assert.ok(fnReadme.includes('pg_cron'),'pg_cron snippet present');
 assert.ok(fnReadme.includes('cron.schedule'));
 assert.ok(fnReadme.includes('השהיה'),'anti-pause note present');
});

test('static shell is subpath-safe: no absolute asset paths (GitHub Pages serves at /lumio-site/, not /)',async()=>{
 const fs=await import('node:fs');
 const read=(p)=>fs.readFileSync(new URL(p,import.meta.url),'utf8');
 const html=read('../index.html');
 const refs=[...html.matchAll(/(?:src|href)="([^"]+)"/g)].map(m=>m[1]);
 for(const ref of refs){
   if(ref.startsWith('http'))continue; // external (none expected in the shell)
   assert.ok(!ref.startsWith('/'),'index.html absolute path breaks subpath hosting: '+ref);
 }
 const sw=read('../sw.js');
 const assets=[...sw.matchAll(/\n?(?:const ASSETS=)?\[(.*?)\]/gs)].pop()[1]||'';
 for(const a of assets.split(',').map(s=>s.trim().replace(/^['"]|['"]$/g,'')).filter(Boolean)){
   assert.ok(!a.startsWith('/'),'sw.js ASSETS absolute path breaks subpath hosting: '+a);
 }
 assert.ok(!fs.existsSync(new URL('../public/sw.js',import.meta.url)),'sw.js must live at the site root (scope cap), not in public/');
 const manifest=JSON.parse(read('../public/manifest.webmanifest'));
 assert.ok(!manifest.start_url.startsWith('/'),'manifest start_url absolute breaks subpath hosting');
 for(const ic of manifest.icons)assert.ok(!ic.src.startsWith('/'),'manifest icon src absolute breaks subpath hosting');
 const app=read('../app.mjs');
 assert.ok(app.includes("register('sw.js')"),'SW registration must be relative to the site root');
});
