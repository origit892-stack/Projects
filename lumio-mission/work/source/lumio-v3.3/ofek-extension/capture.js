// Lumio MOE Sync — capture.js (MAIN world, document_start)
// Rides the browser's EXISTING Ministry-of-Education session. It only OBSERVES
// the JSON the page itself receives from the school system's own API — it never
// reads, stores, or transmits any credential. The browser already holds the
// login; we just watch the data flow and hand it to the isolated-world script
// (content.js) via a DOM CustomEvent. No password ever touches Lumio.
(() => {
  if (window.__lumioCaptureInstalled) return;
  window.__lumioCaptureInstalled = true;

  const MAX_BYTES = 2 * 1024 * 1024;
  const JUNK_HOSTS = /analytics|telemetry|googletagmanager|facebook|hotjar|clarity|sentry|newrelic|google-analytics|doubleclick/i;

  // A response is forwarded only if it looks like school data we care about:
  // homework/tasks, grades, or timetable shapes (per-system, see map.js).
  function looksLikeSchoolData(url, data) {
    if (!data || typeof data !== 'object') return false;
    const u = (url || '').toLowerCase();
    // Strong signals from the URL itself (Mashov /api/..., Ofek, PeTeL endpoints)
    if (/\/api\//.test(u) && /(homework|task|assignment|grade|score|timetable|lesson|report|mishma)/.test(u)) return true;
    // Otherwise judge by the shape.
    const probe = (o) => {
      if (!o || typeof o !== 'object') return false;
      const arr = Array.isArray(o) ? o : (o.items || o.tasks || o.activities || o.students || o.grades || o.lessons || o.data || o.result);
      if (Array.isArray(arr) && arr.length) {
        let hits = 0;
        for (const it of arr.slice(0, 12)) {
          if (!it || typeof it !== 'object') continue;
          const k = Object.keys(it).join(' ').toLowerCase();
          if (/(title|name|subject|mishma|משימה|מקצוע|grade|score|ציון|date|due|מועד|day|start|room)/.test(k)) hits++;
        }
        if (hits >= Math.min(2, arr.length)) return true;
      }
      return false;
    };
    if (probe(data)) return true;
    for (const k of ['items', 'tasks', 'activities', 'grades', 'lessons', 'students', 'data', 'result', 'homework']) {
      if (data[k] && probe(data[k])) return true;
    }
    return false;
  }

  function emit(url, text) {
    try {
      if (!text || text.length > MAX_BYTES) return;
      if (JUNK_HOSTS.test(url || '')) return;
      const data = JSON.parse(text);
      if (!looksLikeSchoolData(url, data)) return;
      // Cross the MAIN → isolated world boundary via a DOM CustomEvent.
      // detail is structured-cloned; plain JSON is cloneable.
      document.dispatchEvent(new CustomEvent('__lumio_capture', { detail: { url: url || '', data } }));
    } catch (e) { /* not JSON or not cloneable — ignore, never break the page */ }
  }

  // --- fetch wrapper ---
  const origFetch = window.fetch;
  if (origFetch) {
    window.fetch = async function (...args) {
      const res = await origFetch.apply(this, args);
      try {
        const url = (typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url) || '');
        const ct = (res && res.headers && res.headers.get('content-type')) || '';
        if (res && res.ok && /json|javascript/i.test(ct)) {
          const clone = res.clone();
          clone.text().then((t) => emit(url, t)).catch(() => {});
        }
      } catch (e) { /* never break the page */ }
      return res;
    };
  }

  // --- XHR wrapper ---
  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    this.__lumioUrl = url;
    return origOpen.call(this, method, url, ...rest);
  };
  XMLHttpRequest.prototype.send = function (...args) {
    this.addEventListener('load', () => {
      try {
        if (this.responseType === '' || this.responseType === 'text') emit(this.__lumioUrl, this.responseText);
      } catch (e) { /* ignore */ }
    });
    return origSend.apply(this, ...[args]);
  };
})();
