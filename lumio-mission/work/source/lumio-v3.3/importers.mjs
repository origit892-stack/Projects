import {normalizeTask,sources} from './core.mjs';

function unfoldICS(text){return String(text).replace(/\r\n/g,'\n').replace(/\n[ \t]/g,'');}
function unescapeICS(value){return String(value||'').replace(/\\n/gi,'\n').replace(/\\([,;\\])/g,'$1');}
function icsDate(raw){const v=String(raw||'').trim();let m=v.match(/^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})?(Z)?)?$/);if(!m)return null;const [,yy,mm,dd,hh='12',mi='00',ss='00',z]=m;const date=new Date(`${yy}-${mm}-${dd}T${hh}:${mi}:${ss}${z?'Z':'+02:00'}`);return Number.isNaN(+date)?null:date.toISOString()}
export function parseICS(text,source='classroom'){
 if(!sources.includes(source))throw Error('מקור לא מוכר');
 const raw=String(text||'');if(raw.length>3_000_000)throw Error('קובץ גדול מדי');
 const lines=unfoldICS(raw).split('\n');let current=null,events=[];
 for(const line of lines){const clean=line.trim();if(clean==='BEGIN:VEVENT'){current={};continue}if(clean==='END:VEVENT'){if(current){events.push(current);current=null}continue}if(!current)continue;const k=clean.indexOf(':');if(k<0)continue;const key=clean.slice(0,k).split(';')[0].toUpperCase(),value=clean.slice(k+1);if(['UID','SUMMARY','DESCRIPTION','DTSTART','DTEND','URL','LOCATION'].includes(key))current[key]=value}
 return events.slice(0,2000).map((v,i)=>normalizeTask({title:unescapeICS(v.SUMMARY),external_id:`ics:${v.UID||`${v.SUMMARY}:${v.DTSTART||i}`}`,description:unescapeICS(v.DESCRIPTION||''),subject:unescapeICS(v.LOCATION||''),due_at:icsDate(v.DTSTART),url:unescapeICS(v.URL||'')},source)).filter(Boolean);
}
function parseRows(raw){const rows=[];let row=[],cell='',quoted=false;for(let i=0;i<raw.length;i++){const c=raw[i];if(quoted){if(c==='"'&&raw[i+1]==='"'){cell+='"';i++}else if(c==='"')quoted=false;else cell+=c}else if(c==='"')quoted=true;else if(c===','){row.push(cell);cell=''}else if(c==='\n'){row.push(cell.replace(/\r$/,''));rows.push(row);row=[];cell=''}else cell+=c}if(quoted)throw Error('CSV עם מרכאות לא סגורות');if(cell||row.length){row.push(cell);rows.push(row)}return rows}
export function parseCSV(text,source='manual'){
 if(!sources.includes(source))throw Error('מקור לא מוכר');const raw=String(text||'').replace(/^\uFEFF/,'');if(raw.length>3_000_000)throw Error('קובץ גדול מדי');const rows=parseRows(raw);if(rows.length<2)return [];
 const head=rows.shift().map(v=>v.trim().toLowerCase());const find=(names)=>head.findIndex(h=>names.includes(h));const titleIdx=find(['title','name','summary','task','משימה','כותרת','שם']);if(titleIdx===-1)throw Error('בקובץ CSV צריכה להיות עמודת title או משימה');
 const subjectIdx=find(['subject','course','מקצוע','קורס']),dueIdx=find(['due','due_at','date','start date','מועד','תאריך']),urlIdx=find(['url','link','source_url','קישור']),idIdx=find(['id','uid','external_id']);
 return rows.slice(0,2000).map((cells,i)=>normalizeTask({title:cells[titleIdx],subject:cells[subjectIdx]||'',due:cells[dueIdx]||null,url:cells[urlIdx]||null,external_id:cells[idIdx]||`csv:${cells[titleIdx]}:${cells[dueIdx]||i}`},source)).filter(Boolean)
}
export function parseDataFile(text,name,source='manual'){
 const n=String(name||'').toLowerCase();if(n.endsWith('.ics'))return parseICS(text,source);if(n.endsWith('.csv'))return parseCSV(text,source);if(n.endsWith('.json')){let parsed;try{parsed=JSON.parse(text)}catch{throw Error('JSON לא תקין')};const rows=Array.isArray(parsed)?parsed:parsed?.tasks;if(!Array.isArray(rows))throw Error('דרוש מערך tasks בקובץ JSON');return rows.slice(0,2000).map(x=>normalizeTask(x,x.source||source)).filter(Boolean)}throw Error('ניתן לייבא רק JSON, CSV או ICS');
}
