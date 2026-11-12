// Lumio 4.0 — connectors.mjs
// Pure, node-testable, no DOM. Research states are FINAL (work/research/*.md, 2026-11-11/12).
// Nothing here presents a provider as connected unless data was actually read.
// Legacy v3.3 connection states ('imported','api_connected') are still understood by
// heStatus/connectionFacts so old rows never break the UI.
import {canonicalText} from './study.mjs';
import {parseICS} from './importers.mjs';

export const CONNECTION_STATES=['not_connected','login_only','awaiting_consent','requires_admin','connected_unverified','syncing','synced','needs_reauth','manual_import_only','unavailable','error'];
export const ERROR_TYPES=['PERMISSION_DENIED','AUTH_EXPIRED','ADMIN_APPROVAL_REQUIRED','API_NOT_AVAILABLE','RATE_LIMITED','SOURCE_NOT_FOUND','SOURCE_CHANGED','NETWORK_ERROR','DATA_VALIDATION_FAILED'];
export const RETRIEVAL_METHODS=['official_api','public_school_feed','local_sync','user_import','user_entry'];
export const VERIFICATION_STATES=['live_verified','sandbox_verified','fixture_only','user_imported_unverified'];
export const FEED_TYPES=['ics_url','public_page'];

// The five real data sources. defaultState is the honest starting point BEFORE any
// user action; classroom's effective default depends on config.google (awaiting_consent
// when an OAuth client is configured, manual_import_only otherwise) — computed in app.mjs
// because this module must stay pure (no config import).
export const PROVIDERS=[
 {id:'classroom',name:'Google Classroom',icon:'📘',sourceLink:'https://classroom.google.com/',
  capabilities:{login:true,apiRead:true,backgroundSync:true,assignments:true,exams:false,grades:true,announcements:true,timetable:false,deepLinks:true},
  defaultState:'awaiting_consent',
  heDescription:'מטלות, מועדי הגשה, הגשות שלי וציונים שניתנו. חיבור דרך API רשמי (OAuth), או סנכרון יומי אוטומטי דרך Apps Script שאתה מפעיל בחשבון Google שלך.',
  howToConnect:'לחץ "חבר Google" ואשר הרשאות — או הפעל את סקריפט הסנכרון היומי (תיקיית apps-script) כדי לקבל סנכרון אוטומטי גם כשהמחשב כבוי.',
  dataPaths:[{label:'מטלות ומועדי הגשה',method:'official_api'},{label:'הגשות שלי',method:'official_api'},{label:'ציונים שניתנו',method:'official_api'}]},
 {id:'mashov',name:'משו״ב',icon:'📊',sourceLink:'https://web.mashov.info/students/login',
  capabilities:{login:true,apiRead:false,backgroundSync:false,assignments:true,exams:true,grades:true,announcements:true,timetable:false,deepLinks:true},
  defaultState:'manual_import_only',
  heDescription:'ציונים, משימות והודעות. אין API רשמי פתוח — אבל יש סקריפט סנכרון מקומי (תיקיית local-sync) שעובד עם ספריית pymashov: אתה רץ אותו פעם אחת במחשב שלך, והוא ממשיך לסנכרן אוטומטית (גם כמתוכנן). הסיסמה נשמרת רק אצלך במחשב, מעולם לא בלומיו.',
  howToConnect:'הפעל את local-sync/mashov_sync.py פעם אחת (הוראות ב־local-sync/README-HE.md) עם מפתח הסנכרון מהכרטיס. או ייבא ידנית.',
  dataPaths:[{label:'משימות',method:'local_sync'},{label:'ציונים',method:'local_sync'},{label:'הודעות',method:'user_import'}]},
 {id:'ofek',name:'אופק',icon:'🌅',sourceLink:'https://ofek.cet.ac.il/',
  capabilities:{login:true,apiRead:false,backgroundSync:false,assignments:true,exams:false,grades:false,announcements:false,timetable:false,deepLinks:true},
  defaultState:'manual_import_only',
  heDescription:'מטלות מתוקשבות. אין API ציבורי — הכניסה דרך הזדהות משרד החינוך. פתרון: תוסף דפדפן (תיקיית ofek-extension) שמתקין פעם אחת וסופג את המשימות מהדף שלך כשאתה פתוח באופק.',
  howToConnect:'התקן את התוסף ofek-extension (הוראות בתיקייה), הקלד את מפתח הסנכרון, פתח את המשימות באופק ולחץ על כפתור "לומיו". או ייבא ידנית.',
  dataPaths:[{label:'מטלות',method:'user_import'}]},
 {id:'petel',name:'פטל',icon:'🧪',sourceLink:'https://stweizmann.proj.ac.il/petel/',
  capabilities:{login:true,apiRead:false,backgroundSync:false,assignments:true,exams:false,grades:false,announcements:false,timetable:false,deepLinks:true},
  defaultState:'manual_import_only',
  heDescription:'תרגולים, מעבדות ומטלות (Moodle). קיימת כתובת יומן ICS אישית שאתה יכול לייצר ולחבר כאן כפיד — זה ייבוא של הנתונים שלך, לא API רשמי (שנעול על ידי מנהל המערכת).',
  howToConnect:'ייצר קישור ICS של היומן שלך בפתל והדבק אותו כאן, או השתמש בסקריפט local-sync/moodle_sync.py (לוח + ציונים), או ייבא קובץ ידנית.',
  dataPaths:[{label:'מועדים מיומן אישי (ICS)',method:'public_school_feed'},{label:'משימות',method:'user_import'}]},
 {id:'shahaf',name:'שחף',icon:'🗓️',sourceLink:'https://play.google.com/store/apps/details?id=com.shahafsoft.timetableapp',
  capabilities:{login:false,apiRead:false,backgroundSync:false,assignments:false,exams:false,grades:false,announcements:true,timetable:true,deepLinks:false},
  defaultState:'not_connected',
  heDescription:'מערכת שעות, שינויים והודעות. מחוברת דרך הדף הציבורי של בית הספר (…shahaf.site) — אין התחברות ואין הרשאות. בית הספר שלכם מפרסם: katzirb.shahaf.site (בדיקה 12.11.2026 — 39 שיעורים נלקחו בהצלחה). אם בית הספר לא מפרסם — אין חיבור.',
  howToConnect:'הדבק את כתובת מערכת השעות של בית הספר (…shahaf.site) ובדוק את הפיד. אם בית הספר לא מפרסם — ייבא ידנית או שלח לבית הספר את הבקשה המוכנה.',
  dataPaths:[{label:'מערכת שעות ושינויים',method:'public_school_feed'},{label:'הודעות',method:'public_school_feed'}]}
];

