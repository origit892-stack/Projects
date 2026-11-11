const $=s=>document.querySelector(s);let items=[];
const esc=x=>String(x||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
function render(){ $('#items').innerHTML=items.map((x,i)=>`<div class="item"><div class="row"><b>משימה ${i+1}</b><button class="remove" data-remove="${i}">הסר</button></div><label>כותרת<input data-field="title" data-i="${i}" value="${esc(x.title)}"></label><label>מקצוע<input data-field="subject" data-i="${i}" value="${esc(x.subject||'')}"></label><label>תאריך (אופציונלי)<input type="date" data-field="due" data-i="${i}" value="${esc(x.due||'')}"></label><label>קישור<input data-field="url" data-i="${i}" value="${esc(x.url||'')}"></label></div>`).join('');document.querySelectorAll('[data-remove]').forEach(x=>x.onclick=()=>{items.splice(Number(x.dataset.remove),1);render()});document.querySelectorAll('[data-field]').forEach(el=>el.oninput=()=>{items[Number(el.dataset.i)][el.dataset.field]=el.value})}
$('#scan').onclick=async()=>{try{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});if(!tab?.id||!/^https?:/.test(tab.url))throw Error('פתח קודם אתר משימות בדפדפן');const result=await chrome.scripting.executeScript({target:{tabId:tab.id},func:()=>{
 const clean=x=>String(x||'').replace(/\s+/g,' ').trim();const visible=el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'};
 const selectors=['[data-assignment-id]','[data-task-id]','[class*="assignment"]','[class*="Assignment"]','[class*="homework"]','[class*="Homework"]','[class*="task-item"]','[class*="TaskItem"]','tr','article','li'];let found=[];for(const sel of selectors){const els=[...document.querySelectorAll(sel)].filter(visible).slice(0,100);for(const el of els){if(el.querySelector('input[type=password]')||el.closest('form[action*="login"]'))continue;const text=clean(el.innerText||'');if(text.length<8||text.length>350)continue;const title=clean(el.querySelector('h1,h2,h3,h4,[class*="title"],[class*="Title"],strong')?.innerText||text).slice(0,150);if(title.length<4||/^(התחברות|סיסמה|שם משתמש|כניסה|התנתקות)$/.test(title))continue;const href=el.querySelector('a[href]')?.href||location.href;found.push({title,subject:'',url:href})}if(found.length>=2&&sel!=='li')break}
 // Selection has priority: if user selected specific homework text, use it.
 const selection=clean(window.getSelection()?.toString());if(selection.length>3&&selection.length<500)found.unshift({title:selection.slice(0,150),subject:'',url:location.href});return found.filter((x,i,a)=>a.findIndex(y=>y.title===x.title)===i).slice(0,35)
 }});items=(result?.[0]?.result||[]);$('#info').textContent=`נמצאו ${items.length} פריטים אפשריים. בדוק ותקן לפני ייבוא — ייתכנו פריטים שאינם משימות.`;render()}catch(e){$('#info').textContent='שגיאה: '+e.message}}
$('#add').onclick=()=>{items.push({title:'',subject:'',url:'',due:''});render()};
$('#download').onclick=async()=>{const source=$('#source').value;const tasks=items.filter(t=>t.title.trim()).map((t,i)=>({source,external_id:`reader:${encodeURIComponent(t.url||'')}:${t.title.slice(0,90)}`,title:t.title.slice(0,240),subject:t.subject||'',due_at:t.due||null,source_url:/^https?:\/\//i.test(t.url||'')?t.url:null}));if(!tasks.length){$('#info').textContent='אין משימות לייצוא';return}const url='data:application/json;charset=utf-8,'+encodeURIComponent(JSON.stringify({source,exported_at:new Date().toISOString(),tasks},null,2));await chrome.downloads.download({url,filename:`lumio-${source}-${new Date().toISOString().slice(0,10)}.json`,saveAs:true});$('#info').textContent=`יוצאו ${tasks.length} משימות. ייבא את הקובץ בלומיו > חיבורים.`};

// User-approved direct handoff. No network request is made by the extension:
// the data is delivered to the Lumio page in a URL fragment, then immediately
// removed from the address bar. No cookies, credentials or tokens are collected.
function makePacket(){
 const source=$('#source').value;
 return {v:1,source,tasks:items.filter(t=>t.title.trim()).slice(0,20).map(t=>({
   source,external_id:`reader:${encodeURIComponent(t.url||'')}:${t.title.slice(0,90)}`,
   title:t.title.slice(0,240),subject:t.subject||'',due_at:t.due||null,
   source_url:/^https?:\/\//i.test(t.url||'')?t.url:null
 }))};
}
function encodePacket(packet){
 const bytes=new TextEncoder().encode(JSON.stringify(packet));
 let bin='';for(const b of bytes)bin+=String.fromCharCode(b);
 return btoa(bin).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
$('#send').onclick=async()=>{
 try{
   const u=new URL($('#lumioUrl').value.trim());
   if(!(['https:','http:'].includes(u.protocol)))throw Error('הכנס כתובת HTTPS');
   if(u.protocol!=='https:'&&!['localhost','127.0.0.1'].includes(u.hostname))throw Error('כתובת לומיו חייבת HTTPS');
   const packet=makePacket();if(!packet.tasks.length)throw Error('אין משימות להעברה');
   const payload=encodePacket(packet);
   if(payload.length>16000)throw Error('יותר מדי מידע להעברה ישירה. השתמש בקובץ JSON');
   await chrome.storage.local.set({lumioUrl:u.origin});
   await chrome.tabs.create({url:u.origin+'/#lumio_import='+payload});
   $('#info').textContent=`נפתח לומיו עם ${packet.tasks.length} משימות. אשר את הייבוא באתר.`;
 }catch(e){$('#info').textContent='שגיאה: '+e.message}
};
chrome.storage.local.get('lumioUrl').then(x=>{if(x.lumioUrl)$('#lumioUrl').value=x.lumioUrl});
