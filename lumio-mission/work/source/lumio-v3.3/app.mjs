import {normalizeTask,mergeTasks,parseImported,parsePastedTasks,classroomToTask} from './core.mjs';
import {lumioConfig} from './config.mjs';
import {parseDataFile} from './importers.mjs';
import {filterAndSortTasks,uniqueTasks,sanitizeStudyEntry} from './study.mjs';
import {PROVIDERS,CONNECTION_STATES,connectionFacts,heStatus,validateFeedUrl,fetchFeed,importFeedItems} from './connectors.mjs';
const $=s=>document.querySelector(s), root=$('#root');
const apps=[{id:'classroom',name:'Google Classroom',icon:'📘',description:'מטלות, הגשות, מועדי הגשה',link:'https://classroom.google.com/'},{id:'mashov',name:'משו״ב',icon:'📊',description:'ציונים, משימות, הודעות',link:'https://web.mashov.info/students/login'},{id:'ofek',name:'אופק',icon:'🌅',description:'מטלות ומשימות מתוקשבות',link:'https://ofek.cet.ac.il/'},{id:'petel',name:'פטל',icon:'🧪',description:'תרגולים, מעבדות ומטלות',link:'https://stweizmann.proj.ac.il/petel/'},{id:'shahaf',name:'שחף',icon:'🗓️',description:'מערכת שעות, שינויים ומבחנים',link:'https://play.google.com/store/apps/details?id=com.shahafsoft.timetableapp'}];
const labels={dashboard:'ראשי',tasks:'משימות',calendar:'יומן',school:'לימודים',connections:'חיבורים',profile:'חשבון'};
const defaultProfile={school:'קציר ב׳',city:'רחובות',grade:'ט׳',classroom:'5',display_name:''};
const state={page:'dashboard',auth:null,client:null,profile:{...defaultProfile},tasks:[],connections:[],token:null,config:lumioConfig,message:'',messageType:'success',filter:'all',sourceFilter:'all',subjectFilter:'all',untilFilter:'',sort:'urgent',schoolItems:[],schoolDataReady:true,schoolView:'exam',loading:false,privacyColsReady:true,feedPreview:null,feedBusy:null};
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
// L4 fix: hrefs rendered from stored data must be http(s) only (esc() does not
// strip schemes; a self-XSS via javascript: URL could target the owner).
function safeHref(u){const s=String(u||'').trim();return /^https?:\/\//i.test(s)?s:'#'}
const isoDate=v=>v?new Date(v).toLocaleDateString('he-IL',{day:'numeric',month:'short',year:'numeric'}):'ללא מועד';
function notice(message,type='success'){state.message=message;state.messageType=type;render();}
function configOK(){return Boolean(state.config.url&&state.config.anon)}
async function initialize(){if(location.hash.startsWith('#lumio_import=')){sessionStorage.setItem('lumio_reader_pending',location.hash);history.replaceState(null,'',location.pathname+location.search)}if(configOK())await createSupabase();render();if('serviceWorker'in navigator&&location.protocol==='https:')navigator.serviceWorker.register('/public/sw.js').catch(()=>{});}
async function createSupabase(){try{const mod=await import('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm');state.client=mod.createClient(state.config.url,state.config.anon,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});const {data,error}=await state.client.auth.getSession();if(error)throw error;state.auth=data.session?.user||null;if(state.auth){await loadAccount();await processReaderImport()}state.client.auth.onAuthStateChange((event,session)=>{if(event==='SIGNED_OUT'){state.auth=null;state.tasks=[];state.connections=[];state.schoolItems=[];state.token=null;state.profile={...defaultProfile};render()}else if(event==='SIGNED_IN'&&session?.user&&session.user.id!==state.auth?.id){state.auth=session.user;setTimeout(()=>loadAccount().then(async()=>{render();await processReaderImport()}),0)}})}catch(e){state.client=null;state.message='בעיה בחיבור Supabase: '+e.message;state.messageType='error'}}
async function loadAccount(){if(!state.client||!state.auth)return;const db=state.client;const [p,t,c]=await Promise.all([db.from('profiles').select('*').eq('user_id',state.auth.id).maybeSingle(),db.from('tasks').select('*').eq('user_id',state.auth.id).order('due_at',{ascending:true,nullsFirst:false}).limit(3000),db.from('connections').select('*').eq('user_id',state.auth.id)]);for(const x of [p,t,c])if(x.error)throw Error(x.error.message+' — האם הרצת database.sql?');state.profile=p.data||{...defaultProfile};state.tasks=t.data||[];state.connections=c.data||[];const result=await db.from('school_items').select('*').eq('user_id',state.auth.id).limit(3000);state.schoolDataReady=!result.error;state.schoolItems=result.data||[];render()}
function nav(){return Object.entries(labels).map(([id,label])=>`<button data-nav="${id}" class="${state.page===id?'active':''}"><span>${{dashboard:'⌂',tasks:'☑',calendar:'▦',school:'🏫',connections:'🔌',profile:'♙'}[id]}</span>${label}</button>`).join('')}
function msg(){return state.message?`<div class="${esc(state.messageType)}" role="status">${esc(state.message)} <button class="btn small alt" data-action="dismiss">סגור</button></div>`:''}
function render(){if(!configOK()||!state.auth){renderAuth();return}const p=state.profile;root.innerHTML=`<div class="shell"><aside class="sidebar"><div class="logo">לומיו<span>✦</span></div><nav class="nav">${nav()}</nav><div class="sidefoot">🎓 ${esc(p.school||'בית ספר')} · ${esc(p.city||'')}<br>שכבה ${esc(p.grade||'')} · כיתה ${esc(p.classroom||'')}</div></aside><main class="main"><div class="top"><div><div class="eyebrow">המרכז הלימודי שלך</div><h1>${esc(labels[state.page])}</h1><span class="muted">${esc(p.school)} · ${esc(p.grade)}${esc(p.classroom)}</span></div><span class="pill">${esc(state.auth.email||'חשבון לומיו')}</span></div>${msg()}${pageHTML()}<div class="foot">לומיו 4.0 · נתונים אישיים נשמרים בחשבונך בלבד · חיבורים שלא אומתו אינם מסומנים כמחוברים</div></main></div><div class="mobilebar">${nav()}</div>`;bind();}
function renderAuth(){root.innerHTML=`<div class="login"><div class="loginbox"><div class="brand">לומיו ✦</div><h2>כל המשימות שלך במקום אחד</h2><p class="muted">חשבון תלמיד אישי עם מסד נתונים וסנכרון בין מכשירים.</p>${msg()}${!configOK()?`<div class="warning">הגדרת השרת חסרה. מנהל לומיו צריך לעדכן את config.mjs.</div>`:`<form id="authForm"><label>אימייל</label><input type="email" required name="email" autocomplete="email" placeholder="you@example.com"><label>סיסמה (6 תווים לפחות)</label><input type="password" minlength="6" required name="password" autocomplete="current-password" placeholder="••••••••"><button class="btn" name="authAction" value="signin">התחברות</button><button class="btn alt" name="authAction" value="signup" type="submit">יצירת חשבון חדש</button></form><p class="tiny">אם Supabase דורש אישור אימייל, יש לאשר את ההודעה שתתקבל.</p>`}</div></div>`;bind()}