const HE_DAYS={ראשון:0,שני:1,שלישי:2,רביעי:3,חמישי:4,שישי:5,שבת:6};
const TIME_RE=/^(?:[01]\d|2[0-3]):[0-5]\d$/;

// Four independent booleans. The connection state is a claim about what is actually
// true; facts are what the UI may display as ✓. 'synced' is the only state where all
// four are true. 'error' keeps dataReadable only when data was previously read
// (lastSyncAt present) — it is then stale, and the status line says so.
export function connectionFacts(state,hasToken=false,lastSyncAt=null,lastError=null){
 const facts={identityAuthenticated:false,permissionGranted:false,dataReadable:false,syncWorking:false};
 switch(state){
  case 'synced':facts.identityAuthenticated=true;facts.permissionGranted=true;facts.dataReadable=true;facts.syncWorking=true;break;
  case 'connected_unverified':
  case 'syncing':facts.identityAuthenticated=true;facts.permissionGranted=true;break;
  case 'requires_admin':facts.identityAuthenticated=true;break;
  case 'awaiting_consent':if(hasToken)facts.identityAuthenticated=true;break;
  case 'error':if(lastSyncAt)facts.dataReadable=true;break;
  // Legacy v3.3 states (widened CHECK keeps them on old rows): honest facts so
  // the status line and the four-fact row never contradict each other.
  case 'api_connected':if(lastSyncAt){facts.identityAuthenticated=true;facts.permissionGranted=true;facts.dataReadable=true;facts.syncWorking=true}break;
  case 'imported':facts.dataReadable=true;break;
  default:break; // not_connected, login_only, needs_reauth, manual_import_only, unavailable
 }
 return facts;
}

