// Chat Bridge v2 — ChatGPT adapter.
// Ports the verified v1 ChatGPT logic (2026-11-10 DOM patch): the current
// data-chatgpt-search-unit-key DOM first, legacy data-message-author-role
// selectors kept as fallback. Verified selectors are preserved verbatim.
(() => {
  "use strict";

  function conversationId(loc) {
    const match = loc.pathname.match(/\/c\/([^/?#]+)/);
    return match ? match[1] : null;
  }

  function messageUnits(doc) {
    // Current ChatGPT DOM (2026-11+): every message unit carries
    // data-chatgpt-search-unit-key="...:user|assistant" plus stable
    // message UUIDs in data-chatgpt-search-message-ids.
    const fresh = [...doc.querySelectorAll('[data-chatgpt-search-unit-key]')].map((el) => {
      const key = el.getAttribute('data-chatgpt-search-unit-key') || '';
      const role = /(^|:)(user|assistant)$/.test(key) ? key.split(':').pop() : null;
      const id = (el.getAttribute('data-chatgpt-search-message-ids') || '').split(/\s+/)[0] || '';
      return role ? { node: el, role, key: id ? `dom:${id}` : '' } : null;
    }).filter(Boolean);
    if (fresh.length) return fresh;
    // Legacy DOM fallback
    return [...doc.querySelectorAll('[data-message-author-role]')].map((el) => {
      const role = el.getAttribute('data-message-author-role');
      const id = el.getAttribute('data-message-id') || (el.closest && el.closest('[data-message-id]')?.getAttribute('data-message-id')) || '';
      return (role === 'user' || role === 'assistant') ? { node: el, role, key: id ? `dom:${id}` : '' } : null;
    }).filter(Boolean);
  }

  function cleanText(node) {
    // Assistant units include a screen-reader label rendered as text.
    return (node.innerText || node.textContent || '').trim().replace(/^ChatGPT said:\s*/i, '').trim();
  }

  function findComposer(doc) {
    // Current DOM: visible ProseMirror editor (role=textbox, aria-label="Ask ChatGPT").
    const editables = [...doc.querySelectorAll('.ProseMirror[role="textbox"], [contenteditable="true"][role="textbox"]')]
      .filter((el) => el.getBoundingClientRect().height > 0);
    if (editables.length) return editables[editables.length - 1];
    return doc.querySelector('#prompt-textarea')
      || doc.querySelector('textarea[placeholder]')
      || doc.querySelector('[contenteditable="true"]');
  }

  function findSendButton(doc, composer) {
    const byLabel = () => [...doc.querySelectorAll('button')].find((button) =>
      /send message|send prompt|שלח/i.test(button.getAttribute('aria-label') || button.title || ''));
    return doc.querySelector('button[data-testid="send-button"]')
      || byLabel()
      || (function () {
        // Current DOM: the composer footer's primary-action slot swaps mic -> send once there is text.
        const root = composer || findComposer(doc);
        if (!root) return null;
        let container = root;
        for (let i = 0; i < 8 && container.parentElement; i += 1) {
          container = container.parentElement;
          if (container.querySelectorAll('button').length >= 2) break;
        }
        return [...container.querySelectorAll('button')].find((b) => b.querySelector('[class*="primary-action"]')) || null;
      })();
  }

  function isGenerating(doc) {
    return !!doc.querySelector('button[data-testid="stop-button"], button[aria-label*="Stop"], button[aria-label*="עצור"]');
  }

  function diagnose(doc) {
    const fresh = doc.querySelectorAll('[data-chatgpt-search-unit-key]').length;
    const legacy = doc.querySelectorAll('[data-message-author-role]').length;
    const editables = doc.querySelectorAll('.ProseMirror[role="textbox"], [contenteditable="true"]').length;
    const hasComposer = !!findComposer(doc);
    return {
      capture_failed: !fresh && !legacy,
      reason: (fresh || legacy)
        ? ""
        : (editables || hasComposer
          ? "message units not found (current + legacy selectors); composer present — layout likely changed"
          : "neither message units nor composer found — page may be pre-login or a different layout"),
      candidates: { fresh_units: fresh, legacy_units: legacy, editables, composer: hasComposer }
    };
  }

  window.__cb.registerAdapter({
    id: "chatgpt",
    label: "ChatGPT",
    domains: ["chatgpt.com", "chat.openai.com"],
    conversationId,
    extractUnits: messageUnits,
    cleanText,
    findComposer,
    findSendButton,
    isGenerating,
    diagnose
  });
})();