function pageHTML(){if(state.page==='tasks')return tasksHTML();if(state.page==='calendar')return calendarHTML();if(state.page==='school')return schoolHTML();if(state.page==='connections')return connectionsHTML();if(state.page==='profile')return profileHTML();return dashboardHTML()}
function stats(){return [['כל המשימות',state.tasks.length],['לביצוע',state.tasks.filter(t=>t.status==='todo').length],['בתהליך',state.tasks.filter(t=>t.status==='progress').length],['הושלמו',state.tasks.filter(t=>t.status==='done').length]].map(([a,b])=>`<div class="stat"><span class="muted">${a}</span><strong>${b}</strong></div>`).join('')}
function dashboardHTML(){const upcoming=uniqueTasks(state.tasks).filter(t=>t.status!=='done').sort((a,b)=>(a.due_at||'9999').localeCompare(b.due_at||'9999')).slice(0,6);const exams=state.schoolItems.filter(x=>x.kind==='exam'&&(!x.event_date||x.event_date>=new Date().toISOString().slice(0,10))).sort((a,b)=>(a.event_date||'9999').localeCompare(b.event_date||'9999')).slice(0,3);const grades=state.schoolItems.filter(x=>x.kind==='grade').sort((a,b)=>String(b.updated_at).localeCompare(String(a.updated_at))).slice(0,3);const announcements=state.schoolItems.filter(x=>x.kind==='announcement').slice(-3).reverse();return `<div class="panel hero"><div><h2>שלום, ${esc(state.profile.display_name||state.auth.email?.split('@')[0]||'תלמיד')} 👋</h2><p class="muted">כל המשימות, המבחנים וההגשות שלך — בחשבון אחד.</p><div class="buttons"><button class="btn" data-nav="connections">חיבור מערכות</button><button class="btn alt" data-nav="tasks">הוספת משימה</button></div></div><span class="hero-icon">✦</span></div><div class="stats">${stats()}</div><div class="grid" style="margin-top:18px"><section class="panel"><div class="row"><h2>בקרוב להגשה</h2><button class="btn alt small" data-nav="tasks">כל המשימות</button></div>${upcoming.length?upcoming.map(taskCard).join(''):'<div class="empty">אין משימות פתוחות כרגע. חבר מערכת או הוסף משימה.</div>'}</section><section class="panel"><h2>מקורות המידע</h2>${apps.map(a=>`<div class="cardline"><span>${a.icon}</span><div class="taskinfo"><b>${a.name}</b><div class="desc">${connectionLabel(a.id)}</div></div></div>`).join('')}<button class="btn alt" data-nav="connections">ניהול חיבורים</button></section></div><div class="grid"><section class="panel"><div class="row"><h2>מבחנים קרובים</h2><button class="btn alt small" data-nav="school">לכל המידע</button></div>${exams.length?exams.map(x=>`<div class="cardline">${sourceMark(x.source)}<div class="taskinfo"><b>${esc(x.title)}</b><div class="desc">${esc(x.subject)} · ${isoDate(x.event_date)}</div></div></div>`).join(''):'<div class="empty">אין מבחנים מעודכנים</div>'}<h2>ציונים אחרונים</h2>${grades.length?grades.map(x=>`<div class="cardline">${sourceMark(x.source)}<div class="taskinfo"><b>${esc(x.title)}</b><div class="desc">${esc(x.subject)} · ${isoDate(x.event_date)}</div></div><span class="pill">${Number(x.score)}/100</span></div>`).join(''):'<div class="empty">אין ציונים מעודכנים</div>'}</section><section class="panel"><h2>הודעות ועדכונים</h2>${announcements.length?announcements.map(x=>`<div class="cardline">${sourceMark(x.source)}<div class="taskinfo"><b>${esc(x.title)}</b><div class="desc">${esc(x.description)}</div></div></div>`).join(''):'<div class="empty">אין הודעות שעודכנו</div>'}<button class="btn alt" data-nav="school">מערכת שעות, ציונים ומבחנים</button></section></div>`}
function sourceLabel(source){return apps.find(a=>a.id===source)?.name||'אישי'}
function sourceMark(source){const a=apps.find(a=>a.id===source);return `<span class="source-logo" role="img" aria-label="${esc(a?.name||'אישי')}">${a?.icon||'✍️'}</span>`}
function taskCard(t){const providers=t.duplicate_sources||[t.source];return `<div class="cardline">${sourceMark(t.source)}<div class="taskinfo"><div class="tasktitle">${esc(t.title)}</div><div class="desc">${esc(t.subject||'ללא מקצוע')} · ${isoDate(t.due_at)}</div><div class="desc">מקור: ${providers.map(x=>esc(sourceLabel(x))).join(' + ')}</div>${provenanceLine(t)}${t.description?`<p class="task-description">${esc(t.description)}</p>`:''}${t.source_url?`<div class="desc"><a href="${safeHref(t.source_url)}" target="_blank" rel="noopener noreferrer">מעבר למשימה המקורית ↗</a></div>`:''}</div><div class="taskactions"><select aria-label="סטטוס משימה" data-taskstatus="${esc(t.id)}"><option value="todo" ${t.status==='todo'?'selected':''}>לא התחלתי</option><option value="progress" ${t.status==='progress'?'selected':''}>בתהליך</option><option value="done" ${t.status==='done'?'selected':''}>הושלם</option></select><button class="btn danger small" data-delete="${esc(t.id)}" aria-label="מחיקת משימה">×</button></div></div>`}
function tasksHTML(){const filtered=filterAndSortTasks(state.tasks,{source:state.sourceFilter,subject:state.subjectFilter,status:state.filter,until:state.untilFilter,sort:state.sort});const subjects=[...new Set(state.tasks.map(t=>t.subject).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'he'));const selectOptions=(items,selected)=>items.map(([value,label])=>`<option value="${esc(value)}" ${selected===value?'selected':''}>${esc(label)}</option>`).join('');return `<section class="panel"><h2>הוספת משימה חדשה</h2><form id="taskForm" class="formgrid"><label class="field">שם המשימה<input name="title" required maxlength="240" placeholder="למשל: תרגילים במתמטיקה"></label><label class="field">מקצוע<input name="subject" maxlength="100" placeholder="מתמטיקה"></label><label class="field">מועד הגשה<input name="due" type="date"></label><label class="field">קישור למקור<input name="url" type="url" placeholder="https://..."></label><label class="field full">תיאור<textarea name="description" maxlength="2000" rows="2" placeholder="מה צריך להגיש?"></textarea></label><div class="field full"><button class="btn">הוספת משימה</button></div></form></section><section class="panel"><div class="row"><h2>כל המשימות במקום אחד</h2><span class="muted">${filtered.length} משימות ייחודיות</span></div><div class="tabbar">${[['all','הכול'],['todo','לא התחילו'],['progress','בתהליך'],['done','הושלמו']].map(([a,b])=>`<button class="tab ${state.filter===a?'active':''}" data-filter="${a}">${b}</button>`).join('')}</div><div class="taskfilters"><label class="field">מערכת<select id="sourceFilter">${selectOptions([['all','כל המערכות'],...apps.map(a=>[a.id,a.name]),['manual','אישי']],state.sourceFilter)}</select></label><label class="field">מקצוע<select id="subjectFilter">${selectOptions([['all','כל המקצועות'],...subjects.map(x=>[x,x])],state.subjectFilter)}</select></label><label class="field">הגשה עד<input id="untilFilter" type="date" value="${esc(state.untilFilter)}"></label><label class="field">מיון<select id="sortFilter">${selectOptions([['urgent','דחיפות (הקרוב קודם)'],['subject','לפי מקצוע'],['newest','עודכן לאחרונה']],state.sort)}</select></label></div>${filtered.length?filtered.map(taskCard).join(''):'<div class="empty">אין משימות בסינון הזה. מידע שלא סונכרן עדיין לא יוצג.</div>'}<p class="tiny">משימות זהות לפי שם, מקצוע ויום הגשה מאוחדות בתצוגה; רשומות המקור נשמרות בנפרד.</p></section>`}
function calendarHTML(){const dates=Array.from({length:14},(_,i)=>{const d=new Date();d.setHours(0,0,0,0);d.setDate(d.getDate()+i);return d});return `<section class="panel"><h2>14 הימים הקרובים</h2><p class="muted">מועדי הגשה מכל המקורות המחוברים</p><div class="calendar">${dates.map(d=>{const tasks=state.tasks.filter(t=>t.due_at&&new Date(t.due_at).toDateString()===d.toDateString());return `<div class="day"><strong>${d.toLocaleDateString('he-IL',{weekday:'short',day:'numeric',month:'short'})}</strong>${tasks.map(t=>`<div class="event" title="${esc(t.title)}">${esc(t.title)}</div>`).join('')}</div>`}).join('')}</div></section>`}
// ---- Lumio 4.0 connection facts (graceful degradation for pre-upgrade-2 rows) ----
const RETRIEVAL_LABELS={official_api:'דרך API מורשה',public_school_feed:'מהמקור הציבורי של בית הספר',user_import:'ייבוא ידני שלך',user_entry:'הזנה ידנית'};
const LEGACY_STATE_WRITE={'synced':'api_connected','syncing':'api_connected','connected_unverified':'api_connected','error':'not_connected','manual_import_only':'imported','awaiting_consent':'not_connected','needs_reauth':'not_connected','unavailable':'not_connected','login_only':'not_connected','requires_admin':'not_connected','not_connected':'not_connected'};
function providerDefault(p){if(!p)return 'not_connected';if(p.id==='classroom')return state.config.google?'awaiting_consent':'manual_import_only';return p.defaultState}
function connState(c,p){if(!c)return providerDefault(p);return CONNECTION_STATES.includes(c.state)?c.state:(['imported','api_connected'].includes(c.state)?c.state:providerDefault(p))}
function connFacts(c,p){const s=connState(c,p);const computed=connectionFacts(s,Boolean(state.token),c?.last_sync_at,c?.last_error);if(!c||!('identity_authenticated' in c))return computed;return {identityAuthenticated:c.identity_authenticated??computed.identityAuthenticated,permissionGranted:c.permission_granted??computed.permissionGranted,dataReadable:c.data_readable??computed.dataReadable,syncWorking:c.sync_working??computed.syncWorking}}
const factMark=b=>b?'✓':'✗';
function connectionLabel(id){const p=PROVIDERS.find(x=>x.id===id);const c=state.connections.find(x=>x.provider===id);return heStatus(connState(c,p),c?.last_sync_at)}
function heRelTime(iso){const ms=Date.now()-new Date(iso).getTime();if(!Number.isFinite(ms))return 'לא ידוע';const m=Math.floor(ms/60000);if(m<1)return 'עכשיו';if(m<60)return `לפני ${m} דק׳`;const h=Math.floor(m/60);if(h<24)return `לפני ${h} שעות`;const d=Math.floor(h/24);return d===1?'לפני יום אחד':`לפני ${d} ימים`}
function provenanceLine(t){const label=RETRIEVAL_LABELS[t.retrieval_method];if(!label&&!t.synced_at)return '';return `<div class="desc tiny muted">נשמר ב: ${label||'הזנה/ייבוא ידני'} · ${t.synced_at?`סונכרן ${heRelTime(t.synced_at)}`:'הזנה/ייבוא ידני'}</div>`}
function capabilityList(p){const names=[];if(p.capabilities.assignments)names.push('מטלות');if(p.capabilities.exams)names.push('מבחנים');if(p.capabilities.grades)names.push('ציונים');if(p.capabilities.announcements)names.push('הודעות');if(p.capabilities.timetable)names.push('מערכת שעות');if(p.capabilities.backgroundSync)names.push('סנכרון רקע');return names.join(' · ')||'ללא יכולות קריאה'}
function feedPreviewHTML(id){
 const pv=state.feedPreview;
 if(!pv||pv.provider!==id)return '';
 const rows=pv.items.map(it=>it.day_of_week!=null?`יום ${Number(it.day_of_week)+1} · ${esc(String(it.start_time||'').slice(0,5))} · ${esc(it.title)}`:esc(it.title)).join('<br>');
 return `<div class="cardline"><div class="taskinfo"><b>תצוגה מקדימה: ${pv.items.length} פריטים${pv.stamp?` · מעודכן ל: ${esc(pv.stamp)}`:''}</b><div class="desc tiny muted">${rows}</div></div><div class="buttons"><button class="btn small" data-action="feedAdd">הוסף לחשבון שלי</button></div></div>`
}
function petelFeedRow(){
 const c=state.connections.find(x=>x.provider==='petel');
 const url=c?.feed_url||'';
 return `<div class="cardline"><div class="taskinfo"><b>חבר פיד ICS</b><div class="desc tiny muted">1. בפתל: פתח את יומן התלמיד שלך. 2. בחר אפשרות שיתוף/קישור ICS של היומן. 3. הדבק כאן את הכתובת שנוצרה. הכתובת מכילה מזהה אישי שלך — היא נשמרת רק בחשבון שלך ונמחקת בנתק.</div><label class="field" style="display:block;margin-top:6px">כתובת הפיד<input id="feed-petel" type="url" value="${esc(url)}" placeholder="https://… (קישור ICS של היומן שלך)"></label><div class="buttons" style="margin-top:6px"><button class="btn small" data-action="feedCheck" data-provider="petel">בדוק פיד</button>${url?`<button class="btn alt small" data-action="feedRefresh" data-provider="petel">רענן פיד</button>`:''}</div>${feedPreviewHTML('petel')}</div></div>`
}
function shahafFeedRow(){
 const c=state.connections.find(x=>x.provider==='shahaf');
 const url=c?.feed_url||'';
 return `<div class="cardline"><div class="taskinfo"><b>חבר מערכת שעות בית-ספר (שחף)</b><div class="desc tiny muted">בית הספר לא מפרסם כרגע את מערכת השעות של חטיבת הביניים (katzir-b.shahaf.site אינו פועל — בדיקה 12.11.2026). ברגע שייפרסם, אפשר לחבר כאן בלי קוד חדש (הממיר אומת על דפים שכן מפורסמים).</div><label class="field" style="display:block;margin-top:6px">כתובת מערכת השעות<input id="feed-shahaf" type="url" value="${esc(url)}" placeholder="https://katzir-b.shahaf.site/?cls=5&tab=timetable&mode=student"></label><div class="buttons" style="margin-top:6px"><button class="btn small" data-action="feedCheck" data-provider="shahaf">בדוק פיד</button>${url?`<button class="btn alt small" data-action="feedRefresh" data-provider="shahaf">רענן פיד</button>`:''}</div>${feedPreviewHTML('shahaf')}<div class="buttons" style="margin-top:6px"><button class="btn alt small" data-action="copyShahafRequest">העתק בקשה לבית הספר</button><span class="desc tiny muted">צורפים: 08-9471653 / katzirb@educ.org.il</span></div></div></div>`
}
function connCard(p){
 const c=state.connections.find(x=>x.provider===p.id);
 const s=connState(c,p);
 const f=connFacts(c,p);
 const btns=[`<a class="btn alt small" href="${esc(p.sourceLink)}" target="_blank" rel="noopener noreferrer">פתיחת האתר ↗</a>`];
 if(p.id==='classroom'){
  if(state.config.google){
   btns.push(`<button class="btn small" data-action="googleConnect">חבר Google</button>`);
   if(state.token)btns.push(`<button class="btn small" data-action="googleConnect">סנכרן עכשיו</button>`);
  }else{
   btns.push(`<span class="desc tiny muted">נדרש OAuth Client של מנהל לומיו</span>`);
  }
 }
 btns.push(`<button class="btn alt small" data-action="disconnect" data-provider="${p.id}">נתק</button>`);
 btns.push(`<button class="btn danger small" data-action="deleteSource" data-provider="${p.id}">מחק נתונים ממערכת זו</button>`);
 const feed=p.id==='petel'?petelFeedRow():p.id==='shahaf'?shahafFeedRow():'';
 return `<div class="conn"><div class="round">${p.icon}</div><main><h3>${p.name}</h3><div class="desc">${p.heDescription}</div><div class="desc"><b>${esc(heStatus(s,c?.last_sync_at))}</b></div><div class="desc tiny muted">עובדות חיבור — זהות: ${factMark(f.identityAuthenticated)} · הרשאה: ${factMark(f.permissionGranted)} · קריאת נתונים: ${factMark(f.dataReadable)} · סנכרון: ${factMark(f.syncWorking)}</div><div class="desc tiny muted">יכולות: ${esc(capabilityList(p))}</div>${feed}<p class="tiny">${p.howToConnect}</p></main><div class="buttons">${btns.join('')}</div></div>`
}
function connectionsHTML(){return `<div class="warning">התחברות באתר מקור ≠ הרשאת קריאה ללומיו. אפשר להשתמש ב־API הרשמי של Classroom, או לייבא נתונים שהאתר מציג באמצעות תוסף לומיו. לא נדרשות סיסמאות משרד החינוך. כרטיס מציג רק "מחובר/סנכרון הצליח" אחרי קריאת נתונים שנבדקה באמת.</div><section class="panel"><h2>מערכות הלימוד שלי</h2><div class="connections">${PROVIDERS.map(connCard).join('')}</div></section><section class="panel"><h2>העברת משימות ישירות מהדפדפן או מקובץ</h2><p class="muted">במחשב: תוסף Lumio Reader מאפשר לסרוק עמוד פתוח, לבדוק את המשימות ולהעביר אותן ישירות ללומיו בלחיצה אחת. לחלופין אפשר לייבא JSON, CSV או ICS. אפשר לבצע זאת גם בטלפון. הייבוא אינו יוצר סנכרון אוטומטי.</p><label class="field">מקור הקובץ<select id="fileSource"><option value="manual">משימות כלליות</option><option value="classroom">Classroom</option><option value="mashov">משו״ב</option><option value="ofek">אופק</option><option value="petel">פטל</option><option value="shahaf">שחף</option></select></label><div class="buttons"><label class="btn" for="importFile">ייבוא JSON / CSV / ICS</label><input style="display:none" type="file" id="importFile" accept=".json,.csv,.ics,application/json,text/csv,text/calendar"><button class="btn alt" data-action="export">ייצוא המשימות שלי</button></div><p class="tiny">ייבוא מקומי לא אומר שהחיבור מסנכרן ברקע. ב־Classroom אפשר לסנכרן שוב בלחיצה כל עוד ההרשאה תקפה.</p></section><section class="panel"><h2>ייבוא מהיר גם בטלפון — בלי תוסף</h2><p class="muted">פתח את המשימה באתר הרשמי, העתק את הטקסט והדבק כאן. כל שורה תהפוך למשימה שתישמר בחשבון שלך. אפשר להוסיף מקצוע ותאריך בפורמט: <code>שם משימה | מקצוע | 2026-11-20</code>.</p><form id="pasteForm"><label class="field">מהיכן המשימות?<select name="source"><option value="mashov">משו״ב</option><option value="ofek">אופק</option><option value="petel">פטל</option><option value="shahaf">שחף</option><option value="classroom">Classroom — ייבוא ידני</option><option value="manual">אחר</option></select></label><label class="field full">הדבק כאן את המשימות<textarea name="pasted" required rows="6" maxlength="25000" placeholder="לקרוא פרק 3 | היסטוריה | 2026-11-20\nלפתור עמוד 42 | מתמטיקה"></textarea></label><button class="btn" type="submit">שמור משימות בחשבון שלי</button></form><p class="tiny">זהו ייבוא ידני, לא קריאה אוטומטית של חשבון משרד החינוך. אל תדביק סיסמאות או פרטים אישיים של תלמידים אחרים.</p></section>`}
const schoolKinds={exam:'מבחנים',grade:'ציונים',announcement:'הודעות',timetable:'מערכת שעות'};
function schoolHTML(){const kind=state.schoolView;const rows=state.schoolItems.filter(x=>x.kind===kind).sort((a,b)=>kind==='timetable'?(Number(a.day_of_week)-Number(b.day_of_week))||String(a.start_time||'').localeCompare(String(b.start_time||'')):(a.event_date||'9999').localeCompare(b.event_date||'9999'));const sourceOptions=[['manual','הזנה אישית'],...apps.map(a=>[a.id,a.name+' (ייבוא ידני)'])];return `${!state.schoolDataReady?'<div class="warning">כדי להפעיל מבחנים, ציונים, הודעות ומערכת שעות, יש להריץ פעם אחת את database-upgrade.sql ב־Supabase. אין שינוי בטבלאות הקיימות.</div>':''}<section class="panel"><h2>המידע הלימודי שלי</h2><div class="tabbar">${Object.entries(schoolKinds).map(([key,label])=>`<button class="tab ${key===kind?'active':''}" data-school-tab="${key}">${label}</button>`).join('')}</div>${rows.length?rows.map(item=>`<div class="cardline">${sourceMark(item.source)}<div class="taskinfo"><div class="tasktitle">${esc(item.title)} ${kind==='grade'?`<span class="pill">${Number(item.score)}/100</span>`:''}</div><div class="desc">${esc(item.subject||'')} · ${esc(sourceLabel(item.source))} (הזנה/ייבוא) · ${kind==='timetable'?`יום ${Number(item.day_of_week)+1} · ${esc(String(item.start_time||'').slice(0,5))} ${item.room?'· '+esc(item.room):''}`:isoDate(item.event_date)}</div>${item.description?`<p class="task-description">${esc(item.description)}</p>`:''}${item.change_type==='cancelled'?'<span class="pill warn">שיעור בוטל</span>':item.change_type==='changed'?'<span class="pill warn">שינוי מערכת</span>':''}${item.source_url?`<div class="desc"><a href="${safeHref(item.source_url)}" target="_blank" rel="noopener noreferrer">מקור המידע ↗</a></div>`:''}</div><button class="btn small danger" data-school-delete="${item.id}">מחק</button></div>`).join(''):'<div class="empty">אין מידע מאומת להצגה בקטגוריה זו. לא מוצגים נתוני דוגמה.</div>'}</section><section class="panel"><h2>הוספת ${schoolKinds[kind].slice(0,-1)} או מידע שהתקבל ממקור מורשה</h2><p class="muted">אפשר להזין נתונים בעצמך או לייבא קובץ שקיבלת מהמערכת המקורית. אין בכך אישור לסנכרון אוטומטי.</p><form id="schoolForm" class="formgrid"><label class="field">מקור<select name="source">${sourceOptions.map(([id,name])=>`<option value="${id}">${esc(name)}</option>`).join('')}</select></label><label class="field">כותרת<input name="title" required maxlength="240"></label><label class="field">מקצוע<input name="subject" maxlength="100"></label><label class="field">${kind==='timetable'?'תאריך (לא חובה)':'תאריך'}<input name="date" type="date"></label>${kind==='grade'?'<label class="field">ציון מתוך 100<input name="score" type="number" min="0" max="100" step="0.01" required></label>':''}${kind==='timetable'?'<label class="field">יום בשבוע (0=ראשון, 6=שבת)<input name="day" type="number" min="0" max="6" required></label><label class="field">שעת התחלה<input name="start" type="time" required></label><label class="field">שעת סיום<input name="end" type="time"></label><label class="field">כיתה / חדר<input name="room"></label><label class="field">שינוי<select name="change"><option value="normal">רגיל</option><option value="changed">השתנה</option><option value="cancelled">בוטל</option></select></label>':''}<label class="field full">תיאור<textarea name="description" rows="2" maxlength="2000"></textarea></label><label class="field full">קישור למקור<input name="url" type="url"></label><div class="field full"><button class="btn" ${!state.schoolDataReady?'disabled':''}>שמור בחשבון</button></div></form></section><section class="panel"><h2>ייבוא נתוני בית ספר בפורמט JSON</h2><p class="muted">קובץ עם מערך <code>items</code>; לכל רשומה יש kind, source, title ושדות לפי הסוג. קובץ זה עובר אימות לפני שמירה.</p><input type="file" id="schoolImport" accept=".json,application/json" ${!state.schoolDataReady?'disabled':''}></section>`}
async function saveSchoolRecords(items,provenance){if(!state.schoolDataReady)throw Error('נדרשת הרצת database-upgrade.sql ב־Supabase');const rows=items.map(x=>({...sanitizeStudyEntry(x,x.kind,x.source),kind:x.kind,user_id:state.auth.id,updated_at:new Date().toISOString()}));await upsertSchoolRows(rows,provenance);await loadAccount();return rows.length}
async function addSchoolItem(e){e.preventDefault();const f=new FormData(e.target);try{const row={kind:state.schoolView,source:String(f.get('source')),title:f.get('title'),subject:f.get('subject'),description:f.get('description'),event_date:f.get('date')||null,score:f.get('score'),day_of_week:f.get('day'),start_time:f.get('start'),end_time:f.get('end'),room:f.get('room'),change_type:f.get('change'),source_url:f.get('url'),external_id:crypto.randomUUID()};await saveSchoolRecords([row],{retrieval_method:'user_entry'});notice('המידע נשמר בחשבון שלך')}catch(err){notice(err.message,'error')}}
async function importSchoolFile(e){try{const file=e.target.files[0];if(!file)return;if(file.size>2000000)throw Error('קובץ גדול מדי');const json=JSON.parse(await file.text());const items=Array.isArray(json)?json:json.items;if(!Array.isArray(items)||items.length>300)throw Error('קובץ לא תקין או גדול מדי');const n=await saveSchoolRecords(items,{retrieval_method:'user_import'});notice(`${n} פריטים יובאו לחשבון שלך`)}catch(err){notice('ייבוא נכשל: '+err.message,'error')}}
async function deleteSchoolItem(id){if(!confirm('למחוק את הפריט?'))return;const {error}=await state.client.from('school_items').delete().eq('id',id).eq('user_id',state.auth.id);if(error)notice(error.message,'error');else{state.schoolItems=state.schoolItems.filter(x=>String(x.id)!==String(id));render()}}
function privacyHTML(){
 const rows=PROVIDERS.map(p=>{
  const c=state.connections.find(x=>x.provider===p.id);
  const s=connState(c,p);
  const f=connFacts(c,p);
  return `<div class="cardline"><div class="taskinfo"><b>${p.name}</b><div class="desc tiny muted">הרשאות פעילות — זהות: ${factMark(f.identityAuthenticated)} · הרשאה: ${factMark(f.permissionGranted)} · קריאת נתונים: ${factMark(f.dataReadable)} · סנכרון: ${factMark(f.syncWorking)}</div><div class="desc tiny muted">${esc(heStatus(s,c?.last_sync_at))}${c?.last_sync_at?` · סנכרון אחרון ${heRelTime(c.last_sync_at)}`:''}</div>${c?.feed_url?`<div class="desc tiny muted">פיד מחובר: <a href="${safeHref(c.feed_url)}" target="_blank" rel="noopener noreferrer">הצג כתובת</a> (כתובת הפיד מכילה מזהה אישי; נמחקת בנתק)</div>`:''}</div><div class="buttons"><button class="btn alt small" data-action="disconnect" data-provider="${p.id}">ביטול</button><button class="btn danger small" data-action="deleteSource" data-provider="${p.id}">מחיקת נתונים מהמקור</button></div></div>`
 }).join('');
 const cls=state.connections.find(x=>x.provider==='classroom');
 const key=cls?.apps_script_key||null;
 const keyPanel=key
  ?`<div class="warning" style="margin-top:12px"><b>מפתח לסנכרון יומי (Classroom, דרך Apps Script שלך):</b> <code>${esc(key)}</code><div class="desc tiny muted" style="margin-top:6px">מי שמחזיק את המפתח יכול להוסיף נתונים לחשבון — שמרו אותו; אפשר לסובב/לבטל כאן. המפתח נשמר בחשבון שלך בלבד. להפעלה: apps-script/README-HE.md.</div><div class="buttons" style="margin-top:6px"><button class="btn alt small" data-action="copyKey">העתק מפתח</button><button class="btn small" data-action="rotateKey">סובב מפתח</button><button class="btn danger small" data-action="cancelDailySync">בטל סנכרון יומי</button></div></div>`
  :`<div class="warning" style="margin-top:12px"><b>סנכרון יומי אוטומטי (Classroom):</b> <button class="btn small" data-action="createKey">צור מפתח לסנכרון יומי</button><div class="desc tiny muted" style="margin-top:6px">המפתח (32 תווים) משמש את סקריפט ה־Apps Script שלך כדי לשלוח נתונים לחשבון זה בלבד. אין סיסמאות ואין refresh token. הוראות: apps-script/README-HE.md.</div></div>`;
 return `<section class="panel"><h2>הגדרות פרטיות</h2><p class="muted">הרשאות פעילות לכל מקור, ביטול חיבור, מחיקת נתונים ומפתח הסנכרון היומי. פתיחת אתר של מקור אינה מעניקה ללומיו שום הרשאה.</p>${rows}${keyPanel}<div class="buttons" style="margin-top:12px"><button class="btn alt" data-action="export">ייצוא כל הנתונים שלי</button></div><p class="tiny">הייצוא כולל פרופיל, משימות ומידע לימודי. אינו כולל מפתחות או כתובות פיד (ניתן למחוק אותן בנתק).</p></section>`
}
function profileHTML(){const p=state.profile;return `<section class="panel"><h2>פרטי תלמיד ובית ספר</h2><form id="profileForm" class="formgrid"><label class="field">שם תצוגה<input name="display_name" value="${esc(p.display_name)}"></label><label class="field">עיר<input name="city" value="${esc(p.city)}" required></label><label class="field">בית ספר<input name="school" value="${esc(p.school)}" required></label><label class="field">שכבה<select name="grade">${['ז׳','ח׳','ט׳','י׳','י"א','י"ב'].map(x=>`<option ${x===p.grade?'selected':''}>${x}</option>`).join('')}</select></label><label class="field">כיתה<input name="classroom" value="${esc(p.classroom)}" required></label><div class="field full"><button class="btn">שמירת פרטים</button></div></form></section>${privacyHTML()}<section class="panel"><h2>ניהול חשבון</h2><p class="muted">${esc(state.auth.email)}</p><div class="buttons"><button class="btn alt" data-action="logout">התנתקות</button><button class="btn alt" data-action="export">הורדת עותק הנתונים שלי</button></div><p class="tiny">מחיקת החשבון כולו מתבצעת מול מנהל פרויקט Supabase. מחיקת משימות בודדות זמינה במסך משימות.</p></section>`}
function bind(){document.querySelectorAll('[data-nav]').forEach(el=>el.addEventListener('click',()=>{state.page=el.dataset.nav;state.message='';render()}));document.querySelectorAll('[data-action]').forEach(el=>el.addEventListener('click',()=>actions(el.dataset.action,el.dataset.provider)));$('#authForm')?.addEventListener('submit',authSubmit);$('#profileForm')?.addEventListener('submit',saveProfile);$('#taskForm')?.addEventListener('submit',addTask);document.querySelectorAll('[data-taskstatus]').forEach(el=>el.addEventListener('change',()=>changeStatus(el.dataset.taskstatus,el.value)));document.querySelectorAll('[data-delete]').forEach(el=>el.addEventListener('click',()=>removeTask(el.dataset.delete)));document.querySelectorAll('[data-filter]').forEach(el=>el.addEventListener('click',()=>{state.filter=el.dataset.filter;render()}));$('#importFile')?.addEventListener('change',importFile);$('#pasteForm')?.addEventListener('submit',importPasted);$('#sourceFilter')?.addEventListener('change',e=>{state.sourceFilter=e.target.value;render()});$('#subjectFilter')?.addEventListener('change',e=>{state.subjectFilter=e.target.value;render()});$('#untilFilter')?.addEventListener('change',e=>{state.untilFilter=e.target.value;render()});$('#sortFilter')?.addEventListener('change',e=>{state.sort=e.target.value;render()});document.querySelectorAll('[data-school-tab]').forEach(el=>el.addEventListener('click',()=>{state.schoolView=el.dataset.schoolTab;render()}));$('#schoolForm')?.addEventListener('submit',addSchoolItem);$('#schoolImport')?.addEventListener('change',importSchoolFile);document.querySelectorAll('[data-school-delete]').forEach(el=>el.addEventListener('click',()=>deleteSchoolItem(el.dataset.schoolDelete)));}

