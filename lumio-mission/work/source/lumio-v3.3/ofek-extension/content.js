// Lumio Ofek Bridge — content.js (isolated world, document_idle)
// Floating button + send-to-Lumio. Reads the captured JSON from the MAIN world
// (window.__lumioCaptured) or falls back to visible-text scraping. Only the
// sync key (a capability token, not a password) is stored — in chrome.storage.
(() => {
  if (window.__lumioUiInstalled) return;
  window.__lumioUiInstalled = true;

  const DEFAULT_INGEST = 'https://zijinurzzwkuqxwhkiuw.supabase.co/functions/v1/apps-script-ingest';
  const DEFAULT_ANON = 'sb_publishable_YiFwqA7lOmOh1g9adNvo7Q_7QmY0rjs';

  // djb2 — stable, dependency-free id for dedupe
  function h(s) {
    let x = 5381;
    for (let i = 0; i < s.length; i++) x = ((x << 5) + x + s.charCodeAt(i)) >>> 0;
    return x.toString(16).padStart(8, '0');
  }

  function parseDue(raw) {
    if (!raw) return null;
    const s = String(raw).trim();
    let m = s.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (m) return `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}T00:00:00Z`;
    m = s.match(/(\d{1,2})[./](\d{1,2})[./](\d{4})/);
    if (m) return `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}T00:00:00Z`;
    return null;
  }

  // Extract candidate task objects from a captured JSON blob
  function extractFromBlob(blob) {
    const out = [];
    const data = blob.data;
    const candidates = [];
    const walk = (o) => {
      if (!o || typeof o !== 'object' || out.length >= 100) return;
      if (Array.isArray(o)) { for (const x of o.slice(0, 100)) walk(x); return; }
      const keys = Object.keys(o);
      const hasTitle = keys.some((k) => /^(title|name|subjectTitle|משימה)$/i.test(k));
      const hasDue = keys.some((k) => /due|submit|date/i.test(k));
      if (hasTitle && (hasDue || keys.some((k) => /subject|course/i.test(k)))) {
        candidates.push(o);
        return;
      }
      for (const k of ['items', 'tasks', 'activities', 'data', 'result', 'rows', 'children']) {
        if (o[k]) walk(o[k]);
      }
    };
    walk(data);
    for (const it of candidates) {
      const title = String(it.title ?? it.name ?? it.subjectTitle ?? '').trim().slice(0, 240);
      if (!title || title.length < 2) continue;
      const subject = String(it.subject ?? it.course ?? it.courseTitle ?? it.subjectName ?? '').trim().slice(0, 100);
      const due = parseDue(it.dueDate ?? it.due_date ?? it.submitDate ?? it.deadline ?? it.due);
      out.push({
        kind: 'task',
        external_id: ('ofek:' + h(title + '|' + (due || ''))).slice(0, 200),
        title,
        course_title: subject,
        due_at: due,
        status: /done|completed|submitted|הושלם/i.test(String(it.status ?? it.state ?? '')) ? 'done' : 'todo',
      });
    }
    return out;
  }

  // Visible-text fallback: list items / rows that look like "title ... date"
  function scrapeVisible() {
    const out = [];
    const nodes = document.querySelectorAll('li, tr, [class*="task"], [class*="activity"], [class*="item"]');
    for (const n of nodes) {
      if (out.length >= 100) break;
      const t = (n.innerText || '').replace(/\s+/g, ' ').trim();
      if (t.length < 6 || t.length > 300) continue;
      const m = t.match(/(\d{4})-(\d{1,2})-(\d{1,2})|(\d{1,2})[./](\d{1,2})[./](\d{4})/);
      if (!m) continue;
      const title = t.slice(0, 200);
      const due = m[1] ? `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}T00:00:00Z`
        : `${m[6]}-${m[4].padStart(2, '0')}-${m[5].padStart(2, '0')}T00:00:00Z`;
      out.push({
        kind: 'task',
        external_id: ('ofek:' + h(title + '|' + due)).slice(0, 200),
        title,
        course_title: '',
        due_at: due,
        status: /הושלם|done|completed/i.test(t) ? 'done' : 'todo',
      });
    }
    // dedupe by external_id
    const seen = new Set();
    return out.filter((x) => (seen.has(x.external_id) ? false : (seen.add(x.external_id), true)));
  }

  function bestItems() {
    const captured = (window.__lumioCaptured || []).slice().sort((a, b) => b.score - a.score);
    for (const blob of captured) {
      const items = extractFromBlob(blob);
      if (items.length >= 2) return { items, via: 'json' };
    }
    for (const blob of captured) {
      const items = extractFromBlob(blob);
      if (items.length === 1) return { items, via: 'json' };
    }
    return { items: scrapeVisible(), via: 'scrape' };
  }

  function toast(msg, isErr) {
    const el = document.getElementById('__lumio_btn');
    if (!el) return;
    const t = el.querySelector('.lumio-toast') || el.appendChild(Object.assign(document.createElement('div'), { className: 'lumio-toast' }));
    t.textContent = msg;
    t.style.cssText = `position:absolute;bottom:100%;margin-bottom:6px;padding:6px 10px;border-radius:8px;background:${isErr ? '#b91c1c' : '#166534'};color:#fff;font-size:12px;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.3)`;
    setTimeout(() => { t.textContent = ''; }, 5000);
  }

  async function send() {
    let cfg = {};
    try { cfg = await chrome.storage.local.get(['syncKey', 'ingestUrl', 'anonKey']); } catch (e) {}
    const key = (cfg.syncKey || '').trim();
    const url = (cfg.ingestUrl || DEFAULT_INGEST).trim();
    const anon = (cfg.anonKey || DEFAULT_ANON).trim();
    if (!key) { toast('חסר מפתח סנכרון — פתח את אפשרויות התוסף והקלד אותו', true); return; }
    const { items, via } = bestItems();
    if (!items.length) { toast('לא נמצאו משימות בדף — פתח את דף המשימות ואז לחץ', true); return; }
    const btn = document.getElementById('__lumio_btn');
    if (btn) btn.textContent = 'שולח...';
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', apikey: anon, Authorization: 'Bearer ' + anon },
        body: JSON.stringify({ key, source: 'ofek', items: items.slice(0, 500) }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.ok) {
        toast(`✓ נשמרו ${data.saved.tasks || 0} משימות (${via === 'json' ? 'מ-JSON' : 'מתצוגה'})`);
      } else {
        toast(`✗ ${data.error || ('שגיאה ' + res.status)}`, true);
      }
    } catch (e) {
      toast('✗ שגיאת רשת — בדוק את החיבור', true);
    } finally {
      if (btn) btn.textContent = '📤 לומיו';
    }
  }

  function install() {
    if (document.getElementById('__lumio_btn')) { send(); return; } // already there
    const btn = document.createElement('button');
    btn.id = '__lumio_btn';
    btn.textContent = '📤 לומיו';
    btn.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:2147483647;padding:8px 14px;border:none;border-radius:10px;background:#1d4ed8;color:#fff;font-size:14px;font-family:inherit;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.35)';
    btn.addEventListener('click', send);
    (document.body || document.documentElement).appendChild(btn);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
})();