// Exact Hebrew status labels (mission doc §15). "מחובר" appears only for proven states
// (connected_unverified / synced). Legacy v3.3 states map to honest legacy labels.
export function heStatus(state,lastSyncAt){
 const t=lastSyncAt?new Date(lastSyncAt).toLocaleString('he-IL',{day:'numeric',month:'numeric',year:'numeric',hour:'2-digit',minute:'2-digit'}):'';
 switch(state){
  case 'not_connected':return 'לא מחובר';
  case 'login_only':return 'נפתח אתר המקור (אין סנכרון)';
  case 'awaiting_consent':return 'ממתין לאישור הרשאות';
  case 'requires_admin':return 'נדרש אישור מנהל מערכת';
  case 'connected_unverified':return 'מחובר, טרם אומתה קריאת נתונים';
  case 'syncing':return 'מבצע סנכרון…';
  case 'synced':return t?`סנכרון הצליח — ${t}`:'סנכרון הצליח';
  case 'needs_reauth':return 'נדרש להתחבר מחדש';
  case 'manual_import_only':return 'חיבור אוטומטי אינו זמין; ניתן לייבא נתונים';
  case 'unavailable':return 'המקור אינו זמין כרגע';
  case 'error':return 'שגיאה בחיבור';
  case 'api_connected':return t?`סנכרון הצליח — ${t}`:'סנכרון הצליח'; // legacy v3.3
  case 'imported':return t?`נשמר ייבוא ידני — ${t}`:'נשמר ייבוא ידני'; // legacy v3.3
  default:return 'לא מחובר';
 }
}

// 401→AUTH_EXPIRED, 403→PERMISSION_DENIED, 429→RATE_LIMITED, 404→SOURCE_NOT_FOUND,
// 5xx→NETWORK_ERROR (server side), timeout→NETWORK_ERROR, default→DATA_VALIDATION_FAILED.
export function classifyHttpError(status,isTimeout=false){
 if(isTimeout)return 'NETWORK_ERROR';
 if(status===401)return 'AUTH_EXPIRED';
 if(status===403)return 'PERMISSION_DENIED';
 if(status===429)return 'RATE_LIMITED';
 if(status===404)return 'SOURCE_NOT_FOUND';
 if(typeof status==='number'&&status>=500&&status<=599)return 'NETWORK_ERROR';
 return 'DATA_VALIDATION_FAILED';
}

// Stable dedup key for (user, source, external id, kind).
export function dedupeKey(user_id,source,external_id,kind){
 return [user_id,source,external_id,kind??''].join('|');
}

// Canonical fingerprint for cross-source view dedup (merged in view only, via
// study.uniqueTasks). Reuses study.canonicalText — never re-implemented here.
// Includes source so different sources stay separate records; different subjects
// are never merged.
export function fallbackFingerprint({title,subject,due_at,source}={}){
 const day=due_at?String(due_at).slice(0,10):'';
 return `${canonicalText(title)}|${canonicalText(subject)}|${day}|${source||''}`;
}

// Provenance for one stored row. An explicit verification_state on the task always
// wins (e.g. fixture data must stay flagged fixture_only).
export function provenanceFor(task,method){
 const m=RETRIEVAL_METHODS.includes(method)?method:'user_entry';
 const t=task||{};
 return {
  provider:t.source||'manual',
  capability:t.kind||'assignments',
  retrieval_method:m,
  verification_state:VERIFICATION_STATES.includes(t.verification_state)?t.verification_state:(m==='official_api'||m==='public_school_feed'?'live_verified':'user_imported_unverified')
 };
}

// Validated timetable row. All errors in Hebrew.
export function normalizeShahafRow(raw){
 const r=raw||{};
 const title=String(r.title||r.subject||'').trim().slice(0,240);
 if(!title)throw Error('חסרה כותרת לשיעור');
 const dayRaw=r.day_of_week??r.day;
 const day=(dayRaw==null||dayRaw==='')?NaN:Number(dayRaw);
 if(!Number.isInteger(day)||day<0||day>6)throw Error('יום השבוע אינו תקין (0=ראשון עד 6=שבת)');
 const start=String(r.start_time||'').slice(0,5);
 if(!TIME_RE.test(start))throw Error('שעת התחלה אינה תקינה (HH:MM)');
 const end=String(r.end_time||'').slice(0,5);
 if(end&&!TIME_RE.test(end))throw Error('שעת סיום אינה תקינה (HH:MM)');
 let changeType='normal';
 if(r.change_type!==undefined&&r.change_type!==null&&r.change_type!==''){
  if(!['normal','cancelled','changed'].includes(r.change_type))throw Error('סוג שינוי אינו תקין (normal/cancelled/changed)');
  changeType=r.change_type;
 }
 const externalId=String(r.external_id||`shahaf:${day}:${start}`).slice(0,200);
 return {day_of_week:day,start_time:start,end_time:end||null,title,subject:title,room:String(r.room||'').slice(0,100),change_type:changeType,external_id:externalId};
}