async function authSubmit(e){e.preventDefault();const btn=e.submitter;const f=new FormData(e.target),email=String(f.get('email')).trim(),password=String(f.get('password'));try{const signup=btn?.value==='signup';const {data,error}=signup?await state.client.auth.signUp({email,password}):await state.client.auth.signInWithPassword({email,password});if(error)throw error;if(data.session){state.auth=data.user;await loadAccount();await processReaderImport();notice(signup?'החשבון נוצר':'התחברת בהצלחה')}else notice('נשלח אליך אימייל אישור. לאחר האישור התחבר שוב.')}catch(e){notice('ההתחברות נכשלה: '+e.message,'error')}}
async function saveProfile(e){e.preventDefault();const f=new FormData(e.target),p={user_id:state.auth.id};for(const key of ['display_name','city','school','grade','classroom'])p[key]=String(f.get(key)).trim().slice(0,100);try{const {error}=await state.client.from('profiles').upsert({...p,updated_at:new Date().toISOString()});if(error)throw error;state.profile=p;notice('הפרטים נשמרו בענן')}catch(e){notice(e.message,'error')}}
async function upsertTasks(tasks,provenance){if(!tasks.length)return 0;const stamp=new Date().toISOString();const build=useProv=>tasks.map(t=>{const out={...t,user_id:state.auth.id,updated_at:stamp};if(useProv){const rm=provenance?.retrieval_method||'user_entry';out.retrieval_method=rm;out.verification_state=provenance?.verification_state||'user_imported_unverified';if(rm==='official_api'||rm==='public_school_feed')out.synced_at=provenance?.synced_at||stamp}return out});const run=async useProv=>{for(let i=0;i<tasks.length;i+=100){const {error}=await state.client.from('tasks').upsert(build(useProv).slice(i,i+100),{onConflict:'user_id,source,external_id'});if(error)throw error}};try{await run(true)}catch(e){if(state.privacyColsReady){state.privacyColsReady=false;notice('להשלמת תצוגת ההרשאות יש להריץ database-upgrade-2.sql','error');await run(false)}else throw e}state.tasks=mergeTasks(state.tasks,build(false));await loadAccount();return tasks.length}
async function upsertSchoolRows(rows,provenance){if(!rows.length)return 0;const stamp=new Date().toISOString();const build=useProv=>rows.map(r=>{const out={...r,user_id:state.auth.id,updated_at:stamp};if(useProv){const rm=provenance?.retrieval_method||'user_entry';out.retrieval_method=rm;out.verification_state=provenance?.verification_state||'user_imported_unverified';if(rm==='official_api'||rm==='public_school_feed')out.synced_at=provenance?.synced_at||stamp}return out});const run=async useProv=>{for(let i=0;i<rows.length;i+=100){const {error}=await state.client.from('school_items').upsert(build(useProv).slice(i,i+100),{onConflict:'user_id,kind,source,external_id'});if(error)throw error}};try{await run(true)}catch(e){if(state.privacyColsReady){state.privacyColsReady=false;notice('להשלמת תצוגת ההרשאות יש להריץ database-upgrade-2.sql','error');await run(false)}else throw e};return rows.length}
async function addTask(e){e.preventDefault();const f=new FormData(e.target);const t=normalizeTask({title:f.get('title'),subject:f.get('subject'),description:f.get('description'),due:f.get('due')||null,url:f.get('url')||null,external_id:crypto.randomUUID()});try{await upsertTasks([t],{retrieval_method:'user_entry'});notice('המשימה נשמרה בחשבון שלך')}catch(err){notice(err.message,'error')}}
async function changeStatus(id,status){const t=state.tasks.find(x=>String(x.id)===String(id));if(!t)return;try{const {error}=await state.client.from('tasks').update({status}).eq('id',t.id).eq('user_id',state.auth.id);if(error)throw error;t.status=status;render()}catch(e){notice(e.message,'error')}}
async function removeTask(id){if(!confirm('למחוק את המשימה?'))return;try{const {error}=await state.client.from('tasks').delete().eq('id',id).eq('user_id',state.auth.id);if(error)throw error;state.tasks=state.tasks.filter(x=>String(x.id)!==String(id));render()}catch(e){notice(e.message,'error')}}
async function trackConnection(provider,stateName,facts,lastError=null,extra=null){
 const base={user_id:state.auth.id,provider,state:stateName,last_sync_at:new Date().toISOString(),last_error:lastError??null};
 const attempts=[];
 if(facts)attempts.push({...base,...(extra||{}),identity_authenticated:facts.identityAuthenticated,permission_granted:facts.permissionGranted,data_readable:facts.dataReadable,sync_working:facts.syncWorking});
 attempts.push({...base,...(extra||{})});
 const legacy=LEGACY_STATE_WRITE[stateName];
 if(legacy&&legacy!==stateName)attempts.push({...base,state:legacy,...(extra||{})});
 if(extra)attempts.push({...base,state:legacy||stateName});
 let ok=false,lastErr=null;
 for(const row of attempts){const {error}=await state.client.from('connections').upsert(row,{onConflict:'user_id,provider'});if(!error){ok=true;if(extra?.feed_url&&!('feed_url' in row))notice('החיבור נשמר, אבל הפיד יתחבר רק אחרי הרצת database-upgrade-2.sql — ללא זה כתובת הפיד תימחק','error');break}lastErr=error}
 if(!ok){if(/could not find the/i.test(lastErr?.message||'')){state.privacyColsReady=false;notice('להשלמת תצוגת ההרשאות יש להריץ database-upgrade-2.sql','error')}else notice('שמירת החיבור נכשלה: '+(lastErr?.message||'שגיאה לא ידועה'),'error')}
 await loadAccount();
}
async function importFile(e){const file=e.target.files[0];if(!file)return;try{if(file.size>3_000_000)throw Error('הקובץ גדול מדי');const source=String($('#fileSource')?.value||'manual');const tasks=parseDataFile(await file.text(),file.name,source);if(!tasks.length)throw Error('לא נמצאו משימות בקובץ');await upsertTasks(tasks,{retrieval_method:'user_import'});for(const source of new Set(tasks.map(x=>x.source).filter(x=>x!=='manual')))await trackConnection(source,'imported');notice(`${tasks.length} משימות יובאו לחשבון לומיו`)}catch(err){notice(err.message,'error')}}
async function importPasted(e){e.preventDefault();try{const f=new FormData(e.target);const source=String(f.get('source'));const tasks=parsePastedTasks(f.get('pasted'),source);if(!tasks.length)throw Error('לא נמצאו משימות');await upsertTasks(tasks,{retrieval_method:'user_import'});if(source!=='manual')await trackConnection(source,'imported');notice(`${tasks.length} משימות נשמרו בחשבון שלך`)}catch(err){notice(err.message,'error')}}
function download(name,obj){const blob=new Blob([JSON.stringify(obj,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
async function actions(a,provider){if(a==='dismiss'){state.message='';render()}if(a==='logout'){await state.client.auth.signOut();state.auth=null;render()}if(a==='export')download('lumio-export.json',{profile:state.profile,tasks:state.tasks.map(t=>({source:t.source,external_id:t.external_id,title:t.title,subject:t.subject,description:t.description,due_at:t.due_at,source_url:t.source_url,status:t.status,retrieval_method:t.retrieval_method||null,verification_state:t.verification_state||null,synced_at:t.synced_at||null})),school_items:state.schoolItems.map(x=>({kind:x.kind,source:x.source,external_id:x.external_id,title:x.title,subject:x.subject,description:x.description,event_date:x.event_date,score:x.score,day_of_week:x.day_of_week,start_time:x.start_time,end_time:x.end_time,room:x.room,change_type:x.change_type,retrieval_method:x.retrieval_method||null,verification_state:x.verification_state||null,synced_at:x.synced_at||null}))});if(a==='googleConnect')connectGoogle();if(a==='feedCheck')feedCheck(provider);if(a==='feedAdd')feedAdd();if(a==='feedRefresh')feedRefresh(provider);if(a==='disconnect')disconnectProvider(provider);if(a==='deleteSource')deleteSourceData(provider);if(a==='copyKey')copySyncKey();if(a==='rotateKey')rotateSyncKey();if(a==='cancelDailySync')cancelDailySync();if(a==='createKey')createSyncKey();if(a==='copyShahafRequest')copyShahafRequest()}
function copyShahafRequest(){const text='נא לפרסם את מערכת השעות של חטיבת הביניים באתר שחף (katzir-b.shahaf.site) לצורכי צפייה בקבוצת תלמידים. תודה. (צורפים: 08-9471653 / katzirb@educ.org.il)';navigator.clipboard?.writeText(text).then(()=>notice('הבקשה הועתקה — אפשר לשלוח לבית הספר.')).catch(()=>notice('ההעתקה נכשלה — העתק את הטקסט ידנית.','error'))}
function fetchFailureHint(e){
 if(e instanceof TypeError)return 'השרת חוסם שליפה ישירה מהדפדפן — אפשרות: הורדת קובץ ICS וייבוא';
 if(e&&e.name==='AbortError')return 'הפיד לא ענה בתוך 20 שניות — אפשרות: הורדת קובץ ICS וייבוא';
 const m={AUTH_EXPIRED:'ההרשאה בקובץ פגה — יש לייצר קישור חדש',PERMISSION_DENIED:'השרת סירב לקריאה (אין הרשאה)',SOURCE_NOT_FOUND:'הכתובת לא נמצאה (404)',RATE_LIMITED:'יותר מדי בקשות — נסה שוב מאוחר יותר',NETWORK_ERROR:'בעיה ברשת או שהשרת חוסם שליפה מהדפדפן — אפשרות: הורדת קובץ ICS וייבוא',DATA_VALIDATION_FAILED:'הפיד גדול מדי או בתוכן לא תקין'};
 return m[e.message]||('שגיאה בשליפת הפיד: '+(e.message||e));
}
async function feedCheck(providerId){
 const p=PROVIDERS.find(x=>x.id===providerId);
 if(!p||state.feedBusy)return;
 const kind=p.id==='petel'?'ics_url':'public_page';
 const input=document.getElementById('feed-'+p.id);
 const v=validateFeedUrl(String(input?.value||'').trim(),kind);
 if(!v.ok)return notice(v.error,'error');
 state.feedPreview=null;
 state.feedBusy=providerId;render();
 try{
  const text=await fetchFeed(v.url);
  const result=importFeedItems(text,p.id,kind);
  state.feedBusy=null;
  if(!result.items.length){state.feedPreview=null;render();return notice('לא זוהו פריטים תקינים בפיד — לא נשמר דבר.','error')}
  state.feedPreview={provider:providerId,kind,url:v.url,items:result.items,stamp:result.stamp};
  render();
  notice(`זוהו ${result.items.length} פריטים מהפיד${result.skipped?` (${result.skipped} שורות פוסלו)`:''}. בדוק ולחץ "הוסף לחשבון שלי".`);
 }catch(e){
  state.feedBusy=null;state.feedPreview=null;render();
  notice(fetchFailureHint(e),'error');
 }
}
function shahafRowsToItems(items,url){return items.map(it=>({kind:'timetable',source:'shahaf',external_id:it.external_id,title:it.title,subject:it.subject||it.title,description:'',event_date:null,source_url:url,day_of_week:it.day_of_week,start_time:it.start_time,end_time:it.end_time||null,room:it.room||null,change_type:it.change_type||'normal'}))}
async function feedAdd(){
 const pv=state.feedPreview;
 if(!pv||state.feedBusy)return;
 state.feedBusy=pv.provider;render();
 const now=new Date().toISOString();
 const prov={retrieval_method:'public_school_feed',verification_state:'live_verified',synced_at:now};
 try{
  if(pv.kind==='ics_url'){
   await upsertTasks(pv.items,prov);
  }else{
   if(!state.schoolDataReady)throw Error('יש להריץ קודם את database-upgrade.sql ב־Supabase כדי להפעיל מערכת שעות');
   await upsertSchoolRows(shahafRowsToItems(pv.items,pv.url),prov);
  }
  const facts=connectionFacts('synced',false,now);
  await trackConnection(pv.provider,'synced',facts,null,{feed_url:pv.url,feed_stamp:pv.stamp||null});
  state.feedPreview=null;
  notice(`נשמרו ${pv.items.length} פריטים מהפיד לחשבון שלך. רענון ידני זמין בכל עת.`);
 }catch(e){notice(e.message,'error')}
 state.feedBusy=null;render();
}
async function feedRefresh(providerId){
 const p=PROVIDERS.find(x=>x.id===providerId);
 const c=state.connections.find(x=>x.provider===providerId);
 const url=c?.feed_url;
 if(!p||!url||state.feedBusy)return notice('אין פיד מחובר למערכת זו — חבר פיד קודם.','error');
 const kind=p.id==='petel'?'ics_url':'public_page';
 state.feedBusy=providerId;state.feedPreview=null;render();
 try{
  const text=await fetchFeed(url);
  const result=importFeedItems(text,p.id,kind);
  state.feedBusy=null;
  if(!result.items.length){render();return notice('הפיד לא החזיר פריטים — לא השתנה דבר.','error')}
  const now=new Date().toISOString();
  const prov={retrieval_method:'public_school_feed',verification_state:'live_verified',synced_at:now};
  if(kind==='ics_url'){
   await upsertTasks(result.items,prov);
  }else{
   if(!state.schoolDataReady)throw Error('יש להריץ קודם את database-upgrade.sql ב־Supabase כדי להפעיל מערכת שעות');
   await upsertSchoolRows(shahafRowsToItems(result.items,url),prov);
  }
  const facts=connectionFacts('synced',false,now);
  const stampChanged=!c.feed_stamp||c.feed_stamp!==result.stamp;
  await trackConnection(providerId,'synced',facts,null,{feed_url:url,feed_stamp:result.stamp||null});
  render();
  notice(stampChanged?`הפיד עודכן${result.stamp?` (מעודכן ל: ${result.stamp})`:''} — נשמרו ${result.items.length} פריטים ללא כפילויות.`:'לא זוהה שינוי במערכת השעות — הנתונים נשארו כפי שהיו.');
 }catch(e){state.feedBusy=null;render();notice(fetchFailureHint(e),'error')}
}
async function disconnectProvider(providerId){
 const p=PROVIDERS.find(x=>x.id===providerId);
 if(!p)return;
try{
 if(!confirm(`להפסיק את החיבור ל${p.name}? הנתונים שכבר נשמרו בחשבון לא יימחקו (למחיקה יש כפתור נפרד: "מחק נתונים ממערכת זו").`))return;
 const facts=connectionFacts('not_connected');
 await trackConnection(providerId,'not_connected',facts,null,{feed_url:null,feed_stamp:null});
 if(providerId==='classroom')state.token=null;
 notice(`החיבור ל${p.name} הופסק.`);
}catch(e){notice('הנתק נכשל: '+e.message,'error')}
}
async function deleteSourceData(providerId){
 const p=PROVIDERS.find(x=>x.id===providerId);
 if(!p)return;
 const taskCount=state.tasks.filter(t=>t.source===providerId).length;
 const itemCount=state.schoolItems.filter(x=>x.source===providerId).length;
 if(!taskCount&&!itemCount)return notice('אין נתונים ממערכת זו בחשבון שלך.');
 // M3 fix: for classroom, deletion must also kill the daily-sync binding, or
 // the 06:00 Apps Script re-ingests everything within 24h (deletion not durable).
 const hasDailyKey=providerId==='classroom'&&!!state.connections.find(x=>x.provider==='classroom')?.apps_script_key;
 if(hasDailyKey){
  if(!confirm(`למחוק לצמיתות: ${taskCount} משימות ו־${itemCount} פריטים מ${p.name}?\n\nהפעולה תבטל גם את הסנכרון היומי (מפתח Apps Script) כדי שהנתונים לא יוחזרו מחר בבוקר. אינה ניתנת לבטול.`))return;
 }else{
  if(!confirm(`למחוק לצמיתות: ${taskCount} משימות ו־${itemCount} פריטי לימודים מ${p.name}? פעולה זו אינה ניתנת לבטול.`))return;
 }
 try{
  const {error:te}=await state.client.from('tasks').delete().eq('source',providerId).eq('user_id',state.auth.id);
  if(te)throw te;
  if(state.schoolDataReady){
   const {error:ie}=await state.client.from('school_items').delete().eq('source',providerId).eq('user_id',state.auth.id);
   if(ie)throw ie;
  }
  if(hasDailyKey){
   await state.client.from('connections').update({apps_script_key:null}).eq('user_id',state.auth.id).eq('provider','classroom');
  }
  await loadAccount();
  notice(`נמחקו ${taskCount} משימות ו־${itemCount} פריטים מחשבונך.`);
 }catch(e){notice(e.message,'error')}
}
function genSyncKey(){const a=new Uint8Array(16);crypto.getRandomValues(a);return [...a].map(b=>b.toString(16).padStart(2,'0')).join('')}
async function setSyncKey(key){
 try{
  const c=state.connections.find(x=>x.provider==='classroom');
  const row={user_id:state.auth.id,provider:'classroom',apps_script_key:key,state:c?c.state:providerDefault(PROVIDERS.find(p=>p.id==='classroom')),last_sync_at:c?.last_sync_at||new Date().toISOString()};
  const {error}=await state.client.from('connections').upsert(row,{onConflict:'user_id,provider'});
  if(error)throw error;
  await loadAccount();
  if(key)notice('המפתח החדש נשמר. הדבק אותו בסקריפט (LUMIO_SYNC_KEY) כדי שסנכרון יומי ימשיך לעבוד.');
  else notice('הסנכרון היומי בוטל — המפתח הופסק.');
 }catch(e){
  if(String(e.message).includes('apps_script_key'))notice('יש להריץ database-upgrade-2.sql ב־Supabase כדי להפעיל סנכרון יומי.','error');
  else notice(e.message,'error');
 }
}
async function createSyncKey(){await setSyncKey(genSyncKey())}
async function rotateSyncKey(){if(!confirm('לסובב את מפתח הסנכרון? המפתח הישן יפסיק לעבוד מיד (יש להדביק את המפתח החדש בסקריפט).'))return;await setSyncKey(genSyncKey())}
async function cancelDailySync(){if(!confirm('לבטל את הסנכרון היומי? הסקריפט יפסיק לשלוח נתונים ללומיו.'))return;await setSyncKey(null)}
function copySyncKey(){const c=state.connections.find(x=>x.provider==='classroom');if(!c?.apps_script_key)return; navigator.clipboard?.writeText(c.apps_script_key).then(()=>notice('המפתח הועתק.')).catch(()=>notice('ההעתקה נכשלה — העתק ידנית.','error'))}
async function googleFetch(url,token){const response=await fetch(url,{headers:{Authorization:`Bearer ${token}`}});if(!response.ok){const t=await response.text();throw Error(`Google API ${response.status}: ${t.slice(0,220)}`)}return response.json()}
async function googlePages(path,key,token){let rows=[],pageToken='';do{const url=new URL('https://classroom.googleapis.com/v1/'+path);url.searchParams.set('pageSize','100');if(pageToken)url.searchParams.set('pageToken',pageToken);const data=await googleFetch(url.toString(),token);rows.push(...(data[key]||[]));pageToken=data.nextPageToken||''}while(pageToken&&rows.length<3000);return rows}
async function syncGoogle(){if(!state.token)throw Error('יש להתחבר מחדש ל־Google');const token=state.token;const courses=await googlePages('courses?courseStates=ACTIVE','courses',token);let tasks=[];for(const course of courses.filter(x=>x.courseState==='ACTIVE')){try{const work=await googlePages(`courses/${encodeURIComponent(course.id)}/courseWork`,'courseWork',token);const submissions=await googlePages(`courses/${encodeURIComponent(course.id)}/courseWork/-/studentSubmissions?userId=me`,'studentSubmissions',token);const byId=new Map(submissions.map(s=>[s.courseWorkId,s]));tasks.push(...work.map(w=>classroomToTask(w,course,byId.get(w.id))).filter(Boolean))}catch(err){console.warn('Classroom course skipped',course.id,err)}}await upsertTasks(tasks,{retrieval_method:'official_api',verification_state:'live_verified'});await trackConnection('classroom','synced',connectionFacts('synced'));notice(`סנכרון Classroom הסתיים: ${courses.length} קורסים, ${tasks.length} מטלות`)}
async function connectGoogle(){if(!state.config.google)return notice('Google Classroom עדיין לא הוגדר על ידי מנהל לומיו. יש להגדיר Google OAuth Client ID בקובץ config.mjs.','error');if(!window.google?.accounts?.oauth2){const script=document.createElement('script');script.src='https://accounts.google.com/gsi/client';script.async=true;document.head.append(script);return notice('טוען את ספריית Google. נסה שוב בעוד כמה שניות.','error')}try{const client=window.google.accounts.oauth2.initTokenClient({client_id:state.config.google,scope:'https://www.googleapis.com/auth/classroom.courses.readonly https://www.googleapis.com/auth/classroom.coursework.me.readonly',callback:async result=>{if(result.error)return notice('Google: '+result.error,'error');state.token=result.access_token;notice('ההרשאה התקבלה. מסנכרן Classroom…');try{await syncGoogle()}catch(e){notice(e.message,'error')}}});client.requestAccessToken({prompt:state.token?'':'consent'})}catch(e){notice(e.message,'error')}}

// Extension handoff: URL fragment contains only reviewed coursework. No session cookies,
// passwords or access tokens are sent. Prompt user before persisting to Supabase.
function decodeReaderPayload(fragment){
  if(!fragment.startsWith('#lumio_import='))return null;
  const encoded=fragment.slice('#lumio_import='.length);
  if(encoded.length>16000)throw Error('חבילת המשימות גדולה מדי להעברה ישירה');
  let decoded;try{decoded=decodeURIComponent(escape(atob(encoded.replace(/-/g,'+').replace(/_/g,'/'))))}catch{throw Error('חבילת ההעברה אינה תקינה')}
  const data=JSON.parse(decoded);
  if(!data||data.v!==1||!Array.isArray(data.tasks)||data.tasks.length>30)throw Error('נתוני ההעברה אינם תקינים');
  const allowed=['mashov','ofek','petel','shahaf','classroom'];
  if(!allowed.includes(data.source))throw Error('מקור המשימות אינו מוכר');
  const normalized=data.tasks.map(x=>normalizeTask({...x,description:'',status:'todo'},data.source)).filter(Boolean);
  if(!normalized.length)throw Error('לא נמצאו משימות בהעברה');
  return {source:data.source,tasks:normalized};
}
async function processReaderImport(){
  try{
    let packet=null;
    if(location.hash.startsWith('#lumio_import=')){
      const fragment=location.hash;
      history.replaceState(null,'',location.pathname+location.search);
      // Temporary local handoff survives a sign-in but is not put in the database unapproved.
      sessionStorage.setItem('lumio_reader_pending',fragment);
    }
    const stored=sessionStorage.getItem('lumio_reader_pending');
    if(!stored||!state.auth||!state.client)return;
    packet=decodeReaderPayload(stored);
    sessionStorage.removeItem('lumio_reader_pending');
    const src=apps.find(a=>a.id===packet.source)?.name||packet.source;
    if(!confirm(`Lumio Reader מצא ${packet.tasks.length} משימות מ${src}. האם לשמור אותן בחשבון לומיו שלך?`))return;
    await upsertTasks(packet.tasks,{retrieval_method:'user_import'});
    await trackConnection(packet.source,'imported');
    notice(`נשמרו ${packet.tasks.length} משימות מ${src}. זהו ייבוא של עמוד נבחר, לא סנכרון רקע.`);
  }catch(e){sessionStorage.removeItem('lumio_reader_pending');notice('ייבוא Reader נכשל: '+e.message,'error')}
}

initialize();
