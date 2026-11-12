// Lumio MOE Sync — content.js (isolated world, document_idle)
// Listens for captures from the MAIN-world interceptor (capture.js) via a DOM
// CustomEvent, maps them with map.js, and pushes them to Lumio's ingest
// endpoint — automatically, on a debounce, plus on page-hide. Reads only the
// per-user sync key (a capability token, NOT a password) from chrome.storage.
// The school-system login stays in the browser; Lumio never sees a password.
(() => {
  if (window.__lumioContentInstalled) return;
  window.__lumioContentInstalled = true;

  const DEFAULT_INGEST = 'https://zijinurzzwkuqxwhkiuw.supabase.co/functions/v1/apps-script-ingest';
  const DEFAULT_ANON = 'sb_publishable_YiFwqA7lOmOh1g9adNvo7Q_7QmY0rjs';
  const DEBOUNCE_MS = 3000;
  const MAX_RETRY = 3;

  // buffer: source -> Map(external_id -> item)  (idempotent upsert downstream)
  const buffer = new Map();
  let timer = null;
  let retryCount = 0;
  let warnedNoKey = false;

  function map() { return globalThis.__lumioMap; }

  function onCapture(e) {
    const detail = e && e.detail;
    if (!detail || !detail.data) return;
    try {
      const m = map();
      if (!m) return;
      const { source, items } = m.mapCapture({ url: detail.url, data: detail.data });
      if (!items.length) return;
      let b = buffer.get(source);
      if (!b) { b = new Map(); buffer.set(source, b); }
      for (const it of items) b.set(it.external_id, it);
      schedulePush();
      setChip('busy');
    } catch (err) { /* never break the page */ }
  }

  function schedulePush() {
    if (timer) clearTimeout(timer);
    timer = setTimeout(push, DEBOUNCE_MS);
  }

  async function getCfg() {
    try {
      const c = await chrome.storage.local.get(['syncKeys', 'ingestUrl', 'anonKey']);
      const keys = { mashov: '', ofek: '', petel: '' };
      const stored = (c.syncKeys && typeof c.syncKeys === 'object') ? c.syncKeys : {};
      for (const k of ['mashov', 'ofek', 'petel']) keys[k] = String(stored[k] || '').trim();
      return { keys, url: (c.ingestUrl || DEFAULT_INGEST).trim(), anon: (c.anonKey || DEFAULT_ANON).trim() };
    } catch (e) { return { keys: { mashov: '', ofek: '', petel: '' }, url: DEFAULT_INGEST, anon: DEFAULT_ANON }; }
  }

  async function push() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (!buffer.size) return;
    const cfg = await getCfg();
    const bufferedSources = [...buffer.keys()].filter((s) => buffer.get(s).size > 0);
    const anyKey = bufferedSources.some((s) => cfg.keys[s]);
    if (!anyKey) {
      if (!warnedNoKey) { warnedNoKey = true; setChip('nokey'); }
      return;
    }
    setChip('busy');
    let okAll = true;
    for (const [source, itemsMap] of [...buffer.entries()]) {
      const items = [...itemsMap.values()].slice(0, 500);
      if (!items.length) continue;
      const key = cfg.keys[source] || '';
      if (!key) continue; // no sync key for this system — leave buffered, warn via chip
      try {
        const res = await fetch(cfg.url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', apikey: cfg.anon, Authorization: 'Bearer ' + cfg.anon },
          body: JSON.stringify({ key, source, items }),
        });
        const data = await res.json().catch(() => ({}));
        if (res.ok && data.ok) {
          buffer.delete(source);
        } else { okAll = false; throw new Error(data.error || ('HTTP ' + res.status)); }
      } catch (e) {
        okAll = false;
        retryCount++;
        if (retryCount < MAX_RETRY) schedulePush();
        setChip('error');
      }
    }
    if (okAll) { retryCount = 0; setChip(buffer.size ? 'busy' : 'done'); }
  }

  // --- small floating status chip (bottom-left) ---
  const CHIP = {
    nokey: { t: '🐴 לומיו: הקלד את מפתח הסנכרון באפשרויות התוסף', c: '#b45309' },
    idle: { t: '🐴 לומיו מחובר — סנכרון אוטומטי', c: '#1d4ed8' },
    busy: { t: '🐴 לומיו מסנכרן…', c: '#1d4ed8' },
    done: { t: '🐴 ✓ לומיו סונכרן', c: '#166534' },
    error: { t: '🐴 ✗ לומיו: שגיאת סנכרון (מנסה שוב)', c: '#b91c1c' },
  };
  let chipEl = null;
  function setChip(state) {
    if (!chipEl) {
      chipEl = document.createElement('div');
      chipEl.id = '__lumio_chip';
      chipEl.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:2147483647;padding:6px 12px;border-radius:16px;color:#fff;font-size:12px;font-family:inherit;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.3);user-select:none;';
      (document.body || document.documentElement).appendChild(chipEl);
      chipEl.addEventListener('click', push);
    }
    const s = CHIP[state] || CHIP.idle;
    chipEl.textContent = s.t;
    chipEl.style.background = s.c;
  }

  // init
  function ready() {
    document.addEventListener('__lumio_capture', onCapture);
    window.addEventListener('pagehide', () => { try { push(); } catch (e) {} });
    (async () => {
      const cfg = await getCfg();
      const hasAny = Object.values(cfg.keys).some(Boolean);
      setChip(hasAny ? 'idle' : 'nokey');
    })();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready);
  else ready();
})();