// Parse the verified public Shahaf platform shape: first row = day headers
// (2+ of the 6 day names), following rows have the period time label in the
// first cell and one cell per day column. Tolerant: schools differ in period
// counts (11–14 rows); unknown/invalid cells are reported, never guessed.
export function parseShahafTimetableTable(rows){
 const items=[],skipped=[];
 if(!Array.isArray(rows)||rows.length<2)return {items,skipped};
 const header=rows[0].map(x=>String(x||'').trim());
 const dayCols=[];
 header.forEach((cell,col)=>{for(const [name,day] of Object.entries(HE_DAYS)){if(cell.includes(name)){dayCols.push({col,day});break}}});
 for(let i=1;i<rows.length;i++){
  const row=rows[i];
  if(!Array.isArray(row))continue;
  const label=String(row[0]||'').trim();
  const tm=label.match(/([0-9]{1,2}):([0-9]{2})/);
  if(!tm){skipped.push({row:i,reason:'לא זוהתה שעה בשורת התווית'});continue}
  const start=`${tm[1].padStart(2,'0')}:${tm[2]}`;
  if(!TIME_RE.test(start)){skipped.push({row:i,reason:'לא זוהתה שעת התחלה תקינה (HH:MM) בשורת התווית'});continue}
  const em=label.match(/([0-9]{1,2}):([0-9]{2})\s*[-–—]\s*([0-9]{1,2}):([0-9]{2})/)||label.match(/([0-9]{1,2}):([0-9]{2})\s+([0-9]{1,2}):([0-9]{2})/);
  let end=null;
  if(em){const cand=`${em[3].padStart(2,'0')}:${em[4]}`;if(TIME_RE.test(cand)&&cand!==start)end=cand;}
  for(const {col,day} of dayCols){
   const cell=String(row[col]||'').trim();
   if(!cell)continue;
   let text=cell;
   let room=null;
   const rm=text.match(/[(（]([^\)）]{1,40})[)）]\s*$/);
   if(rm){room=rm[1].trim();text=text.replace(rm[0],'')}
   const changeType=/בוטל|ביטול/.test(cell)?'cancelled':/שינוי|השתנה/.test(cell)?'changed':'normal';
   text=text.replace(/—?\s*(בוטל|ביטול|שינוי|השתנה)\s*—?/g,' ').replace(/\s+/g,' ').trim();
   if(!text)continue;
   try{
    items.push(normalizeShahafRow({day,start_time:start,end_time:end,title:text,room,change_type:changeType,external_id:`shahaf:${day}:${start}`}));
   }catch(e){skipped.push({row:i,reason:e.message})}
  }
 }
 return {items,skipped};
}

// Idempotent merge by (source, external_id): a change updates the existing row,
// never duplicates; cancelled/changed change_type is preserved as received.
export function upsertTimetable(existing,incoming){
 const ex=Array.isArray(existing)?existing:[];
 const inc=Array.isArray(incoming)?incoming:[];
 const map=new Map();
 for(const t of ex)map.set(`${t.source}:${t.external_id}`,{...t});
 for(const t of inc){
  const key=`${t.source}:${t.external_id}`;
  const old=map.get(key);
  map.set(key,old?{...old,...t}:{...t});
 }
 return [...map.values()];
}

// Feed URLs: http(s) only, never credentials-in-URL; public_page is restricted to
// the verified public platform host (2026-11-12).
export function validateFeedUrl(raw,kind){
 const s=String(raw||'').trim();
 if(!s)return {ok:false,error:'נדרשת כתובת פיד'};
 if(!FEED_TYPES.includes(kind))return {ok:false,error:'סוג פיד לא מוכר'};
 let u;
 try{u=new URL(s)}catch{return {ok:false,error:'הכתובת אינה תקינה'}}
 if(u.protocol!=='https:')return {ok:false,error:'יש להשתמש בכתובת https בלבד'};
 if(u.username||u.password)return {ok:false,error:'הכתובת מכילה פרטי הגשה — יש להסירם'};
 if(kind==='public_page'){
  if(!/^([a-z0-9-]+\.shahaf\.site|shahaf\.site)$/i.test(u.hostname))return {ok:false,error:'כתובת מערכת שעות חייבת להיות באתר שחף (…shahaf.site)'};
 }
 return {ok:true,url:u.href};
}

