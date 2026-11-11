export const sources=['classroom','mashov','ofek','petel','shahaf','manual'];
export function cleanText(v, limit=300){return String(v??'').replace(/\s+/g,' ').trim().slice(0,limit)}
export function safeUrl(raw){try{const u=new URL(raw);return ['https:','http:'].includes(u.protocol)?u.href:null}catch{return null}}
export function normalizeTask(raw,source='manual'){
 const title=cleanText(raw.title||raw.name||raw.text,240);if(!title)return null;
 const src=sources.includes(source)?source:'manual';
 const due=raw.due_at||raw.dueAt||raw.due||null;
 const validDue=due&&!Number.isNaN(new Date(due).getTime())?new Date(due).toISOString():null;
 return {source:src,external_id:cleanText(raw.external_id||raw.externalId||`${title}|${validDue||''}`,200),title,subject:cleanText(raw.subject||raw.course||'',100),description:cleanText(raw.description||'',2000),due_at:validDue,source_url:safeUrl(raw.source_url||raw.url),status:['todo','progress','done'].includes(raw.status)?raw.status:'todo'};
}
export function mergeTasks(existing,incoming){const map=new Map();for(const t of existing){map.set(`${t.source}:${t.external_id}`,t)}for(const t of incoming){const key=`${t.source}:${t.external_id}`;const old=map.get(key);map.set(key,{...old,...t,status:old?.status==='done'&&t.status==='todo'?'done':t.status})}return [...map.values()]}
export function parseImported(text,source='manual'){let data;try{data=JSON.parse(text)}catch{throw Error('הקובץ אינו JSON תקין')};if(!Array.isArray(data)&&!Array.isArray(data.tasks))throw Error('נדרשת רשימת tasks');return (Array.isArray(data)?data:data.tasks).map(x=>normalizeTask(x,x.source||source)).filter(Boolean).slice(0,1500)}
export function dueISO(dueDate,dueTime){if(!dueDate)return null;const dt=new Date(`${dueDate.year}-${String(dueDate.month).padStart(2,'0')}-${String(dueDate.day).padStart(2,'0')}T${String(dueTime?.hours||0).padStart(2,'0')}:${String(dueTime?.minutes||0).padStart(2,'0')}:00Z`);return Number.isNaN(dt.getTime())?null:dt.toISOString()}
export function classroomToTask(work,course,submission){const status=['TURNED_IN','RETURNED'].includes(submission?.state)?'done':submission?.state==='CREATED'?'todo':'todo';return normalizeTask({external_id:`${course.id}:${work.id}`,title:work.title,subject:course.name,description:work.description,due_at:dueISO(work.dueDate,work.dueTime),url:work.alternateLink||`https://classroom.google.com/c/${course.id}`,status},'classroom')}

// A user-controlled import path that also works on Android and iPhone.
// Never fetches private websites, reads cookies, or guesses authentication tokens.
export function parsePastedTasks(input,source='manual'){
 if(!sources.includes(source))throw Error('מקור לא מוכר');
 const raw=String(input||'').trim();
 if(!raw)throw Error('הדבק לפחות משימה אחת');
 if(raw.length>25000)throw Error('יש להדביק עד 25,000 תווים');
 const lines=raw.split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
 if(lines.length>100)throw Error('ניתן לייבא עד 100 שורות בכל פעם');
 return lines.map((line,index)=>{
   // Supports "title | subject | YYYY-MM-DD | https://..." or a plain title.
   const parts=line.split(/\s*\|\s*/);
   const title=parts[0].replace(/^[-*•\d.)\s]+/,'').trim();
   if(!title)return null;
   const subject=parts[1]||'';
   const due=/^\d{4}-\d{2}-\d{2}$/.test(parts[2]||'')?parts[2]:null;
   const url=parts[3]||(/https?:\/\/\S+/.exec(line)||[])[0]||null;
   return normalizeTask({title,subject,due,url,external_id:`paste:${source}:${title}:${due||''}`},source);
 }).filter(Boolean);
}
