// Lumio Ofek Bridge — capture.js (document_start)
// Passively captures JSON responses that look task-like, from the page's own
// authenticated session. No credentials are read or stored: the browser already
// holds the login; we only observe the data the page itself receives.
(() => {
  if (window.__lumioCaptureInstalled) return;
  window.__lumioCaptureInstalled = true;
  const store = (window.__lumioCaptured = window.__lumioCaptured || []);
  const MAX = 50;
  const MAX_BYTES = 2 * 1024 * 1024;

  const TASK_HINTS = /dueDate|due_date|due|submitDate|assignment|task|mishma|משימה|הגשה|מועד|subject|course|subjectTitle|title/i;
  const JUNK_HOSTS = /analytics|telemetry|googletagmanager|facebook|hotjar|clarity|sentry|newrelic/i;

  function looksTaskLike(o) {
    if (!o || typeof o !== 'object') return 0;
    let score = 0;
    const arr = Array.isArray(o) ? o : (o.items || o.tasks || o.activities || o.data || o.result);
    if (Array.isArray(arr) && arr.length) {
      const sample = arr.slice(0, 10);
      for (const it of sample) {
        if (!it || typeof it !== 'object') continue;
        const keys = Object.keys(it);
        const hit = keys.filter((k) => /due|assign|task|subject|course|title|name|date/i.test(k)).length;
        if (hit >= 2) score += 3;
        else if (hit === 1 && TASK_HINTS.test(keys.join(' '))) score += 1;
      }
      if (score >= 3) return score + arr.length * 0.1;
    }
    if (typeof o === 'object' && TASK_HINTS.test(JSON.stringify(Object.keys(o)).slice(0, 400))) {
      const keys = Object.keys(o).filter((k) => /due|assign|task|subject|course/i.test(k));
      if (keys.length >= 2) return keys.length;
    }
    return 0;
  }

  function maybeStore(url, text) {
    try {
      if (!text || text.length > MAX_BYTES || JUNK_HOSTS.test(url || '')) return;
      const data = JSON.parse(text);
      const score = looksTaskLike(data);
      if (score >= 3) {
        store.push({ url: url, score: score, data: data, at: Date.now() });
        if (store.length > MAX) store.shift();
      }
    } catch (e) { /* not JSON — ignore */ }
  }

  // --- fetch wrapper ---
  const origFetch = window.fetch;
  if (origFetch) {
    window.fetch = async function (...args) {
      const res = await origFetch.apply(this, args);
      try {
        const url = (typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url) || '');
        if (res && res.ok && /json|javascript|text/i.test(res.headers.get('content-type') || '')) {
          const clone = res.clone();
          clone.text().then((t) => maybeStore(url, t)).catch(() => {});
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
        if (this.responseType === '' || this.responseType === 'text') {
          maybeStore(this.__lumioUrl, this.responseText);
        }
      } catch (e) { /* ignore */ }
    });
    return origSend.apply(this, args);
  };
})();