// Plain fetch, 20s timeout, no credentials/cookies, 2MB cap, CORS mode.
// Non-200 → throws with a classifyHttpError code; network/CORS failures pass
// through as the native TypeError for the UI to map to the Hebrew hint.
export async function fetchFeed(url){
 const ctrl=new AbortController();
 const timer=setTimeout(()=>ctrl.abort(),20000);
 try{
  const res=await fetch(url,{signal:ctrl.signal,mode:'cors',credentials:'omit'});
  if(!res.ok)throw new Error(classifyHttpError(res.status,false));
  const len=Number(res.headers.get('content-length')||0);
  if(len>2000000)throw new Error('DATA_VALIDATION_FAILED');
  const text=await res.text();
  if(text.length>2000000)throw new Error('DATA_VALIDATION_FAILED');
  return text;
 }catch(e){
  if(e&&e.name==='AbortError')throw new Error('NETWORK_ERROR');
  throw e;
 }finally{
  clearTimeout(timer);
 }
}

// ics_url → reuses importers.parseICS (never duplicated); public_page →
// parseShahafPage + parseShahafTimetableTable. Empty/garbage input yields zero
// items and never invents data.
export function importFeedItems(text,source,kind){
 if(!FEED_TYPES.includes(kind))throw Error('סוג פיד לא מוכר');
 const out={items:[],skipped:0,preview:[],stamp:null};
 const raw=String(text||'');
 try{
  if(kind==='ics_url'){
   out.items=raw.trim()?parseICS(raw,source):[];
  }else{
   const page=parseShahafPage(raw);
   out.stamp=page.stamp;
   const parsed=parseShahafTimetableTable(page.rows);
   out.items=parsed.items;
   out.skipped=parsed.skipped.length;
  }
 }catch(e){
  out.items=[];
 }
 out.preview=out.items.slice(0,3);
 return out;
}

function decodeEntities(s){return String(s).replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&nbsp;/g,' ')}
function stripTags(s){return decodeEntities(String(s||'').replace(/<br\s*\/?>/gi,' ').replace(/<[^>]+>/g,' ')).replace(/\s+/g,' ').trim()}

// Tolerant HTML-string parser (no live DOM) for the verified public Shahaf shape:
// a <table> whose header row contains 2+ day names, period rows with time labels
// in the first cell. Extracts the "מעודכן ל: DD.MM.YYYY[, שעה: HH:MM]" stamp when
// present (freshness + change-detect). Returns {rows, stamp, error?}.
export function parseShahafPage(htmlText){
 const html=String(htmlText||'');
 const stampM=html.match(/מעודכן ל:\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4}(?:\s*,?\s*שעה:\s*[0-9]{2}:[0-9]{2})?)/);
 const stamp=stampM?stampM[1].trim():null;
 const tables=[...html.matchAll(/<table[\s\S]*?<\/table>/gi)];
 for(const m of tables){
  const table=m[0];
  const trs=[...table.matchAll(/<tr[\s\S]*?<\/tr>/gi)].map(tr=>{
   const cells=[...tr[0].matchAll(/<t[hd][\s\S]*?<\/t[hd]>/gi)].map(c=>stripTags(c[0]));
   return cells;
  }).filter(r=>r.length);
  if(trs.length<2)continue;
  const dayCount=trs[0].filter(c=>Object.keys(HE_DAYS).some(d=>c.includes(d))).length;
  if(dayCount>=2)return {rows:trs,stamp};
 }
 return {rows:[],stamp,error:tables.length?'לא זוהתה טבלת שעות בדף (נדרשים לפחות שני שמות ימים בשורת הכותרת)':'לא נמצאה טבלת שעות בדף'};
}

// Verified URL template (2026-11-12): https://<school>.shahaf.site/?cls=<N>&tab=<tab>&mode=student[&week=<±N>]
export function buildShahafUrl(schoolSubdomain,cls,tab='timetable',week=0){
 const school=String(schoolSubdomain||'').trim().toLowerCase();
 if(!/^[a-z0-9-]+$/.test(school))throw Error('שם בית הספר אינו תקין (אותיות, ספרות ומקף בלבד)');
 const n=/^\d+$/.test(String(cls).trim())?Number(String(cls).trim()):NaN;
 if(!Number.isInteger(n)||n<=0)throw Error('מספר כיתה אינו תקין');
 const t=['timetable','announcements','calendar'].includes(tab)?tab:'timetable';
 const w=Number(week)||0;
 const base=`https://${school}.shahaf.site/?cls=${n}&tab=${t}&mode=student`;
 return w?`${base}&week=${w}`:base;
}
