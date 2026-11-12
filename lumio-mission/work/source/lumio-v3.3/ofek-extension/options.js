// Lumio MOE Sync — options.js
// Stores ONE sync key per system (mashov / ofek / petel) — matching Lumio's
// per-connection key model. Each non-empty key is validated live against the
// ingest (which resolves the owner from the key itself). A key is a capability
// token, NOT a password; the school login stays in the browser.
const $ = (id) => document.getElementById(id);
const SOURCES = ['mashov', 'ofek', 'petel'];
const ANON = 'sb_publishable_YiFwqA7lOmOh1g9adNvo7Q_7QmY0rjs';
const DEFAULT_URL = 'https://zijinurzzwkuqxwhkiuw.supabase.co/functions/v1/apps-script-ingest';

chrome.storage.local.get(['syncKeys', 'ingestUrl', 'anonKey'], (cfg) => {
  const keys = (cfg.syncKeys && typeof cfg.syncKeys === 'object') ? cfg.syncKeys : {};
  for (const s of SOURCES) { const el = $('key-' + s); if (el) el.value = keys[s] || ''; }
  if ($('ingestUrl')) $('ingestUrl').value = cfg.ingestUrl || '';
});

$('save').addEventListener('click', async () => {
  const keys = {};
  let any = false;
  for (const s of SOURCES) { const v = ($('key-' + s).value || '').trim(); keys[s] = v; if (v) any = true; }
  if (!any) { setStatus('הקלד לפחות מפתח סנכרון אחד (מכרטיס המערכת המתאים בלומיו)', true); return; }
  const ingestUrl = ($('ingestUrl').value || '').trim();
  await chrome.storage.local.set({ syncKeys: keys, ingestUrl });
  // Validate each provided key (best-effort; a bad key just won't sync that system).
  const url = ingestUrl || DEFAULT_URL;
  let bad = 0, ok = 0;
  for (const s of SOURCES) {
    if (!keys[s]) continue;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', apikey: ANON, Authorization: 'Bearer ' + ANON },
        body: JSON.stringify({ key: keys[s], source: s, items: [] }),
      });
      if (res.status === 401) bad++;
      else if (res.ok) ok++;
      else bad++;
    } catch (e) { /* offline — treat as unverified, not bad */ }
  }
  if (bad > 0 && ok === 0) setStatus('✗ אף מפתח לא נמצא — וודא שהם נוצרו בלומיו (לא סובבו)', true);
  else if (bad > 0) setStatus(`⚠ נשמר. ${ok} מפתח(ים) תקין(ים), ${bad} לא זוהה — רק המערכות עם מפתח תקין ייסנכרנו`, true);
  else setStatus('✓ נשמר — כל המפתחות מזוהים. הסנכרון האוטומטי פעיל.');
});

function setStatus(msg, isErr) {
  const el = $('status');
  el.textContent = msg;
  el.className = isErr ? 'err' : 'ok';
}
