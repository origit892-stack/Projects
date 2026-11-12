// Lumio Ofek Bridge — options.js
const $ = (id) => document.getElementById(id);

chrome.storage.local.get(['syncKey', 'ingestUrl', 'anonKey'], (cfg) => {
  $('syncKey').value = cfg.syncKey || '';
  $('ingestUrl').value = cfg.ingestUrl || '';
});

$('save').addEventListener('click', async () => {
  const syncKey = $('syncKey').value.trim();
  const ingestUrl = $('ingestUrl').value.trim();
  if (!syncKey) {
    setStatus('יש להקליד את מפתח הסנכרון', true);
    return;
  }
  await chrome.storage.local.set({ syncKey, ingestUrl });
  // light validation: the key must be recognized by the ingest function
  const anon = 'sb_publishable_YiFwqA7lOmOh1g9adNvo7Q_7QmY0rjs';
  const url = ingestUrl || 'https://zijinurzzwkuqxwhkiuw.supabase.co/functions/v1/apps-script-ingest';
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: anon, Authorization: 'Bearer ' + anon },
      body: JSON.stringify({ key: syncKey, source: 'ofek', items: [] }),
    });
    if (res.status === 401) {
      setStatus('✗ המפתח לא מוכר — וודא שיוצר בלומיו ושלא סובב מאז', true);
      return;
    }
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.ok) setStatus('✓ נשמר — המפתח מוכר. אפשר לעבוד.');
    else setStatus('⚠ נשמר, אבל השליחה החוזרת דחתה: ' + (data.error || res.status), true);
  } catch (e) {
    setStatus('⚠ נשמר (הבדיקה לא הגיעה לשרת — תגדול בשליחה הבאה)', true);
  }
});

function setStatus(msg, isErr) {
  const el = $('status');
  el.textContent = msg;
  el.className = isErr ? 'err' : 'ok';
}
